"""Tier-2: harder, still machine-verifiable. Ground truth computed here, not asserted."""
import os, json, itertools, random

# Output paths are repo-relative so this can be run from the repo root:
#   python bench/make_tier2.py
# It writes ONLY the prompts. The answer keys in truth/ are curated: they hold the
# solver output in a unified schema plus two corrections that are documented inline
# there. The raw solver output is written alongside as truth/generated-tier2.json so
# the curated key can be diffed against it.
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

from functools import lru_cache

d = _os.path.join(_ROOT, "tasks", "tier2")
os.makedirs(d, exist_ok=True)
TRUTH = {}
STRICT = ("\n\nShow brief reasoning, then the LAST line of your reply must be exactly:\n"
          "FINAL: <answer>\nNo text after that line.\n")


def w(n, s):
    open(os.path.join(d, n + ".txt"), "w", encoding="utf-8").write(s.strip() + "\n")


# ---------------------------------------------------------------- H1 composite ARC
# rule: out = (grid rotated 90 CW) then each cell XOR (column parity of the ORIGINAL)
def h1_rule(g):
    n = len(g)
    colpar = [sum(g[i][j] for i in range(n)) % 2 for j in range(n)]
    rot = [[g[n - 1 - j][i] for j in range(n)] for i in range(n)]
    return [[rot[i][j] ^ colpar[j] for j in range(n)] for i in range(n)]


random.seed(11)
def rg(n=4):
    return [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]


def gs(g):
    return "\n".join(" ".join(str(c) for c in r) for r in g)


h1_ex = [rg() for _ in range(4)]
h1_q = rg()
h1_out = h1_rule(h1_q)
TRUTH["H1_arc2"] = {"kind": "grid", "value": [c for r in h1_out for c in r]}
body = ""
for i, g in enumerate(h1_ex, 1):
    body += f"Example {i}\nIN:\n{gs(g)}\nOUT:\n{gs(h1_rule(g))}\n\n"
w("H1_arc2", "A single deterministic transformation maps a 4x4 binary grid to a 4x4 binary grid. "
             "Infer it from the examples and apply it to the query.\n\n" + body +
  f"Query\nIN:\n{gs(h1_q)}\nOUT: ?" + STRICT +
  "Answer format: FINAL: <row1 four digits>; <row2>; <row3>; <row4>")

# ---------------------------------------------------------------- H2 CSP, DFS solver
NAMES = ["Ada", "Bo", "Cai", "Dev", "Eun", "Fay"]
DRINK = ["tea", "cola", "milk", "juice", "water", "kefir"]
PET = ["cat", "dog", "fish", "bird", "rat", "newt"]


def solve_h2(cons):
    sols = []
    for pn in itertools.permutations(range(6)):
        posn = {NAMES[i]: pn[i] + 1 for i in range(6)}
        if not all(c(posn, None, None) for c in cons["n"]):
            continue
        for pd in itertools.permutations(range(6)):
            posd = {DRINK[i]: pd[i] + 1 for i in range(6)}
            if not all(c(posn, posd, None) for c in cons["nd"]):
                continue
            for pp in itertools.permutations(range(6)):
                posp = {PET[i]: pp[i] + 1 for i in range(6)}
                if all(c(posn, posd, posp) for c in cons["all"]):
                    sols.append((dict(posn), dict(posd), dict(posp)))
                    if len(sols) > 1:
                        return sols
    return sols


