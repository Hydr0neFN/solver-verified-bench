"""Is H1_arc2's rule uniquely determined by its examples? Enumerate a rule family and see."""
import random, itertools

N = 4
random.seed(11)


def rg():
    return [[random.randint(0, 1) for _ in range(N)] for _ in range(N)]


# regenerate exactly the grids mktier2.py used
ex = [rg() for _ in range(4)]
q = rg()

T = {
    "identity":   lambda g: [[g[i][j] for j in range(N)] for i in range(N)],
    "rot90cw":    lambda g: [[g[N - 1 - j][i] for j in range(N)] for i in range(N)],
    "rot90ccw":   lambda g: [[g[j][N - 1 - i] for j in range(N)] for i in range(N)],
    "rot180":     lambda g: [[g[N - 1 - i][N - 1 - j] for j in range(N)] for i in range(N)],
    "transpose":  lambda g: [[g[j][i] for j in range(N)] for i in range(N)],
    "antitrans":  lambda g: [[g[N - 1 - j][N - 1 - i] for j in range(N)] for i in range(N)],
    "fliph":      lambda g: [[g[i][N - 1 - j] for j in range(N)] for i in range(N)],
    "flipv":      lambda g: [[g[N - 1 - i][j] for j in range(N)] for i in range(N)],
}


def colpar(g):
    return [sum(g[i][j] for i in range(N)) % 2 for j in range(N)]


def rowpar(g):
    return [sum(g[i]) % 2 for i in range(N)]


# parity vector source: from original or from the transformed grid; by row or column
PV = {
    "colpar(orig)": lambda g, r: colpar(g),
    "rowpar(orig)": lambda g, r: rowpar(g),
    "colpar(out)":  lambda g, r: colpar(r),
    "rowpar(out)":  lambda g, r: rowpar(r),
}
# how the vector indexes into the cell
IDX = {"by j": lambda v, i, j: v[j], "by i": lambda v, i, j: v[i]}


def build(tname, pname, iname):
    def f(g):
        r = T[tname](g)
        v = PV[pname](g, r)
        ix = IDX[iname]
        return [[r[i][j] ^ ix(v, i, j) for j in range(N)] for i in range(N)]
    return f


TRUE = build("rot90cw", "colpar(orig)", "by j")
outs = [TRUE(g) for g in ex]
truth_q = TRUE(q)


def fmt(g):
    return "; ".join("".join(str(c) for c in r) for r in g)


print("intended rule  : rot90cw XOR colpar(orig) by j")
print("truth on query :", fmt(truth_q))
print()

fits = []
for tn, pn, iname in itertools.product(T, PV, IDX):
    f = build(tn, pn, iname)
    if all(f(g) == o for g, o in zip(ex, outs)):
        fits.append((tn, pn, iname, fmt(f(q))))

print(f"rules in this family that fit ALL {len(ex)} examples: {len(fits)}")
preds = {}
for tn, pn, iname, pred in fits:
    print(f"  {tn:<10} XOR {pn:<13} {iname:<6} -> {pred}")
    preds.setdefault(pred, []).append(f"{tn}/{pn}/{iname}")

print()
print(f"distinct predictions on the query: {len(preds)}")
for pred, who in preds.items():
    tag = "  <-- intended" if pred == fmt(truth_q) else ""
    print(f"  {pred}  from {len(who)} rule(s){tag}")

if len(preds) > 1:
    print("\nVERDICT: the query does NOT have a unique answer under this rule family.")
    print("The examples underdetermine the rule -> item is INVALID as scored.")
else:
    print("\nVERDICT: unique within this family.")
