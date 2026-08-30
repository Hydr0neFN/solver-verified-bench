# solver-verified-bench

A small, reproducible task battery comparing the models reachable through the Antigravity CLI. Every answer is produced by a solver that also confirms it is unique, and scoring is entirely mechanical.

> 繁體中文版：[README.md](README.md)

**Read this first:** [METHODOLOGY.md](METHODOLOGY.md) sets out what this benchmark *cannot* support. The most important point is that the models had code execution during every run, so these are model-plus-tools scores, not reasoning in isolation.

## Results

### Tier 1 — baseline

| model | F01 | F02 | F03 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.7-flash-medium` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.6-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.1-pro-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0% ⚠** |
| `gpt-oss-120b-medium` | 100 | 100 | 100 | 100 | 100 | 100 | 50 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **96.7%** |

### Tier 2 — hard

| model | F04 | F05 | H10 | H11 | H12 | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 100 | 100 | 100 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **95.2%** |
| `gemini-3.7-flash-medium` | 100 | 100 | 100 | 100 | 100 | 0 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 67 | **90.5%** |
| `gemini-3.6-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0% ⚠** |
| `gemini-3.1-pro-high` | 100 | 100 | 100 | 100 | 100 | 67 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **97.6%** |
| `gpt-oss-120b-medium` | 96 | 67 | 100 | 100 | 67 | 33 | 100 | 33 | 100 | 0 | 100 | 100 | 100 | 83 | **77.1%** |

### Tier 3 — rule induction

| model | A1 | A2 | A3 | A4 | mean |
|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 60 | 80 | **85.0%** |
| `gemini-3.7-flash-medium` | 80 | 100 | 60 | 80 | **80.0%** |
| `gemini-3.6-flash-high` | — | 100 | 67 | — | **partial 2/4** |
| `gemini-3.1-pro-high` | 0 | 100 | 40 | 40 | **45.0%** |
| `claude-opus-4-6-thinking` | — | 100 | — | — | **partial 1/4** |
| `claude-sonnet-4-6` | — | 100 | — | — | **partial 1/4** |
| `gpt-oss-120b-medium` | 0 | 60 | 0 | 0 | **15.0%** |

Cells are mean score % for that task. `⚠` means at least one cell for that model has fewer trials than the tier target (2 / 3 / 5 for tiers 1 / 2 / 3) — one sample fewer is enough to flip a ranking, so treat that row's mean as indicative. `partial` means the model is missing whole tasks, and no mean is given for it.

## Latency

Only tiers with adequate timing coverage are shown. **Not comparable across accounts** — see [ACCOUNT-PROVENANCE.md](ACCOUNT-PROVENANCE.md); serving capacity differs by subscription tier and time of day.

| model | tier 1 | tier 2 | tier 3 |
|---|---|---|---|
| `gemini-3.7-flash-high` | — | 14s | 165s |
| `gemini-3.7-flash-medium` | — | 12s | 215s |
| `gemini-3.6-flash-high` | 9s | 10s | 24s |
| `gemini-3.1-pro-high` | — | 29s | 467s |
| `claude-opus-4-6-thinking` | — | — | 7s |
| `claude-sonnet-4-6` | — | — | 6s |
| `gpt-oss-120b-medium` | 10s | 16s | 55s |

## Reproducing

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

## Layout

| | |
|---|---|
| `bench/` | generators, runner, scorer, ambiguity audit |
| `tasks/` | the exact prompts sent to the models |
| `truth/` | answer keys as data, not code; includes why two keys were corrected |
| `results/` | scores plus every raw output, stderr and timing |
| `METHODOLOGY.md` | how it was run, and what it cannot support |
| `ACCOUNT-PROVENANCE.md` | which runs used which account, and why latency does not cross |

## Two scoring rules worth knowing

1. **A model that burns its own time budget scores zero, and is not dropped.** Dropping timeouts flatters whichever model is slowest. A timeout is also pinned: a later successful retry does not lift it, because otherwise re-running until it passes would launder a real failure away.

2. **Infrastructure failures (quota, throttling, auth) are excluded** — those are not the model's doing. The two are told apart by stderr content and elapsed time.

## License

MIT — see [LICENSE](LICENSE).
