[English](bench.md) · [繁體中文](bench.zh-TW.md)

# Bench setup

[Back to README](../README.en.md)

How the runner sweeps the tasks, why parallelism changes the result, and why one task
carries more trials than the rest. These notes come from [METHODOLOGY.md](../METHODOLOGY.md);
read that file for the full method.

## The runner

`bench/run-model.sh <model-slug> [parallelism] [tiers] [budget]` takes one optional
budget, for example `15m`, that overrides the per-tier print timeout. The runner gives
tier 1 six minutes (`6m`, 420 in the elapsed-seconds unit) and tiers 2 and 3 ten minutes
(`10m`, 700). It skips any cell that already has a non-empty output, so it is safe to
re-run after a quota block. The default parallelism is six. It calls
`agy -p <prompt> --model <slug> --output-format text`.

## Parallelism changes the result, so it is part of the method

The runner takes a parallelism argument. That is not a convenience knob — set it wrong
and you measure the harness instead of the model.

Running three tier-3 cells at once with a 10-minute budget, one model failed at a flat
**~201 s every time**, with an empty reply and nothing on stderr. Run alone with a
15-minute budget, the same task finished in **3 min 14 s with the correct answer**.
Nothing about the model changed; the parallel runs were being throttled, and scoring
them would have recorded "cannot solve it" for a task it solves. (That model was dropped
from these tables for unrelated reasons — it never got enough coverage to report — but
the lesson survives it.)

Failure duration is the tell, and the scorer uses it:

| elapsed before failure | reading | treatment |
|---|---|---|
| a few seconds | quota or capacity refusal | excluded, not the model's doing |
| ~200 s under parallelism | throttling | excluded; re-run sequentially |
| the whole budget (~600 s+) | the model did not converge | scored zero |

The Gemini models tolerated six-way parallelism. Not every model does. If you add one,
start it sequentially with a generous budget, and check the elapsed time on every
failure before believing it.

## Uneven trial counts on one task, and why

`H1_arc2` carries more trials than any other cell: nine for `gemini-3.6-flash-high` and
eight for `gemini-3.7-flash-high`, against three for everything else. That is deliberate.
It was the single task where those two models disagreed most, and three trials could not
tell a real gap from a run of luck — a lesson this benchmark had already learned the hard
way on the induction tier, where a 2-of-3 lead reversed completely once twenty trials
were run.

Both models were given the same extra trials; 3.7 has one fewer only because the run was
interrupted mid-pair. The gap widened rather than closed, which is why it is reported as
a finding rather than as noise. No other model was given extra trials, so read the
`H1_arc2` row as better-sampled than its neighbours rather than as a like-for-like
comparison of sample sizes.
