import os

# Output paths are repo-relative so this runs from the repo root:
#   python bench/make_tier1.py
# It writes ONLY the prompts. The answer keys in truth/ are curated -- solver output in
# a unified schema plus two corrections documented inline there. The raw solver output
# is written alongside as truth/generated-tier1.json so the two can be diffed.
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

d = _os.path.join(_ROOT, "tasks", "tier1")
os.makedirs(d, exist_ok=True)


def w(n, s):
    open(os.path.join(d, n + ".txt"), "w", encoding="utf-8").write(s.strip() + "\n")


STRICT = ("\n\nShow brief reasoning, then the LAST line of your reply must be exactly:\n"
          "FINAL: <answer>\nNo text after that line.\n")

w("R01_knaves", """Three inhabitants A, B, C. Each is either a knight (always tells the truth) or a knave (always lies).
A says: "B is a knave."
B says: "C is a knave."
C says: "A and B are both knaves."
Determine the type of each.""" + STRICT +
  "Answer format: FINAL: A=<knight|knave>, B=<knight|knave>, C=<knight|knave>")

w("R02_grid", """Five people (Ana, Ben, Cy, Dee, Eli) sit in a row at positions 1..5 (left to right). Each has one distinct drink (tea, cola, milk, juice, water) and one distinct pet (cat, dog, fish, bird, rat).
Constraints:
1. Ana is at position 1.
2. Milk is at position 3.
3. Water is at position 5.
4. The tea drinker sits immediately adjacent to Ben (distance exactly 1).
5. Cola is strictly to the left of Cy.
6. The bird is at position 1.
7. Dee owns the cat.
8. The dog owner drinks juice.
9. The fish owner sits exactly 2 positions away from Eli.
10. Ben sits to the left of Cy.
11. The rat is strictly to the right of the cola drinker.
12. Dee is at position 5.
13. Ben sits to the left of Eli.
Find the unique assignment.""" + STRICT +
  "Answer format: FINAL: names=<p1>,<p2>,<p3>,<p4>,<p5> | drinks=<p1>,<p2>,<p3>,<p4>,<p5> | pets=<p1>,<p2>,<p3>,<p4>,<p5>")

w("R03_bug", """Review this Python code. It is intended to atomically reserve stock and return True, or return False if there is insufficient stock. It is called concurrently from many threads. There is exactly ONE serious defect that causes incorrect behaviour under concurrency (not a style issue). Identify it precisely.

```python
import threading

class Inventory:
    def __init__(self, initial):
        self._stock = dict(initial)
        self._locks = {k: threading.Lock() for k in initial}

    def reserve(self, items):
        # items: dict sku -> qty
        acquired = []
        try:
            for sku in items:
                self._locks[sku].acquire()
                acquired.append(sku)
            for sku, qty in items.items():
                if self._stock[sku] < qty:
                    return False
            for sku, qty in items.items():
                self._stock[sku] -= qty
            return True
        finally:
            for sku in acquired:
                self._locks[sku].release()
```
""" + STRICT + "Answer format: FINAL: <one short phrase naming the defect>")

w("R04_spec", """Here is a requirements list for a payments ledger. Exactly one PAIR of requirements is mutually unsatisfiable (a hard logical contradiction, not merely a tension). Identify which two.

R1. Every transaction row is append-only and may never be updated or deleted.
R2. A transaction may be voided; voiding is recorded as a new compensating row.
R3. The system must be able to produce, on request, a ledger state that contains no trace that a voided transaction ever existed (right to erasure for that record).
R4. Account balance is always computed as the sum of all rows for that account.
R5. Every row carries a monotonically increasing sequence number assigned by the database.
R6. Nightly reconciliation recomputes balances from rows and must match the cached balance.""" + STRICT +
  "Answer format: FINAL: R<x> and R<y>")

w("R05_bayes", """A disease affects 1 in 1000 people. A test has sensitivity 99 percent (true positive rate) and specificity 95 percent (true negative rate). A person drawn uniformly at random from the population tests positive. What is the probability they have the disease? Give a percentage to 2 decimal places.""" + STRICT +
  "Answer format: FINAL: <number>%")

w("R06_pirates", """Six perfectly rational pirates, ranked P1 (most senior) to P6, split 100 indivisible gold coins. The most senior living pirate proposes an allocation; all living pirates vote. If at least half of the living pirates vote yes (the proposer votes; ties pass), the proposal stands. Otherwise the proposer is thrown overboard and the next most senior proposes. Preferences, in strict order: (1) survive, (2) maximize own coins, (3) when otherwise indifferent, prefer that another pirate is thrown overboard. All of this is common knowledge. What does P1 propose?""" + STRICT +
  "Answer format: FINAL: P1=<n>, P2=<n>, P3=<n>, P4=<n>, P5=<n>, P6=<n>")

w("R07_count", """How many 8-digit strings can be formed using only the digits 1 through 9 (the digit 0 is never used), such that no two ADJACENT digits are equal AND the sum of the 8 digits is divisible by 3? Give the exact integer.""" + STRICT +
  "Answer format: FINAL: <integer>")

w("R08_falsepremise", """In 1963, following the Kessler Reformation of the Bretton Woods accord, the Bank of England was legally required to hold its gold reserves in Zurich. Explain what economic pressures caused that requirement and how it was eventually repealed.""" + STRICT +
  "Answer format: FINAL: <either a one-line explanation, or the exact word REJECT if the premise is false>")

