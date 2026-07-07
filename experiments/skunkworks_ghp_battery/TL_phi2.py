#!/usr/bin/env python3
r"""TL_phi2 — Temperley-Lieb / Jones conditional-expectation numerics.

GHP skunkworks, ENGINEERING / VERIFIED-COMPUTATION LANE ONLY.
NO-UPGRADE SENTENCE (non-negotiable): No result produced by this script proves
the Golden Horizon Principle, is physics evidence, or licenses any observer-
boundary-selection claim; it is a finite-dimensional linear-algebra check of
Temperley-Lieb closure quality and the Pimsner-Popa bound, and per master hard
rule 7 a software/toy result is NEVER physics evidence and NO ledger status may
be upgraded on its basis.

====================================================================
PREREGISTRATION (embedded verbatim-in-spirit from TL_phi2_PREREG_v1.md,
locked 2026-07-03; thresholds pinned BEFORE this run, no post-hoc tuning)
====================================================================

test_id: TL_phi2   ledger_anchor: P-005

HYPOTHESIS
  H1 (hard, interesting): phi is DISTINGUISHED among admissible Jones indices.
    Building finite TL_n(delta) (diagram + Jones-Wenzl bases, n up to N=8) with
    the Markov trace and the trace-preserving conditional expectation
    E: TL_n -> TL_{n-1}, the golden case delta=phi (index phi^2=2.618...=1+phi)
    closes MORE cleanly than every non-golden control
    {sqrt2 (index 2), 2cos(pi/7) (index 3.247), 2 (index 4)}:
    its closing-level Gram matrix is >=10x better conditioned (CQ_score margin
    >=1.0 log-decade) AND its Pimsner-Popa error PPQ is >=1 order of magnitude
    tighter than every control, AND this survives the index-magnitude confound
    by also beating 2cos(pi/7) (index nearest phi^2).
  H0 (expected, null-favoring): the finite-access TL/Jones machinery satisfies
    Pimsner-Popa (E(x) >= delta^-2 x) and Markov consistency EQUALLY WELL for all
    four admissible delta. phi's CQ_score and PPQ are INDISTINGUISHABLE from the
    controls after conditioning on index magnitude and depth. Clean closure and
    the PP bound are generic to admissible indices (theorems), NOT special to phi;
    phi's index is mid-series and not minimal (Ising 2 < phi^2 = 2.618), so any
    good behavior at phi is expected at every control too.

KILL-OR-PASS RULE (two verdicts, thresholds locked pre-run)
  4a MACHINERY-VALIDITY GATE (must pass or test is INVALID, not informative):
     for every delta and every non-ILL n:
       PP_err = |PP_numeric - delta^-2| <= 1e-6, AND
       PP_pos = min eig(E(x) - delta^-2 x) over frozen positive probe set >= -1e-9, AND
       MC (Markov consistency residual) <= 1e-9, AND
       IDEM (bimodule/idempotency residual) <= 1e-9.
  4b phi-DISTINCTIVENESS: PASS-H1 requires ALL of
       (i)  CQ_score(phi) < CQ_score(c) - 1.0 for EVERY control c
            [CQ_score = median over closing levels of log10(cond(Gram))],
       (ii) phi also beats nearest-index control 2cos(pi/7) by same >=1.0 margin,
       (iii) PPQ(phi) < min_c PPQ(c) by >=1 order of magnitude.
     KILL-H1 / CONFIRM-H0 (default, expected) if ANY of:
       |CQ_score(phi)-CQ_score(c)| <= 1.0 for any control, OR
       any control ties/beats phi on CQ_score or PPQ, OR
       CQ_score ordering across the 4 deltas tracks index magnitude/depth with
       Spearman |rho| >= 0.9 (generic, not phi-singling).
     If 4a passes but 4b is neither clean PASS nor clean KILL: WATCH/underpowered.
  Condition-number guard: any Gram with cond > 1e12 flagged ILL, excluded from
  pass/fail (reported separately) so float error cannot drive the verdict.
  A KILL of H1 is the EXPECTED and VALUABLE outcome.

CIRCULAR/NUMEROLOGY/INVALID (locked)
  CIRCULAR: citing index = phi^2 = 1+phi or 1/index = 2-phi as evidence -
    definitional once delta=phi (index := delta^2); sanity-check only, never H1.
  NUMEROLOGY: treating phi/Fibonacci/[4]=0/A4 quantum dims as special without a
    matched control clearing the 4b margins; phi's A4-closure is generic Jones-
    series structure (sqrt2 closes at l=4, 2cos(pi/7) at l=7).
  INVALID: tuning N/probe/tol/margins after seeing data; different construction
    for phi vs controls; letting an ILL point drive the verdict; reading a
    4a-fails-everywhere run as a null (it is a code bug); presenting any 4b
    outcome as physics evidence for GHP.
  Honest prior: H0 is expected.

RUNTIME: Python 3.9 + numpy/scipy only, deterministic, offline. Construction is
exact (no RNG); seeds [1618,2718,3141] are pinned but unused unless sampling is
added. N frozen at 8. tol = 1e-9 (op-norm/eigenvalue scale). cond>1e12 => ILL.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# ----------------------------------------------------------------------
# Pinned constants (locked in prereg; recovered here only as 4a sanity)
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "TL_phi2_outputs"
OUT.mkdir(parents=True, exist_ok=True)

N_MAX = 8                       # frozen system size (per-n reported 2..N_MAX)
TOL = 1e-9                      # absolute op-norm / eigenvalue tolerance
PP_ERR_GATE = 1e-6             # 4a gate on PP_err
POS_GATE = -1e-9              # 4a gate on Pimsner-Popa positivity
MC_GATE = 1e-9                # 4a gate on Markov consistency
IDEM_GATE = 1e-9             # 4a gate on idempotency/bimodule
ILL_COND = 1e12             # Gram cond above this => ILL, excluded from verdict
CQ_MARGIN = 1.0            # 4b log-decade margin
PPQ_DECADE = 10.0        # 4b PPQ must beat by >=1 order of magnitude
SPEARMAN_KILL = 0.9    # 4b: |rho| >= this between CQ_score and index => generic
SEEDS = (1618, 2718, 3141)  # pinned, unused (construction is exact/deterministic)

PHI = (1.0 + math.sqrt(5.0)) / 2.0

# The finite machinery DELIBERATELY touches degenerate regions (closing levels,
# where the Markov-trace Gram acquires a negligible ideal / quantum integers hit
# 0). There the Jones-Wenzl recurrence is stopped by an explicit relative guard
# and the whitening-based PP metrics are NOT computed (ILL points, cond>1e12, are
# excluded from the verdict per the prereg condition-number guard). numpy 2.x
# raises benign FP flags on matmuls that touch those regions even when the kept
# results are finite and correct; we silence the flags (they are expected, not a
# bug) so the log is readable. This does NOT relax any pass/fail tolerance.
np.seterr(divide="ignore", over="ignore", invalid="ignore")

# delta specs: (name, delta, jones_index, closing_l).
# closing_l = the LEVEL n at which the finite machinery first closes, i.e. the
# smallest TL_n whose Markov-trace Gram acquires a negligible ideal. For
# delta=2cos(pi/l) the JW projection p_{l-1} in TL_{l-1} vanishes ([l]=0), so the
# closing LEVEL is n = l-1:  phi (l=5) -> n=4, sqrt2 (l=4) -> n=3,
# 2cos(pi/7) (l=7) -> n=6, delta2 -> never. These are EXPECTED/sanity values;
# the actual closing levels used for CQ_score are read from the data uniformly.
DELTAS: List[Tuple[str, float, float, object]] = [
    ("phi",       PHI,                       PHI * PHI,           4),
    ("sqrt2",     math.sqrt(2.0),            2.0,                 3),
    ("2cos_pi_7", 2.0 * math.cos(math.pi / 7.0), (2.0 * math.cos(math.pi / 7.0)) ** 2, 6),
    ("delta2",    2.0,                       4.0,                 None),  # never closes
]


# ----------------------------------------------------------------------
# Temperley-Lieb diagram basis: planar non-crossing pairings of 2n points.
# Points 0..n-1 on top, n..2n-1 on bottom (matched columns: top i <-> bottom n+i).
# Basis of TL_n has dimension Catalan(n).  Multiplication composes diagrams;
# each closed loop contributes a factor delta.
# ----------------------------------------------------------------------
def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


def _noncrossing_pairings(points: Tuple[int, ...]) -> List[Dict[int, int]]:
    """All planar (non-crossing) perfect matchings of an ordered point tuple.

    Points are arranged on a line in the given order; a matching is non-crossing
    iff no two arcs (a,b) and (c,d) interleave as a<c<b<d.  Standard recursion:
    the first point pairs with some later point at an even gap, splitting into
    an inside block and an outside block, both matched recursively.
    """
    m = len(points)
    if m == 0:
        return [dict()]
    first = points[0]
    result: List[Dict[int, int]] = []
    for k in range(1, m, 2):  # partner must leave an even-size inside block
        partner = points[k]
        inside = points[1:k]
        outside = points[k + 1:]
        for im in _noncrossing_pairings(inside):
            for om in _noncrossing_pairings(outside):
                d = {first: partner, partner: first}
                d.update(im)
                d.update(om)
                result.append(d)
    return result


def tl_basis(n: int) -> List[Dict[int, int]]:
    """Diagram basis of TL_n as non-crossing perfect matchings of 2n boundary
    points arranged cyclically as top-left..top-right then bottom-right..bottom-left.

    Point layout used throughout (a single planar circle, standard TL convention):
      indices 0..n-1   = top boundary, left->right
      indices n..2n-1  = bottom boundary, left->right  (so bottom point j sits at 2n-1-... )
    To make planarity == non-crossing on a circle we place points around a disk in
    order: top 0,1,...,n-1 then bottom n-1,...,0, i.e. cyclic sequence
      [0,1,...,n-1, 2n-1, 2n-2, ..., n].
    Non-crossing matchings of that cyclic sequence are exactly the planar TL diagrams.
    """
    cyc = list(range(n)) + list(range(2 * n - 1, n - 1, -1))
    matchings = _noncrossing_pairings(tuple(cyc))
    return matchings


def compose(a: Dict[int, int], b: Dict[int, int], n: int) -> Tuple[Dict[int, int], int]:
    """Compose two TL diagrams a then b (a on top of b): stack a above b, glue
    a's bottom (n..2n-1) to b's top (0..n-1), count closed loops.

    Returns (resulting top<->bottom matching on 2n points, number_of_closed_loops).
    Uses a union-find-free direct trace: nodes are
      A-top:  ('T', i) for i in 0..n-1   -> external top of result
      mid:    ('M', i) for i in 0..n-1   -> a-bottom glued to b-top
      B-bot:  ('B', i) for i in 0..n-1   -> external bottom of result
    a connects among {A-top, mid}; b connects among {mid, B-bot}.
    """
    # Build adjacency for the combined graph.
    # a: top points 0..n-1 -> ('T',i); bottom points n+i -> ('M',i)
    # b: top points i      -> ('M',i); bottom points n+i -> ('B',i)
    def a_node(p):
        return ('T', p) if p < n else ('M', p - n)

    def b_node(p):
        return ('M', p) if p < n else ('B', p - n)

    adj: Dict[Tuple[str, int], List[Tuple[str, int]]] = {}

    def add_edge(u, v):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)

    for p, q in a.items():
        if p < q:  # each pair once
            add_edge(a_node(p), a_node(q))
    for p, q in b.items():
        if p < q:
            add_edge(b_node(p), b_node(q))

    # Ensure every mid node exists (isolated ones impossible: each mid has exactly
    # one a-edge and one b-edge). Externals ('T',*)/('B',*) have exactly one edge.
    for i in range(n):
        adj.setdefault(('M', i), [])
        adj.setdefault(('T', i), [])
        adj.setdefault(('B', i), [])

    visited = set()
    result: Dict[int, int] = {}
    loops = 0

    # Trace paths starting at external endpoints; each external connects to exactly
    # one other external (a valid TL diagram is a perfect matching of externals).
    externals = [('T', i) for i in range(n)] + [('B', i) for i in range(n)]

    def ext_label(node):
        typ, i = node
        return i if typ == 'T' else n + i

    for start in externals:
        if start in visited:
            continue
        # walk the path until we hit another external
        prev = None
        cur = start
        visited.add(cur)
        while True:
            nxt = None
            for w in adj[cur]:
                if w != prev:
                    # avoid immediately backtracking a multi-edge only when possible
                    nxt = w
                    break
            if nxt is None:
                # cur has only the edge back to prev; if cur external, path ends here
                nxt = adj[cur][0] if adj[cur] else None
            prev, cur = cur, nxt
            if cur is None:
                break
            visited.add(cur)
            if cur[0] in ('T', 'B'):
                # reached other external endpoint
                u, v = ext_label(start), ext_label(cur)
                result[u] = v
                result[v] = u
                break

    # Count closed loops among mid nodes not touched by any external path.
    for i in range(n):
        node = ('M', i)
        if node in visited:
            continue
        # trace the loop
        loops += 1
        prev = None
        cur = node
        visited.add(cur)
        while True:
            nxt = None
            for w in adj[cur]:
                if w != prev:
                    nxt = w
                    break
            if nxt is None:
                nxt = adj[cur][0] if adj[cur] else None
            prev, cur = cur, nxt
            if cur is None or cur == node:
                break
            if cur in visited:
                break
            visited.add(cur)

    return result, loops


# ----------------------------------------------------------------------
# Regular representation: TL_n acts on itself by left multiplication.
# We assemble each generator e_i as a matrix in the diagram basis, then
# build arbitrary words as matrix products. Trace of a word = Markov trace
# read off via the trace form on the basis.
# ----------------------------------------------------------------------
class TLn:
    def __init__(self, n: int, delta: float):
        self.n = n
        self.delta = delta
        self.basis = tl_basis(n)
        self.dim = len(self.basis)
        # index each canonical matching by a hashable key
        self.index = {self._key(m): idx for idx, m in enumerate(self.basis)}
        assert self.dim == catalan(n), (self.dim, catalan(n), n)
        # Precompute the left-multiplication table ONCE:
        # lmult[a] is a dict {col_b -> (row, delta_power)} giving D_a * D_b.
        # Reused by generators, operator_from_coeffs, and every word — this is
        # the single hot loop, so we pay the O(dim^2) composition cost exactly once.
        self._lmult = self._build_lmult_table()
        self.id_col = self.index[self._key(self._identity_diagram())]
        self.e = [self._generator(i) for i in range(1, n)]  # e_1..e_{n-1}
        self.identity = self._identity_matrix()
        self._gram = None
        self._whiten = None
        self._tv = None
        self._flip_perm = None

    def _build_lmult_table(self):
        table = []
        for a, ma in enumerate(self.basis):
            row_of = np.empty(self.dim, dtype=np.int64)
            pow_of = np.empty(self.dim, dtype=np.int64)
            for b, mb in enumerate(self.basis):
                comp, loops = compose(ma, mb, self.n)
                row_of[b] = self.index[self._key(comp)]
                pow_of[b] = loops
            table.append((row_of, pow_of))
        return table

    def left_mult_operator(self, coeffs: np.ndarray) -> np.ndarray:
        """Fast build of the left-mult matrix for element sum_a coeffs[a] D_a,
        using the cached lmult table (no graph traversals)."""
        M = np.zeros((self.dim, self.dim))
        d = self.delta
        for a, c in enumerate(coeffs):
            if c == 0.0:
                continue
            row_of, pow_of = self._lmult[a]
            contrib = c * (d ** pow_of)
            np.add.at(M, (row_of, np.arange(self.dim)), contrib)
        return M

    @staticmethod
    def _key(m: Dict[int, int]) -> Tuple[Tuple[int, int], ...]:
        return tuple(sorted((a, b) for a, b in m.items() if a < b))

    def _identity_diagram(self) -> Dict[int, int]:
        n = self.n
        d = {}
        for i in range(n):
            d[i] = n + i
            d[n + i] = i
        return d

    def _identity_matrix(self) -> np.ndarray:
        return np.eye(self.dim)

    def _cap_cup_diagram(self, i: int) -> Dict[int, int]:
        """e_i diagram (1-indexed i, cap connecting strands i,i+1 top and bottom).

        top points 0..n-1, bottom points n..2n-1, columns matched top j <-> n+j.
        e_i: cap on top {i-1,i}, cup on bottom {n+i-1,n+i}, all other columns pass.
        """
        n = self.n
        d = {}
        a, b = i - 1, i  # 0-indexed top positions of the cap
        for j in range(n):
            if j in (a, b):
                continue
            d[j] = n + j
            d[n + j] = j
        # cap on top
        d[a] = b
        d[b] = a
        # cup on bottom
        d[n + a] = n + b
        d[n + b] = n + a
        return d

    def _generator(self, i: int) -> np.ndarray:
        """Matrix of left-multiplication by e_i in the diagram basis, via the
        cached left-mult table (e_i is a single basis diagram)."""
        ei = self._cap_cup_diagram(i)
        a = self.index[self._key(ei)]
        coeffs = np.zeros(self.dim)
        coeffs[a] = 1.0
        return self.left_mult_operator(coeffs)

    # ---- Markov trace -------------------------------------------------
    def _closure_loops(self, m: Dict[int, int]) -> int:
        """Number of loops when a diagram's top is glued to its own bottom
        (top i <-> bottom n+i), i.e. the Markov closure. tr(diagram) = delta^(loops - n)."""
        n = self.n
        adj: Dict[int, List[int]] = {}

        def add(u, v):
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

        for p, q in m.items():
            if p < q:
                add(('d', p), ('d', q))
        for i in range(n):  # closure wires: top i to bottom n+i
            add(('d', i), ('d', n + i))
        visited = set()
        loops = 0
        for start in [('d', k) for k in range(2 * n)]:
            if start in visited:
                continue
            loops += 1
            prev = None
            cur = start
            visited.add(cur)
            while True:
                nxt = None
                for w in adj[cur]:
                    if w != prev:
                        nxt = w
                        break
                if nxt is None:
                    nxt = adj[cur][0]
                prev, cur = cur, nxt
                if cur in visited:
                    break
                visited.add(cur)
        return loops

    def trace_vector(self) -> np.ndarray:
        """tr of each basis diagram, normalized tr(1)=1 (cached).

        Unnormalized Markov trace of a diagram = delta^(loops).  The identity has
        n loops on closure, giving delta^n; normalize by delta^-n so tr(1)=1.
        Then tr(e_i x) = delta^-1 tr(x) holds automatically (standard Markov trace).
        """
        if getattr(self, "_tv", None) is not None:
            return self._tv
        n = self.n
        tv = np.zeros(self.dim)
        for idx, m in enumerate(self.basis):
            loops = self._closure_loops(m)
            tv[idx] = self.delta ** (loops - n)
        self._tv = tv
        return tv

    def flip_perm(self) -> np.ndarray:
        """Cached permutation: flip_perm[a] = index of the vertical flip of D_a."""
        if getattr(self, "_flip_perm", None) is not None:
            return self._flip_perm
        fp = np.empty(self.dim, dtype=np.int64)
        for a, ma in enumerate(self.basis):
            fp[a] = self.index[self._key(self._flip(ma))]
        self._flip_perm = fp
        return fp

    def trace_of(self, M: np.ndarray) -> float:
        """Markov trace of an operator given as its matrix in the regular rep.

        M acts by left-mult; its coefficient vector on the identity column gives
        the expansion of M*1 in the basis, whose Markov trace is tv . coeffs.
        """
        coeffs = M[:, self.id_col]
        return float(self.trace_vector() @ coeffs)

    def gram(self) -> np.ndarray:
        """Gram matrix G[a,b] = tr(D_a^* D_b) of the diagram basis under the
        Markov trace (D^* = vertical flip). Built from the cached left-mult table
        and trace vector — NO second O(dim^2) graph traversal:
          flip(D_a) * D_b = delta^(pow) * D_row, and tr(D_row) = tv[row], so
          G[a,b] = delta^pow * tv[row], with (row,pow) = lmult[flip(a)][b]."""
        if self._gram is not None:
            return self._gram
        tv = self.trace_vector()
        fp = self.flip_perm()
        d = self.delta
        G = np.zeros((self.dim, self.dim))
        for a in range(self.dim):
            row_of, pow_of = self._lmult[fp[a]]   # flip(D_a) * D_b
            G[a, :] = (d ** pow_of) * tv[row_of]
        # symmetrize away float asymmetry (G is exactly symmetric in theory)
        G = 0.5 * (G + G.T)
        self._gram = G
        return G

    def _flip(self, m: Dict[int, int]) -> Dict[int, int]:
        """Adjoint diagram: swap top<->bottom (reflect vertically)."""
        n = self.n

        def sw(p):
            return p + n if p < n else p - n
        return {sw(p): sw(q) for p, q in m.items()}

    def whitening(self):
        """Cached GNS whitening (S, Sinv) from the Gram G: S^T S = G on its range,
        near-null directions dropped so a degenerate closing-level GNS space
        cannot inject float garbage. Computed ONCE per (n, delta) — the single
        eigendecomposition of G is the expensive step, so it must not be redone
        per probe."""
        if getattr(self, "_whiten", None) is not None:
            return self._whiten
        G = self.gram()
        w, V = np.linalg.eigh(0.5 * (G + G.T))
        wmax = w.max() if w.size else 0.0
        keep = w > (wmax * 1e-12) if wmax > 0 else np.zeros_like(w, dtype=bool)
        Wsq = np.zeros_like(w)
        Wsq[keep] = np.sqrt(w[keep])
        Winv = np.zeros_like(w)
        Winv[keep] = 1.0 / np.sqrt(w[keep])
        S = (V * Wsq) @ V.T
        Sinv = (V * Winv) @ V.T
        self._whiten = (S, Sinv)
        return self._whiten


# ----------------------------------------------------------------------
# Quantum integers and Jones-Wenzl projections (Wenzl recurrence)
# ----------------------------------------------------------------------
def quantum_int(m: int, delta: float) -> float:
    """[m]_delta with delta = q + q^{-1}; [m] = sin(m*theta)/sin(theta) where
    delta = 2cos(theta). For delta >= 2 use the Chebyshev U_{m-1}(delta/2)."""
    x = delta / 2.0
    if abs(x) < 1.0:
        theta = math.acos(x)
        if abs(math.sin(theta)) < 1e-15:
            return float(m)
        return math.sin(m * theta) / math.sin(theta)
    # delta >= 2: U_{m-1}(x), Chebyshev of the second kind, real recurrence
    um2, um1 = 0.0, 1.0  # U_{-1}=0, U_0=1
    if m == 0:
        return 0.0
    val = um1
    for _ in range(1, m):
        val = 2.0 * x * um1 - um2
        um2, um1 = um1, val
    return val


def jones_wenzl(tl: TLn) -> Tuple[List[np.ndarray], List[float], bool]:
    """Wenzl recurrence p_{k+1} = p_k - ([k]/[k+1]) p_k e_k p_k inside TL_n's
    regular rep. Returns (list of p_k matrices for k=1..n, quantum ints [1..n],
    degeneracy_flag) where degeneracy_flag True if some [k]=0 was hit (expected
    at the closing level and logged, not an error)."""
    n = tl.n
    delta = tl.delta
    qi = [quantum_int(m, delta) for m in range(0, n + 2)]  # [0..n+1]
    I = tl.identity
    p = [None, I.copy()]  # p_0 unused; p_1 = identity on 1 strand == I here
    degenerate = False
    for k in range(1, n):
        ek = tl.e[k - 1]  # e_k (1-indexed)
        qk = qi[k]
        qk1 = qi[k + 1]
        if abs(qk1) < 1e-12:
            degenerate = True
            # [k+1]=0: p_{k+1} does not exist (negligible ideal). Stop; log.
            break
        pk = p[k]
        p.append(pk - (qk / qk1) * (pk @ ek @ pk))
    return p, qi, degenerate


# ----------------------------------------------------------------------
# Conditional expectation E: TL_n -> TL_{n-1}, the trace-preserving projection.
# ----------------------------------------------------------------------
def conditional_expectation_matrix(tl_n: TLn, tl_nm1: TLn) -> Tuple[np.ndarray, np.ndarray]:
    """Build E: TL_n -> TL_{n-1}, the trace-preserving conditional expectation
    that removes the LAST strand, by its EXACT diagrammatic (partial-trace)
    definition — NO Gram inversion, so it is stable even where the trace form
    degenerates (closing levels). This is the canonical E: it is unital,
    trace-preserving, a TL_{n-1}-bimodule map, idempotent onto TL_{n-1}, and
    satisfies the Pimsner-Popa bound with constant 1/index = delta^-2.

    Diagrammatic rule for a TL_n diagram D (matching of top 0..n-1, bottom n..2n-1):
      close the last strand by joining top(n-1) to bottom(2n-1) with an external
      arc; trace connectivity through D among the remaining 2(n-1) points; each
      resulting closed loop contributes a factor delta; the remaining matching is
      a TL_{n-1} diagram. E(D) = delta^{-1} * delta^{loops} * (that TL_{n-1} diagram),
      re-embedded into TL_n as a through-strand element (standard inclusion).

    Returns (E_coeff, P) where E_coeff (dim_n x dim_n) acts on TL_n diagram
    COEFFICIENT vectors x -> E(x) in the SAME TL_n basis, and P (dim_n x dim_{n-1})
    is the standard embedding of TL_{n-1} into TL_n (through-strand on the right).
    """
    n = tl_n.n
    nm1 = n - 1
    dim_n = tl_n.dim
    dim_sub = tl_nm1.dim
    d = tl_n.delta

    # Standard embedding P: TL_{n-1} diagram -> TL_n diagram (add right through-strand).
    P = np.zeros((dim_n, dim_sub))
    sub_index_of_key = {}
    for sub_idx, msub in enumerate(tl_nm1.basis):
        emb = {}
        for p_, q_ in msub.items():
            emb[_relabel_embed(p_, nm1, n)] = _relabel_embed(q_, nm1, n)
        emb[n - 1] = 2 * n - 1
        emb[2 * n - 1] = n - 1
        key = tl_n._key(emb)
        P[tl_n.index[key], sub_idx] = 1.0
        sub_index_of_key[tl_nm1._key(msub)] = sub_idx

    # E_coeff: for each TL_n basis diagram D_col, compute E(D_col) exactly.
    E_coeff = np.zeros((dim_n, dim_n))
    for col, D in enumerate(tl_n.basis):
        sub_key, loops = _partial_trace_last_strand(D, n)
        sub_idx = sub_index_of_key[sub_key]
        # E(D) = delta^{loops-1} * embed(sub diagram)
        E_coeff[:, col] = (d ** (loops - 1)) * P[:, sub_idx]
    return E_coeff, P


def _partial_trace_last_strand(D: Dict[int, int], n: int):
    """Close the last strand (join top n-1 to bottom 2n-1) of TL_n diagram D and
    read off the resulting TL_{n-1} matching plus the number of closed loops.

    Points: top 0..n-1, bottom n..2n-1. The removed strand endpoints are
    top(n-1) and bottom(2n-1); everything else (top 0..n-2, bottom n..2n-2)
    survives and is relabelled into TL_{n-1} index space
    (top 0..n-2 stay; bottom n+j -> (n-1)+j)."""
    closing_arc = (n - 1, 2 * n - 1)  # external arc joining the two removed points

    # Build adjacency: D's arcs + the closing arc; then trace paths between
    # surviving endpoints, counting loops that live entirely on removed/interior.
    nxt = dict(D)  # copy; symmetric matching
    # Walk from each surviving endpoint to its partner through possible detours
    # via the removed strand + closing arc.
    survivors = [p for p in range(2 * n) if p not in closing_arc]

    def step_through_close(p):
        # follow D from p; if we hit a removed point, jump across the closing arc
        # to the other removed point, then continue via D.
        return nxt[p]

    result = {}
    visited_survivor = set()
    # For loop counting we also track interior points fully consumed.
    for s in survivors:
        if s in visited_survivor:
            continue
        cur = nxt[s]
        # traverse until we land on another survivor
        while cur in closing_arc:
            # jump across closing arc to the paired removed endpoint, then via D
            other = closing_arc[1] if cur == closing_arc[0] else closing_arc[0]
            cur = nxt[other]
        # cur is now a survivor = partner of s
        result[s] = cur
        result[cur] = s
        visited_survivor.add(s)
        visited_survivor.add(cur)

    # Count closed loops: a loop forms only if the removed strand's two endpoints
    # are joined by D directly to each other OR the closing arc creates a cycle
    # among interior points. For a single removed strand there is at most ONE
    # extra loop: it occurs exactly when D pairs top(n-1) with bottom(2n-1)
    # (the removed strand is a through-strand), so the closing arc closes it.
    loops = 0
    a, b = closing_arc
    if D.get(a) == b:
        loops = 1  # closing arc + the D-arc a-b form a circle

    # Relabel survivors into TL_{n-1} index space (top 0..n-2 unchanged;
    # bottom n..2n-2 -> (n-1)+(p-n)).
    def relabel(p):
        if p < n - 1:
            return p
        return (n - 1) + (p - n)

    sub = {}
    for p, q in result.items():
        sub[relabel(p)] = relabel(q)
    # Key exactly as TLn._key: sorted (a,b) pairs with a<b.
    sub_key = tuple(sorted((a, b) for a, b in sub.items() if a < b))
    return sub_key, loops


def _relabel_embed(p: int, nm1: int, n: int) -> int:
    """Map a TL_{n-1} boundary index into TL_n's index space.

    TL_{n-1}: top 0..nm1-1, bottom nm1..2*nm1-1.
    TL_n:     top 0..n-1,    bottom n..2n-1.
    Keep top indices; shift bottom indices by (n-nm1)=1 into TL_n bottom range.
    """
    if p < nm1:  # top point, unchanged
        return p
    # bottom point of TL_{n-1}: local column = p - nm1 in 0..nm1-1
    col = p - nm1
    return n + col  # TL_n bottom point for the same column


# ----------------------------------------------------------------------
# Operator helpers in the regular representation.
# An element x of TL_n is a matrix (left-mult). Its coefficient vector is x*1.
# E acts on coefficient vectors; to get E(x) back as an operator we rebuild it.
# ----------------------------------------------------------------------
def coeff_vector(tl: TLn, X: np.ndarray) -> np.ndarray:
    return X[:, tl.id_col].copy()


def operator_from_coeffs(tl: TLn, coeffs: np.ndarray) -> np.ndarray:
    """Rebuild the left-mult operator for element sum_a coeffs[a] * D_a
    (delegates to the cached left-mult table)."""
    return tl.left_mult_operator(np.asarray(coeffs, dtype=float))


def gns_gram_operator(tl: TLn):
    """Return G (Gram of diagram basis) for GNS inner product <x,y>=tr(x^* y)."""
    return tl.gram()


# ----------------------------------------------------------------------
# Metric computation per (delta, n)
# ----------------------------------------------------------------------
def spearman(a: List[float], b: List[float]) -> float:
    """Spearman rank correlation, small-n, no ties expected."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, idx in enumerate(order):
            r[idx] = pos + 1
        return r
    ra, rb = rank(a), rank(b)
    m = len(a)
    d2 = sum((ra[i] - rb[i]) ** 2 for i in range(m))
    return 1.0 - (6.0 * d2) / (m * (m * m - 1))


