#!/usr/bin/env python3
"""Generate README.md (zh-TW) and README.en.md from the scored results.

Both files come from one computation, so they cannot disagree with each other or with
results/scores-tier*.json. Nothing here is transcribed by hand -- transcription is how
a report ends up claiming something the data does not.

usage: python bench/render_readme.py
"""
import collections, json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
TRIALS_PER_TIER = {1: 2, 2: 3, 3: 5}
LAT_COVERAGE_MIN = 0.9

ORDER = ["gemini-3.7-flash-high", "gemini-3.7-flash-medium", "gemini-3.6-flash-high",
         "gemini-3.1-pro-high", "claude-opus-4-6-thinking", "claude-sonnet-4-6",
         "gpt-oss-120b-medium"]

TIER_NAME = {
    1: ("Tier 1 &mdash; baseline", "Tier 1 — 基準"),
    2: ("Tier 2 &mdash; hard", "Tier 2 — 硬題"),
    3: ("Tier 3 &mdash; rule induction", "Tier 3 — 範例歸納"),
}


# --------------------------------------------------------------------------- data
def load():
    tiers = {}
    for t in (1, 2, 3):
        p = os.path.join(RES, f"scores-tier{t}.json")
        if os.path.exists(p):
            tiers[t] = json.load(open(p, encoding="utf-8"))
    return tiers


def cell(rows, task, model):
    ss = [r["score"] for r in rows if r["task"] == task and r["model"] == model
          and r["score"] is not None]
    return (sum(ss) / len(ss), len(ss)) if ss else (None, 0)


def summarise(tiers):
    models = [m for m in ORDER
              if any(r["model"] == m for rows in tiers.values() for r in rows)]
    extra = sorted({r["model"] for rows in tiers.values() for r in rows} - set(models))
    models += extra

    out = {}
    for t, rows in tiers.items():
        tasks = sorted({r["task"] for r in rows})
        per = {}
        for m in models:
            vals, trials = [], []
            for task in tasks:
                v, n = cell(rows, task, m)
                if v is not None:
                    vals.append(v)
                    trials.append(n)
            ms = sorted(r["ms"] / 1000 for r in rows if r["model"] == m and r.get("ms"))
            cells = [r for r in rows if r["model"] == m]
            cover = len(ms) / len(cells) if cells else 0
            per[m] = {
                "mean": sum(vals) / len(vals) if vals else None,
                "tasks_covered": len(vals), "tasks_total": len(tasks),
                "min_trials": min(trials) if trials else 0,
                "target_trials": TRIALS_PER_TIER[t],
                "median_s": statistics.median(ms) if cover >= LAT_COVERAGE_MIN else None,
                "runs": len(cells),
            }
        out[t] = {"tasks": tasks, "per": per}
    return models, out


def fmt_mean(d):
    if d["mean"] is None:
        return "—"
    if d["tasks_covered"] < d["tasks_total"]:
        return f"partial {d['tasks_covered']}/{d['tasks_total']}"
    flag = " ⚠" if d["min_trials"] < d["target_trials"] else ""
    return f"{d['mean'] * 100:.1f}%{flag}"


def table(models, summ, tier):
    tasks, per = summ[tier]["tasks"], summ[tier]["per"]
    head = "| model | " + " | ".join(t.split("_")[0] for t in tasks) + " | mean |"
    sep = "|---|" + "---|" * (len(tasks) + 1)
    lines = [head, sep]
    for m in models:
        d = per[m]
        if d["mean"] is None and d["runs"] == 0:
            continue
        cells = []
        for t in tasks:
            v, n = cell_from(summ, tier, t, m)
            cells.append("—" if v is None else f"{v * 100:.0f}")
        lines.append(f"| `{m}` | " + " | ".join(cells) + f" | **{fmt_mean(d)}** |")
    return "\n".join(lines)


CELLS = {}


def cell_from(summ, tier, task, model):
    return CELLS[(tier, task, model)]


def build_cells(tiers):
    for t, rows in tiers.items():
        for task in sorted({r["task"] for r in rows}):
            for m in {r["model"] for r in rows}:
                CELLS[(t, task, m)] = cell(rows, task, m)


