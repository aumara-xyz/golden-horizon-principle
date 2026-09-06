"""D4 checker: Schur-complement verdict for 'finite block + bounded tail'. Refuses to rule without every input. Independently falsifiable via tests."""
def verdict(lambda0_certified, lambda0, eps_D=None, eps_C=None, eps_p=None, beta=None, norm_pN=None):
    """All bounds must be rigorous upper bounds supplied by the caller; None => NO_VERDICT."""
    if any(v is None for v in (eps_D,eps_C,eps_p,beta,norm_pN)): return "NO_VERDICT: missing tail/coupling/pole/beta evidence"
    if not lambda0_certified: return "NO_VERDICT: lambda0 not interval-certified"
    d_low = beta - eps_D - 2*eps_p*eps_p
    if d_low <= 0: return "REJECT: discarded block not certified positive (beta - eps_D - 2 eps_p^2 <= 0)"
    off = eps_C + 2*norm_pN*eps_p
    margin = lambda0 - off*off/d_low
    return ("ACCEPT" if margin > 0 else "REJECT") + f": margin = lambda0 - off^2/d_low = {margin:.3e} (lambda0={lambda0:.3e}, off={off:.3e}, d_low={d_low:.3e})"
if __name__=="__main__":
    tests={
     "T-a excess coupling (A=1e-13, D=0.5, C=1e-3) must REJECT": verdict(True,1e-13,eps_D=0.0,eps_C=1e-3,eps_p=0.0,beta=0.5,norm_pN=1.0),
     "T-b missing eps_D must NO_VERDICT": verdict(True,1e-13,eps_D=None,eps_C=1e-20,eps_p=0.0,beta=0.5,norm_pN=1.0),
     "T-c understated error: certified flag False must NO_VERDICT": verdict(False,1e-13,eps_D=1e-40,eps_C=1e-40,eps_p=0.0,beta=0.5,norm_pN=1.0),
     "T-c2 coupling 1e-5 with tiny radii must REJECT": verdict(True,1e-13,eps_D=1e-40,eps_C=1e-5,eps_p=0.0,beta=0.5,norm_pN=1.0),
     "T-d positive control (C=1e-20) must ACCEPT": verdict(True,1e-13,eps_D=1e-30,eps_C=1e-20,eps_p=1e-100,beta=0.5,norm_pN=1.0),
    }
    ok=True
    for k,v in tests.items():
        want=k.split("must ")[1].split()[0]; got=v.split(":")[0].split()[0]; flag=(want==got); ok&=flag
        print("PASS" if flag else "FAIL", "|", k, "->", v)
    print("CHECKER", "OK" if ok else "BROKEN")
