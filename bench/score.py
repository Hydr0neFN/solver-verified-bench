#!/usr/bin/env python3
"""Score every tier from the raw model outputs.

Reads  truth/tier{1,2,3}.json  +  results/raw/tier{1,2,3}/*.txt
Writes results/scores-tier{1,2,3}.json and prints a comparison table.

Scoring is mechanical. Every answer is taken from the last line of the reply, which
the prompt requires to be `FINAL: <answer>`.

Empty replies are NOT silently dropped:
  * the model burned its own time budget and returned nothing  -> scored 0
  * the harness or the provider failed (quota, auth)           -> excluded
Dropping timeouts would flatter whichever model is slowest, so it is not done.

usage: python bench/score.py [--tier N] [--quiet]
"""
import argparse, collections, glob, json, os, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUTH_DIR = os.path.join(ROOT, "truth")
RAW_DIR = os.path.join(ROOT, "results", "raw")
OUT_DIR = os.path.join(ROOT, "results")

# a run that returned nothing because the provider refused is not the model's fault
INFRA_MARKERS = ("eligibility check failed", "authentication required",
                 "quota", "resource_exhausted")
TIMEOUT_MARKERS = ("timeout waiting for response",)
PRINT_TIMEOUT_MS = 590_000     # agy --print-timeout was 600s for tiers 2 and 3
TRIALS_PER_TIER = {1: 2, 2: 3, 3: 5}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def final_line(txt):
    ls = [l.strip() for l in txt.splitlines() if l.strip().upper().startswith("FINAL:")]
    return ls[-1][len("FINAL:"):].strip() if ls else ""


# --------------------------------------------------------------------------- kinds
def k_tokens(spec, fl, txt):
    n = norm(fl)
    return 1.0 if all(t in n for t in spec["value"]) else 0.0


def k_groups(spec, fl, txt):
    n = norm(fl)
    hits = sum(1 for g in spec["value"] if g in n)
    return round(hits / len(spec["value"]), 4)


def k_ordered_tokens(spec, fl, txt):
    want = spec["value"]
    got = [w for w in re.findall(r"[A-Za-z]+", fl) if w.lower() not in spec.get("skip", [])]
    if len(got) < len(want):
        return 0.0
    return round(sum(1 for a, b in zip(got[:len(want)], want) if a.lower() == b.lower())
                 / len(want), 4)


def k_keywords(spec, fl, txt):
    hay = (fl + " " + txt[-spec.get("tail", 2000):]).lower()
    return 1.0 if all(any(re.search(p, hay) for p in grp) for grp in spec["value"]) else 0.0


def k_labels(spec, fl, txt):
    n = norm(fl)
    return 1.0 if all(v in n for v in spec["value"]) else 0.0


def k_labels_any(spec, fl, txt):
    """One required label plus any one of several acceptable partners."""
    u = fl.upper()
    need = re.search(r"\b%s\b" % spec["require"], u)
    full = any(re.search(r"\b%s\b" % a, u) for a in spec["accept"])
    if need and full:
        return 1.0
    partial = any(re.search(r"\b%s\b" % a, u) for a in spec.get("partial", []))
    return 0.5 if partial and (need or full) else 0.0


def k_float(spec, fl, txt):
    m = re.search(r"(\d+\.\d+)", fl)
    return 1.0 if m and abs(float(m.group(1)) - spec["value"]) <= spec.get("tol", 0.05) else 0.0


def k_labelled_ints(spec, fl, txt):
    got = re.findall(spec["pattern"], fl)
    return 1.0 if got[:len(spec["value"])] == spec["value"] else 0.0


def k_int(spec, fl, txt):
    nums = re.findall(r"-?\d[\d,]*", fl)
    return 1.0 if nums and nums[0].replace(",", "") == str(spec["value"]) else 0.0


def k_reject(spec, fl, txt):
    return 1.0 if "reject" in fl.lower() else 0.0


def k_grid(spec, fl, txt):
    got = re.findall(r"[01]", fl)
    want = [str(x) for x in spec["value"]]
    return 1.0 if got[:len(want)] == want else 0.0


def k_simpson(spec, fl, txt):
    low = fl.lower().replace(" ", "")
    pref = re.search(r"prefer=([ab])", low)
    tail = fl.split("A_overall")[-1] if "A_overall" in fl else fl
    pctm = re.search(r"(\d+\.\d+)", tail)
    a = 1.0 if pref and pref.group(1) == spec["prefer"] else 0.0
    b = 1.0 if pctm and abs(float(pctm.group(1)) - spec["overall"]) <= spec.get("tol", 0.05) else 0.0
    return round((a + b) / 2, 4)