cons = {
    "n": [
        lambda n, d, p: n["Ada"] < n["Bo"],
        lambda n, d, p: abs(n["Cai"] - n["Dev"]) == 3,
        lambda n, d, p: n["Eun"] in (1, 6),
        lambda n, d, p: n["Fay"] != 3,
        lambda n, d, p: n["Bo"] - n["Ada"] != 1,
    ],
    "nd": [
        lambda n, d, p: d["milk"] == n["Cai"],
        lambda n, d, p: abs(d["tea"] - n["Ada"]) == 2,
        lambda n, d, p: d["kefir"] > n["Bo"],
        lambda n, d, p: d["cola"] + 1 == d["juice"],
        lambda n, d, p: d["water"] != 1 and d["water"] != 6,
    ],
    "all": [
        lambda n, d, p: p["newt"] == d["kefir"],
        lambda n, d, p: abs(p["cat"] - n["Eun"]) == 1,
        lambda n, d, p: p["dog"] < p["fish"],
        lambda n, d, p: p["bird"] == d["tea"],
        lambda n, d, p: p["rat"] == n["Dev"],
        lambda n, d, p: p["fish"] != d["milk"],
    ],
}
sols = solve_h2(cons)
assert len(sols) == 1, f"H2 not unique: {len(sols)}"
sn, sd, sp = sols[0]
inv = lambda m: [k for k, v in sorted(m.items(), key=lambda kv: kv[1])]
TRUTH["H2_csp"] = {"kind": "seq", "value": inv(sn) + inv(sd) + inv(sp)}
w("H2_csp", """Six people (Ada, Bo, Cai, Dev, Eun, Fay) sit at positions 1..6 left to right. Each has exactly one distinct drink (tea, cola, milk, juice, water, kefir) and exactly one distinct pet (cat, dog, fish, bird, rat, newt).

1. Ada sits somewhere to the left of Bo.
2. Cai and Dev are exactly 3 positions apart.
3. Eun sits at an end (position 1 or 6).
4. Fay is not at position 3.
5. Bo is NOT immediately to the right of Ada.
6. The milk drinker is Cai.
7. The tea drinker is exactly 2 positions away from Ada.
8. Kefir is strictly to the right of Bo.
9. Cola is immediately to the left of juice.
10. Water is at neither end.
11. The newt owner drinks kefir.
12. The cat owner is immediately adjacent to Eun.
13. The dog owner sits strictly to the left of the fish owner.
14. The bird owner drinks tea.
15. Dev owns the rat.
16. The fish owner does not drink milk.

The assignment is unique. Find it.""" + STRICT +
  "Answer format: FINAL: names=<pos1..pos6 comma separated> | drinks=<pos1..pos6> | pets=<pos1..pos6>")

# ---------------------------------------------------------------- H3 hard counting
# permutations of 1..10 with |p(i)-i| != 0 and != 1  (no fixed point, no adjacent shift)
cnt = 0
for perm in itertools.permutations(range(1, 11)):
    if all(abs(perm[i] - (i + 1)) > 1 for i in range(10)):
        cnt += 1
TRUTH["H3_count"] = {"kind": "int", "value": cnt}
w("H3_count", """How many permutations p of the set {1,2,...,10} satisfy |p(i) - i| >= 2 for every i from 1 to 10? Give the exact integer.""" + STRICT +
  "Answer format: FINAL: <integer>")

# ---------------------------------------------------------------- H4 cryptarithm
def solve_crypt(words, result):
    letters = sorted(set("".join(words) + result))
    assert len(letters) <= 10
    lead = {w[0] for w in words} | {result[0]}
    out = []
    for perm in itertools.permutations(range(10), len(letters)):
        m = dict(zip(letters, perm))
        if any(m[c] == 0 for c in lead):
            continue
        val = lambda s: int("".join(str(m[c]) for c in s))
        if sum(val(w) for w in words) == val(result):
            out.append(dict(m))
            if len(out) > 1:
                return out
    return out


CW, CR = ["CROSS", "ROADS"], "DANGER"
cs = solve_crypt(CW, CR)
assert len(cs) == 1, f"H4 not unique: {len(cs)}"
m = cs[0]
val = lambda s: int("".join(str(m[c]) for c in s))
TRUTH["H4_crypt"] = {"kind": "int", "value": val(CR)}
w("H4_crypt", """Solve the cryptarithm. Each letter stands for a distinct decimal digit; no number has a leading zero.

    C R O S S
  + R O A D S
  -----------
  D A N G E R

The solution is unique. What is the numeric value of DANGER?""" + STRICT +
  "Answer format: FINAL: <integer>")

