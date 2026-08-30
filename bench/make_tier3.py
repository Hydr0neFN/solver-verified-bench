"""ARC-focus battery: composite grid rules, the one axis where tier-2 discriminated."""
import os, json, random

d = "tasks3"
os.makedirs(d, exist_ok=True)
TRUTH = {}
N = 4

STRICT = ("\n\nShow brief reasoning, then the LAST line of your reply must be exactly:\n"
          "FINAL: <answer>\nNo text after that line.\n"
          "Answer format: FINAL: <row1 four digits>; <row2>; <row3>; <row4>")


def rot90(g):
    return [[g[N - 1 - j][i] for j in range(N)] for i in range(N)]


def A1(g):  # rot90 CW, then XOR the column parity of the ORIGINAL
    cp = [sum(g[i][j] for i in range(N)) % 2 for j in range(N)]
    r = rot90(g)
    return [[r[i][j] ^ cp[j] for j in range(N)] for i in range(N)]


def A2(g):  # transpose, then XOR the row parity of the ORIGINAL
    rp = [sum(g[i]) % 2 for i in range(N)]
    return [[g[j][i] ^ rp[i] for j in range(N)] for i in range(N)]


def A3(g):  # transpose XOR 180-rotation
    return [[g[j][i] ^ g[N - 1 - i][N - 1 - j] for j in range(N)] for i in range(N)]


def A4(g):  # cyclic neighbour XOR: cell below XOR cell to the right
    return [[g[(i + 1) % N][j] ^ g[i][(j + 1) % N] for j in range(N)] for i in range(N)]


RULES = {"A1_rot_colparity": A1, "A2_transpose_rowparity": A2,
         "A3_transpose_xor_rot180": A3, "A4_cyclic_neighbour_xor": A4}


def gs(g):
    return "\n".join(" ".join(str(c) for c in r) for r in g)


rnd = random.Random(2026)


def rg():
    return [[rnd.randint(0, 1) for _ in range(N)] for _ in range(N)]


for name, fn in RULES.items():
    # reject degenerate examples/queries (all-equal rows or a uniform output)
    exs = []
    while len(exs) < 5:
        g = rg()
        o = fn(g)
        flat = [c for r in o for c in r]
        if len(set(flat)) == 2:
            exs.append((g, o))
    while True:
        q = rg()
        qo = fn(q)
        flat = [c for r in qo for c in r]
        if len(set(flat)) == 2 and all(q != e[0] for e in exs):
            break
    TRUTH[name] = {"kind": "grid", "value": [c for r in qo for c in r]}
    body = ""
    for i, (g, o) in enumerate(exs, 1):
        body += f"Example {i}\nIN:\n{gs(g)}\nOUT:\n{gs(o)}\n\n"
    open(os.path.join(d, name + ".txt"), "w", encoding="utf-8").write(
        "One deterministic transformation maps a 4x4 binary grid to a 4x4 binary grid. "
        "Every example uses the same rule. Infer it and apply it to the query.\n\n"
        + body + f"Query\nIN:\n{gs(q)}\nOUT: ?" + STRICT + "\n")

json.dump(TRUTH, open("truth3.json", "w"), indent=1)
for k, v in TRUTH.items():
    print(k, v["value"])
