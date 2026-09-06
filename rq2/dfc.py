"""RQ2 — D/F/C construction with a fixed depth notion and a k-round reasoner.

Depth of a query (hyp, goal) under a clause set: the minimal number of
parallel forward-chaining rounds (all applicable clauses fire each round)
from {hyp} until goal is derived; None if never.

Conditions on a base theory D with target query (a, goal), depth d_D >= 3:
  F : add one derivable single-atom clause x -> y that reduces the target
      depth (d_F < d_D);
  C : add one derivable single-atom clause that leaves the target depth
      unchanged (d_C = d_D), chosen to match F's clause shape.
Exclusion (fixed): bases without at least one F candidate and one C
candidate are dropped; when several exist, the deterministic first in
sorted order is taken.

A k-round symbolic reasoner answers YES iff the goal is derived within k
rounds. Its disagreement pattern D-F vs D-C across k is the control
validation for the RQ2 hypothesis.
"""

from __future__ import annotations

import itertools
import random

ATOMS = list("abcdefg")


def rounds_to_derive(clauses, hyp, goal, max_rounds=20):
    known = {hyp}
    if goal in known:
        return 0
    for r in range(1, max_rounds + 1):
        new = set(known)
        for body, head in clauses:
            if all(x in known for x in body):
                new |= set(head)
        if new == known:
            return None
        known = new
        if goal in known:
            return r
    return None


def closure(clauses, facts):
    known = set(facts); changed = True
    while changed:
        changed = False
        for body, head in clauses:
            if all(x in known for x in body) and not set(head) <= known:
                known |= set(head); changed = True
    return known


def k_round_reasoner(k):
    """YES iff derivable within k parallel rounds."""
    def answer(clauses, hyp, goal):
        r = rounds_to_derive(clauses, hyp, goal)
        return r is not None and r <= k
    return answer


def exact_oracle(clauses, hyp, goal):
    return goal in closure(clauses, [hyp])


def derivable_singles(clauses):
    # exclude restatements: x -> y is a sub-clause of an existing clause x -> (y, z)
    present = {(b[0], y) for b, h in clauses if len(b) == 1 for y in h}
    out = []
    for x in ATOMS:
        cl = closure(clauses, [x])
        for y in ATOMS:
            if y != x and y in cl and (x, y) not in present:
                out.append(((x,), (y,)))
    return out


def random_base(rng, n_clauses, min_depth=3):
    """Random Horn theory over 7 atoms with target (a, goal) of depth >= min_depth."""
    for _ in range(2000):
        clauses = []
        for _ in range(n_clauses):
            k = rng.random()
            if k < 0.7:
                b, h = rng.sample(ATOMS, 2); clauses.append(((b,), (h,)))
            elif k < 0.85:
                x, y, z = rng.sample(ATOMS, 3); clauses.append(((x, y), (z,)))
            else:
                x, y, z = rng.sample(ATOMS, 3); clauses.append(((x,), (y, z)))
        goals = [g for g in ATOMS if g != "a" and (rounds_to_derive(clauses, "a", g) or 0) >= min_depth]
        if goals:
            goal = sorted(goals, key=lambda g: (-rounds_to_derive(clauses, "a", g), g))[0]
            return clauses, "a", goal
    return None


def dfc(clauses, hyp, goal):
    """Return (F_clause, C_clause) or None under the fixed rules.

    F = sorted-first among depth-reducing derivable single-atom clauses with
        the *largest* resulting depth (minimal shortening; never the direct
        clause hyp -> goal when depth_D >= 3);
    C = sorted-first among depth-preserving candidates whose overlap with
        {hyp, goal} equals F's (fallback: any depth-preserving candidate).
    """
    d = rounds_to_derive(clauses, hyp, goal)
    F, C = [], []
    for c in derivable_singles(clauses):
        ext = clauses + [c]
        dd = rounds_to_derive(ext, hyp, goal)
        if dd is not None and dd < d:
            F.append((dd, c))
        elif dd == d:
            C.append(c)
    if not F or not C:
        return None
    dmax = max(dd for dd, _ in F)
    Fc = sorted(c for dd, c in F if dd == dmax)[0]
    overlap = lambda c: len({c[0][0], c[1][0]} & {hyp, goal})  # noqa: E731
    matched = sorted(c for c in C if overlap(c) == overlap(Fc))
    Cc = matched[0] if matched else sorted(C)[0]
    return Fc, Cc


def make_cases(n, seed=0, n_clauses=5, min_depth=3):
    rng = random.Random(seed)
    cases = []
    tried = 0
    while len(cases) < n and tried < 20000:
        tried += 1
        b = random_base(rng, n_clauses, min_depth)
        if b is None:
            continue
        clauses, hyp, goal = b
        fc = dfc(clauses, hyp, goal)
        if fc is None:
            continue
        F, C = fc
        cases.append({"D": clauses, "hyp": hyp, "goal": goal, "F": clauses + [F], "C": clauses + [C],
                      "F_clause": F, "C_clause": C,
                      "depth_D": rounds_to_derive(clauses, hyp, goal),
                      "depth_F": rounds_to_derive(clauses + [F], hyp, goal),
                      "depth_C": rounds_to_derive(clauses + [C], hyp, goal)})
    return cases


if __name__ == "__main__":
    cases = make_cases(64)
    from collections import Counter
    print("cases", len(cases), "depth_D", Counter(c["depth_D"] for c in cases), "depth_F", Counter(c["depth_F"] for c in cases))
    # control validation: k-round reasoner disagreement with D on the target query
    for k in (1, 2, 3, 4, 6):
        ans = k_round_reasoner(k)
        dF = sum(ans(c["D"], c["hyp"], c["goal"]) != ans(c["F"], c["hyp"], c["goal"]) for c in cases) / len(cases)
        dC = sum(ans(c["D"], c["hyp"], c["goal"]) != ans(c["C"], c["hyp"], c["goal"]) for c in cases) / len(cases)
        accD = sum(ans(c["D"], c["hyp"], c["goal"]) == exact_oracle(c["D"], c["hyp"], c["goal"]) for c in cases) / len(cases)
        print(f"k={k}: D-F disagreement {dF:.2f}  D-C disagreement {dC:.2f}  accuracy(D) {accD:.2f}")