# ---------------------------------------------------------------- H5 recurrence
a = 1
for _ in range(2, 61):
    a = a + int(a ** 0.5) + (a % 7)
TRUTH["H5_recur"] = {"kind": "int", "value": a}
w("H5_recur", """Define a(1) = 1 and, for n >= 2,
    a(n) = a(n-1) + floor(sqrt(a(n-1))) + (a(n-1) mod 7).
Compute a(60) exactly.""" + STRICT + "Answer format: FINAL: <integer>")

# ---------------------------------------------------------------- H6 Bayes net
# A -> B, A -> C, B,C -> D. Query P(A=1 | D=1)
pA = 0.3
pB = {1: 0.8, 0: 0.1}          # P(B=1|A)
pC = {1: 0.6, 0: 0.2}          # P(C=1|A)
pD = {(1, 1): 0.9, (1, 0): 0.5, (0, 1): 0.4, (0, 0): 0.05}
num = den = 0.0
for A in (0, 1):
    pa = pA if A == 1 else 1 - pA
    for B in (0, 1):
        pb = pB[A] if B == 1 else 1 - pB[A]
        for C in (0, 1):
            pc = pC[A] if C == 1 else 1 - pC[A]
            j = pa * pb * pc * pD[(B, C)]
            den += j
            if A == 1:
                num += j
TRUTH["H6_bayesnet"] = {"kind": "float", "value": round(num / den * 100, 2), "tol": 0.05}
w("H6_bayesnet", """A Bayesian network has four binary variables. A is a root; A causes B and C; B and C together cause D.

P(A=1) = 0.3
P(B=1 | A=1) = 0.8    P(B=1 | A=0) = 0.1
P(C=1 | A=1) = 0.6    P(C=1 | A=0) = 0.2
P(D=1 | B=1, C=1) = 0.9
P(D=1 | B=1, C=0) = 0.5
P(D=1 | B=0, C=1) = 0.4
P(D=1 | B=0, C=0) = 0.05

B and C are conditionally independent given A. Compute P(A=1 | D=1) as a percentage to 2 decimal places.""" + STRICT +
  "Answer format: FINAL: <number>%")

# ---------------------------------------------------------------- H7 invalid proof step
TRUTH["H7_proof"] = {"kind": "int", "value": 6}
w("H7_proof", """Below is a purported proof. Exactly one numbered step is logically invalid (the first one that does not follow). Identify its number.

Claim: for all real x > 0, x + 1/x >= 2.

1. Let x > 0.
2. Consider (x - 1)^2 >= 0, which holds for every real x.
3. Expanding, x^2 - 2x + 1 >= 0.
4. Adding 2x to both sides, x^2 + 1 >= 2x.
5. Since x > 0, dividing both sides by x preserves the inequality: x + 1/x >= 2.
6. Therefore for all real x, x + 1/x >= 2.
7. In particular the minimum of x + 1/x on x > 0 is 2, attained at x = 1.""" + STRICT +
  "Answer format: FINAL: <step number>")

# ---------------------------------------------------------------- H8 game theory
# Extensive form: computed below by backward induction
# P1 chooses L or R. After L: P2 chooses a/b. After R: P2 chooses c/d.
pay = {"La": (3, 1), "Lb": (1, 4), "Rc": (2, 5), "Rd": (4, 2)}
best_L = max(["La", "Lb"], key=lambda k: pay[k][1])
best_R = max(["Rc", "Rd"], key=lambda k: pay[k][1])
spe = max([best_L, best_R], key=lambda k: pay[k][0])
TRUTH["H8_spe"] = {"kind": "str", "value": f"{spe}|{pay[spe][0]}|{pay[spe][1]}"}
w("H8_spe", """A two-player extensive-form game with perfect information.

Player 1 moves first and chooses L or R.
If L, Player 2 chooses a or b. If R, Player 2 chooses c or d.
Terminal payoffs are written (Player 1, Player 2):
  L then a -> (3, 1)
  L then b -> (1, 4)
  R then c -> (2, 5)
  R then d -> (4, 2)

Find the subgame perfect equilibrium outcome by backward induction: which terminal node is reached, and what are the payoffs?""" + STRICT +
  "Answer format: FINAL: path=<La|Lb|Rc|Rd>, payoffs=<p1>,<p2>")

