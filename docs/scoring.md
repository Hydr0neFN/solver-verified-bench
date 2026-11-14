[English](scoring.md) · [繁體中文](scoring.zh-TW.md)

# Scoring

[Back to README](../README.en.md)

How `bench/score.py` turns a raw reply into a score, and how it tells a model failure
from an infrastructure failure.

## How a reply is scored

Scoring is mechanical. The prompt requires every reply to end with `FINAL: <answer>`;
the scorer takes the answer from the last such line and compares it with the key in
`truth/tier{1,2,3}.json`. Each answer is normalized before the comparison: lower case
and ASCII letters and digits only, which drops punctuation. The scorer writes
`results/scores-tier{1,2,3}.json` and prints a comparison table.

## Empty replies

Empty replies are not silently dropped:

1. **A model that burns its own time budget scores zero, and is not dropped.** Dropping
   timeouts flatters whichever model is slowest. A timeout is also pinned: a later
   successful retry does not lift it, because otherwise re-running until it passes would
   launder a real failure away.
2. **Infrastructure failures (quota, throttling, auth) are excluded** — those are not the
   model's doing. The two are told apart by stderr content and elapsed time.

The stderr markers the scorer looks for are `eligibility check failed`,
`authentication required`, `quota` and `resource_exhausted` for infrastructure, and
`timeout waiting for response` for a timeout. The timeout pin is at 590 s, because
`agy --print-timeout` was 600 s for tiers 2 and 3. The elapsed-time table that separates
a throttled run from a real time-out is in [bench.md](bench.md).
