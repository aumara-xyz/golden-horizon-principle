#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modular_www_v2 — Modular-Flow Write/Witness/Release Stress Test (ternary vs binary)
====================================================================================
REBUILD of modular_www with a LIVE (non-unitary) substrate + a non-tautological
contradiction stream. Same prereg, controls, thresholds, seeds, numerology guard,
and determinism as v1.

LANE: Engineering / verified-computation telemetry ONLY. Deterministic, offline,
Python 3.9 + numpy/scipy only, fixed seeds 0-9. Runs small/fast on system python3.

------------------------------------------------------------------------------
NO-UPGRADE SENTENCE (verbatim, load-bearing):
Software/toy success is NEVER physics evidence (master hard rule 7): no outcome
of this script proves GHP, observer-boundary selection, phi selection, or a
write-law, and even a clean PASS is a single-toy engineering result -- claiming
"ternary witness is a universal memory law" is the forbidden upgrade and voids
interpretation.
------------------------------------------------------------------------------

FIX NOTE (why v2 exists; addresses the verifier critique of v1):
  (1) INERT SUBSTRATE (v1 bug): v1's rho started maximally mixed (I/dim) and every
      operation (local_kick, modular_flow_step) was UNITARY, which preserves I/dim
      EXACTLY. So D(rho_t||rho_ref) was pinned at a constant (~1.97), the relative-
      entropy trigger fired 100% of the time doing zero work, and the test silently
      collapsed to classical cosine-sorting.
      FIX: the substrate is now genuinely NON-UNITARY / DISSIPATIVE. Each step
      applies a completely-positive trace-preserving (CPTP) channel:
        - a payload-dependent amplitude-damping + dephasing relaxation that pulls
          rho toward a payload-CONDITIONED target state (a weak-measurement / update
          channel), interleaved with
        - a modular-flow drift toward the Gibbs reference (Kraus mixture with
          rho_ref), so the state genuinely relaxes and is re-excited.
      Because these maps are NOT unitary, I/dim is NOT a fixed point: rho leaves the
      maximally-mixed manifold, D(rho_t||rho_ref) takes many distinct values, rises
      and falls, and the theta-trigger now carries real information. A runtime
      assertion checks ||rho_final - I/dim||_F is NOT ~0 and that D over the run
      takes MANY distinct values (recorded in summary as substrate_liveness).
  (2) TAUTOLOGICAL CONTRADICTION STREAM (v1 bug): v1 made +1 payloads exactly
      parallel to an anchor and -1 payloads exactly ANTIPODAL (-anchor), so a
      cosine-sign release rule trivially discarded the whole -1 half. That is
      near-tautological, not a general witness capability.
      FIX: contradictory payloads now have PARTIAL, non-trivial cosine separation
      from consensus (spread over ~60-120 degrees, i.e. cosine in roughly
      [-0.5, +0.5], NOT -1). A cosine-sign release can no longer trivially win; the
      witness/quarantine machinery must earn its keep. The +1/-1 populations
      overlap in cosine space, so binary matching or winning is a live, honest
      outcome. Recorded as contradiction_separation_audit in summary.

Everything else (metrics, regimes, controls, prereg bars, leak-scan, seeds,
numerology guard) is carried over unchanged from v1.

------------------------------------------------------------------------------
PREREGISTRATION (LOCKED before run; embedded verbatim-in-substance):

test_id: modular_www_v2

H1 (ternary advantage): In a phi-free modular-flow memory channel (2-4 qubit
sites, fixed XXZ Gibbs reference rho_ref, LIVE non-unitary substrate, boundary
updates fired when D(rho_t||rho_ref) > theta), a TERNARY policy {WRITE /
WITNESS-quarantine / RELEASE} beats a BINARY policy {WRITE / NO-WRITE} on at
least one predeclared metric x regime pair. "Beats" at the LOCKED primary
operating point (theta=0.10, quarantine window w=4) means:
  (a) Delta >= 0.05 absolute on the metric (>= 0.05 pollution reduction),
  (b) same-sign per-seed paired difference in >= 8 of 10 seeds, and
  (c) seed-paired bootstrap 95% CI (10k resamples) excluding 0.
Designated metric per regime: delayed-meaning -> delayed-meaning-recovery;
contradiction -> pollution (negative = better); overload -> overload-recovery;
concept-drift -> retention. Ternary must clear this bar over BINARY and over
BOTH degenerate-ternary controls (random-third, rate-matched-binary throttle)
on the same winning pair.

H0 (AU v1-v3 prior): Binary matches or beats ternary everywhere. On EVERY
predeclared metric x regime pair ternary's advantage fails the H1 bar at the
primary operating point -- |Delta| < 0.05, OR sign unstable in < 8/10 seeds, OR
paired-bootstrap 95% CI includes 0. A null result is fully valuable and is
recorded verbatim as "binary matches/wins -- AU v1-v3 prior confirmed."

KILL / PASS RULE (primary operating point theta=0.10, w=4 ONLY; sweeps are
robustness context and CANNOT move the call):
  PASS (ternary): H1 satisfied on >= 1 metric x regime pair, over binary AND
    both degenerate controls, AND ternary does NOT lose by the same bar on
    retention or pollution in ANY regime (a win offset by a symmetric loss
    elsewhere is NOT a pass).
  KILL / null holds: no metric x regime pair meets the full H1 bar -> record
    "binary matches/wins -- AU v1-v3 prior confirmed."
  HARDER KILL: ternary strictly worse than binary by the H1 bar on retention
    or pollution in >= 1 regime with no offsetting qualifying win -> net-negative.
No parameter, threshold, seed count, or metric definition may change after the
first data is observed.

CIRCULAR / INVALID (auto-fail, neither pass nor kill):
  (1) Ground-truth leak (policy reads truth stamp / regime label / future
      stream) -- enforced by a leak-scan assertion.
  (2) Metric defined by the winner (references WITNESS/quarantine state).
  (3) Tuning after seeing data.
  (4) Asymmetric effort (bigger register / extra looks for ternary).
  (5) NUMEROLOGY: this channel contains NO phi / Fibonacci / golden structure
      anywhere -- any golden constant in H, the update, the metrics, or the
      analysis makes the result CIRCULAR to the wider GHP program and INVALID.
  (6) Universality overreach.