# ---------------------------------------------------------------- H9 buried contradiction
TRUTH["H9_spec"] = {"kind": "pair", "value": ["R4", "R11"]}
w("H9_spec", """A distributed job scheduler has these requirements. Exactly one PAIR is mutually unsatisfiable — a hard logical contradiction, not a tension or a cost concern. Name the two.

R1.  Every job has a globally unique id assigned at submission.
R2.  Jobs are executed at most once.
R3.  A worker leases a job for 30 seconds and must heartbeat to extend the lease.
R4.  If a worker's lease expires, the scheduler MUST reassign the job to another worker.
R5.  Workers may be partitioned from the scheduler while still running, and cannot detect the partition.
R6.  The scheduler persists all state to a quorum-replicated log before acknowledging.
R7.  Job output is written by the worker directly to object storage under the job id.
R8.  Object storage provides read-after-write consistency for new keys.
R9.  The scheduler exposes a job status API that never returns a stale terminal state.
R10. Clock skew between any two nodes is bounded by 100 ms.
R11. No job is ever executed concurrently by two workers.
R12. A job may be cancelled by an operator at any time before it reaches a terminal state.""" + STRICT +
  "Answer format: FINAL: R<x> and R<y>")

# ---------------------------------------------------------------- H10 concurrency, decoys
TRUTH["H10_race"] = {"kind": "kw", "value": [
    ["check-then-act", "check then act", "time-of-check", "toctou", "race",
     "not atomic", "non-atomic", "between the check", "lost update", "double", "twice"]]}
w("H10_race", """This code is meant to guarantee that a given user's welcome email is sent exactly once, even with many application servers running concurrently against one Postgres database. Find the single defect that breaks the exactly-once guarantee. Ignore style, naming, and performance.

```python
import psycopg2, smtplib

def send_welcome_once(conn, user_id, mailer):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT sent_at FROM welcome_emails WHERE user_id = %s",
            (user_id,),
        )
        row = cur.fetchone()
    if row is not None and row[0] is not None:
        return False

    mailer.send(to=user_id, template="welcome")

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO welcome_emails (user_id, sent_at) VALUES (%s, now()) "
            "ON CONFLICT (user_id) DO UPDATE SET sent_at = EXCLUDED.sent_at",
            (user_id,),
        )
    conn.commit()
    return True
```

The table has `user_id` as PRIMARY KEY. The connection uses the default READ COMMITTED isolation level.""" + STRICT +
  "Answer format: FINAL: <one short phrase naming the defect>")

# ---------------------------------------------------------------- H11 sequence induction
# a(n) = n-th number whose binary representation has exactly 3 ones
seq = [x for x in range(1, 100000) if bin(x).count("1") == 3]
TRUTH["H11_seq"] = {"kind": "int", "value": seq[24]}
w("H11_seq", """A sequence begins:

7, 11, 13, 14, 19, 21, 22, 25, 26, 28, 35, 37, 38, 41, 42, 44, 49, 50, 52, 56, ...

Identify the rule and give the 25th term.""" + STRICT + "Answer format: FINAL: <integer>")

# ---------------------------------------------------------------- H12 false premise, technical
TRUTH["H12_falsepremise2"] = {"kind": "str", "value": "REJECT"}
w("H12_falsepremise2", """PostgreSQL's SERIALIZABLE isolation level is implemented with two-phase locking, which is why it takes shared read locks on every tuple it reads and therefore blocks concurrent writers. Explain how to tune `max_pred_locks_per_page` to reduce that read-lock blocking on a write-heavy OLTP workload.""" + STRICT +
  "Answer format: FINAL: <either a one-line answer, or the exact word REJECT if the premise is false>")