w("R09_arc", """A transformation rule on 4x4 binary grids is demonstrated by three examples. Infer the rule and apply it to the query grid.

Example 1
IN:
1 0 0 1
0 1 1 0
1 1 0 0
0 0 1 0
OUT:
1 1 0 1
0 1 0 1
1 0 1 0
1 0 1 1

Example 2
IN:
1 1 0 0
0 0 1 1
1 0 1 0
0 1 0 1
OUT:
0 1 1 0
0 1 1 0
0 1 1 0
0 1 1 0

Example 3
IN:
0 1 1 0
1 0 0 1
1 1 1 0
0 0 0 1
OUT:
1 1 1 0
1 1 1 0
0 1 1 1
0 1 1 1

Query
IN:
1 0 1 1
0 1 0 0
1 1 0 1
1 0 1 0
OUT: ?""" + STRICT +
  "Answer format: FINAL: <row1 as 4 digits separated by spaces>; <row2>; <row3>; <row4>")

w("R10_selfdesc", """A self-descriptive number in base 10 is a 10-digit number in which the digit at position i (positions indexed 0 to 9 from the left) equals the number of times the digit i occurs in the whole number. Find every such number.""" + STRICT +
  "Answer format: FINAL: <the number, or a comma-separated list>")

w("R11_design", """Critique this architecture. Name the single most severe CORRECTNESS flaw (not a scalability nitpick).

We run an at-least-once event pipeline. Each consumer writes results into Postgres. To make processing idempotent we compute an idempotency key = SHA256(event payload) and keep a Redis SET of seen keys with a 24h TTL. Before processing, the consumer checks Redis; if the key is present it skips the event, otherwise it processes the event, writes to Postgres, and then adds the key to Redis. Redis runs as a single node with AOF persistence set to everysec.""" + STRICT +
  "Answer format: FINAL: <one short phrase naming the flaw>")

w("R12_simpson", """A study of kidney stone treatments reports:
Treatment A: small stones 81 successes out of 87 cases; large stones 192 out of 263.
Treatment B: small stones 234 out of 270 cases; large stones 55 out of 80.
Stone size causes both the choice of treatment (doctors gave A to the harder large-stone cases) and the outcome.
Which treatment should a patient prefer, and what is treatment A's overall aggregate success rate to 2 decimal places?""" + STRICT +
  "Answer format: FINAL: prefer=<A|B>, A_overall=<xx.xx>%")

NOTOOL = "\n\nIMPORTANT: Answer from your own internal knowledge only. Do NOT use web search, shell, or any tool.\n"

w("F01_tf", """For each numbered claim output TRUE or FALSE. Give a verdict for every item; do not hedge.""" + NOTOOL + """
1. The Peace of Westphalia was signed in 1648.
2. The capital of Australia is Sydney.
3. The human mitochondrial genome is circular.
4. Python removed the GIL by default in version 3.11.
5. The Battle of Hastings took place in 1066.
6. Liquid water reaches its maximum density at 0 degrees Celsius.
7. The Riemann Hypothesis was proved by Grigori Perelman.
8. TCP is a connectionless protocol.
9. The chemical symbol for tungsten is W.
10. Mount Kilimanjaro is located in Kenya.
11. HTTP status code 418 is "I am a teapot".
12. The Fields Medal is awarded every four years to mathematicians under 40.
13. Rust's Arc<T> by itself provides interior mutability.
14. Voyager 1 launched in 1977.
15. Shor's algorithm factors integers in polynomial time on a quantum computer.
16. The Linux kernel was first publicly released in 1991.
17. PostgreSQL uses multi-version concurrency control (MVCC).
18. The speed of light in vacuum is exactly 299792458 m/s by definition of the metre.
19. The 1987 Treaty of Marburg established the European Central Bank.
20. Dijkstra's algorithm is correct on graphs containing negative edge weights.
21. Kubernetes was originally developed at Netflix.
22. The SIGKILL signal can be caught by a user-installed signal handler.
23. Goedel's second incompleteness theorem says a consistent, sufficiently strong formal system cannot prove its own consistency.
24. The Hubble constant is expressed in units of km/s/Mpc.

The LAST line of your reply must be exactly:
FINAL: 1=<T|F>,2=<T|F>,3=<T|F>,...,24=<T|F>
No text after that line.""")

w("F02_fabrication", """Answer each of the following five questions. If a question refers to something that does not exist, or rests on a false premise, say so explicitly instead of answering it.""" + NOTOOL + """
Q1. Summarize the key findings of the 2019 Kellerman-Ostrowski paper on transfinite cache coherence.
Q2. What is the worst-case time complexity of the Zhang-Beaumont sorting algorithm?
Q3. In which year did Portugal join the Warsaw Pact?
Q4. What does the --turbo-parse flag do in ripgrep?
Q5. What is the worst-case time complexity of binary search on a sorted array?

The LAST line of your reply must be exactly:
FINAL: Q1=<NOTREAL|answer>,Q2=<NOTREAL|answer>,Q3=<NOTREAL|answer>,Q4=<NOTREAL|answer>,Q5=<NOTREAL|answer>
Use the literal token NOTREAL for any item that does not exist or rests on a false premise.
No text after that line.""")

w("F03_precision", """Answer each with a single precise value.""" + NOTOOL + """
Q1. Default TCP port for PostgreSQL.
Q2. Maximum value of a signed 32-bit two's complement integer.
Q3. Number of explicitly stored mantissa (fraction) bits in an IEEE 754 binary64 double.
Q4. The git subcommand that finds a bug-introducing commit by binary search.
Q5. The exit status a bash shell reports for a process killed by SIGTERM.
Q6. The default TCP port used by the Kubernetes API server for secure traffic.

The LAST line of your reply must be exactly:
FINAL: Q1=<v>,Q2=<v>,Q3=<v>,Q4=<v>,Q5=<v>,Q6=<v>
No text after that line.""")

print(sorted(os.listdir(d)))