def k_truefalse(spec, fl, txt):
    got = dict(re.findall(r"(\d+)\s*=\s*([TF])", fl.upper()))
    want = spec["value"]
    if len(got) < spec.get("min_parsed", len(want) - 4):
        return None
    return round(sum(1 for i, v in enumerate(want, 1) if got.get(str(i)) == v) / len(want), 4)


def k_fabrication(spec, fl, txt):
    got = dict(re.findall(r"(Q[1-9])\s*=\s*([^,]+)", fl.upper()))
    if len(got) < spec.get("min_parsed", 4):
        return None
    hits = sum(1 for q in spec["notreal"] if "NOTREAL" in got.get(q, ""))
    for q, pat in spec.get("real", {}).items():
        v = got.get(q, "")
        if re.search(pat, v, re.I) and "NOTREAL" not in v:
            hits += 1
    return round(hits / (len(spec["notreal"]) + len(spec.get("real", {}))), 4)


def k_per_key_regex(spec, fl, txt):
    got = dict(re.findall(r"(Q[1-9])\s*=\s*([^,]+)", fl))
    if len(got) < spec.get("min_parsed", 4):
        return None
    hits = sum(1 for k, pat in spec["value"].items()
               if re.search(pat, got.get(k, ""), re.I))
    return round(hits / len(spec["value"]), 4)


KINDS = {
    "tokens": k_tokens, "groups": k_groups, "ordered_tokens": k_ordered_tokens,
    "keywords": k_keywords, "labels": k_labels, "labels_any": k_labels_any,
    "float": k_float, "labelled_ints": k_labelled_ints, "int": k_int,
    "reject": k_reject, "grid": k_grid, "simpson": k_simpson,
    "truefalse": k_truefalse, "fabrication": k_fabrication,
    "per_key_regex": k_per_key_regex,
}


# --------------------------------------------------------------------------- driver
def why_empty(tier, task, model, trial, ms, rc):
    p = os.path.join(RAW_DIR, f"tier{tier}", "logs", f"{task}__{model}__{trial}.err")
    err = ""
    try:
        err = open(p, encoding="utf-8", errors="replace").read().lower()
    except OSError:
        pass
    if any(s in err for s in INFRA_MARKERS):
        return "infra"
    if any(s in err for s in TIMEOUT_MARKERS):
        return "timeout"
    # agy can burn its whole --print-timeout and exit quietly
    if rc not in (0, None) and (ms or 0) >= PRINT_TIMEOUT_MS:
        return "timeout"
    return "unknown"


def score_tier(tier):
    truth = json.load(open(os.path.join(TRUTH_DIR, f"tier{tier}.json"), encoding="utf-8"))

    # Every attempt is kept, not just the last one, because cells were re-run whenever
    # the provider failed and the history is the only record of what happened.
    #
    # An earlier version of this scorer pinned any cell with a timeout to zero, on the
    # reasoning that re-running until it passes launders a real failure. That rule was
    # withdrawn once a bug was found in the runner: a failing re-run used to overwrite
    # a previous successful answer with an empty file, so some cells that the model had
    # solved looked like timeouts. Penalising those would blame the model for a defect
    # in the harness. The rule now is simply: score what the model actually produced,
    # and report retries-after-timeout separately instead of folding them into the mean.
    attempts = collections.defaultdict(list)
    tf = os.path.join(RAW_DIR, f"tier{tier}", "timings.csv")
    if os.path.exists(tf):
        for line in open(tf, encoding="utf-8"):
            p = line.strip().split("|")
            if len(p) == 5:
                attempts[(p[0], p[1], p[2])].append((int(p[3]), int(p[4])))
    timings = {k: v[-1] for k, v in attempts.items()}
    had_timeout = {k for k, v in attempts.items()
                   if any(rc != 0 and ms >= PRINT_TIMEOUT_MS for rc, ms in v)}
    had_success = {k for k, v in attempts.items() if any(rc == 0 for rc, _ in v)}

    rows = []
    for f in sorted(glob.glob(os.path.join(RAW_DIR, f"tier{tier}", "*.txt"))):
        task, model, trial = os.path.basename(f)[:-4].split("__")
        trial = trial.lstrip("t")
        txt = open(f, encoding="utf-8", errors="replace").read()
        spec = truth.get(task)
        rc, ms = timings.get((task, model, trial), (None, None))

        key = (task, model, trial)
        sc, reason = None, None
        if spec is None:
            reason = "no-truth"
        elif txt.strip():
            sc = KINDS[spec["kind"]](spec, final_line(txt), txt)
        elif key in had_success:
            # the model answered at least once, but the answer was overwritten by a
            # later failing re-run before the runner was fixed -- lost, not failed
            reason = "lost-to-clobber"
        else:
            reason = why_empty(tier, task, model, trial, ms, rc)
            if reason == "timeout":
                sc = 0.0                        # never delivered inside its own budget
        rows.append({"task": task, "model": model, "trial": trial,
                     "score": sc, "empty_reason": reason, "rc": rc, "ms": ms,
                     "retried_after_timeout": key in had_timeout and key in had_success})
    return rows


