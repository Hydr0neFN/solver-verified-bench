# Which account each sweep ran on

Runs were executed through the Antigravity CLI, which is logged in to one Google account
at a time. Two accounts were used, so latency comparisons are only clean *within* a
block.

| block | models | account tier | window (2026-08-30) |
|---|---|---|---|
| A | gemini-3.7-flash-high, gemini-3.7-flash-medium, gemini-3.1-pro-high | Google AI Pro | 01:50 - 11:45 |
| B | gpt-oss-120b-medium, gemini-3.6-flash-high (tiers 1-2, part of tier 3) | Google AI Plus | 12:00 - 12:15 |
| C | gemini-3.6-flash-high (rest of tiers 2-3) | Google AI Pro | 17:45 - 18:10 |

Block A ran until that account's Gemini 5-hour quota was exhausted. Block B started on a
second account and ended when *its* Gemini weekly limit ran out. Block C finished 3.6
after the first account's 5-hour bucket refilled.

**Accuracy is unaffected by any of this**: the same model id serves the same weights
whatever tier the request is billed to. Every accuracy number in the tables is
comparable.

**Latency is not comparable across blocks.** Serving capacity and queueing differ by
subscription tier and by time of day. In particular `gemini-3.6-flash-high` spans blocks
B and C, so its latency figures mix two accounts and should be read as indicative only.
The clean latency comparison is 3.7-flash-high vs 3.7-flash-medium vs 3.1-pro-high, all
of which ran entirely inside block A.
