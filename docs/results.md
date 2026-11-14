[English](results.md) · [繁體中文](results.zh-TW.md)

# Full results

[Back to README](../README.en.md)

Cells are mean score % for that task. `⚠` means at least one cell for that model has fewer
trials than the tier target (2 / 3 / 5 for tiers 1 / 2 / 3) — one sample fewer is enough to
flip a ranking, so treat that row's mean as indicative. `partial` means the model is
missing whole tasks, and no mean is given for it.

## Tier 1 — baseline

| model | F01 | F02 | F03 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.7-flash-medium` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.6-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.1-pro-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0% ⚠** |
| `gpt-oss-120b-medium` | 100 | 100 | 100 | 100 | 100 | 100 | 50 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **96.7%** |

## Tier 2 — hard

| model | F04 | F05 | H10 | H11 | H12 | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 100 | 100 | 100 | 38 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **95.5%** |
| `gemini-3.7-flash-medium` | 100 | 100 | 100 | 100 | 100 | 0 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 67 | **90.5%** |
| `gemini-3.6-flash-high` | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **100.0%** |
| `gemini-3.1-pro-high` | 100 | 100 | 100 | 100 | 100 | 67 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | **97.6%** |
| `gpt-oss-120b-medium` | 96 | 67 | 100 | 100 | 67 | 33 | 100 | 33 | 100 | 0 | 100 | 100 | 100 | 83 | **77.1%** |

## Tier 3 — rule induction

| model | A1 | A2 | A3 | A4 | mean |
|---|---|---|---|---|---|
| `gemini-3.7-flash-high` | 100 | 100 | 60 | 80 | **85.0%** |
| `gemini-3.7-flash-medium` | 80 | 100 | 60 | 80 | **80.0%** |
| `gemini-3.6-flash-high` | 80 | 100 | 60 | 100 | **85.0%** |
| `gemini-3.1-pro-high` | 0 | 100 | 40 | 40 | **45.0%** |
| `gpt-oss-120b-medium` | 0 | 60 | 0 | 0 | **15.0%** |

## Latency

Only tiers with adequate timing coverage are shown. **Not comparable across accounts** —
see [ACCOUNT-PROVENANCE.md](../ACCOUNT-PROVENANCE.md); serving capacity differs by
subscription tier and time of day.

| model | tier 1 | tier 2 | tier 3 |
|---|---|---|---|
| `gemini-3.7-flash-high` | — | 15s | 165s |
| `gemini-3.7-flash-medium` | — | 12s | 215s |
| `gemini-3.6-flash-high` | 9s | 11s | 65s |
| `gemini-3.1-pro-high` | — | 29s | 467s |
| `gpt-oss-120b-medium` | 10s | 16s | 55s |

These tables also appear in the README, which [bench/render_readme.py](../bench/render_readme.py)
generates from `results/scores-tier{1,2,3}.json`.
