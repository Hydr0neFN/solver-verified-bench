[English](answer-keys.md) · [繁體中文](answer-keys.zh-TW.md)

# Answer keys

[Back to README](../README.en.md)

How each tier's answer key is checked, and the two keys that were corrected after the
results. Details per file are in [truth/README.md](../truth/README.md) and in the
`note` fields of `truth/tier2.json`.

## Verification per tier

- **Tier 1.** There is no generator output to diff the hand-written `tier1.json`
  against, so `bench/verify_tier1.py` re-derives every computable answer from scratch
  and compares it with the key. It reports **8 verified, 0 mismatched, 7 not computable**.
  The seven are listed by name in its output.
- **Tier 2.** `generated-tier2.json` holds the raw solver output; `tier2.json` is the
  curated key. Both are checked in, so the difference can be audited.
- **Tier 3.** The curated key holds the same values as the generated one; only the
  wrapper changed. `bench/audit_ambiguity.py` enumerates a 64-rule family and confirms
  exactly one prediction survives.

## Two answer keys were wrong, and were corrected after seeing results

Both were caught by the same rule: *if every model misses an item, suspect the key
before the models.* Both corrections were applied identically to all models, so neither
can favour one. Both are documented inline in `truth/tier2.json`.

1. **Largest exactly-representable integer in IEEE 754 binary64.** The key said
   `2^53`. Every model answered `2^1024 - 2^971`, which is correct; `2^53` answers the
   different question of the largest *n* below which every integer is representable.
2. **The scheduler spec-contradiction item.** It shipped with a redundant answer: the
   requirement "must reassign on lease expiry" contradicts both "executed at most once"
   and "never executed concurrently". 7 of 9 runs gave the stronger of the two pairs.
   The key now accepts either.

A third item was audited and survived. On one composite grid rule all models converged
on the same wrong grid, which usually signals an ambiguous task. `bench/audit_ambiguity.py`
enumerates a 64-rule family and confirms the examples pin the rule uniquely, and that
both parity values are demonstrated for every column the query depends on. The task is
sound; the models simply got it wrong together.
