#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modular_www — Modular-Flow Write/Witness/Release Stress Test (ternary vs binary)
================================================================================

LANE: Engineering / verified-computation telemetry ONLY. Deterministic, offline,
Python 3.9 + numpy/scipy only, fixed seeds 0-9.

------------------------------------------------------------------------------
NO-UPGRADE SENTENCE (verbatim, load-bearing):
Software/toy success is NEVER physics evidence (master hard rule 7): no outcome
of this script proves GHP, observer-boundary selection, phi selection, or a
write-law, and even a clean PASS is a single-toy engineering result -- claiming
"ternary witness is a universal memory law" is the forbidden upgrade and voids
interpretation.
------------------------------------------------------------------------------

PREREGISTRATION (LOCKED before run; embedded verbatim-in-substance):

test_id: modular_www

H1 (ternary advantage): In a phi-free modular-flow memory channel (2-4 qubit
sites, fixed XXZ Gibbs reference rho_ref, modular flow sigma_t = rho_ref^{it}(.)
rho_ref^{-it}, boundary updates fired when D(rho_t||rho_ref) > theta), a TERNARY
policy {WRITE / WITNESS-quarantine / RELEASE} beats a BINARY policy {WRITE /
NO-WRITE} on at least one predeclared metric x regime pair. "Beats" at the LOCKED
primary operating point (theta=0.10, quarantine window w=4) means:
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

Closest prior precedent: T-096 CAS-009 (write/witness/release ternary PASSED,
harmful confusion 0.0020) -- but that was NOT a head-to-head vs binary, which is
exactly the gap modular_www closes. AU-001 / ghp-research-discipline carry the
AU v1-v3 null-favoring prior.

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

# Suppress the KNOWN-BENIGN matmul RuntimeWarnings emitted by the macOS
# Accelerate/BLAS backend when multiplying tensor-embedded Pauli operators that
# contain exact-zero blocks (dim-16, n=4 smoke check). These are spurious
# denormal-flush warnings from the BLAS layer, NOT numerical errors: verified
# that trace(rho_ref)=1.0000000000, hermiticity error 0, and all relative-
# entropy values remain finite for every n in {2,3,4}. Suppressing them keeps
# stdout clean; no computed value is affected.
warnings.filterwarnings("ignore", message=".*encountered in matmul.*",
                        category=RuntimeWarning)

