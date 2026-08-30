#!/usr/bin/env python3
"""Re-derive the tier-1 answer keys from scratch and check truth/tier1.json against them.

Tier 1 was written by hand, so unlike tiers 2 and 3 its key is not emitted by a
generator. This closes that gap: every tier-1 answer that *can* be computed is computed
here, independently of the key file, and compared. A repository claiming its answers are
solver-verified should not have a tier where you are asked to take that on faith.

The few items that are not computable (keyword judgements on the two defect-identification
tasks, and the fact batteries) are listed as such rather than quietly skipped.

usage: python bench/verify_tier1.py
"""
import itertools, json, os, sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = json.load(open(os.path.join(ROOT, "truth", "tier1.json"), encoding="utf-8"))

derived = {}
notes = {}


# --------------------------------------------------------------- R01 knights and knaves
sols = []
for A, B, C in itertools.product([True, False], repeat=3):      # True = knight
    if A == (not B) and B == (not C) and C == ((not A) and (not B)):
        sols.append((A, B, C))
assert len(sols) == 1, sols
A, B, C = sols[0]
derived["R01_knaves"] = ["a" + ("knight" if A else "knave"),
                         "b" + ("knight" if B else "knave"),
                         "c" + ("knight" if C else "knave")]


# --------------------------------------------------------------- R02 logic grid
NAMES = ["Ana", "Ben", "Cy", "Dee", "Eli"]
DRINK = ["tea", "cola", "milk", "juice", "water"]
PET = ["cat", "dog", "fish", "bird", "rat"]
grid = []
for pn in itertools.permutations(NAMES):
    n = {p: i + 1 for i, p in enumerate(pn)}
    if n["Ana"] != 1 or n["Ben"] > n["Cy"] or n["Ben"] > n["Eli"] or n["Dee"] != 5:
        continue
    for pd in itertools.permutations(DRINK):
        d = {x: i + 1 for i, x in enumerate(pd)}
        if d["milk"] != 3 or d["water"] != 5:
            continue
        if abs(d["tea"] - n["Ben"]) != 1 or d["cola"] >= n["Cy"]:
            continue
        for pp in itertools.permutations(PET):
            p = {x: i + 1 for i, x in enumerate(pp)}
            if p["bird"] != 1 or p["cat"] != n["Dee"] or p["dog"] != d["juice"]:
                continue
            if abs(p["fish"] - n["Eli"]) != 2 or p["rat"] <= d["cola"]:
                continue
            grid.append((pn, pd, pp))
assert len(grid) == 1, f"logic grid has {len(grid)} solutions"
pn, pd, pp = grid[0]
derived["R02_grid"] = ["".join(pn).lower(), "".join(pd).lower(), "".join(pp).lower()]


# --------------------------------------------------------------- R05 base rate
p = 0.001 * 0.99 / (0.001 * 0.99 + 0.999 * 0.05)
derived["R05_bayes"] = round(p * 100, 2)


# --------------------------------------------------------------- R06 pirates
def pirates(n_pirates, coins):
    memo = {}

    def solve(n):
        if n in memo:
            return memo[n]
        if n == 1:
            memo[n] = [coins]
            return memo[n]
        prev = solve(n - 1)
        buy = (n + 1) // 2 - 1
        alloc = [0] * n
        spent = bought = 0
        for i in sorted(range(1, n), key=lambda i: (prev[i - 1], i)):
            if bought >= buy:
                break
            alloc[i] = prev[i - 1] + 1
            spent += alloc[i]
            bought += 1
        alloc[0] = coins - spent
        memo[n] = alloc
        return alloc
    return solve(n_pirates)


derived["R06_pirates"] = [str(x) for x in pirates(6, 100)]


# --------------------------------------------------------------- R07 constrained count
@lru_cache(None)
def count(pos, last, rem):
    if pos == 8:
        return 1 if rem == 0 else 0
    return sum(count(pos + 1, d, (rem + d) % 3) for d in range(1, 10) if d != last)


derived["R07_count"] = count(0, 0, 0)


# --------------------------------------------------------------- R09 grid rule
q = [[1, 0, 1, 1], [0, 1, 0, 0], [1, 1, 0, 1], [1, 0, 1, 0]]
derived["R09_arc"] = [q[i][j] ^ q[3 - i][3 - j] for i in range(4) for j in range(4)]


# --------------------------------------------------------------- R10 self-descriptive
# A 10-digit self-descriptive number has digits d0..d9 that together account for all
# ten positions, so sum(d) == 10. Enumerating compositions of 10 into 10 parts is
# 92378 candidates; scanning the integers themselves would be nine billion.
def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest

found = []
for digits in compositions(10, 10):
    if digits[0] == 0:
        continue
    if all(digits[i] == digits.count(i) for i in range(10)):
        found.append(int("".join(map(str, digits))))
assert len(found) == 1, f"expected a unique self-descriptive number, got {found}"
derived["R10_selfdesc"] = found[0]


# --------------------------------------------------------------- R12 Simpson
a_overall = (81 + 192) / (87 + 263)
b_overall = (234 + 55) / (270 + 80)
a_small, b_small = 81 / 87, 234 / 270
a_large, b_large = 192 / 263, 55 / 80
assert a_small > b_small and a_large > b_large and a_overall < b_overall, "not a paradox"
derived["R12_simpson"] = ("a", round(a_overall * 100, 2))


# --------------------------------------------------------------- compare
NOT_COMPUTABLE = {
    "R03_bug": "keyword judgement on a defect description",
    "R04_spec": "which requirement pair contradicts; argued, not computed",
    "R08_falsepremise": "the premise is fictional; the answer is to refuse",
    "R11_design": "keyword judgement on an architecture critique",
    "F01_tf": "24 factual claims, verified against sources by hand",
    "F02_fabrication": "invented papers and flags, verified by hand",
    "F03_precision": "documented constants, verified by hand",
}

ok = bad = 0
print("re-derived from scratch and compared with truth/tier1.json:\n")
for task in sorted(KEY):
    spec = KEY[task]
    if task in NOT_COMPUTABLE:
        print(f"  {task:<20} not computable  — {NOT_COMPUTABLE[task]}")
        continue
    got = derived.get(task)
    if task == "R12_simpson":
        want = (spec["prefer"], spec["overall"])
    elif task == "R05_bayes":
        want = spec["value"]
    else:
        want = spec["value"]
    match = got == want
    ok, bad = (ok + 1, bad) if match else (ok, bad + 1)
    tail = "" if match else f"   derived={got!r} key={want!r}"
    print(f"  {task:<20} {'match' if match else 'MISMATCH'}{tail}")

print(f"\n{ok} verified, {bad} mismatched, {len(NOT_COMPUTABLE)} not computable")
sys.exit(1 if bad else 0)