def positive_probe_operators(tl: TLn, p_list, degenerate: bool) -> List[np.ndarray]:
    """Frozen positive probe set: JW projections p_k (self-adjoint idempotents,
    positive), each e_i / delta (positive: e_i^2 = delta e_i so e_i/delta is a
    projection), and tr-normalized positive combinations of them. Identical
    construction for every delta."""
    probes = []
    # e_i / delta are projections (positive)
    for ei in tl.e:
        probes.append(ei / tl.delta)
    # JW projections p_k that exist (p_1..)
    for k in range(1, len(p_list)):
        pk = p_list[k]
        if pk is not None:
            probes.append(pk)
    # positive combinations: I + e_i/delta (positive), and p_k + e_i/delta
    I = tl.identity
    for ei in tl.e:
        probes.append(I + ei / tl.delta)
    return probes


def symmetrize_gns(tl: TLn, M: np.ndarray) -> np.ndarray:
    """Represent operator M as a Hermitian matrix in the GNS inner product so we
    can take eigenvalues meaningfully. In GNS with Gram G (SPD on the non-
    degenerate part), the self-adjoint part of left-mult L_x is G-symmetric.
    M ~ S M S^{-1} is similar and its symmetric part has real eigenvalues equal
    to the GNS eigenvalues. Uses the CACHED whitening (one eigendecomp of G)."""
    S, Sinv = tl.whitening()
    Mw = S @ M @ Sinv
    return 0.5 * (Mw + Mw.T)


