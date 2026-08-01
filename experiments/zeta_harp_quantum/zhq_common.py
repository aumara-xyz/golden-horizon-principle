#!/usr/bin/env python3
"""Shared helpers for the Zeta Harp Quantum Portal experiments.

Pure Python + numpy + mpmath. No qiskit, no quantum SDK: everything here is
classical state-vector simulation and exact finite-dimensional linear algebra.

Central objects (N = floor(sqrt(t/2pi)), A_N = sum_{n=1}^{N} n^(-1/2)):

    M(t)      = 2 * sum_{n=1}^{N} n^(-1/2) cos(theta(t) - t ln n)   (Riemann-Siegel main sum)
    |psi(t)>  = (1/sqrt(A_N)) sum_n n^(-1/4) e^{i phi_n(t)} |n>,  phi_n(t) = theta(t) - t ln n
    |w_N>     = (1/sqrt(A_N)) sum_n n^(-1/4) |n>

    Identity: M(t) = 2 A_N Re<w_N|psi(t)>,  with <psi|psi> = <w|w> = 1.

    Two-line proof:
      <w_N|psi(t)> = (1/A_N) sum_n n^(-1/4) * n^(-1/4) e^{i phi_n(t)} = (1/A_N) sum_n n^(-1/2) e^{i phi_n(t)}
      2 A_N Re<w_N|psi(t)> = 2 sum_n n^(-1/2) cos(phi_n(t)) = M(t).

Scope statement (binding): this is an EXACT FINITE-DIMENSIONAL EMBEDDING of the
Riemann-Siegel MAIN SUM. It is not the full Hardy function Z(t) (the O(t^(-1/4))
remainder is outside the register), it makes no speedup claim, and it supports no
statement about the Riemann Hypothesis.
"""

import json
import math
import os
import subprocess
import sys
import time

import numpy as np
import mpmath as mp

MP_DPS = 50
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Tolerances (stated, machine-enforced)
TOL_IDENTITY = 1e-12       # |M_direct - 2 A_N Re<w|psi>| in float64
TOL_NORM = 1e-12           # | <psi|psi> - 1 | and | <w|w> - 1 |
TOL_EXACT_SIM = 1e-12      # noiseless Hadamard-test recovery vs analytic overlap
TOL_TT_FULL = 1e-10        # full-bond tensor-train reconstruction

# ---------------------------------------------------------------------------
# Riemann-Siegel main-sum machinery
# ---------------------------------------------------------------------------

def n_terms(t):
    """N(t) = floor(sqrt(t/2pi)), computed in mpmath."""
    with mp.workdps(MP_DPS):
        return int(mp.floor(mp.sqrt(mp.mpf(t) / (2 * mp.pi))))


def theta_mp(t):
    """Riemann-Siegel theta(t) at high precision (mpmath.siegeltheta)."""
    with mp.workdps(MP_DPS):
        return mp.siegeltheta(mp.mpf(t))


def phases(t, N=None):
    """Return (N, numpy float64 array of phi_n(t) mod 2pi for n = 1..N).

    phi_n(t) = theta(t) - t ln n, reduced mod 2pi in mpmath BEFORE the cast to
    float64, so the float phases are accurate even at t ~ 1e6 where t ln n is
    ~ 1e7 and naive float64 subtraction would lose digits.
    """
    if N is None:
        N = n_terms(t)
    out = np.empty(N, dtype=np.float64)
    with mp.workdps(MP_DPS):
        tm = mp.mpf(t)
        th = mp.siegeltheta(tm)
        twopi = 2 * mp.pi
        for n in range(1, N + 1):
            ph = th - tm * mp.log(n)
            out[n - 1] = float(ph - twopi * mp.floor(ph / twopi))
    return N, out


def amplitude_data(N):
    """Return (A_N float, amps float64 array a_n = n^(-1/4)/sqrt(A_N))."""
    ns = np.arange(1, N + 1, dtype=np.float64)
    A = float(np.sum(ns ** -0.5))
    amps = (ns ** -0.25) / math.sqrt(A)
    return A, amps


def psi_state(t, N=None):
    """Return (N, A_N, psi) — normalized complex state vector of length N."""
    N, phi = phases(t, N)
    A, amps = amplitude_data(N)
    return N, A, amps * np.exp(1j * phi)


def w_state(N):
    """Normalized real reference state |w_N> of length N."""
    _, amps = amplitude_data(N)
    return amps.astype(np.complex128)


def M_direct(t, N=None):
    """M(t) = 2 sum n^(-1/2) cos(phi_n) computed directly from the same phases."""
    N, phi = phases(t, N)
    ns = np.arange(1, N + 1, dtype=np.float64)
    return float(2.0 * np.sum(ns ** -0.5 * np.cos(phi)))


def M_from_overlap(t, N=None):
    """M(t) reconstructed as 2 A_N Re<w_N|psi(t)>."""
    N, A, psi = psi_state(t, N)
    w = w_state(N)
    return float(2.0 * A * np.real(np.vdot(w, psi)))


# ---------------------------------------------------------------------------
# Qutrit register mappings (terms 1..26 -> noncentral states of {0,1,2}^3)
# |0,0,0> (index 0) is the RESERVED REFERENCE BASIS STATE / INTERFACE ANCHOR:
# it carries zero amplitude in every mapping.
# ---------------------------------------------------------------------------

def trits_to_index(trits):
    a, b, c = trits
    return 9 * a + 3 * b + c


