# Which account each sweep ran on

Runs were executed through the Antigravity CLI, which is logged in to one Google
account at a time. Two accounts were used, so latency comparisons across models are
only clean *within* a block.

| block | models | account tier | window (2026-08-30) |
|---|---|---|---|
| A | gemini-3.7-flash-high, gemini-3.7-flash-medium, gemini-3.1-pro-high | Google AI Pro | 01:50 - 11:45 |
| B | gpt-oss-120b-medium, gemini-3.6-flash-high | Google AI Plus | 12:00 onward |

Block A ran until that account's Gemini 5-hour quota was exhausted. Block B started on a
second account with both quota groups full.

**Accuracy** is unaffected: the same model id serves the same weights regardless of the
subscription tier the request is billed to.

**Latency is NOT comparable across blocks.** Serving capacity and queueing may differ by
tier and by time of day. Any latency claim in the report must either compare models
inside one block, or be re-measured with all models on one account.

Known-clean latency comparison: 3.7-flash-high vs 3.7-flash-medium vs 3.1-pro-high
(all block A, Tier 2).