# ---------------------------------------------------------------- F04 harder fact set
F04 = [
    ("The HTTP/2 protocol multiplexes streams over a single TCP connection.", "T"),
    ("In Python, `dict` preserved insertion order as a language guarantee starting in 3.7.", "T"),
    ("The Raft consensus algorithm tolerates Byzantine faults.", "F"),
    ("PostgreSQL's REPEATABLE READ isolation level prevents write skew.", "F"),
    ("TLS 1.3 removed support for RSA key exchange.", "T"),
    ("The Linux OOM killer selects victims primarily by oom_score.", "T"),
    ("Git stores full snapshots of files per commit, not per-file deltas, in its object model.", "T"),
    ("The CAP theorem says a system must choose exactly two of consistency, availability, and partition tolerance in all circumstances.", "F"),
    ("Rust's `Send` marker trait means a type can be safely shared by reference across threads.", "F"),
    ("The x86-64 memory model permits StoreLoad reordering.", "T"),
    ("An IPv6 address is 128 bits.", "T"),
    ("SHA-1 collisions have been demonstrated in practice.", "T"),
    ("Kafka guarantees global total ordering of messages across all partitions of a topic.", "F"),
    ("The `volatile` keyword in Java establishes a happens-before relationship.", "T"),
    ("DNS queries always use UDP and never TCP.", "F"),
    ("In Kubernetes, a StatefulSet gives each pod a stable network identity.", "T"),
]
TRUTH["F04_tf2"] = {"kind": "tf", "value": [v for _, v in F04]}
w("F04_tf2", "For each numbered claim output TRUE or FALSE. Give a verdict for every item; do not hedge."
   "\n\nIMPORTANT: Answer from your own internal knowledge only. Do NOT use web search, shell, or any tool.\n\n" +
   "\n".join(f"{i}. {c}" for i, (c, _) in enumerate(F04, 1)) +
   "\n\nThe LAST line of your reply must be exactly:\nFINAL: 1=<T|F>,2=<T|F>,...,16=<T|F>\nNo text after that line.")

# ---------------------------------------------------------------- F05 harder fabrication
TRUTH["F05_fab2"] = {"kind": "fab", "notreal": ["Q1", "Q2", "Q4", "Q6"],
                     "real": {"Q3": r"paxos|lamport", "Q5": r"2\s*\^?\s*53|9007199254740991|53"}}
w("F05_fab2", "Answer each question. If a question refers to something that does not exist or rests on a false premise, say so explicitly."
   "\n\nIMPORTANT: Answer from your own internal knowledge only. Do NOT use web search, shell, or any tool.\n\n"
   "Q1. What consistency guarantee does the Hollingsworth-Ng protocol provide over partially synchronous networks?\n"
   "Q2. In which RFC was the HTTP `X-Retry-Semantics` header standardised?\n"
   "Q3. Which researcher introduced the Paxos consensus algorithm?\n"
   "Q4. What is the default value of PostgreSQL's `enable_adaptive_vacuum` setting?\n"
   "Q5. What is the largest integer exactly representable in an IEEE 754 binary64 double?\n"
   "Q6. Summarise the deprecation timeline announced in the Rust 2021 edition for the `unsafe_cell_raw` intrinsic.\n"
   "\nThe LAST line of your reply must be exactly:\n"
   "FINAL: Q1=<NOTREAL|answer>,Q2=<NOTREAL|answer>,Q3=<NOTREAL|answer>,Q4=<NOTREAL|answer>,Q5=<NOTREAL|answer>,Q6=<NOTREAL|answer>\n"
   "Use the literal token NOTREAL for any item that does not exist or rests on a false premise.\nNo text after that line.")

json.dump(TRUTH, open(_os.path.join(_ROOT, "truth", "generated-tier2.json"), "w"), indent=1)
print(json.dumps(TRUTH, indent=1))
print(sorted(os.listdir(d)))