def index_to_trits(i):
    return (i // 9, (i // 3) % 3, i % 3)


def map_lexicographic():
    """n -> base-3 digits of n (3 trits, MSB first), n = 1..26.

    n = 0 would be (0,0,0); it is excluded, so the reserved state is never hit.
    """
    return {n: index_to_trits(n) for n in range(1, 27)}


def _balanced_ternary_digits(v):
    """Balanced-ternary digits (d2, d1, d0) in {-1,0,+1} with v = 9 d2 + 3 d1 + d0."""
    digits = []
    for _ in range(3):
        r = v % 3
        if r == 2:
            r = -1
        digits.append(r)
        v = (v - r) // 3
    assert v == 0
    return tuple(reversed(digits))


def map_balanced_ternary():
    """n -> balanced-ternary digits of a signed value v(n), digit d -> trit (d mod 3).

    v(n) = n - 14 for n <= 13 (values -13..-1) and n - 13 for n >= 14 (values 1..13):
    a bijection of 1..26 onto the NONZERO balanced-ternary range {-13..-1, 1..13}.
    Each v has a unique 3-digit balanced-ternary form (d2, d1, d0) in {-1,0,+1};
    digits map digitwise to trits by d mod 3 (so -1 -> 2, 0 -> 0, +1 -> 1). The
    trit triple (0,0,0) corresponds only to v = 0, which is excluded, so |0,0,0>
    is reserved and the map is a bijection onto the 26 noncentral states.

    NOTE (bug fixed during build, kept for the record): the naive shift d -> d+1
    on balanced digits of (n - 13) is the IDENTITY index map
    9(d2+1) + 3(d1+1) + (d0+1) = (n-13) + 13 = n, i.e. it silently duplicates the
    lexicographic mapping. The d mod 3 form above is genuinely distinct.
    """
    out = {}
    for n in range(1, 27):
        v = n - 14 if n <= 13 else n - 13
        d = _balanced_ternary_digits(v)
        out[n] = tuple(x % 3 for x in d)
    return out


def map_gray_ternary():
    """n -> reflected-ternary-Gray code of n (3 trits), n = 1..26.

    Gray digits from base-3 digits (MSB first): g[0] = d[0]; g[i] = (d[i] - d[i-1]) mod 3.
    This is a bijection on 0..26 with gray(0) = (0,0,0), so indices 1..26 give a
    bijection onto the 26 noncentral states with |0,0,0> reserved. Successive codes
    differ in a single trit (Gray-like property).
    """
    out = {}
    for n in range(1, 27):
        d = index_to_trits(n)
        g = (d[0], (d[1] - d[0]) % 3, (d[2] - d[1]) % 3)
        out[n] = g
    return out


MAPPINGS = {
    "lexicographic": map_lexicographic,
    "balanced_ternary": map_balanced_ternary,
    "gray_ternary": map_gray_ternary,
}


def embed_terms(term_amplitudes, mapping, dim=27):
    """Embed complex amplitudes for terms 1..len into a dim-vector via mapping."""
    v = np.zeros(dim, dtype=np.complex128)
    for n, amp in enumerate(term_amplitudes, start=1):
        v[trits_to_index(mapping[n])] = amp
    return v


# ---------------------------------------------------------------------------
# Tensor-train (sequential SVD) machinery
# ---------------------------------------------------------------------------

def tt_svd(x, max_bond):
    """Tensor-train decomposition of ndarray x by sequential SVD.

    Bond dimensions are capped at max_bond (no tolerance-based truncation, so the
    error-vs-bond curve is clean). Returns list of cores with shapes
    (r_{k-1}, d_k, r_k).
    """
    dims = x.shape
    cores = []
    r_prev = 1
    T = x.reshape(dims[0], -1)
    for k in range(len(dims) - 1):
        T = T.reshape(r_prev * dims[k], -1)
        U, S, Vh = np.linalg.svd(T, full_matrices=False)
        r = min(max_bond, len(S))
        cores.append(U[:, :r].reshape(r_prev, dims[k], r))
        T = S[:r, None] * Vh[:r]
        r_prev = r
    cores.append(T.reshape(r_prev, dims[-1], 1))
    return cores


def tt_reconstruct(cores):
    out = cores[0]
    for core in cores[1:]:
        out = np.tensordot(out, core, axes=([out.ndim - 1], [0]))
    return out.reshape([c.shape[1] for c in cores])


def tt_param_count(cores):
    return int(sum(c.size for c in cores))


# ---------------------------------------------------------------------------
# Output metadata (every output carries source commit, seeds, tolerances)
# ---------------------------------------------------------------------------

def source_commit():
    try:
        h = subprocess.run(
            ["git", "-C", REPO_ROOT, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        b = subprocess.run(
            ["git", "-C", REPO_ROOT, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return {"base_commit": h, "branch": b,
                "note": "outputs generated from the working tree that became the "
                        "'Quantum Portal v1' commit; base_commit is its parent HEAD"}
    except Exception as exc:  # pragma: no cover
        return {"base_commit": "unknown", "branch": "unknown", "error": str(exc)}


def run_metadata(seeds=None, tolerances=None):
    meta = {
        "source": source_commit(),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "mpmath": mp.__version__,
        "mp_dps": MP_DPS,
        "seeds": seeds if seeds is not None else "none (deterministic)",
        "tolerances": tolerances or {},
        "claim_boundary": (
            "exact finite-dimensional embedding of the Riemann-Siegel MAIN SUM; "
            "remainder term outside the register; no speedup claim; no RH claim; "
            "state preparation treated as an assumed oracle whose cost is NOT claimed"
        ),
    }
    return meta


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"wrote {os.path.relpath(path, REPO_ROOT)}")