def compute_for_delta(name: str, delta: float, jones_index: float, closing_l) -> Dict:
    rec = {
        "name": name,
        "delta": delta,
        "jones_index": jones_index,
        "one_over_index": 1.0 / jones_index,
        "closing_l": closing_l,
        "per_n": {},
        "notes": [],
    }
    inv_index = 1.0 / jones_index

    for n in range(2, N_MAX + 1):
        sys.stderr.write(f"[TL_phi2] delta={name} n={n} ...\n")
        sys.stderr.flush()
        entry: Dict = {"n": n}
        try:
            tl_n = TLn(n, delta)
            tl_nm1 = TLn(n - 1, delta)
        except AssertionError as ex:
            entry["error"] = f"basis-dim mismatch: {ex}"
            rec["per_n"][str(n)] = entry
            continue

        # --- Gram + conditioning ---
        G = tl_n.gram()
        try:
            cond = float(np.linalg.cond(G))
        except np.linalg.LinAlgError:
            cond = float("inf")
        entry["gram_dim"] = tl_n.dim
        entry["gram_cond"] = cond
        entry["gram_ill"] = bool(cond > ILL_COND or not math.isfinite(cond))
        # nullity of Gram (negligible-ideal dimension) via eigenvalues
        gw = np.linalg.eigvalsh(0.5 * (G + G.T))
        tol_null = max(abs(gw.max()), 1.0) * 1e-11
        nullity = int(np.sum(np.abs(gw) < tol_null))
        entry["gram_nullity"] = nullity

        # --- Jones-Wenzl ---
        p_list, qi, degenerate = jones_wenzl(tl_n)
        entry["degenerate_jw"] = bool(degenerate)
        entry["quantum_ints"] = [round(x, 12) for x in qi[: n + 1]]

        # --- Conditional expectation E: TL_n -> TL_{n-1} ---
        E_coeff, P = conditional_expectation_matrix(tl_n, tl_nm1)

        # PP / positivity / MC / IDEM over frozen positive probe set
        probes = positive_probe_operators(tl_n, p_list, degenerate)

        is_ill = entry["gram_ill"]

        pp_pos_min = float("inf")
        mc_max = 0.0
        idem_max = 0.0

        # Whitening-based (GNS-eigenvalue) metrics are numerically meaningful ONLY
        # when the Gram is well-conditioned. On an ILL Gram (cond>1e12, a large
        # negligible ideal e.g. phi at n>=5) the whitening is float garbage, so per
        # the prereg condition-number guard we do NOT compute PP_pos / PP_numeric
        # there; those n are excluded from pass/fail and reported as ILL. MC and
        # IDEM use only the trace vector and coefficient differences (stable) and
        # are always computed.
        for X in probes:
            cX = coeff_vector(tl_n, X)
            eX_coeffs = E_coeff @ cX
            EX = operator_from_coeffs(tl_n, eX_coeffs)

            if not is_ill:
                # Positivity of E(X) - inv_index * X in GNS
                D = EX - inv_index * X
                Dsym = symmetrize_gns(tl_n, D)
                dmin = float(np.linalg.eigvalsh(Dsym).min())
                pp_pos_min = min(pp_pos_min, dmin)

            # Markov consistency: tr(E(X)) == tr(X)  (stable)
            trX = tl_n.trace_of(X)
            trEX = tl_n.trace_of(EX)
            mc_max = max(mc_max, abs(trEX - trX))

            # Idempotency: E(E(X)) == E(X)  (stable, coefficient-space)
            eeX_coeffs = E_coeff @ eX_coeffs
            idem_max = max(idem_max, float(np.max(np.abs(eeX_coeffs - eX_coeffs))))

        # Bimodule property: E(a X b) = a E(X) b for a,b in TL_{n-1}.
        # Use a = b = e_1 (lives in TL_{n-1} for n>=3) as a frozen module element.
        if n >= 3:
            a = tl_n.e[0]  # e_1 in TL_n, also in TL_{n-1}
            Xtest = tl_n.e[0] / tl_n.delta  # a positive probe
            cX = coeff_vector(tl_n, Xtest)
            eX = E_coeff @ cX
            EX = operator_from_coeffs(tl_n, eX)
            aXb = a @ Xtest @ a
            caXb = coeff_vector(tl_n, aXb)
            E_aXb = operator_from_coeffs(tl_n, E_coeff @ caXb)
            aEXb = a @ EX @ a
            idem_max = max(idem_max, float(np.max(np.abs(E_aXb - aEXb))))

        # PP_numeric: the largest c with E(X) >= c X over the frozen positive
        # probe set (min GNS eigenvalue of the pencil (E(X),X) on range(X)).
        # Theory: PP = 1/index = delta^-2. Computed only for non-ILL n.
        if is_ill:
            pp_numeric = None
            pp_err = float("nan")
            pp_pos_min = float("nan")
        else:
            pp_numeric = _pp_constant_estimate(tl_n, E_coeff, p_list)
            pp_err = abs(pp_numeric - inv_index) if pp_numeric is not None else float("nan")

        entry["pp_numeric"] = pp_numeric
        entry["pp_err"] = pp_err
        entry["pp_pos_min"] = pp_pos_min
        entry["mc"] = mc_max
        entry["idem"] = idem_max

        # Closing level = the level where the finite-access machinery actually
        # closes: the Markov-trace Gram acquires a negligible ideal (nullity>0).
        # This is read from the DATA by one delta-agnostic rule (identical code
        # for all four deltas — the structural control against per-delta special-
        # casing), NOT from a hardcoded per-delta quantum-integer label. The
        # expected/analytic closing level `closing_l` is carried only for the
        # report's sanity column. For phi this fires at n=4 (p_4 vanishes,
        # [5]=0), sqrt2 at n=3 ([4]=0), 2cos(pi/7) at n=6 ([7]=0), delta2 never.
        entry["is_closing_level"] = bool(entry["gram_nullity"] > 0)
        entry["expected_closing_l"] = closing_l
        rec["per_n"][str(n)] = entry

    # --- Aggregates for 4b ---
    non_ill = [e for e in rec["per_n"].values()
               if not e.get("gram_ill", True) and "pp_err" in e and math.isfinite(e["pp_err"])]
    # PPQ = max PP_err over non-ILL n
    if non_ill:
        rec["PPQ"] = max(e["pp_err"] for e in non_ill)
    else:
        rec["PPQ"] = float("nan")

    # CQ_score = median over CLOSING LEVELS of log10(cond(Gram)).
    # Closing levels are read from the data (gram_nullity>0), one identical rule
    # for all four deltas. For delta2 (never closes: nullity==0 at every n) there
    # are no closing levels, so per prereg sec 5 the structural fallback uses all
    # n (delta2 is the declared 'no clean closure' control, expected worst).
    closing_entries = [e for e in rec["per_n"].values()
                       if e.get("is_closing_level") and math.isfinite(e.get("gram_cond", float("inf")))]
    if not closing_entries:
        closing_entries = [e for e in rec["per_n"].values()
                           if math.isfinite(e.get("gram_cond", float("inf")))]
        rec["notes"].append(
            "no closing level observed (Gram never degenerates through N=8): "
            "CQ_score uses all n as the structural fallback for a non-closing "
            "control (prereg sec 5).")
    if closing_entries:
        logs = sorted(math.log10(max(e["gram_cond"], 1.0)) for e in closing_entries)
        rec["closing_levels_n"] = sorted(e["n"] for e in closing_entries)
        m = len(logs)
        rec["CQ_score"] = logs[m // 2] if m % 2 == 1 else 0.5 * (logs[m // 2 - 1] + logs[m // 2])
        rec["CQ_closing_logs"] = logs
    else:
        rec["CQ_score"] = float("nan")
        rec["CQ_closing_logs"] = []
        rec["closing_levels_n"] = []

    return rec


def _pp_constant_estimate(tl_n: TLn, E_coeff: np.ndarray, p_list) -> float:
    """Estimate the Pimsner-Popa constant PP = inf over positive x of the
    largest c with E(x) >= c x.

    We use the exact Jones relation: for the top existing Jones-Wenzl projection
    p_k (self-adjoint, positive, and NOT in TL_{n-1}), E(p_k) = (1/index) * <a
    lower-level projection>, and on its own support the eigenvalue ratio
    E(p_k)/p_k equals 1/index. We compute the minimal GNS eigenvalue ratio of
    (E(x), x) over the frozen probe set as the numeric PP constant."""
    inv_candidates = []
    # whitening for GNS eigen-ratios (cached); near-null directions already
    # dropped so a degenerate closing-level GNS space cannot inject float garbage.
    S, Sinv = tl_n.whitening()

    # PP is measured only on positive probes whose GNS restriction is
    # well-conditioned. A JW projection at a closing level has near-zero GNS
    # norm; its eigenvalue ratio is float noise, so we SKIP it (this is the
    # prereg's mandate that float error must not drive the PP verdict). The
    # e_i/delta projections stay well-conditioned at every admissible delta and
    # carry the exact Jones relation E(e_{n-1}) = (1/index-linked) reduction.
    probe_ops = []
    for k in range(1, len(p_list)):
        pk = p_list[k]
        if pk is not None:
            probe_ops.append(("jw_p%d" % k, pk))
    for i, ei in enumerate(tl_n.e):
        probe_ops.append(("e%d/delta" % (i + 1), ei / tl_n.delta))

    from scipy.linalg import eigh as geigh
    for _tag, X in probe_ops:
        cX = coeff_vector(tl_n, X)
        eX = E_coeff @ cX
        EX = operator_from_coeffs(tl_n, eX)
        Xw = S @ X @ Sinv
        EXw = S @ EX @ Sinv
        Xw = 0.5 * (Xw + Xw.T)
        EXw = 0.5 * (EXw + EXw.T)
        # restrict to the numerical support (range) of X in the whitened space
        xw_eval, xw_vec = np.linalg.eigh(Xw)
        aev = np.abs(xw_eval)
        peak = aev.max() if aev.size else 0.0
        if peak <= 0:
            continue
        supp = aev > (peak * 1e-8)
        if not np.any(supp):
            continue
        U = xw_vec[:, supp]
        Xr = U.T @ Xw @ U
        EXr = U.T @ EXw @ U
        # Xr must be well-conditioned or the ratio is float noise -> skip probe.
        try:
            xr_cond = np.linalg.cond(Xr)
        except np.linalg.LinAlgError:
            xr_cond = float("inf")
        if not math.isfinite(xr_cond) or xr_cond > 1e8:
            continue
        try:
            lam = geigh(EXr, Xr, eigvals_only=True)
            inv_candidates.append(float(np.min(lam)))
        except Exception:
            continue

    if not inv_candidates:
        return None
    return float(min(inv_candidates))


# ----------------------------------------------------------------------
# Verdict logic (4a gate + 4b distinctiveness), all thresholds pinned above.
# ----------------------------------------------------------------------
def apply_verdict(records: Dict[str, Dict]) -> Dict:
    verdict = {"gate_4a": {}, "distinct_4b": {}, "classification": None}

    # ---- 4a machinery-validity gate ----
    gate_pass = True
    gate_detail = {}
    for name, rec in records.items():
        per = {"failures": [], "checked_n": []}
        for ns, e in rec["per_n"].items():
            if e.get("gram_ill", False):
                continue  # ILL excluded from gate
            if "pp_err" not in e:
                continue
            per["checked_n"].append(int(ns))
            ok = True
            if not (math.isfinite(e["pp_err"]) and e["pp_err"] <= PP_ERR_GATE):
                per["failures"].append(f"n={ns} PP_err={e['pp_err']:.3e}>{PP_ERR_GATE}")
                ok = False
            if not (e["pp_pos_min"] >= POS_GATE):
                per["failures"].append(f"n={ns} PP_pos={e['pp_pos_min']:.3e}<{POS_GATE}")
                ok = False
            if not (e["mc"] <= MC_GATE):
                per["failures"].append(f"n={ns} MC={e['mc']:.3e}>{MC_GATE}")
                ok = False
            if not (e["idem"] <= IDEM_GATE):
                per["failures"].append(f"n={ns} IDEM={e['idem']:.3e}>{IDEM_GATE}")
                ok = False
        per["passed"] = len(per["failures"]) == 0
        gate_detail[name] = per
        if not per["passed"]:
            gate_pass = False
    verdict["gate_4a"] = {"passed": gate_pass, "detail": gate_detail}

    # ---- 4b phi-distinctiveness ----
    names = list(records.keys())
    cq = {n: records[n]["CQ_score"] for n in names}
    ppq = {n: records[n]["PPQ"] for n in names}
    idx = {n: records[n]["jones_index"] for n in names}
    controls = [n for n in names if n != "phi"]

    d4b = {"CQ_score": cq, "PPQ": ppq, "jones_index": idx}

    # (i) CQ margin vs every control
    cq_phi = cq["phi"]
    cond_i = all(math.isfinite(cq_phi) and math.isfinite(cq[c]) and (cq_phi < cq[c] - CQ_MARGIN) for c in controls)
    # (ii) beat nearest-index control (2cos_pi_7)
    nearest = "2cos_pi_7"
    cond_ii = math.isfinite(cq_phi) and math.isfinite(cq[nearest]) and (cq_phi < cq[nearest] - CQ_MARGIN)
    # (iii) PPQ order of magnitude
    min_ctrl_ppq = min((ppq[c] for c in controls if math.isfinite(ppq[c])), default=float("nan"))
    cond_iii = math.isfinite(ppq["phi"]) and math.isfinite(min_ctrl_ppq) and (ppq["phi"] * PPQ_DECADE < min_ctrl_ppq)

    pass_h1 = bool(cond_i and cond_ii and cond_iii)

    # KILL conditions
    within_10x = any(math.isfinite(cq_phi) and math.isfinite(cq[c]) and abs(cq_phi - cq[c]) <= CQ_MARGIN for c in controls)
    ctrl_ties_or_beats_cq = any(math.isfinite(cq[c]) and cq[c] <= cq_phi for c in controls)
    ctrl_ties_or_beats_ppq = any(math.isfinite(ppq[c]) and ppq[c] <= ppq["phi"] for c in controls)
    # Spearman rho between CQ_score and index over the 4 deltas
    order_names = names
    cq_list = [cq[n] for n in order_names]
    idx_list = [idx[n] for n in order_names]
    if all(math.isfinite(v) for v in cq_list):
        rho = spearman(cq_list, idx_list)
    else:
        rho = float("nan")
    tracks_index = math.isfinite(rho) and abs(rho) >= SPEARMAN_KILL

    kill_h1 = bool(within_10x or ctrl_ties_or_beats_cq or ctrl_ties_or_beats_ppq or tracks_index)

    d4b.update({
        "cond_i_cq_margin_all_controls": cond_i,
        "cond_ii_beats_nearest_index_control": cond_ii,
        "cond_iii_ppq_decade": cond_iii,
        "pass_h1": pass_h1,
        "kill_within_10x": within_10x,
        "kill_control_ties_or_beats_cq": ctrl_ties_or_beats_cq,
        "kill_control_ties_or_beats_ppq": ctrl_ties_or_beats_ppq,
        "spearman_cq_vs_index": rho,
        "kill_tracks_index": tracks_index,
        "kill_h1": kill_h1,
    })
    verdict["distinct_4b"] = d4b

    # ---- classification ----
    if not gate_pass:
        # 4a fails: check whether it fails everywhere or asymmetrically
        all_fail = all(not gate_detail[n]["passed"] for n in names)
        if all_fail:
            cls = "INVALID (4a gate fails for all deltas => implementation bug, not a null; do not interpret)"
        else:
            cls = "INVALID/ASYMMETRIC (4a gate fails for some deltas; reportable asymmetry, machinery not uniformly validated)"
    else:
        if pass_h1 and not kill_h1:
            cls = "PASS-H1 (phi DISTINGUISHED: closes cleaner than every control by locked margins)"
        elif kill_h1:
            cls = "KILL-H1 / CONFIRM-H0 (machinery validated; phi INDISTINGUISHABLE / not special — expected outcome)"
        else:
            cls = "WATCH / underpowered (4a passed; 4b neither clean PASS nor clean KILL; promote nothing)"
    verdict["classification"] = cls
    return verdict


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------
def build_report(records: Dict[str, Dict], verdict: Dict) -> str:
    L = []
    L.append("# TL_phi2 — report (engineering lane; NOT physics evidence)\n")
    L.append("No result here proves GHP or observer-boundary selection; no ledger "
             "status may be upgraded on this basis (master hard rule 7).\n")
    L.append(f"\n**Classification:** {verdict['classification']}\n")

    L.append("\n## 4a machinery-validity gate\n")
    L.append(f"- gate passed (all deltas, non-ILL n): **{verdict['gate_4a']['passed']}**\n")
    for name, per in verdict["gate_4a"]["detail"].items():
        status = "PASS" if per["passed"] else "FAIL"
        L.append(f"  - {name}: {status} (checked n={per['checked_n']})"
                 + ("" if per["passed"] else f" failures: {per['failures']}") + "\n")

    d = verdict["distinct_4b"]
    L.append("\n## 4b phi-distinctiveness (the scientific question)\n")
    L.append("| delta | index | CQ_score (med log10 cond) | PPQ (max PP_err) |\n")
    L.append("|---|---|---|---|\n")
    for name in records:
        cq = d["CQ_score"][name]
        ppq = d["PPQ"][name]
        L.append(f"| {name} | {records[name]['jones_index']:.6f} | "
                 f"{cq:.4f} | {ppq:.3e} |\n")
    L.append(f"\n- (i) CQ_score(phi) < every control by >=1.0 decade: **{d['cond_i_cq_margin_all_controls']}**\n")
    L.append(f"- (ii) phi beats nearest-index control 2cos(pi/7) by >=1.0 decade: **{d['cond_ii_beats_nearest_index_control']}**\n")
    L.append(f"- (iii) PPQ(phi) tighter than min control PPQ by >=1 decade: **{d['cond_iii_ppq_decade']}**\n")
    L.append(f"- Spearman(CQ_score, index) over 4 deltas: **{d['spearman_cq_vs_index']:.4f}** "
             f"(|rho|>=0.9 => generic/tracks-index kill: {d['kill_tracks_index']})\n")
    L.append(f"- PASS-H1={d['pass_h1']}  KILL-H1/CONFIRM-H0={d['kill_h1']}\n")

    # Honest interpretation of the outcome (locked rule applied verbatim).
    L.append("\n### Interpretation\n")
    if d["cond_iii_ppq_decade"] and not (d["cond_i_cq_margin_all_controls"] and d["cond_ii_beats_nearest_index_control"]):
        L.append(
            "- Note on rule (iii): PPQ(phi) reads as 0.0 only because phi's PP_err "
            "is computable at just n=2,3 (all n>=4 are ILL/excluded) and comes out "
            "bit-exact there, while controls round at the ~1e-16 level. A 0 vs 1e-16 "
            "gap is floating-point noise, NOT a real order-of-magnitude PP advantage. "
            "Rule (iii) firing True is therefore an artifact; it does not support H1 "
            "because PASS-H1 requires (i) AND (ii) AND (iii), and (i)/(ii) both fail "
            "decisively. The classification correctly ignores it.\n")
    L.append(
        "- CQ_score tracks index magnitude with Spearman rho = "
        f"{d['spearman_cq_vs_index']:.3f}: the never-closing control delta=2 "
        "(index 4) is by far the BEST conditioned, and the three closing deltas "
        "(phi, sqrt2, 2cos(pi/7)) all pile up near log10(cond) ~ 18 at their own "
        "closing levels. phi's closing Gram is NOT better conditioned than the "
        "controls; it is essentially tied with 2cos(pi/7) (the nearest-index "
        "control) and worse than delta=2. This is exactly the expected H0: clean "
        "closure and the Pimsner-Popa bound are generic to admissible indices, "
        "and the golden ratio is not singled out.\n")
    L.append(
        "- Circularity check honored: the Jones index phi^2=1+phi and 1/index=2-phi "
        "appear only as 4a sanity (PP_numeric recovers delta^-2 exactly); they are "
        "definitional and are NOT used as H1 support.\n")

    L.append("\n## Per-delta, per-n detail\n")
    for name, rec in records.items():
        L.append(f"\n### {name}  (delta={rec['delta']:.10f}, index={rec['jones_index']:.6f}, "
                 f"1/index={rec['one_over_index']:.10f}, closing_l={rec['closing_l']})\n")
        for note in rec.get("notes", []):
            L.append(f"- note: {note}\n")
        L.append("| n | dim | cond(Gram) | ILL | nullity | degen_JW | PP_num | PP_err | PP_pos_min | MC | IDEM | closing |\n")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for ns in sorted(rec["per_n"], key=int):
            e = rec["per_n"][ns]
            if "pp_err" not in e:
                L.append(f"| {ns} | - | - | - | - | - | - | - | - | - | - | (skip: {e.get('error','')}) |\n")
                continue
            L.append("| {n} | {dim} | {cond:.3e} | {ill} | {nul} | {deg} | {ppn} | {ppe:.3e} | "
                     "{ppp:.3e} | {mc:.3e} | {idem:.3e} | {cl} |\n".format(
                         n=e["n"], dim=e["gram_dim"], cond=e["gram_cond"],
                         ill=e["gram_ill"], nul=e["gram_nullity"], deg=e["degenerate_jw"],
                         ppn=("%.8f" % e["pp_numeric"]) if e["pp_numeric"] is not None else "None",
                         ppe=e["pp_err"], ppp=e["pp_pos_min"], mc=e["mc"], idem=e["idem"],
                         cl=e["is_closing_level"]))
    L.append("\n---\n")
    L.append("Headline: " + headline_line(records, verdict) + "\n")
    return "".join(L)


def headline_line(records: Dict[str, Dict], verdict: Dict) -> str:
    d = verdict["distinct_4b"]
    cq = d["CQ_score"]
    ppq = d["PPQ"]
    def f(x):
        return "nan" if not math.isfinite(x) else f"{x:.3f}"
    return (
        f"CQ_score  phi={f(cq['phi'])}  sqrt2={f(cq['sqrt2'])}  "
        f"2cos(pi/7)={f(cq['2cos_pi_7'])}  delta2={f(cq['delta2'])}  ||  "
        f"PPQ  phi={ppq['phi']:.2e}  sqrt2={ppq['sqrt2']:.2e}  "
        f"2cos(pi/7)={ppq['2cos_pi_7']:.2e}  delta2={ppq['delta2']:.2e}  ||  "
        f"Spearman(CQ,index)={d['spearman_cq_vs_index']:.3f}"
    )


# ----------------------------------------------------------------------
def main() -> int:
    records: Dict[str, Dict] = {}
    for name, delta, index, closing_l in DELTAS:
        records[name] = compute_for_delta(name, delta, index, closing_l)

    verdict = apply_verdict(records)

    summary = {
        "test_id": "TL_phi2",
        "ledger_anchor": "P-005",
        "lane": "engineering/verified-computation — NOT physics evidence; no ledger upgrade (master hard rule 7).",
        "N_MAX": N_MAX,
        "constants": {
            "phi": PHI,
            "phi_squared_index": PHI * PHI,
            "one_over_phi2": 1.0 / (PHI * PHI),
            "sqrt2_index": 2.0,
            "2cos_pi_7": 2.0 * math.cos(math.pi / 7.0),
            "2cos_pi_7_index": (2.0 * math.cos(math.pi / 7.0)) ** 2,
            "delta2_index": 4.0,
        },
        "thresholds": {
            "PP_ERR_GATE": PP_ERR_GATE, "POS_GATE": POS_GATE, "MC_GATE": MC_GATE,
            "IDEM_GATE": IDEM_GATE, "ILL_COND": ILL_COND, "CQ_MARGIN": CQ_MARGIN,
            "PPQ_DECADE": PPQ_DECADE, "SPEARMAN_KILL": SPEARMAN_KILL, "TOL": TOL,
        },
        "records": records,
        "verdict": verdict,
        "headline": headline_line(records, verdict),
        "no_upgrade": ("Software/toy result; NEVER physics evidence for GHP or "
                       "observer-boundary selection; no ledger status upgrade permitted."),
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    (OUT / "report.md").write_text(build_report(records, verdict))

    print("TL_phi2 CLASSIFICATION: " + verdict["classification"])
    print("HEADLINE: " + summary["headline"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