# --------------------------------------------------------------------------- render
def render(models, summ, lang):
    zh = lang == "zh"
    L = []
    A = L.append

    if zh:
        A("# solver-verified-bench\n")
        A("一組小型、可重現的題庫，用來比較 Antigravity CLI 能取用的模型。"
          "每題答案都由 solver 產生並確認唯一解，計分完全機械化。\n")
        A("> 英文版：[README.en.md](README.en.md)\n")
        A("**先讀這個：**[METHODOLOGY.md](METHODOLOGY.md) 說明這份測試"
          "*不能*用來主張什麼。最重要的一點是模型在測試中有程式執行權，"
          "所以分數是「模型 + 工具」，不是純推理。\n")
    else:
        A("# solver-verified-bench\n")
        A("A small, reproducible task battery comparing the models reachable through the "
          "Antigravity CLI. Every answer is produced by a solver that also confirms it is "
          "unique, and scoring is entirely mechanical.\n")
        A("> 繁體中文版：[README.md](README.md)\n")
        A("**Read this first:** [METHODOLOGY.md](METHODOLOGY.md) sets out what this "
          "benchmark *cannot* support. The most important point is that the models had "
          "code execution during every run, so these are model-plus-tools scores, not "
          "reasoning in isolation.\n")

    A("## " + ("結果" if zh else "Results") + "\n")
    for t in sorted(summ):
        A(f"### {TIER_NAME[t][1 if zh else 0].replace('&mdash;', '—')}\n")
        A(table(models, summ, t) + "\n")

    if zh:
        A("格內為該題平均得分 %。`⚠` 表示該模型至少有一格的 trial 數低於該層目標"
          f"（Tier 1 各 2 次、Tier 2 各 3 次、Tier 3 各 5 次）——"
          "少一次抽樣就足以翻轉排名，看到 `⚠` 請把該列的平均當成參考值。"
          "`partial` 表示該模型有題目完全沒跑，這種情況不給平均。\n")
    else:
        A("Cells are mean score % for that task. `⚠` means at least one cell for that "
          "model has fewer trials than the tier target (2 / 3 / 5 for tiers 1 / 2 / 3) — "
          "one sample fewer is enough to flip a ranking, so treat that row's mean as "
          "indicative. `partial` means the model is missing whole tasks, and no mean is "
          "given for it.\n")

    # latency, only where coverage allows and only within one account block
    A("## " + ("延遲" if zh else "Latency") + "\n")
    if zh:
        A("僅列覆蓋率足夠的層。**跨帳號不可比** —— 見 "
          "[ACCOUNT-PROVENANCE.md](ACCOUNT-PROVENANCE.md)，"
          "不同訂閱層級與時段的服務容量不同。\n")
    else:
        A("Only tiers with adequate timing coverage are shown. **Not comparable across "
          "accounts** — see [ACCOUNT-PROVENANCE.md](ACCOUNT-PROVENANCE.md); serving "
          "capacity differs by subscription tier and time of day.\n")
    hdr = "| model | " + " | ".join(f"tier {t}" for t in sorted(summ)) + " |"
    A(hdr)
    A("|---|" + "---|" * len(summ))
    for m in models:
        cells = []
        for t in sorted(summ):
            d = summ[t]["per"][m]
            cells.append("—" if d["median_s"] is None else f"{d['median_s']:.0f}s")
        if set(cells) != {"—"}:
            A(f"| `{m}` | " + " | ".join(cells) + " |")
    A("")

    A("## " + ("重現" if zh else "Reproducing") + "\n")
    A("```bash")
    A("# regenerate the task files (fixed seeds, byte-identical to the ones used)"
      if not zh else "# 重新生成題目檔（固定 seed，與實際跑測用的逐位元相同）")
    A("python bench/make_tier1.py && python bench/make_tier2.py && python bench/make_tier3.py")
    A("")
    A("# sweep one model; skips any cell that already has output" if not zh
      else "# 跑單一模型；已有輸出的格子會自動跳過")
    A("bash bench/run-model.sh <model-slug> [parallelism] [tiers]")
    A("")
    A("# score everything from the raw outputs" if not zh else "# 從原始輸出重新計分")
    A("python bench/score.py")
    A("")
    A("# check whether an induction task is actually unambiguous" if not zh
      else "# 檢查某道歸納題的規則是否真的唯一")
    A("python bench/audit_ambiguity.py")
    A("```\n")

    A("## " + ("目錄" if zh else "Layout") + "\n")
    rows = [
        ("bench/", "生成器、runner、計分器、歧義稽核" if zh
                   else "generators, runner, scorer, ambiguity audit"),
        ("tasks/", "實際送給模型的題目全文" if zh else "the exact prompts sent to the models"),
        ("truth/", "答案，資料而非程式碼；含兩次改 key 的理由" if zh
                   else "answer keys as data, not code; includes why two keys were corrected"),
        ("results/", "分數 JSON + 全部原始輸出、stderr、計時" if zh
                     else "scores plus every raw output, stderr and timing"),
        ("METHODOLOGY.md", "怎麼測的，以及不能主張什麼" if zh
                           else "how it was run, and what it cannot support"),
        ("ACCOUNT-PROVENANCE.md", "哪些跑在哪個帳號，為何延遲不可跨組比"
                                  if zh else "which runs used which account, and why latency does not cross"),
    ]
    A("| | |")
    A("|---|---|")
    for a, b in rows:
        A(f"| `{a}` | {b} |")
    A("")

    A("## " + ("計分規則中值得注意的兩點" if zh else "Two scoring rules worth knowing") + "\n")
    if zh:
        A("1. **模型跑爆自己的時間預算 → 計 0 分，不剔除。** 剔除逾時等於偏袒最慢的模型。"
          "而且逾時一旦發生就被釘死：事後重跑成功也不會把那一格改回來，"
          "否則「重跑到過為止」就能把真實失敗洗掉。\n")
        A("2. **基礎設施失敗（配額、節流、認證）則排除不計**，那不是模型的問題。"
          "兩者用 stderr 內容與耗時區分。\n")
    else:
        A("1. **A model that burns its own time budget scores zero, and is not dropped.** "
          "Dropping timeouts flatters whichever model is slowest. A timeout is also "
          "pinned: a later successful retry does not lift it, because otherwise "
          "re-running until it passes would launder a real failure away.\n")
        A("2. **Infrastructure failures (quota, throttling, auth) are excluded** — those "
          "are not the model's doing. The two are told apart by stderr content and "
          "elapsed time.\n")

    A("## " + ("授權" if zh else "License") + "\n")
    A("MIT — see [LICENSE](LICENSE).\n")
    return "\n".join(L)


def main():
    tiers = load()
    if not tiers:
        print("no scores found; run bench/score.py first")
        return
    build_cells(tiers)
    models, summ = summarise(tiers)
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(render(models, summ, "zh"))
    open(os.path.join(ROOT, "README.en.md"), "w", encoding="utf-8").write(render(models, summ, "en"))
    print(f"wrote README.md and README.en.md for {len(models)} models, "
          f"tiers {sorted(summ)}")


if __name__ == "__main__":
    main()
