"""Opus D7.4 - attack the checker BEFORE accepting authentic results.

Independent re-implementation (not an import of d4_checker.py / d6_checker.py) of:
  (a) the finite-block + infinite-tail Schur verdict,
  (b) the congruence-to-eigenvalue conversion lambda_min(A) >= lambda_min(V^T A V) / lambda_max(V^T V),
  (c) the advertised-constant endpoint test.
Six required negative/positive controls are run.  A control that does not fail as designed is itself a finding.
"""
import json, sys
from flint import arb, ctx
ctx.prec = 256

# ---------------------------------------------------------------- (a) Schur verdict
def schur_mu(lam0, off, d_low):
    """Smallest eigenvalue of [[lam0, -off],[-off, d_low]] as an arb ball (exact 2x2 formula)."""
    return (lam0 + d_low)/2 - (((d_low - lam0)/2)**2 + off*off).sqrt()

def verdict(lambda0_certified, lam0=None, eps_D=None, eps_C=None, eps_p=None, beta=None, norm_pN=None):
    """Refuses to rule without EVERY input.  All eps_* must be rigorous UPPER bounds, beta/lam0 rigorous LOWER bounds."""
    if any(v is None for v in (lam0, eps_D, eps_C, eps_p, beta, norm_pN)):
        return "NO_VERDICT: missing tail/coupling/pole/beta evidence", None
    if not lambda0_certified:
        return "NO_VERDICT: lambda0 not interval-certified", None
    lam0, eps_D, eps_C, eps_p, beta, norm_pN = (arb(str(v)) for v in (lam0, eps_D, eps_C, eps_p, beta, norm_pN))
    d_low = beta - eps_D - 2*eps_p*eps_p
    if not (d_low > 0):
        return "REJECT: discarded block not certified positive", None
    if not (lam0 > 0):
        return "REJECT: finite block not certified positive", None
    off = eps_C + 2*norm_pN*eps_p
    mu = schur_mu(arb(lam0.lower()), arb(off.upper()), arb(d_low.lower()))
    return ("ACCEPT" if mu > 0 else "REJECT") + f": mu = {mu.str(8)}", mu

def endpoint_test(claimed, mu):
    """ACCEPT only when claimed <= mu is CERTAIN (arb comparison is False when undecidable)."""
    return "ACCEPT" if (arb(claimed) <= mu) else "REJECT"