NOTE ON SYSTEM SIZE: this script uses n=3 sites (Hilbert dim 8) as the primary
system for the full 10-seed x 4-regime x 4-policy x (theta,w) sweep so the run
finishes quickly on system python3. n in {2,4} are exercised in a shape/validity
smoke check (see run_size_smoke). The primary pass/kill decision is taken at n=3,
theta=0.10, w=4. This shrink is declared here, before any decision is read.
"""

import os
import json
import warnings
import numpy as np
from scipy.linalg import expm

warnings.filterwarnings("ignore", message=".*encountered in matmul.*",
                        category=RuntimeWarning)

# ----------------------------------------------------------------------------
# NUMEROLOGY GUARD (declared): no golden / Fibonacci / phi constant anywhere.
# ----------------------------------------------------------------------------

# ---- Frozen system Hamiltonian coefficients (XXZ, phi-FREE) -----------------
J_COUPLING   = 1.0     # nearest-neighbour XX+YY coupling
DELTA_ANISO  = 0.7     # ZZ anisotropy (XXZ). NOT golden.
H_FIELD      = 0.35    # transverse field, breaks trivial degeneracy. NOT golden.

# ---- Frozen protocol constants ----------------------------------------------
N_SITES_PRIMARY = 3          # primary system size (Hilbert dim 8)
T_STEPS         = 60         # step budget (identical for all policies)
DT_MODULAR      = 0.30       # modular-flow time increment per step
REGISTER_SIZE   = 6          # boundary memory slots (identical for all policies)
ADMISS_BAND     = 0.5        # frozen admissibility magnitude band (normalized)
SEEDS           = list(range(10))
N_BOOT          = 10000      # bootstrap resamples (seed-paired)
EPS_FRAC        = 0.15       # epsilon-sensitivity perturbation fraction

# ---- LIVE-SUBSTRATE (non-unitary) channel constants (phi-FREE) --------------
# These govern the completely-positive trace-preserving (CPTP) evolution. None is
# golden or Fibonacci. They are held fixed for all policies and all regimes.
GAMMA_RELAX   = 0.25   # amplitude-damping / measurement-update strength per event
GAMMA_DEPHASE = 0.15   # dephasing strength per event
GAMMA_DRIFT   = 0.20   # relaxation strength toward Gibbs reference per step
KICK_MEAS     = 0.8    # weight of payload-conditioned target in the update channel

# Sweeps (robustness context only -- cannot move the call)
THETA_SWEEP = [0.05, 0.10, 0.20, 0.40]
W_SWEEP     = [2, 4, 8]

# LOCKED primary operating point
THETA_PRIMARY = 0.10
W_PRIMARY     = 4

REGIMES = ["delayed-meaning", "contradiction", "overload", "concept-drift"]
POLICIES = ["binary", "ternary", "random-third", "rate-matched-binary"]

# Designated headline metric per regime (prereg section 10)
DESIGNATED_METRIC = {
    "delayed-meaning": "delayed_meaning_recovery",
    "contradiction":   "pollution",            # lower better -> advantage = binary - ternary
    "overload":        "overload_recovery",
    "concept-drift":   "retention",
}
# metrics where LOWER is better (advantage sign flips)
LOWER_BETTER = {"pollution"}

H1_DELTA = 0.05  # absolute margin bar

# Regime-specific frozen inverse temperature (declared in prereg section 3)
BETA_BY_REGIME = {
    "delayed-meaning": 0.9,
    "contradiction":   0.9,
    "overload":        0.9,
    "concept-drift":   0.9,   # ref frozen; "drift" is in the STREAM, not in rho_ref
}


# ============================================================================
# Reference state and modular flow (the ONLY use of modular structure)
# ============================================================================
def pauli():
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    return I, X, Y, Z


def op_at(op, site, n):
    """Embed single-site operator at `site` in an n-site chain."""
    I = np.eye(2, dtype=complex)
    mats = [I] * n
    mats[site] = op
    out = mats[0]
    for k in range(1, n):
        out = np.kron(out, mats[k])
    return out


def xxz_hamiltonian(n):
    """Frozen nearest-neighbour XXZ Hamiltonian + transverse field. phi-FREE."""
    I, X, Y, Z = pauli()
    dim = 2 ** n
    H = np.zeros((dim, dim), dtype=complex)
    for i in range(n - 1):
        H += J_COUPLING * (op_at(X, i, n) @ op_at(X, i + 1, n))
        H += J_COUPLING * (op_at(Y, i, n) @ op_at(Y, i + 1, n))
        H += DELTA_ANISO * (op_at(Z, i, n) @ op_at(Z, i + 1, n))
    for i in range(n):
        H += H_FIELD * op_at(X, i, n)
    return H  # Hermitian by construction


def gibbs_reference(n, beta):
    H = xxz_hamiltonian(n)
    M = expm(-beta * H)
    rho = M / np.trace(M).real
    rho = 0.5 * (rho + rho.conj().T)  # hermitize numerical noise
    return rho


def modular_unitary(rho_ref, dt):
    """
    U(dt) = rho_ref^{i*dt} = exp(i*dt*log rho_ref) via eigendecomposition of the
    Hermitian PD reference. The ONLY use of modular structure. phi-FREE.
    """
    ev, U = np.linalg.eigh(0.5 * (rho_ref + rho_ref.conj().T))
    ev = np.clip(ev, 1e-15, None)
    phase = np.exp(1j * dt * np.log(ev))      # lambda^{i*dt}
    return (U * phase) @ U.conj().T


def modular_flow_unitary_step(rho, rho_ref, dt):
    """sigma_dt(rho) = rho_ref^{i*dt} rho rho_ref^{-i*dt} (unitary modular flow)."""
    Umod = modular_unitary(rho_ref, dt)
    out = Umod @ rho @ Umod.conj().T
    out = 0.5 * (out + out.conj().T)
    tr = np.trace(out).real
    if tr != 0:
        out = out / tr
    return out


# ----------------------------------------------------------------------------
# LIVE SUBSTRATE: genuine non-unitary (CPTP) evolution. THE v2 FIX #1.
# ----------------------------------------------------------------------------
def dissipative_drift_step(rho, rho_ref, dt, gamma_drift):
    """
    One step of substrate evolution that is NON-UNITARY:
      1. unitary modular-flow drift (mixes coherences), then
      2. a convex relaxation toward the Gibbs reference:
             rho <- (1-g) * sigma_dt(rho) + g * rho_ref.
    Step 2 is a valid CPTP map (a mixture of the identity channel and the
    "replace-with-rho_ref" channel, both CPTP; a convex mixture of CPTP maps is
    CPTP). It is NOT unitary and I/dim is NOT its fixed point (the fixed point is
    rho_ref, which is not maximally mixed), so D(rho||rho_ref) genuinely relaxes.
    """
    rho = modular_flow_unitary_step(rho, rho_ref, dt)
    g = gamma_drift
    out = (1.0 - g) * rho + g * rho_ref
    out = 0.5 * (out + out.conj().T)
    tr = np.trace(out).real
    if tr != 0:
        out = out / tr
    return out


def _local_target_from_payload(payload, n):
    """
    Build a per-site Bloch target from the boundary-visible payload direction ONLY
    (no truth stamp, no regime label). The payload is a unit vector in R^PAYLOAD_DIM;
    we deterministically fold it into n Bloch vectors (one per qubit) with |b|<=1.
    Returns a product target density matrix (pure-ish, payload-conditioned).
    """
    # deterministic fold of the payload into 3*n Bloch components
    comps = np.resize(payload, 3 * n)
    rho_t = None
    I, X, Y, Z = pauli()
    for s in range(n):
        bx, by, bz = comps[3 * s:3 * s + 3]
        b = np.array([bx, by, bz], dtype=float)
        nb = np.linalg.norm(b)
        if nb > 1.0:
            b = b / nb          # keep inside/on the Bloch ball -> valid state
        single = 0.5 * (I + b[0] * X + b[1] * Y + b[2] * Z)
        rho_t = single if rho_t is None else np.kron(rho_t, single)
    return rho_t


def measurement_update_channel(rho, payload, n, gamma_relax, gamma_dephase,
                               kick_meas):
    """
    Payload-CONDITIONED weak-measurement / relaxation channel (NON-UNITARY, CPTP).
    Moves rho toward a payload-conditioned target and adds dephasing. The channel
    depends ONLY on the boundary-visible payload direction (leak-safe).

      1. amplitude-damping-like pull toward the payload target:
             rho <- (1 - a) * rho + a * rho_target,   a = gamma_relax * kick_meas
      2. dephasing toward the diagonal in the payload-target eigenbasis:
             rho <- (1 - d) * rho + d * diag_in_basis(rho),  d = gamma_dephase
    Both are convex mixtures of CPTP maps -> CPTP. Neither is unitary; I/dim is not
    preserved. This is what makes D(rho||rho_ref) actually move with the stream.
    """
    rho_target = _local_target_from_payload(payload, n)

    a = gamma_relax * kick_meas
    rho = (1.0 - a) * rho + a * rho_target

    # dephasing in the target eigenbasis (a genuine decoherence channel)
    evals, V = np.linalg.eigh(0.5 * (rho_target + rho_target.conj().T))
    coeff = V.conj().T @ rho @ V
    coeff_dephased = coeff.copy()
    off = ~np.eye(coeff.shape[0], dtype=bool)
    coeff_dephased[off] = (1.0 - gamma_dephase) * coeff[off]
    rho = V @ coeff_dephased @ V.conj().T

    rho = 0.5 * (rho + rho.conj().T)
    tr = np.trace(rho).real
    if tr != 0:
        rho = rho / tr
    return rho


def relative_entropy(rho, rho_ref):
    """D(rho||rho_ref) = tr[rho(log rho - log rho_ref)] >= 0. Trigger signal."""
    ev_r, U_r = np.linalg.eigh(0.5 * (rho + rho.conj().T))
    ev_ref, U_ref = np.linalg.eigh(0.5 * (rho_ref + rho_ref.conj().T))
    ev_r = np.clip(ev_r, 1e-12, None)
    ev_ref = np.clip(ev_ref, 1e-12, None)
    log_rho = (U_r * np.log(ev_r)) @ U_r.conj().T
    log_ref = (U_ref * np.log(ev_ref)) @ U_ref.conj().T
    D = np.trace(rho @ (log_rho - log_ref)).real
    return max(D, 0.0)


# ============================================================================
# Stream generator (ground truth stamped here; visible ONLY to the scorer)
# ============================================================================
class Event:
    __slots__ = ("payload", "site", "angle", "axis", "truth", "reveal_step")

    def __init__(self, payload, site, angle, axis, truth, reveal_step=-1):
        self.payload = payload          # unit vector in R^PAYLOAD_DIM
        self.site = site
        self.angle = angle
        self.axis = axis
        self.truth = truth              # +1 meaningful, -1 spurious/contradictory (GT)
        self.reveal_step = reveal_step  # for delayed-meaning: meaningful after this step


PAYLOAD_DIM = 8  # abstract payload embedding dimension (independent of n)


def _rand_unit(rng, dim=PAYLOAD_DIM):
    v = rng.standard_normal(dim)
    return v / (np.linalg.norm(v) + 1e-12)


def _normalize(v):
    return v / (np.linalg.norm(v) + 1e-12)


def _orthogonalize(v, ref):
    """Return unit component of v orthogonal to ref (Gram-Schmidt)."""
    ref = _normalize(ref)
    v = v - np.dot(v, ref) * ref
    return _normalize(v)


def _partial_contradiction(anchor, ortho_dir, cos_target, rng, jitter=0.08):
    """
    Build a unit payload whose cosine with `anchor` is ~cos_target (NON-antipodal),
    by mixing anchor and an orthogonal direction:
        p = cos_target*anchor + sqrt(1-cos_target^2)*ortho + small jitter.
    This gives PARTIAL, non-trivial cosine separation (v2 FIX #2): contradictory
    payloads are ~60-120 degrees from consensus, NOT at 180 degrees, so a
    cosine-sign release cannot trivially discard them.
    """
    c = float(cos_target)
    c = max(-0.9, min(0.9, c))
    p = c * _normalize(anchor) + np.sqrt(max(0.0, 1 - c * c)) * _normalize(ortho_dir)
    p = p + jitter * _rand_unit(rng)
    return _normalize(p)


def make_stream(regime, seed, T=T_STEPS):
    """Return list of length T; each entry is Event or None (no candidate)."""
    rng = np.random.default_rng(seed * 1000 + REGIMES.index(regime))
    events = [None] * T
    anchor_true = _rand_unit(rng)
    anchor_true2 = _rand_unit(rng)

    if regime == "delayed-meaning":
        reveal = T // 2
        for t in range(T):
            if t % 3 == 0:
                strong = t >= reveal
                angle = (0.9 if strong else 0.18) + 0.03 * rng.standard_normal()
                payload = _normalize(anchor_true + 0.15 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  angle, rng.choice(["x", "y", "z"]),
                                  truth=+1, reveal_step=reveal)
            elif t % 3 == 1:
                events[t] = Event(_rand_unit(rng), rng.integers(0, N_SITES_PRIMARY),
                                  0.25 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=-1)

    elif regime == "contradiction":
        # v2 FIX #2: contradictory candidates have PARTIAL (non-antipodal) cosine
        # separation from the consensus anchor. Meaningful (+1) payloads cluster
        # NEAR the anchor (cosine ~ +0.6..+0.9); contradictory (-1) payloads sit at
        # a PARTIAL angle (cosine ~ -0.4..+0.4, i.e. roughly orthogonal / 60-120deg),
        # NOT antipodal. The two populations OVERLAP in cosine, so a cosine-sign
        # release cannot trivially win and binary matching/winning is honest.
        ortho = _orthogonalize(_rand_unit(rng), anchor_true)
        for t in range(T):
            if t % 2 == 0:
                # meaningful, consistent: near the anchor (partial spread)
                cos_t = 0.75 + 0.12 * rng.standard_normal()
                payload = _partial_contradiction(anchor_true, ortho, cos_t, rng)
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.8 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=+1)
            else:
                # contradictory: PARTIAL separation, NOT antipodal
                cos_t = 0.0 + 0.28 * rng.standard_normal()   # ~orthogonal spread
                # rotate the orthogonal direction each step so contradictions are
                # not a single fixed vector (mutually inconsistent among themselves)
                ortho_t = _orthogonalize(_rand_unit(rng), anchor_true)
                payload = _partial_contradiction(anchor_true, ortho_t, cos_t, rng)
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.85 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=-1)

    elif regime == "overload":
        burst_end = int(T * 0.6)
        for t in range(T):
            if t < burst_end:
                is_true = (t % 2 == 0)
                base = anchor_true if is_true else anchor_true2
                payload = _normalize(base + 0.12 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.9 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]),
                                  truth=+1 if is_true else -1)
            else:
                if t % 3 == 0:
                    payload = _normalize(anchor_true + 0.1 * _rand_unit(rng))
                    events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                      0.85 + 0.05 * rng.standard_normal(),
                                      rng.choice(["x", "y", "z"]), truth=+1)

    elif regime == "concept-drift":
        drift = T // 2
        for t in range(T):
            cur_true = anchor_true if t < drift else anchor_true2
            if t % 2 == 0:
                payload = _normalize(cur_true + 0.1 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.8 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=+1)
            else:
                if t >= drift:
                    payload = _normalize(anchor_true + 0.1 * _rand_unit(rng))
                    events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                      0.8 + 0.05 * rng.standard_normal(),
                                      rng.choice(["x", "y", "z"]), truth=-1)
                else:
                    events[t] = Event(_rand_unit(rng), rng.integers(0, N_SITES_PRIMARY),
                                      0.25 + 0.05 * rng.standard_normal(),
                                      rng.choice(["x", "y", "z"]), truth=-1)
    else:
        raise ValueError(regime)

    return events


# ============================================================================
# Boundary memory register (identical for all policies)
# ============================================================================
class Register:
    def __init__(self, size, dim=PAYLOAD_DIM):
        self.size = size
        self.dim = dim
        self.slots = []

    def committed_consensus(self):
        if not self.slots:
            return np.zeros(self.dim)
        v = np.sum([s["payload"] for s in self.slots], axis=0)
        return _normalize(v)

    def commit(self, payload, truth, step):
        if len(self.slots) >= self.size:
            self.slots.pop(0)  # FIFO eviction (identical rule for all policies)
        self.slots.append({"payload": payload, "truth": truth, "birth": step})


# ============================================================================
# Policies. Each is a function of BOUNDARY-VISIBLE HISTORY ONLY.
# ============================================================================
POLICY_VISIBLE_EVENT_FIELDS = {"payload", "site", "angle", "axis"}
POLICY_FORBIDDEN_EVENT_FIELDS = {"truth", "reveal_step"}


def _cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _advance_substrate(rho, rho_ref, ev, n):
    """
    One full substrate step, IDENTICAL for every policy (fair effort). This is the
    LIVE non-unitary evolution: a dissipative modular drift toward rho_ref every
    step, plus a payload-conditioned measurement/relaxation channel when an event
    is present. Returns the new rho.
    """
    rho = dissipative_drift_step(rho, rho_ref, DT_MODULAR, GAMMA_DRIFT)
    if ev is not None:
        rho = measurement_update_channel(rho, ev.payload, n,
                                         GAMMA_RELAX, GAMMA_DEPHASE, KICK_MEAS)
    return rho


def run_policy(policy, events, rho_ref, theta, w, seed, n=N_SITES_PRIMARY,
               collect_D=False):
    """
    Simulate one policy over the stream. All four policies share: same LIVE
    substrate evolution, same trigger (D>theta), same candidate stream, same
    register size, same step budget. Only the ACTION differs.
    """
    rng = np.random.default_rng(10_000 + seed)  # for random-third bucket only
    reg = Register(REGISTER_SIZE)
    dim = 2 ** n
    rho = np.eye(dim, dtype=complex) / dim       # all policies start identically

    D_hist = []
    quarantine = []
    commit_steps = []

    for t, ev in enumerate(events):
        rho = _advance_substrate(rho, rho_ref, ev, n)
        D = relative_entropy(rho, rho_ref)
        D_hist.append(D)
        D_slope = 0.0
        if len(D_hist) >= 3:
            D_slope = D_hist[-1] - D_hist[-3]

        if quarantine:
            for q in quarantine:
                q["age"] += 1
            quarantine = [q for q in quarantine if q["age"] <= w]

        if ev is None:
            continue
        candidate = ev.payload

        if not (D > theta):
            continue

        # ---------------- BINARY: write / no-write ----------------
        if policy == "binary":
            reg.commit(candidate, ev.truth, t)
            commit_steps.append(t)

        # ---------------- TERNARY: write / witness / release ----------------
        elif policy == "ternary":
            consensus = reg.committed_consensus()
            agree = _cosine(candidate, consensus)      # boundary-visible
            spiking = abs(D_slope) > (0.6 * theta)     # "chaotic spike" proxy
            for q in quarantine:
                if _cosine(candidate, q["payload"]) > ADMISS_BAND:
                    reg.commit(q["payload"], q["truth_stamp_hidden"], t)
                    commit_steps.append(t)
                    q["age"] = w + 1
            quarantine = [q for q in quarantine if q["age"] <= w]

            if len(reg.slots) == 0:
                quarantine.append({"payload": candidate, "age": 0,
                                   "truth_stamp_hidden": ev.truth})
            elif agree >= ADMISS_BAND and not spiking:
                reg.commit(candidate, ev.truth, t)      # WRITE
                commit_steps.append(t)
            elif agree <= -ADMISS_BAND:
                pass                                    # RELEASE (discard)
            else:
                quarantine.append({"payload": candidate, "age": 0,   # WITNESS
                                   "truth_stamp_hidden": ev.truth})

        # ---------------- random-third degenerate control ----------------
        elif policy == "random-third":
            u = rng.random()
            if u < 1.0 / 3.0:
                reg.commit(candidate, ev.truth, t)
                commit_steps.append(t)
            elif u < 2.0 / 3.0:
                quarantine.append({"payload": candidate, "age": 0,
                                   "truth_stamp_hidden": ev.truth})
                if quarantine and rng.random() < 0.3:
                    q = quarantine.pop(0)
                    reg.commit(q["payload"], q["truth_stamp_hidden"], t)
                    commit_steps.append(t)
            else:
                pass  # release

        elif policy == "rate-matched-binary":
            raise RuntimeError("rate-matched-binary must be run via run_rate_matched")

    out = {
        "register": reg,
        "commit_steps": commit_steps,
        "n_commit": len(commit_steps),
        "quarantine_final": len(quarantine),
    }
    if collect_D:
        out["D_hist"] = D_hist
        out["rho_final"] = rho
    return out


def run_rate_matched(events, rho_ref, theta, w, seed, target_commit_rate,
                     n=N_SITES_PRIMARY):
    """
    Binary policy whose commit rate is throttled to match ternary's effective
    commit rate. Same LIVE substrate, same trigger, same candidate stream, same
    register, same budget. Throttle uses ONLY a seed-fixed Bernoulli gate.
    """
    rng = np.random.default_rng(20_000 + seed)
    reg = Register(REGISTER_SIZE)
    dim = 2 ** n
    rho = np.eye(dim, dtype=complex) / dim
    n_triggers = 0
    for t, ev in enumerate(events):
        rho = _advance_substrate(rho, rho_ref, ev, n)
        D = relative_entropy(rho, rho_ref)
        if ev is not None and D > theta:
            n_triggers += 1
    if n_triggers == 0:
        return {"register": reg, "commit_steps": [], "n_commit": 0,
                "quarantine_final": 0}
    gate_p = min(1.0, max(0.0, target_commit_rate))

    reg = Register(REGISTER_SIZE)
    rho = np.eye(dim, dtype=complex) / dim
    commit_steps = []
    for t, ev in enumerate(events):
        rho = _advance_substrate(rho, rho_ref, ev, n)
        D = relative_entropy(rho, rho_ref)
        if ev is None or D <= theta:
            continue
        if rng.random() < gate_p:
            reg.commit(ev.payload, ev.truth, t)
            commit_steps.append(t)
    return {"register": reg, "commit_steps": commit_steps,
            "n_commit": len(commit_steps), "quarantine_final": 0}


# ============================================================================
# Scorer (ground-truth visible ONLY here). NO metric references quarantine.
# ============================================================================
def score(regime, events, result):
    reg = result["register"]
    committed = reg.slots

    gt_meaningful = [ev for ev in events if ev is not None and ev.truth == +1]
    n_gt_true = len(gt_meaningful)

    def _committed_true_matches():
        matched = 0
        for ev in gt_meaningful:
            for s in committed:
                if s["truth"] == +1 and _cosine(ev.payload, s["payload"]) > 0.9:
                    matched += 1
                    break
        return matched

    retention = (_committed_true_matches() / n_gt_true) if n_gt_true else 0.0

    if committed:
        pollution = sum(1 for s in committed if s["truth"] == -1) / len(committed)
    else:
        pollution = 0.0

    delayed = [ev for ev in events
               if ev is not None and ev.truth == +1 and ev.reveal_step >= 0]
    if delayed:
        matched = 0
        for ev in delayed:
            for s in committed:
                if s["truth"] == +1 and s["birth"] >= ev.reveal_step \
                        and _cosine(ev.payload, s["payload"]) > 0.85:
                    matched += 1
                    break
        delayed_meaning_recovery = matched / len(delayed)
    else:
        delayed_meaning_recovery = 0.0

    T = len(events)
    tail_start = int(T * 0.6)
    tail_true = [ev for ev in events[tail_start:]
                 if ev is not None and ev.truth == +1]
    if tail_true:
        matched = 0
        for ev in tail_true:
            for s in committed:
                if s["truth"] == +1 and _cosine(ev.payload, s["payload"]) > 0.9:
                    matched += 1
                    break
        overload_recovery = matched / len(tail_true)
    else:
        overload_recovery = 0.0

    return {
        "retention": retention,
        "pollution": pollution,
        "delayed_meaning_recovery": delayed_meaning_recovery,
        "overload_recovery": overload_recovery,
        "n_commit": result["n_commit"],
    }


# ============================================================================
# Leak-scan assertion (flip hidden truth -> commit trajectory must NOT change).
# ============================================================================
def leak_scan(refs_by_regime, theta, w, seed, n=N_SITES_PRIMARY):
    reasons = []
    for regime in REGIMES:
        rho_ref = refs_by_regime[regime]
        base = make_stream(regime, seed)
        flipped = []
        for ev in base:
            if ev is None:
                flipped.append(None)
            else:
                flipped.append(Event(ev.payload.copy(), ev.site, ev.angle,
                                     ev.axis, truth=-ev.truth,
                                     reveal_step=(ev.reveal_step)))
        for policy in ["binary", "ternary", "random-third"]:
            r0 = run_policy(policy, base, rho_ref, theta, w, seed, n)
            r1 = run_policy(policy, flipped, rho_ref, theta, w, seed, n)
            if r0["commit_steps"] != r1["commit_steps"]:
                reasons.append(
                    f"{policy}/{regime}: commit trajectory changed when hidden "
                    f"truth flipped -> GROUND-TRUTH LEAK")
    return reasons


# ============================================================================
# Statistics: seed-paired bootstrap 95% CI (10k), same-sign seed count.
# ============================================================================
def paired_bootstrap_ci(diffs, n_boot=N_BOOT, seed=12345):
    d = np.asarray(diffs, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    means = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def same_sign_count(diffs):
    d = np.asarray(diffs, dtype=float)
    mean_sign = np.sign(np.mean(d))
    if mean_sign == 0:
        return 0
    return int(np.sum(np.sign(d) == mean_sign))


def advantage_diffs(metric_name, ternary_vals, other_vals):
    t = np.asarray(ternary_vals, float)
    o = np.asarray(other_vals, float)
    if metric_name in LOWER_BETTER:
        return o - t   # positive => ternary cleaner (less pollution)
    return t - o


# ============================================================================
# Full run at a given (theta, w)
# ============================================================================
def run_operating_point(theta, w, refs_by_regime, n=N_SITES_PRIMARY):
    per = {}
    for regime in REGIMES:
        rho_ref = refs_by_regime[regime]
        per[regime] = {p: [] for p in POLICIES}
        for seed in SEEDS:
            events = make_stream(regime, seed)
            n_trig = _count_triggers(events, rho_ref, theta, n)

            r_bin = run_policy("binary", events, rho_ref, theta, w, seed, n)
            r_ter = run_policy("ternary", events, rho_ref, theta, w, seed, n)
            r_rnd = run_policy("random-third", events, rho_ref, theta, w, seed, n)
            ter_rate = (r_ter["n_commit"] / n_trig) if n_trig > 0 else 0.0
            r_rmb = run_rate_matched(events, rho_ref, theta, w, seed, ter_rate, n)

            per[regime]["binary"].append(score(regime, events, r_bin))
            per[regime]["ternary"].append(score(regime, events, r_ter))
            per[regime]["random-third"].append(score(regime, events, r_rnd))
            per[regime]["rate-matched-binary"].append(score(regime, events, r_rmb))
    return per


def _count_triggers(events, rho_ref, theta, n):
    dim = 2 ** n
    rho = np.eye(dim, dtype=complex) / dim
    cnt = 0
    for ev in events:
        rho = _advance_substrate(rho, rho_ref, ev, n)
        D = relative_entropy(rho, rho_ref)
        if ev is not None and D > theta:
            cnt += 1
    return cnt


def summarize_designated(per):
    out = {}
    for regime in REGIMES:
        m = DESIGNATED_METRIC[regime]
        ter = [s[m] for s in per[regime]["ternary"]]
        stats = {"metric": m, "regime": regime}
        for comp in ["binary", "random-third", "rate-matched-binary"]:
            comp_vals = [s[m] for s in per[regime][comp]]
            diffs = advantage_diffs(m, ter, comp_vals)
            mean = float(np.mean(diffs))
            lo, hi = paired_bootstrap_ci(diffs)
            k = same_sign_count(diffs)
            passes = (mean >= H1_DELTA) and (k >= 8) and (lo > 0.0)
            stats[comp] = {
                "mean_adv": mean, "ci_lo": lo, "ci_hi": hi,
                "same_sign_k": k, "h1_pass": bool(passes),
                "ternary_mean": float(np.mean(ter)),
                "comp_mean": float(np.mean(comp_vals)),
            }
        for sec in ["retention", "pollution"]:
            ter_s = [s[sec] for s in per[regime]["ternary"]]
            bin_s = [s[sec] for s in per[regime]["binary"]]
            diffs = advantage_diffs(sec, ter_s, bin_s)
            mean = float(np.mean(diffs))
            lo, hi = paired_bootstrap_ci(diffs)
            k = same_sign_count(diffs)
            loses = (mean <= -H1_DELTA) and (k >= 8) and (hi < 0.0)
            stats[f"secondary_{sec}_vs_binary"] = {
                "mean_adv": mean, "ci_lo": lo, "ci_hi": hi,
                "same_sign_k": k, "ternary_loses_by_bar": bool(loses),
            }
        out[regime] = stats
    return out


# ============================================================================
# Epsilon-sensitivity (brittleness flag, NOT optimized) at primary point
# ============================================================================
def epsilon_sensitivity(refs_by_regime, n=N_SITES_PRIMARY):
    global ADMISS_BAND
    out = {}
    saved = ADMISS_BAND
    variants = {
        "theta_lo": (THETA_PRIMARY * (1 - EPS_FRAC), saved),
        "theta_hi": (THETA_PRIMARY * (1 + EPS_FRAC), saved),
        "cut_lo":   (THETA_PRIMARY, saved - EPS_FRAC),
        "cut_hi":   (THETA_PRIMARY, saved + EPS_FRAC),
        "base":     (THETA_PRIMARY, saved),
    }
    for regime in REGIMES:
        m = DESIGNATED_METRIC[regime]
        means = {}
        for name, (th, cut) in variants.items():
            ADMISS_BAND = cut
            rho_ref = refs_by_regime[regime]
            ter_vals, bin_vals = [], []
            for seed in SEEDS:
                events = make_stream(regime, seed)
                r_ter = run_policy("ternary", events, rho_ref, th, W_PRIMARY, seed, n)
                r_bin = run_policy("binary", events, rho_ref, th, W_PRIMARY, seed, n)
                ter_vals.append(score(regime, events, r_ter)[m])
                bin_vals.append(score(regime, events, r_bin)[m])
            diffs = advantage_diffs(m, ter_vals, bin_vals)
            means[name] = float(np.mean(diffs))
        spread = float(max(means.values()) - min(means.values()))
        out[regime] = {"variant_means": means, "spread": spread}
    ADMISS_BAND = saved
    return out


# ============================================================================
# Size smoke check (n in {2,4}) -- validity/shape only, not the decision
# ============================================================================
def run_size_smoke():
    smoke = {}
    for n in [2, 4]:
        beta = BETA_BY_REGIME["contradiction"]
        rho_ref = gibbs_reference(n, beta)
        events = make_stream("contradiction", 0)
        r_bin = run_policy("binary", events, rho_ref, THETA_PRIMARY, W_PRIMARY, 0, n)
        r_ter = run_policy("ternary", events, rho_ref, THETA_PRIMARY, W_PRIMARY, 0, n)
        smoke[f"n={n}"] = {
            "dim": 2 ** n,
            "binary_commits": r_bin["n_commit"],
            "ternary_commits": r_ter["n_commit"],
            "trace_ref": float(np.trace(rho_ref).real),
            "min_eig_ref": float(np.linalg.eigvalsh(rho_ref).min()),
        }
    return smoke


# ============================================================================
# SUBSTRATE-LIVENESS AUDIT (v2 FIX #1 verification). Proves the substrate is NOT
# inert: rho leaves I/dim and D(rho||rho_ref) takes many distinct values.
# ============================================================================
def substrate_liveness_audit(refs_by_regime, n=N_SITES_PRIMARY):
    audit = {}
    dim = 2 ** n
    I_over_d = np.eye(dim, dtype=complex) / dim
    worst_min_distinct = None
    for regime in REGIMES:
        rho_ref = refs_by_regime[regime]
        per_seed = []
        for seed in SEEDS[:3]:   # a few seeds are enough to characterize liveness
            events = make_stream(regime, seed)
            r = run_policy("binary", events, rho_ref, THETA_PRIMARY, W_PRIMARY,
                           seed, n, collect_D=True)
            D_hist = r["D_hist"]
            rho_final = r["rho_final"]
            dist_from_mixed = float(np.linalg.norm(rho_final - I_over_d))
            # count distinct D values (rounded) to prove it is NOT constant
            n_distinct = int(len(set(np.round(D_hist, 4))))
            per_seed.append({
                "seed": seed,
                "D_min": float(np.min(D_hist)),
                "D_max": float(np.max(D_hist)),
                "D_range": float(np.max(D_hist) - np.min(D_hist)),
                "D_n_distinct": n_distinct,
                "final_dist_from_I_over_d": dist_from_mixed,
            })
            mn = n_distinct
            worst_min_distinct = mn if worst_min_distinct is None \
                else min(worst_min_distinct, mn)
        audit[regime] = per_seed
    # liveness passes if D is genuinely non-constant everywhere and rho left I/dim
    all_dist = [s["final_dist_from_I_over_d"]
                for rg in audit.values() for s in rg]
    all_range = [s["D_range"] for rg in audit.values() for s in rg]
    live = (min(all_dist) > 1e-3) and (worst_min_distinct >= 5) and (min(all_range) > 1e-3)
    return {
        "per_regime": audit,
        "min_final_dist_from_I_over_d": float(min(all_dist)),
        "min_D_n_distinct": int(worst_min_distinct),
        "min_D_range": float(min(all_range)),
        "substrate_is_live": bool(live),
        "note": ("v1 was inert: rho pinned at I/dim, D constant ~1.97. v2 uses a "
                 "non-unitary CPTP substrate; these numbers must be >> 0 / >> 1 "
                 "distinct value or the fix failed."),
    }


# ============================================================================
# CONTRADICTION-SEPARATION AUDIT (v2 FIX #2 verification). Proves contradictory
# payloads are NOT antipodal -- they have partial cosine separation and OVERLAP
# with the meaningful population, so cosine-sign release cannot trivially win.
# ============================================================================
def contradiction_separation_audit():
    cos_true, cos_false = [], []
    for seed in SEEDS:
        events = make_stream("contradiction", seed)
        # reconstruct the consensus anchor the way the stream built it
        rng = np.random.default_rng(seed * 1000 + REGIMES.index("contradiction"))
        anchor = _rand_unit(rng)  # first draw is anchor_true
        for ev in events:
            if ev is None:
                continue
            c = _cosine(ev.payload, anchor)
            (cos_true if ev.truth == +1 else cos_false).append(c)
    cos_true = np.asarray(cos_true)
    cos_false = np.asarray(cos_false)
    # fraction of contradictory payloads that a naive cosine-sign rule would
    # (correctly) discard as "negative": if this is ~1.0 the stream is tautological
    frac_false_negative_cos = float(np.mean(cos_false < 0.0)) if len(cos_false) else 0.0
    return {
        "true_cos_mean": float(cos_true.mean()) if len(cos_true) else 0.0,
        "true_cos_min": float(cos_true.min()) if len(cos_true) else 0.0,
        "false_cos_mean": float(cos_false.mean()) if len(cos_false) else 0.0,
        "false_cos_min": float(cos_false.min()) if len(cos_false) else 0.0,
        "false_cos_max": float(cos_false.max()) if len(cos_false) else 0.0,
        "frac_contradictions_with_negative_cosine": frac_false_negative_cos,
        "non_tautological": bool(cos_false.min() > -0.95 and
                                 frac_false_negative_cos < 0.9),
        "note": ("v1 made contradictions antipodal (cosine ~ -1, frac_negative ~1) "
                 "so cosine-sign release trivially won. v2: contradictions have "
                 "partial separation; frac_negative should be well below 0.9 and "
                 "min cosine well above -1, and the +1/-1 cosine ranges overlap."),
    }


# ============================================================================
# Numerology guard: assert NO golden / phi constant is present.
# ============================================================================
def numerology_guard():
    phi = (1 + 5 ** 0.5) / 2  # 1.618...
    inv_phi = phi - 1         # 0.618...
    frozen = [J_COUPLING, DELTA_ANISO, H_FIELD, DT_MODULAR, ADMISS_BAND,
              THETA_PRIMARY, float(W_PRIMARY),
              GAMMA_RELAX, GAMMA_DEPHASE, GAMMA_DRIFT, KICK_MEAS] + THETA_SWEEP + \
             [float(x) for x in W_SWEEP] + list(BETA_BY_REGIME.values())
    bad = [c for c in frozen if abs(c - phi) < 1e-6 or abs(c - inv_phi) < 1e-6]
    assert not bad, f"NUMEROLOGY VIOLATION: golden constant present: {bad}"
    return {"phi": phi, "checked_constants": frozen, "violation": False}


# ============================================================================
# Decision logic (prereg section 7), applied IN CODE.
# ============================================================================
def decide(designated):
    winning_pairs = []
    for regime, st in designated.items():
        cleared_all = (st["binary"]["h1_pass"]
                       and st["random-third"]["h1_pass"]
                       and st["rate-matched-binary"]["h1_pass"])
        if cleared_all:
            winning_pairs.append((regime, st["metric"]))

    symmetric_losses = []
    for regime, st in designated.items():
        for sec in ["retention", "pollution"]:
            if st[f"secondary_{sec}_vs_binary"]["ternary_loses_by_bar"]:
                symmetric_losses.append((regime, sec))

    if winning_pairs and not symmetric_losses:
        classification = "PASS-TERNARY"
    elif winning_pairs and symmetric_losses:
        classification = "KILL-NULL (win offset by symmetric loss; not a pass)"
    elif symmetric_losses:
        classification = "KILL-NET-NEGATIVE (ternary strictly worse on retention/pollution)"
    else:
        classification = "KILL-NULL (binary matches/wins -- AU v1-v3 prior confirmed)"

    return classification, {
        "winning_pairs": winning_pairs,
        "symmetric_losses": symmetric_losses,
    }


# ============================================================================
# Main
# ============================================================================
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "modular_www_v2_outputs")
    os.makedirs(out_dir, exist_ok=True)

    numer = numerology_guard()

    refs = {rg: gibbs_reference(N_SITES_PRIMARY, BETA_BY_REGIME[rg]) for rg in REGIMES}

    # ---- v2 fix verifications (must hold or the rebuild failed) ----
    liveness = substrate_liveness_audit(refs)
    sep_audit = contradiction_separation_audit()
    assert liveness["substrate_is_live"], (
        "SUBSTRATE STILL INERT -- v2 fix #1 failed: " + json.dumps(liveness))
    assert sep_audit["non_tautological"], (
        "CONTRADICTION STREAM STILL TAUTOLOGICAL -- v2 fix #2 failed: "
        + json.dumps(sep_audit))

    # ---- leak-scan (must be empty; else INVALID) ----
    leak_reasons = []
    for seed in SEEDS:
        leak_reasons.extend(leak_scan(refs, THETA_PRIMARY, W_PRIMARY, seed))
    invalid = len(leak_reasons) > 0

    # ---- primary operating point ----
    per_primary = run_operating_point(THETA_PRIMARY, W_PRIMARY, refs)
    designated = summarize_designated(per_primary)

    # ---- sweeps (robustness context only) ----
    sweeps = {}
    for theta in THETA_SWEEP:
        for w in W_SWEEP:
            if theta == THETA_PRIMARY and w == W_PRIMARY:
                continue
            per = run_operating_point(theta, w, refs)
            dsg = summarize_designated(per)
            sweeps[f"theta={theta},w={w}"] = {
                rg: {
                    "metric": dsg[rg]["metric"],
                    "mean_adv_vs_binary": dsg[rg]["binary"]["mean_adv"],
                    "same_sign_k": dsg[rg]["binary"]["same_sign_k"],
                    "ci_lo": dsg[rg]["binary"]["ci_lo"],
                    "ci_hi": dsg[rg]["binary"]["ci_hi"],
                } for rg in REGIMES
            }

    eps = epsilon_sensitivity(refs)
    smoke = run_size_smoke()

    if invalid:
        classification = "INVALID (ground-truth leak detected)"
        decision_detail = {"leak_reasons": leak_reasons}
    else:
        classification, decision_detail = decide(designated)

    summary = {
        "test_id": "modular_www_v2",
        "lane": "engineering/verified-computation telemetry only",
        "fix_note": ("v2 rebuild: (1) LIVE non-unitary CPTP substrate (was inert "
                     "unitary-only in v1, D pinned ~1.97); (2) non-tautological "
                     "contradiction stream with partial (non-antipodal) cosine "
                     "separation (was perfectly antipodal in v1)."),
        "no_upgrade": ("Software/toy success is NEVER physics evidence (master "
                       "hard rule 7): no outcome proves GHP, observer-boundary "
                       "selection, phi selection, or a write-law; even a clean "
                       "PASS is a single-toy engineering result and 'ternary "
                       "witness is a universal memory law' is the forbidden "
                       "upgrade that voids interpretation."),
        "system": {
            "n_sites_primary": N_SITES_PRIMARY, "hilbert_dim": 2 ** N_SITES_PRIMARY,
            "T_steps": T_STEPS, "register_size": REGISTER_SIZE,
            "dt_modular": DT_MODULAR, "admiss_band": ADMISS_BAND,
            "J": J_COUPLING, "Delta_aniso": DELTA_ANISO, "h_field": H_FIELD,
            "gamma_relax": GAMMA_RELAX, "gamma_dephase": GAMMA_DEPHASE,
            "gamma_drift": GAMMA_DRIFT, "kick_meas": KICK_MEAS,
            "seeds": SEEDS,
        },
        "primary_operating_point": {"theta": THETA_PRIMARY, "w": W_PRIMARY},
        "numerology_guard": {"phi": numer["phi"], "violation": numer["violation"]},
        "substrate_liveness": liveness,
        "contradiction_separation_audit": sep_audit,
        "leak_scan": {"invalid": invalid, "reasons": leak_reasons},
        "designated_primary": designated,
        "decision": {"classification": classification, "detail": decision_detail},
        "sweeps_robustness_only": sweeps,
        "epsilon_sensitivity_brittleness": eps,
        "size_smoke_check": smoke,
    }

    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=lambda o: float(o))

    write_report(out_dir, summary)

    headline = build_headline(summary)
    print("CLASSIFICATION: " + classification)
    print("SUBSTRATE LIVE: " + str(liveness["substrate_is_live"])
          + f" (min final ||rho-I/d||={liveness['min_final_dist_from_I_over_d']:.4f}, "
          f"min distinct D={liveness['min_D_n_distinct']}, "
          f"min D-range={liveness['min_D_range']:.4f})")
    print("CONTRADICTION NON-TAUTOLOGICAL: " + str(sep_audit["non_tautological"])
          + f" (false-cos mean={sep_audit['false_cos_mean']:+.3f}, "
          f"min={sep_audit['false_cos_min']:+.3f}, "
          f"frac-neg={sep_audit['frac_contradictions_with_negative_cosine']:.2f})")
    print("HEADLINE: " + headline)
    return summary, classification, headline


def build_headline(summary):
    dsg = summary["designated_primary"]
    parts = []
    for rg in REGIMES:
        st = dsg[rg]
        b = st["binary"]
        parts.append(
            f"{rg}[{st['metric']}]: ternary-minus-binary={b['mean_adv']:+.3f} "
            f"(k={b['same_sign_k']}/10, CI[{b['ci_lo']:+.3f},{b['ci_hi']:+.3f}], "
            f"H1={'Y' if b['h1_pass'] else 'n'})")
    return " | ".join(parts)


def write_report(out_dir, summary):
    dsg = summary["designated_primary"]
    lines = []
    lines.append("# modular_www_v2 — Result Report (write/witness/release, LIVE substrate)\n")
    lines.append(f"- **test_id:** modular_www_v2")
    lines.append(f"- **Lane:** {summary['lane']}")
    lines.append(f"- **Fix note:** {summary['fix_note']}")
    lines.append(f"- **Primary operating point:** theta={summary['primary_operating_point']['theta']}, "
                 f"w={summary['primary_operating_point']['w']}")
    lines.append(f"- **System:** n={summary['system']['n_sites_primary']} sites "
                 f"(dim {summary['system']['hilbert_dim']}), T={summary['system']['T_steps']} steps, "
                 f"register={summary['system']['register_size']}, 10 seeds.")
    lines.append(f"- **Numerology guard:** phi={summary['numerology_guard']['phi']:.6f}, "
                 f"violation={summary['numerology_guard']['violation']} (phi-FREE channel).")
    lines.append(f"- **Leak-scan:** invalid={summary['leak_scan']['invalid']}.")
    lines.append("")

    lv = summary["substrate_liveness"]
    lines.append("## v2 FIX #1 — substrate liveness (was INERT in v1)\n")
    lines.append(f"- substrate_is_live: **{lv['substrate_is_live']}**")
    lines.append(f"- min final ||rho_final - I/dim||_F = {lv['min_final_dist_from_I_over_d']:.4f} "
                 f"(v1 was ~0; must be >> 0)")
    lines.append(f"- min distinct D values over a run = {lv['min_D_n_distinct']} "
                 f"(v1 was 1 constant ~1.97; must be many)")
    lines.append(f"- min D-range (max-min over a run) = {lv['min_D_range']:.4f}")
    lines.append("")

    sa = summary["contradiction_separation_audit"]
    lines.append("## v2 FIX #2 — contradiction stream is non-tautological (was antipodal in v1)\n")
    lines.append(f"- non_tautological: **{sa['non_tautological']}**")
    lines.append(f"- meaningful(+1) cosine to anchor: mean {sa['true_cos_mean']:+.3f}, "
                 f"min {sa['true_cos_min']:+.3f}")
    lines.append(f"- contradictory(-1) cosine to anchor: mean {sa['false_cos_mean']:+.3f}, "
                 f"range [{sa['false_cos_min']:+.3f}, {sa['false_cos_max']:+.3f}] "
                 f"(v1 was ~ -1.0 antipodal)")
    lines.append(f"- fraction of contradictions a naive cosine-sign rule would flag "
                 f"negative = {sa['frac_contradictions_with_negative_cosine']:.2f} "
                 f"(v1 was ~1.0; low here => release cannot trivially win)")
    lines.append("")

    lines.append(f"## CLASSIFICATION: {summary['decision']['classification']}\n")
    lines.append("> " + summary["no_upgrade"] + "\n")

    lines.append("## Primary: designated metric per regime, ternary vs binary "
                 "and degenerate controls (theta=0.10, w=4)\n")
    lines.append("| regime | metric | vs | mean adv | k/10 | 95% CI | H1 pass |")
    lines.append("|---|---|---|---|---|---|---|")
    for rg in REGIMES:
        st = dsg[rg]
        for comp in ["binary", "random-third", "rate-matched-binary"]:
            c = st[comp]
            lines.append(f"| {rg} | {st['metric']} | {comp} | {c['mean_adv']:+.4f} | "
                         f"{c['same_sign_k']}/10 | [{c['ci_lo']:+.4f}, {c['ci_hi']:+.4f}] | "
                         f"{'YES' if c['h1_pass'] else 'no'} |")
    lines.append("")

    lines.append("## Symmetric-loss guard (secondary retention & pollution vs binary)\n")
    lines.append("| regime | secondary metric | mean adv (ternary better>0) | k/10 | ternary loses by H1 bar |")
    lines.append("|---|---|---|---|---|")
    for rg in REGIMES:
        st = dsg[rg]
        for sec in ["retention", "pollution"]:
            s = st[f"secondary_{sec}_vs_binary"]
            lines.append(f"| {rg} | {sec} | {s['mean_adv']:+.4f} | {s['same_sign_k']}/10 | "
                         f"{'YES' if s['ternary_loses_by_bar'] else 'no'} |")
    lines.append("")

    det = summary["decision"]["detail"]
    lines.append("## Decision detail\n")
    lines.append(f"- Winning metric x regime pairs (cleared H1 over binary AND both "
                 f"degenerate controls): {det.get('winning_pairs', [])}")
    lines.append(f"- Symmetric losses (ternary loses by H1 bar on retention/pollution): "
                 f"{det.get('symmetric_losses', [])}")
    lines.append("")

    lines.append("## Robustness sweep (theta x w) — CANNOT move the call\n")
    lines.append("Designated-metric ternary-minus-binary mean advantage per regime:\n")
    lines.append("| op point | " + " | ".join(REGIMES) + " |")
    lines.append("|---|" + "|".join(["---"] * len(REGIMES)) + "|")
    for pt, d in summary["sweeps_robustness_only"].items():
        row = [pt] + [f"{d[rg]['mean_adv_vs_binary']:+.3f} (k{d[rg]['same_sign_k']})" for rg in REGIMES]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Epsilon-sensitivity (brittleness flag, NOT optimized)\n")
    lines.append("| regime | designated-metric adv spread across ±0.15 theta/cut |")
    lines.append("|---|---|")
    for rg in REGIMES:
        lines.append(f"| {rg} | {summary['epsilon_sensitivity_brittleness'][rg]['spread']:.4f} |")
    lines.append("")

    lines.append("## Size smoke check (n in {2,4}) — validity only, not the decision\n")
    lines.append("| n | dim | binary commits | ternary commits | tr(rho_ref) | min eig |")
    lines.append("|---|---|---|---|---|---|")
    for k, v in summary["size_smoke_check"].items():
        n = k.split("=")[1]
        lines.append(f"| {n} | {v['dim']} | {v['binary_commits']} | {v['ternary_commits']} | "
                     f"{v['trace_ref']:.4f} | {v['min_eig_ref']:.2e} |")
    lines.append("")
    lines.append("---")
    lines.append("Preregistration embedded in the module docstring (LOCKED before run). "
                 "Ledger slots to be written AFTER the run, carrying this classification "
                 "verbatim with the forbidden-upgrade sentence attached. "
                 "NO-UPGRADE: software/toy success is never physics evidence; a PASS is a "
                 "single-toy engineering result, not GHP / phi / write-law evidence.")

    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