# ----------------------------------------------------------------------------
# NUMEROLOGY GUARD (declared): no golden / Fibonacci / phi constant anywhere.
# The only structural constants below are XXZ coupling, transverse field, and
# beta -- none of them is (1+sqrt5)/2 or a Fibonacci ratio. A guard at the end
# of the file asserts phi does not appear in any frozen constant.
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
    Hermitian PD reference. This is exactly the modular unitary generated by the
    modular Hamiltonian K = -log rho_ref (up to sign convention): the ONLY use
    of modular structure. phi-FREE.
    """
    ev, U = np.linalg.eigh(0.5 * (rho_ref + rho_ref.conj().T))
    ev = np.clip(ev, 1e-15, None)
    phase = np.exp(1j * dt * np.log(ev))      # lambda^{i*dt}
    return (U * phase) @ U.conj().T


def modular_flow_step(rho, rho_ref, dt):
    """sigma_dt(rho) = rho_ref^{i*dt} rho rho_ref^{-i*dt} (modular flow)."""
    Umod = modular_unitary(rho_ref, dt)
    out = Umod @ rho @ Umod.conj().T
    out = 0.5 * (out + out.conj().T)
    tr = np.trace(out).real
    if tr != 0:
        out = out / tr
    return out


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


def local_kick(rho, site, n, angle, axis):
    """Apply a unitary local perturbation (drive event) to rho."""
    I, X, Y, Z = pauli()
    P = {"x": X, "y": Y, "z": Z}[axis]
    U1 = expm(-1j * angle * P)
    U = op_at_from_single(U1, site % n, n)   # clamp to system size (smoke n=2)
    out = U @ rho @ U.conj().T
    out = 0.5 * (out + out.conj().T)
    return out / np.trace(out).real


def op_at_from_single(U1, site, n):
    I = np.eye(2, dtype=complex)
    mats = [I] * n
    mats[site] = U1
    out = mats[0]
    for k in range(1, n):
        out = np.kron(out, mats[k])
    return out


# ============================================================================
# Stream generator (ground truth stamped here; visible ONLY to the scorer)
# ============================================================================
class Event:
    __slots__ = ("payload", "site", "angle", "axis", "truth", "reveal_step")

    def __init__(self, payload, site, angle, axis, truth, reveal_step=-1):
        self.payload = payload          # unit vector in R^REGISTER-embedding space
        self.site = site
        self.angle = angle
        self.axis = axis
        self.truth = truth              # +1 meaningful, -1 spurious/contradictory (GT)
        self.reveal_step = reveal_step  # for delayed-meaning: becomes meaningful after this step


PAYLOAD_DIM = 8  # abstract payload embedding dimension (independent of n)


def _rand_unit(rng, dim=PAYLOAD_DIM):
    v = rng.standard_normal(dim)
    return v / (np.linalg.norm(v) + 1e-12)


def make_stream(regime, seed, T=T_STEPS):
    """Return list of length T; each entry is Event or None (no candidate)."""
    rng = np.random.default_rng(seed * 1000 + REGIMES.index(regime))
    events = [None] * T
    # a small set of "meaningful direction" anchors and a "spurious" anchor
    anchor_true = _rand_unit(rng)
    anchor_true2 = _rand_unit(rng)

    if regime == "delayed-meaning":
        # early sub-threshold meaningful pattern, revealed (kick grows) after delay
        reveal = T // 2
        for t in range(T):
            if t % 3 == 0:
                # meaningful payload, but weak kick early -> sub-threshold until reveal
                strong = t >= reveal
                angle = (0.9 if strong else 0.18) + 0.03 * rng.standard_normal()
                payload = _normalize(anchor_true + 0.15 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  angle, rng.choice(["x", "y", "z"]),
                                  truth=+1, reveal_step=reveal)
            elif t % 3 == 1:
                # noise / spurious, always weak
                events[t] = Event(_rand_unit(rng), rng.integers(0, N_SITES_PRIMARY),
                                  0.25 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=-1)

    elif regime == "contradiction":
        # bursts of mutually inconsistent candidates vs committed consensus
        for t in range(T):
            if t % 2 == 0:
                # meaningful consistent
                payload = _normalize(anchor_true + 0.1 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.8 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=+1)
            else:
                # contradictory: opposite direction, still crosses threshold
                payload = _normalize(-anchor_true + 0.1 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.85 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=-1)

    elif regime == "overload":
        # trigger rate far exceeds capacity in a burst, then a calmer tail
        burst_end = int(T * 0.6)
        for t in range(T):
            if t < burst_end:
                # dense strong candidates, mixed truth
                is_true = (t % 2 == 0)
                base = anchor_true if is_true else anchor_true2
                payload = _normalize(base + 0.12 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.9 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]),
                                  truth=+1 if is_true else -1)
            else:
                # tail: sparse meaningful candidates (recovery region)
                if t % 3 == 0:
                    payload = _normalize(anchor_true + 0.1 * _rand_unit(rng))
                    events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                      0.85 + 0.05 * rng.standard_normal(),
                                      rng.choice(["x", "y", "z"]), truth=+1)

    elif regime == "concept-drift":
        # meaning shifts midway: anchor_true meaningful early, anchor_true2 late;
        # old anchor becomes spurious after drift (stale-memory eviction test)
        drift = T // 2
        for t in range(T):
            if t < drift:
                cur_true = anchor_true
            else:
                cur_true = anchor_true2
            if t % 2 == 0:
                payload = _normalize(cur_true + 0.1 * _rand_unit(rng))
                events[t] = Event(payload, rng.integers(0, N_SITES_PRIMARY),
                                  0.8 + 0.05 * rng.standard_normal(),
                                  rng.choice(["x", "y", "z"]), truth=+1)
            else:
                # post-drift: the OLD anchor is now spurious
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


def _normalize(v):
    return v / (np.linalg.norm(v) + 1e-12)


# ============================================================================
# Boundary memory register (identical for all policies)
# ============================================================================
class Register:
    def __init__(self, size, dim=PAYLOAD_DIM):
        self.size = size
        self.dim = dim
        self.slots = []   # list of dict(payload, truth, birth_step)

    def committed_consensus(self):
        if not self.slots:
            return np.zeros(self.dim)
        v = np.sum([s["payload"] for s in self.slots], axis=0)
        return _normalize(v)

    def commit(self, payload, truth, step):
        if len(self.slots) >= self.size:
            # FIFO eviction (identical rule for all policies)
            self.slots.pop(0)
        self.slots.append({"payload": payload, "truth": truth, "birth": step})

    def committed_true_dirs(self):
        return [s for s in self.slots]


# ============================================================================
# Policies. Each is a function of BOUNDARY-VISIBLE HISTORY ONLY.
# Boundary-visible inputs (leak-scan enforced): current D, D-slope over last 2
# steps, cosine agreement with committed consensus, quarantine age. NEVER the
# truth stamp, regime label, or future stream.
# ============================================================================

# ---- leak-scan: the ONLY fields a policy decision may touch on an Event ----
POLICY_VISIBLE_EVENT_FIELDS = {"payload", "site", "angle", "axis"}
POLICY_FORBIDDEN_EVENT_FIELDS = {"truth", "reveal_step"}


def _cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def run_policy(policy, events, rho_ref, theta, w, seed, n=N_SITES_PRIMARY):
    """
    Simulate one policy over the stream. Returns register + telemetry.
    All four policies share: same trigger (D>theta), same candidate stream,
    same register size, same step budget. Only the ACTION differs.
    """
    rng = np.random.default_rng(10_000 + seed)  # for random-third bucket only
    reg = Register(REGISTER_SIZE)
    dim = 2 ** n
    # neutral start state (maximally mixed) so all policies start identically
    rho = np.eye(dim, dtype=complex) / dim

    D_hist = []
    committed_events = []   # (payload, truth, step) actually committed
    quarantine = []         # ternary WITNESS slots: dict(payload, age, event)
    commit_steps = []       # steps at which a commit happened (for rate telemetry)

    # ternary effective commit rate is measured to configure rate-matched-binary.
    for t, ev in enumerate(events):
        # advance the running state by modular flow every step
        rho = modular_flow_step(rho, rho_ref, DT_MODULAR)
        # apply the drive event (kick) if present
        if ev is not None:
            rho = local_kick(rho, ev.site, n, ev.angle, ev.axis)
        D = relative_entropy(rho, rho_ref)
        D_hist.append(D)
        D_slope = 0.0
        if len(D_hist) >= 3:
            D_slope = D_hist[-1] - D_hist[-3]  # slope over last 2 steps

        # age quarantine, evict expired (ternary + random-third only)
        if quarantine:
            for q in quarantine:
                q["age"] += 1
            quarantine = [q for q in quarantine if q["age"] <= w]

        if ev is None:
            continue
        candidate = ev.payload  # boundary-visible payload direction

        triggered = (D > theta)

        if not triggered:
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
            # re-confirm any quarantined item this candidate agrees with
            reconfirmed = False
            for q in quarantine:
                if _cosine(candidate, q["payload"]) > ADMISS_BAND:
                    # independent re-confirmation within window -> commit
                    reg.commit(q["payload"], q["truth_stamp_hidden"], t)
                    commit_steps.append(t)
                    q["age"] = w + 1  # mark for eviction
                    reconfirmed = True
            quarantine = [q for q in quarantine if q["age"] <= w]

            if len(reg.slots) == 0:
                # empty consensus: no basis to judge -> WITNESS (quarantine)
                quarantine.append({"payload": candidate, "age": 0,
                                   "truth_stamp_hidden": ev.truth})
            elif agree >= ADMISS_BAND and not spiking:
                reg.commit(candidate, ev.truth, t)      # WRITE
                commit_steps.append(t)
            elif agree <= -ADMISS_BAND:
                pass                                    # RELEASE (discard)
            else:
                # ambiguous band -> WITNESS (quarantine, decays over w)
                quarantine.append({"payload": candidate, "age": 0,
                                   "truth_stamp_hidden": ev.truth})

        # ---------------- random-third degenerate control ----------------
        elif policy == "random-third":
            # same trigger; third bucket assigned AT RANDOM at the same design
            # rate the witness fires (1/3 write, 1/3 witness, 1/3 release),
            # WITHOUT the admissibility content.
            u = rng.random()
            if u < 1.0 / 3.0:
                reg.commit(candidate, ev.truth, t)
                commit_steps.append(t)
            elif u < 2.0 / 3.0:
                quarantine.append({"payload": candidate, "age": 0,
                                   "truth_stamp_hidden": ev.truth})
                # random re-confirmation: commit an aged quarantine item at random
                if quarantine and rng.random() < 0.3:
                    q = quarantine.pop(0)
                    reg.commit(q["payload"], q["truth_stamp_hidden"], t)
                    commit_steps.append(t)
            else:
                pass  # release

        # rate-matched-binary handled in a second pass (needs ternary rate)
        elif policy == "rate-matched-binary":
            raise RuntimeError("rate-matched-binary must be run via run_rate_matched")

    return {
        "register": reg,
        "commit_steps": commit_steps,
        "n_commit": len(commit_steps),
        "quarantine_final": len(quarantine),
        "D_hist": D_hist,
    }


def run_rate_matched(events, rho_ref, theta, w, seed, target_commit_rate,
                     n=N_SITES_PRIMARY):
    """
    Binary policy whose commit rate is throttled to match ternary's effective
    commit rate. Controls for 'ternary just writes less'. Same trigger, same
    candidate stream, same register, same budget. Throttle decision uses ONLY a
    seed-fixed Bernoulli gate at the matched rate (boundary-agnostic, no GT).
    """
    rng = np.random.default_rng(20_000 + seed)
    reg = Register(REGISTER_SIZE)
    dim = 2 ** n
    rho = np.eye(dim, dtype=complex) / dim
    D_hist = []
    commit_steps = []
    n_triggers = 0
    # first count triggers to convert a per-commit target into a per-trigger gate
    for t, ev in enumerate(events):
        rho = modular_flow_step(rho, rho_ref, DT_MODULAR)
        if ev is not None:
            rho = local_kick(rho, ev.site, n, ev.angle, ev.axis)
        D = relative_entropy(rho, rho_ref)
        D_hist.append(D)
        if ev is not None and D > theta:
            n_triggers += 1
    if n_triggers == 0:
        return {"register": reg, "commit_steps": [], "n_commit": 0,
                "quarantine_final": 0, "D_hist": D_hist}
    gate_p = min(1.0, max(0.0, target_commit_rate))  # commits-per-trigger target

    # second pass with the throttle gate
    reg = Register(REGISTER_SIZE)
    rho = np.eye(dim, dtype=complex) / dim
    D_hist = []
    for t, ev in enumerate(events):
        rho = modular_flow_step(rho, rho_ref, DT_MODULAR)
        if ev is not None:
            rho = local_kick(rho, ev.site, n, ev.angle, ev.axis)
        D = relative_entropy(rho, rho_ref)
        D_hist.append(D)
        if ev is None or D <= theta:
            continue
        if rng.random() < gate_p:
            reg.commit(ev.payload, ev.truth, t)
            commit_steps.append(t)
    return {"register": reg, "commit_steps": commit_steps,
            "n_commit": len(commit_steps), "quarantine_final": 0,
            "D_hist": D_hist}


# ============================================================================
# Scorer (ground-truth visible ONLY here). All metrics computable identically
# for a quarantine-free policy: they read only committed-slot truth stamps and
# the stream's ground-truth stamps. NO metric references WITNESS/quarantine.
# ============================================================================
def score(regime, events, result):
    reg = result["register"]
    committed = reg.slots  # dict(payload, truth, birth)

    # ground-truth counts from the stream
    gt_meaningful = [ev for ev in events if ev is not None and ev.truth == +1]
    n_gt_true = len(gt_meaningful)

    # retention: fraction of GT-meaningful payloads committed AND still present
    # matched by cosine to a committed slot with truth==+1
    def _committed_true_matches():
        matched = 0
        for ev in gt_meaningful:
            for s in committed:
                if s["truth"] == +1 and _cosine(ev.payload, s["payload"]) > 0.9:
                    matched += 1
                    break
        return matched

    retention = (_committed_true_matches() / n_gt_true) if n_gt_true else 0.0

    # pollution: fraction of committed slots holding spurious/contradictory (truth==-1)
    if committed:
        pollution = sum(1 for s in committed if s["truth"] == -1) / len(committed)
    else:
        pollution = 0.0

    # delayed-meaning recovery: fraction of delayed-reveal meaningful payloads
    # (truth==+1 AND reveal_step>=0) committed after reveal
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

    # overload recovery: retention measured on the post-burst tail
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
# Leak-scan assertion: prove policy decisions are functions of boundary-visible
# history only, i.e. flipping the hidden truth stamps in the stream (without
# changing any boundary-visible field) does NOT change the policy's commit
# TRAJECTORY (which candidates it commits, at which steps). If it does, a policy
# is reading ground truth -> INVALID.
# ============================================================================
def leak_scan(refs_by_regime, theta, w, seed, n=N_SITES_PRIMARY):
    reasons = []
    for regime in REGIMES:
        rho_ref = refs_by_regime[regime]
        base = make_stream(regime, seed)
        # build a truth-flipped copy: identical boundary-visible fields, flipped truth
        flipped = []
        rng = np.random.default_rng(99_000 + seed)
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
    """
    Per-seed advantage of ternary over `other` on `metric_name`.
    For higher-better metrics: ternary - other.
    For pollution (lower better): other - ternary (positive => ternary cleaner).
    """
    t = np.asarray(ternary_vals, float)
    o = np.asarray(other_vals, float)
    if metric_name in LOWER_BETTER:
        return o - t
    return t - o


# ============================================================================
# Full run at a given (theta, w)
# ============================================================================
def run_operating_point(theta, w, refs_by_regime, n=N_SITES_PRIMARY):
    """
    Returns nested dict:
      results[regime][policy][seed] = metric dict
    plus per-regime designated-metric advantage stats vs each control.
    """
    per = {}  # regime -> policy -> list-over-seeds metric dict
    for regime in REGIMES:
        rho_ref = refs_by_regime[regime]
        per[regime] = {p: [] for p in POLICIES}
        # measure ternary commit rate per seed to configure rate-matched binary
        for seed in SEEDS:
            events = make_stream(regime, seed)
            n_trig = _count_triggers(events, rho_ref, theta, n)

            r_bin = run_policy("binary", events, rho_ref, theta, w, seed, n)
            r_ter = run_policy("ternary", events, rho_ref, theta, w, seed, n)
            r_rnd = run_policy("random-third", events, rho_ref, theta, w, seed, n)
            # ternary effective commits-per-trigger, for rate matching
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
        rho = modular_flow_step(rho, rho_ref, DT_MODULAR)
        if ev is not None:
            rho = local_kick(rho, ev.site, n, ev.angle, ev.axis)
        D = relative_entropy(rho, rho_ref)
        if ev is not None and D > theta:
            cnt += 1
    return cnt


def summarize_designated(per):
    """
    For each regime, compute ternary-vs-{binary, random-third, rate-matched}
    advantage on the DESIGNATED metric, with mean, CI, same-sign count, and the
    H1 verdict vs each comparator.
    Also compute secondary retention & pollution advantage vs binary (for the
    'no symmetric-loss' pass rule).
    """
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
            # H1 bar: mean advantage >= 0.05 (positive), k>=8, CI excludes 0 on positive side
            passes = (mean >= H1_DELTA) and (k >= 8) and (lo > 0.0)
            stats[comp] = {
                "mean_adv": mean, "ci_lo": lo, "ci_hi": hi,
                "same_sign_k": k, "h1_pass": bool(passes),
                "ternary_mean": float(np.mean(ter)),
                "comp_mean": float(np.mean(comp_vals)),
            }
        # secondary: retention & pollution advantage vs binary (symmetric-loss guard)
        for sec in ["retention", "pollution"]:
            ter_s = [s[sec] for s in per[regime]["ternary"]]
            bin_s = [s[sec] for s in per[regime]["binary"]]
            diffs = advantage_diffs(sec, ter_s, bin_s)
            mean = float(np.mean(diffs))
            lo, hi = paired_bootstrap_ci(diffs)
            k = same_sign_count(diffs)
            # does ternary LOSE by the H1 bar? (advantage <= -0.05, k>=8 same neg sign, CI<0)
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
# Numerology guard: assert NO golden / phi constant is present.
# ============================================================================
def numerology_guard():
    phi = (1 + 5 ** 0.5) / 2  # 1.618...
    inv_phi = phi - 1         # 0.618...
    frozen = [J_COUPLING, DELTA_ANISO, H_FIELD, DT_MODULAR, ADMISS_BAND,
              THETA_PRIMARY, float(W_PRIMARY)] + THETA_SWEEP + \
             [float(x) for x in W_SWEEP] + list(BETA_BY_REGIME.values())
    bad = [c for c in frozen if abs(c - phi) < 1e-6 or abs(c - inv_phi) < 1e-6]
    assert not bad, f"NUMEROLOGY VIOLATION: golden constant present: {bad}"
    return {"phi": phi, "checked_constants": frozen, "violation": False}


# ============================================================================
# Decision logic (prereg section 7), applied IN CODE.
# ============================================================================
def decide(designated):
    """
    Returns classification string + machine verdict dict.
    A metric x regime pair PASSES H1 iff ternary clears the bar over binary AND
    over BOTH degenerate controls. PASS overall additionally requires no
    symmetric loss on retention/pollution in ANY regime.
    """
    winning_pairs = []
    for regime, st in designated.items():
        cleared_all = (st["binary"]["h1_pass"]
                       and st["random-third"]["h1_pass"]
                       and st["rate-matched-binary"]["h1_pass"])
        if cleared_all:
            winning_pairs.append((regime, st["metric"]))

    # symmetric-loss guard: does ternary LOSE by the bar on retention/pollution
    # anywhere with no offsetting qualifying win?
    symmetric_losses = []
    for regime, st in designated.items():
        for sec in ["retention", "pollution"]:
            if st[f"secondary_{sec}_vs_binary"]["ternary_loses_by_bar"]:
                symmetric_losses.append((regime, sec))

    if winning_pairs and not symmetric_losses:
        classification = "PASS-TERNARY"
    elif winning_pairs and symmetric_losses:
        # a qualifying win exists but offset by a symmetric loss -> not a pass
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
    out_dir = os.path.join(here, "modular_www_outputs")
    os.makedirs(out_dir, exist_ok=True)

    numer = numerology_guard()

    # frozen references (n=3 primary)
    refs = {rg: gibbs_reference(N_SITES_PRIMARY, BETA_BY_REGIME[rg]) for rg in REGIMES}

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
            # store only compact designated summary vs binary
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

    # ---- assemble summary ----
    summary = {
        "test_id": "modular_www",
        "lane": "engineering/verified-computation telemetry only",
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
            "seeds": SEEDS,
        },
        "primary_operating_point": {"theta": THETA_PRIMARY, "w": W_PRIMARY},
        "numerology_guard": {"phi": numer["phi"], "violation": numer["violation"]},
        "leak_scan": {"invalid": invalid, "reasons": leak_reasons},
        "designated_primary": designated,
        "decision": {"classification": classification, "detail": decision_detail},
        "sweeps_robustness_only": sweeps,
        "epsilon_sensitivity_brittleness": eps,
        "size_smoke_check": smoke,
    }

    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=lambda o: float(o))

    # ---- report.md ----
    write_report(out_dir, summary)

    # ---- headline (golden-vs-control carrying the content) ----
    headline = build_headline(summary)
    print("CLASSIFICATION: " + classification)
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
    lines.append("# modular_www — Result Report (write/witness/release)\n")
    lines.append(f"- **test_id:** modular_www")
    lines.append(f"- **Lane:** {summary['lane']}")
    lines.append(f"- **Primary operating point:** theta={summary['primary_operating_point']['theta']}, "
                 f"w={summary['primary_operating_point']['w']}")
    lines.append(f"- **System:** n={summary['system']['n_sites_primary']} sites "
                 f"(dim {summary['system']['hilbert_dim']}), T={summary['system']['T_steps']} steps, "
                 f"register={summary['system']['register_size']}, 10 seeds.")
    lines.append(f"- **Numerology guard:** phi={summary['numerology_guard']['phi']:.6f}, "
                 f"violation={summary['numerology_guard']['violation']} (phi-FREE channel).")
    lines.append(f"- **Leak-scan:** invalid={summary['leak_scan']['invalid']}.")
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
    lines.append("Preregistration: experiments/MODULAR_WWW_PREREG_v1.md (LOCKED before run). "
                 "Ledger slots T-004 / E-001 to be written AFTER the run, carrying this "
                 "classification verbatim with the forbidden-upgrade sentence attached.")

    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