# ---------------------------------------------------------------- (b) congruence conversion
def congruence_lower_bound(A, V):
    """Rigorous lower bound on lambda_min(A) for symmetric ball matrix A and ANY real invertible V.
    Refuses (returns None, reason) if V is not certified invertible."""
    n = len(A)
    AV  = [[sum((A[i][k]*V[k][j] for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
    Bm  = [[sum((V[k][i]*AV[k][j] for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
    VtV = [[sum((V[k][i]*V[k][j] for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
    vmin = min(VtV[i][i].lower() - sum((VtV[i][j].abs_upper() for j in range(n) if j != i), arb(0)) for i in range(n))
    vmax = max(VtV[i][i].upper() + sum((VtV[i][j].abs_upper() for j in range(n) if j != i), arb(0)) for i in range(n))
    if not (vmin > 0):
        return None, f"REFUSED: V not certified invertible (Gershgorin lower bound on V^T V is {vmin.str(6)}, must be > 0)"
    g = min(Bm[i][i].lower() - sum((Bm[i][j].abs_upper() for j in range(n) if j != i), arb(0)) for i in range(n))
    # x = V y :  x^T A x >= g ||y||^2  and  ||x||^2 in [vmin ||y||^2, vmax ||y||^2]
    return (g/vmax if g >= 0 else g/vmin), f"OK (Gershgorin min {g.str(8)}, lambda_max(V^TV) <= {vmax.str(8)}, lambda_min(V^TV) >= {vmin.str(8)})"

def naive_bound(A, V):
    """The WRONG conversion that forgets the norm change: lambda_min(V^T A V) alone."""
    n = len(A)
    AV = [[sum((A[i][k]*V[k][j] for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
    Bm = [[sum((V[k][i]*AV[k][j] for k in range(n)), arb(0)) for j in range(n)] for i in range(n)]
    return min(Bm[i][i].lower() - sum((Bm[i][j].abs_upper() for j in range(n) if j != i), arb(0)) for i in range(n))

# ---------------------------------------------------------------- controls
def run():
    import mpmath as mp
    mp.mp.dps = 50
    res, ok = {}, True
    def rec(name, want, got, extra=""):
        nonlocal ok
        good = (want == got); ok &= good
        res[name] = {"want": want, "got": got, "pass": good, "detail": extra}
        print(("PASS" if good else "FAIL"), "|", name, "-> want", want, "got", got, extra, flush=True)

    # C1 missing tail evidence -> no certificate
    v, _ = verdict(True, lam0='1e-13', eps_D=None, eps_C='1e-20', eps_p='0', beta='0.5', norm_pN='1')
    rec("C1 missing eps_D", "NO_VERDICT", v.split(":")[0], v)
    # C2 excessive coupling -> rejection when the certified inequality fails
    v, _ = verdict(True, lam0='1e-13', eps_D='0', eps_C='1e-5', eps_p='0', beta='0.5', norm_pN='1')
    rec("C2 coupling 1e-5 vs lambda0 1e-13", "REJECT", v.split(":")[0], v)
    # C2b coupling that is large but still admissible -> ACCEPT
    v, _ = verdict(True, lam0='1e-13', eps_D='0', eps_C='1e-9', eps_p='0', beta='0.5', norm_pN='1')
    rec("C2b positive control coupling 1e-9", "ACCEPT", v.split(":")[0], v)
    # C3 uncertified lambda0
    v, _ = verdict(False, lam0='1e-13', eps_D='1e-40', eps_C='1e-40', eps_p='0', beta='0.5', norm_pN='1')
    rec("C3 lambda0 not certified", "NO_VERDICT", v.split(":")[0], v)
    # C4 discarded block not positive
    v, _ = verdict(True, lam0='1e-13', eps_D='1', eps_C='1e-40', eps_p='0', beta='0.5', norm_pN='1')
    rec("C4 eps_D swamps beta", "REJECT", v.split(":")[0], v)

    # C5 advertised constant above the rigorous endpoint, using MY reconstructed endpoints
    for tag, fn in (("even", "opus_d7_even_NE80_pole+1.json"), ("odd", "opus_d7_odd_NE80_pole-1.json")):
        try:
            d = json.load(open(fn))
        except FileNotFoundError:
            print("skip C5", tag, "(reconstruction not present)"); continue
        mu = arb(arb(d["full_form_lower_bound"]).lower())
        claims = {"even": [("1.031e-13", "ACCEPT"), ("1.032e-13", "REJECT"), ("1.03e-13", "ACCEPT"), ("1.0311e-13", "REJECT")],
                  "odd":  [("5.859e-11", "ACCEPT"), ("5.86e-11", "REJECT"), ("5.85e-11", "ACCEPT"), ("5.8591e-11", "REJECT")]}[tag]
        for c, want in claims:
            rec(f"C5 {tag} advertised {c}", want, endpoint_test(c, mu), f"endpoint {mu.str(15)}")

    # C6/C7 basis-transformation controls on a small synthetic A with a 1e-13 smallest eigenvalue
    n = 6
    lams = [mp.mpf('1e-13'), mp.mpf('1e-8'), mp.mpf(1), mp.mpf(2), mp.mpf(3), mp.mpf(4)]
    Q = mp.matrix(n, n)
    for i in range(n):
        for j in range(n):
            Q[i, j] = mp.cos(mp.mpf(1 + i*n + j))
    Q, _ = mp.qr(Q)
    Amp = Q*mp.diag(lams)*Q.T
    A = [[arb(mp.nstr(Amp[i, j], 40)) + arb(0, 1e-30) for j in range(n)] for i in range(n)]
    Vorth = [[arb(mp.nstr(Q[i, j], 40)) for j in range(n)] for i in range(n)]
    b, msg = congruence_lower_bound(A, Vorth)
    rec("C6 orthogonal V recovers 1e-13", "OK", "OK" if (b is not None and b > arb('0.99e-13') and b < arb('1.01e-13')) else "BAD", f"{b.str(8) if b else msg}")
    # C7 singular V (duplicated column) must be REFUSED
    Vsing = [row[:] for row in Vorth]
    for i in range(n): Vsing[i][1] = Vsing[i][0]
    b, msg = congruence_lower_bound(A, Vsing)
    rec("C7 singular V refused", "REFUSED", "REFUSED" if b is None else "ACCEPTED", msg)
    # C8 nonorthogonal invertible V: bound must stay valid (<= true 1e-13) and > 0; the naive conversion must be shown wrong
    # scale UP the eigendirection that carries the smallest eigenvalue: then V^T A V = diag(lam_i s_i^2)
    # has minimum 1e-9, and a checker that forgets to divide by lambda_max(V^T V) = 1e4 would falsely
    # advertise lambda_min(A) >= 1e-9 instead of the true 1e-13.
    S = mp.diag([mp.mpf(100), mp.mpf(1), mp.mpf(1), mp.mpf(1), mp.mpf(1), mp.mpf(1)])
    Vs = Q*S
    Vscaled = [[arb(mp.nstr(Vs[i, j], 40)) for j in range(n)] for i in range(n)]
    b, msg = congruence_lower_bound(A, Vscaled)
    nb = naive_bound(A, Vscaled)
    valid = (b is not None) and (b > 0) and (b <= arb('1.0000001e-13'))
    rec("C8 nonorthogonal invertible V: correct norm conversion", "VALID", "VALID" if valid else "INVALID",
        f"correct bound {b.str(8) if b else msg}; naive (no /lambda_max(V^TV)) would claim {nb.str(8)}, which is {'ABOVE the true 1e-13 -> the naive conversion is demonstrably unsound' if nb > arb('1.0000001e-13') else 'below the true 1e-13 -> this control did not bite'}")
    res["all_pass"] = ok
    json.dump(res, open("opus_d7_controls.json", "w"), indent=1, default=str)
    print("OPUS D7 CONTROLS", "OK" if ok else "BROKEN")

if __name__ == "__main__":
    run()
