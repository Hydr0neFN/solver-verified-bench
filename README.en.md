**English** · [繁體中文](README.md)

# solver-verified-bench

A small, reproducible task battery that compares the models reachable through the
Antigravity CLI. Each answer comes from a solver that also confirms it is unique, and
scoring is fully mechanical.

**Read this first:** [METHODOLOGY.md](METHODOLOGY.md) sets out what this benchmark
*cannot* support. The most important point is that the models had code execution during
every run, so these are model-plus-tools scores, not reasoning in isolation.

## At a glance

| | |
|---|---|
| Problem | Compare the models reachable through the Antigravity CLI on tasks with one verified answer. |
| What I built | Three tiers of generated tasks, solver-verified answer keys, a runner, a mechanical scorer and an ambiguity audit. |
| Result (measured) | `gemini-3.6-flash-high` scores **100.0%** on tiers 1 and 2 and **85.0%** on tier 3; `gpt-oss-120b-medium` scores **96.7%**, **77.1%** and **15.0%**. |
| Stack | Python generators, scorer and audit; bash runner; Antigravity CLI (`agy`) |
| Status | Paused 2026-10-10 — `bench/run-model.sh` runs need agy restored (Student re-verification). See [METHODOLOGY.md](METHODOLOGY.md). |

## How it works

```
bench/make_tier{1,2,3}.py --fixed seeds--> tasks/tier{1,2,3}/  (prompts)
                                             |
      bench/run-model.sh <model> --agy------>  results/raw/  (reply, stderr, timing)
                                             |
      truth/tier{1,2,3}.json --bench/score.py--> results/scores-tier{1,2,3}.json
```

1. A generator writes each prompt and emits the answer key.
2. The runner sends one prompt per `agy` call and keeps every raw reply, stderr and timing.
3. The scorer reads only the `FINAL: <answer>` line of each reply and compares it to the
   truth file.

In the curated key, `H8_spe` and `H12_falsepremise2` keep the same answer value, but
`truth/tier2.json` rewrites their shape: the string `"Rc|2|5"` becomes the token list
`["rc","2","5"]`, and the string `"REJECT"` becomes the `reject` kind. `F05_fab2` and
`H9_spec` were corrected; see [docs/answer-keys.md](docs/answer-keys.md).

The runner and its settings are described in [docs/bench.md](docs/bench.md).

## The three tiers

| tier | tasks | trials per cell | what it is |
|---|---|---|---|
| 1 — baseline | 15: 12 reasoning + 3 fact batteries | 2 | Baseline. Four of the five models scored 100% on all of it and `gpt-oss-120b-medium` scored 96.7%, so it tells models apart only at the floor. |
| 2 — hard | 14, solver-verified | 3 | Written after tier 1 saturated. Each answer comes from a brute-force or DFS solver that also confirmed the answer is unique. |
| 3 — rule induction | 4 composite grid-induction rules | 5 | Built to settle the single task on which tier 2 disagreed. |

## Results

Cells are mean score % for that task. Each tier has its own table:

- [Tier 1 — baseline](docs/results.md#tier-1--baseline)
- [Tier 2 — hard](docs/results.md#tier-2--hard)
- [Tier 3 — rule induction](docs/results.md#tier-3--rule-induction)

`⚠` means at least one cell for that model has fewer trials than the tier target
(2 / 3 / 5 for tiers 1 / 2 / 3): one sample fewer is enough to flip a ranking, so treat
that row's mean as indicative. `partial` means the model is missing whole tasks, and no
mean is given for it.

In short: four of the five models reach **100.0%** on tier 1. Tier 2 separates them from
**77.1%** to **100.0%**. Tier 3 separates them from **15.0%** to **85.0%**, and
`gemini-3.1-pro-high` drops from **97.6%** on tier 2 to **45.0%**.

## Latency

Only tiers with adequate timing coverage are shown. **Not comparable across accounts** —
see [ACCOUNT-PROVENANCE.md](ACCOUNT-PROVENANCE.md); serving capacity differs by
subscription tier and time of day.

| model | tier 1 | tier 2 | tier 3 |
|---|---|---|---|
| `gemini-3.7-flash-high` | — | 15s | 165s |
| `gemini-3.7-flash-medium` | — | 12s | 215s |
| `gemini-3.6-flash-high` | 9s | 11s | 65s |
| `gemini-3.1-pro-high` | — | 29s | 467s |
| `gpt-oss-120b-medium` | 10s | 16s | 55s |

## What it measures, and what it does not

The models had shell and code-execution access during every run, and they used it. On
the induction tasks they wrote and ran Python to search for the rule. So the scores
measure **model + tools**. Every model had the same access, which keeps the comparison
between models fair. The long latency on tier 3 comes from these iteration loops.

Limits: 2–5 trials per cell, tasks written for this test (so the numbers do not compare
to any published leaderboard), two subscription accounts, and one provider on one day.
The full list is in the Limits section of [METHODOLOGY.md](METHODOLOGY.md).

## Scoring rules

1. **A model that burns its own time budget scores zero, and is not dropped.** Dropping
   timeouts flatters whichever model is slowest. A timeout is also pinned: a later
   successful retry does not lift it, because otherwise re-running until it passes would
   erase a real failure.
2. **Infrastructure failures (quota, throttling, auth) are excluded** — those are not
   the model's doing. The two are told apart by stderr content and elapsed time.

The elapsed-time thresholds and the parallelism lesson behind the second rule are in
[docs/scoring.md](docs/scoring.md).

## Build / run

Python 3 and bash. To score the checked-in raw outputs, no `agy` is needed:

```bash
# regenerate the task files (fixed seeds, byte-identical to the ones used)
python bench/make_tier1.py && python bench/make_tier2.py && python bench/make_tier3.py

# sweep one model; skips any cell that already has output
bash bench/run-model.sh <model-slug> [parallelism] [tiers]

# score everything from the raw outputs
python bench/score.py

# check whether an induction task is actually unambiguous
python bench/audit_ambiguity.py
```

Two more checks: `python bench/verify_tier1.py` re-derives the hand-written tier-1 key
from scratch, and `python bench/render_readme.py` regenerates `README.md` and
`README.en.md` from `results/scores-tier{1,2,3}.json`. The `run-model.sh` sweep needs
the Antigravity CLI (`agy`), which is not runnable at the moment (see Status).

## Repo layout

| | |
|---|---|
| `bench/` | generators, runner, scorer, ambiguity audit |
| `tasks/` | the exact prompts sent to the models |
| `truth/` | answer keys as data, not code; includes why two keys were corrected |
| `results/` | scores plus every raw output, stderr and timing |
| `METHODOLOGY.md` | how it was run, and what it cannot support |
| `ACCOUNT-PROVENANCE.md` | which runs used which account, and why latency does not cross |
| `docs/` | deeper notes: [bench setup](docs/bench.md), [scoring](docs/scoring.md), [answer keys](docs/answer-keys.md), [full results](docs/results.md) |

## Docs

- [docs/bench.md](docs/bench.md) — the runner, the parallelism problem and how trials were uneven.
- [docs/scoring.md](docs/scoring.md) — how the scorer reads a reply and classifies a failure.
- [docs/answer-keys.md](docs/answer-keys.md) — how keys are verified, and the two that were corrected.
- [docs/results.md](docs/results.md) — all three result tables and the latency table, in full.

## License

MIT — see [LICENSE](LICENSE).
