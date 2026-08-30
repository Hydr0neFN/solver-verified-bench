# Answer keys

`tierN.json` is what `bench/score.py` reads. `generated-tierN.json` is what the
generators emit straight from their solvers, before any curation. Both are checked in
so the difference between them is auditable rather than asserted.

Run `python bench/make_tier2.py && python bench/make_tier3.py` to regenerate the
`generated-*` files and diff them yourself. The prompts in `tasks/` regenerate
byte-identically from the same fixed seeds.

## Tier 1

`tier1.json` is hand-written. Its tasks are fixed puzzles whose answers were verified by
brute force during construction (knights-and-knaves enumeration, a permutation search
for the logic grid, a DP for the constrained count, and so on), but the generator does
not emit a key file, so there is nothing to diff. The answers are checkable directly:
every one of them is a short fact you can verify with a few lines of Python.

## Tier 2 — how the curated key differs from the generated one

| task | relationship |
|---|---|
| F04_tf2, H10_race, H11_seq, H1_arc2, H2_csp, H3_count, H4_crypt, H5_recur, H6_bayesnet, H7_proof | identical value |
| H8_spe | same answer, rewritten from the string `"Rc\|2\|5"` to the token list `["rc","2","5"]` |
| H12_falsepremise2 | same answer, rewritten from a `"REJECT"` string to the `reject` kind |
| F05_fab2 | **corrected.** The key demanded `2^53` as the largest exactly-representable integer in binary64. Every model answered `2^1024 - 2^971`, which is right; `2^53` answers a different question. The key now accepts both readings. |
| H9_spec | **corrected.** The item shipped with a redundant answer: "must reassign on lease expiry" contradicts both "executed at most once" and "never executed concurrently". 7 of 9 runs gave the stronger pair. The key now accepts either. |

Both corrections were applied identically to every model, and both are recorded in a
`note` field inside `tier2.json` itself, not only here.

## Tier 3

Every entry is a grid, and the curated file carries the same values as the generated
one — only the wrapper changed. `bench/audit_ambiguity.py` additionally checks that the
worked example's rule is uniquely determined by its examples, by enumerating a 64-rule
family and confirming exactly one prediction survives.
