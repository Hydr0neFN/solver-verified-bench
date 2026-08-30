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

## Update, later the same day

A third block was added when the first account's Gemini 5-hour bucket refilled and the
CLI was switched back to it.

| block | models | account tier | note |
|---|---|---|---|
| C | claude-sonnet-4-6, claude-opus-4-6-thinking | Google AI Pro | tier 3 only; billed to the CLAUDE+GPT quota group, which is separate from GEMINI |

Blocks B and C therefore both exist for the non-Gemini models. `gpt-oss-120b-medium` ran
entirely in block B (AI Plus); the two Claude models ran entirely in block C (AI Pro).
Comparing their latencies to each other, or to the Gemini models in block A, is not
meaningful. Their **accuracy** is comparable to everything else.