def summarise(all_rows, quiet=False):
    models = sorted({r["model"] for rows in all_rows.values() for r in rows})
    if quiet:
        return
    for tier, rows in sorted(all_rows.items()):
        tasks = sorted({r["task"] for r in rows})
        print(f"\n=== tier {tier} " + "=" * 52)
        print(f"{'task':<26}" + "".join(f"{m[:22]:>24}" for m in models))
        agg = collections.defaultdict(list)
        for t in tasks:
            line = f"{t:<26}"
            for m in models:
                ss = [r["score"] for r in rows
                      if r["task"] == t and r["model"] == m and r["score"] is not None]
                if ss:
                    v = sum(ss) / len(ss)
                    agg[m].append(v)
                    line += f"{v * 100:>19.0f}({len(ss)}) "
                else:
                    line += f"{'--':>24}"
            print(line)
        print("-" * (26 + 24 * len(models)))
        # A mean over a subset of the tasks is not comparable to a mean over all of
        # them, so it is withheld rather than printed with a caveat nobody reads.
        line = f"{'MEAN':<26}"
        for m in models:
            if not agg[m]:
                line += f"{'--':>24}"
            elif len(agg[m]) < len(tasks):
                line += f"{'partial ' + str(len(agg[m])) + '/' + str(len(tasks)):>24}"
            else:
                line += f"{sum(agg[m]) / len(agg[m]) * 100:>19.1f}    "
        print(line)

        # Task coverage is not enough. A cell scored over 2 trials instead of 5 swings
        # on a single lucky run, and that is exactly how a weaker model can appear to
        # win a tier mean. Show the thinnest cell per model so the reader can discount.
        target = TRIALS_PER_TIER[tier]
        tl = f"{'min trials/cell':<26}"
        for m in models:
            counts = []
            for t in tasks:
                n = len([r for r in rows if r["task"] == t and r["model"] == m
                         and r["score"] is not None])
                if n:
                    counts.append(n)
            if not counts:
                tl += f"{'--':>24}"
            else:
                lo = min(counts)
                tl += f"{(str(lo) + ' of ' + str(target) + (' !' if lo < target else '')):>24}"
        print(tl)

        # Reliability, kept out of the mean on purpose: how many cells only produced an
        # answer after an earlier attempt had burned the whole time budget, and how many
        # were lost to the runner bug described above.
        rl = f"{'timeout then retry':<26}"
        for m in models:
            nr = sum(1 for r in rows if r["model"] == m and r.get("retried_after_timeout"))
            lost = sum(1 for r in rows if r["model"] == m
                       and r.get("empty_reason") == "lost-to-clobber")
            txt = f"{nr}" + (f" (+{lost} lost)" if lost else "")
            rl += f"{txt:>24}"
        print(rl)

        # Latency needs near-complete timing coverage to mean anything; tier 1's
        # timings file was truncated early in the run, so it is usually withheld here.
        lat = f"{'median s':<26}"
        for m in models:
            cells = [r for r in rows if r["model"] == m]
            ms = sorted(r["ms"] / 1000 for r in cells if r.get("ms"))
            cover = len(ms) / len(cells) if cells else 0
            lat += (f"{statistics.median(ms):>19.1f}    " if cover >= 0.9
                    else f"{'cover ' + format(cover * 100, '.0f') + '%':>24}")
        print(lat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", type=int, choices=[1, 2, 3])
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    tiers = [a.tier] if a.tier else [1, 2, 3]
    os.makedirs(OUT_DIR, exist_ok=True)
    all_rows = {}
    for t in tiers:
        if not os.path.isdir(os.path.join(RAW_DIR, f"tier{t}")):
            continue
        rows = score_tier(t)
        all_rows[t] = rows
        with open(os.path.join(OUT_DIR, f"scores-tier{t}.json"), "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1)
    summarise(all_rows, a.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
