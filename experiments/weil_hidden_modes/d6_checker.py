"""D6 endpoint checker: an advertised lower bound is accepted only if it is <= the certified lower endpoint minus the Schur correction.
Inputs are ball STRINGS as printed in the JSONs (Arb's printed balls enclose the computed balls, so parsing them is rigorous)."""
from flint import arb, ctx
ctx.prec=192
def corrected_bound(lambda0_str, eps_C_str, eps_p_str, norm_pN_str, beta_str, eps_D_str):
    lam=arb(lambda0_str); eC=arb(eps_C_str); ep=arb(eps_p_str); pN=arb(norm_pN_str); beta=arb(beta_str); eD=arb(eps_D_str)
    lam_lo=arb(lam.lower()); off=arb((eC+2*pN*ep).upper()); d_low=arb((beta-eD-2*ep*ep).lower())
    assert d_low>lam_lo>0
    # smallest eigenvalue of [[lam_lo,-off],[-off,d_low]]: exact 2x2 formula, then take its lower endpoint
    mu=(lam_lo+d_low)/2-(((d_low-lam_lo)/2)**2+off*off).sqrt()
    return arb(mu.lower()), lam_lo, off, d_low
def verdict(claimed, bound):
    """ACCEPT only if claimed <= bound is certain (arb comparison is False when undecidable)."""
    c=arb(claimed)
    return "ACCEPT" if (c<=bound) else "REJECT: claimed %s exceeds certified lower bound %s"%(claimed, bound.str(15))
def round_down(x, sig=4):
    """Decimal string <= x with sig significant digits (truncation of a positive lower endpoint)."""
    s=arb(x.lower()).str(sig+6, radius=False)   # e.g. '5.859070853209e-11'
    mant,exp=(s.split('e')+['0'])[:2]; digs=mant.replace('.','').replace('-','')
    lead=digs[:sig]; out=lead[0]+'.'+lead[1:]+'e'+exp
    assert arb(out)<=x, (out,x); return out
if __name__=="__main__":
    import json
    odd=json.load(open('d5_results_odd_NE80_pole-1.json')); even=json.load(open('d5_results_even_NE80_pole+1.json'))
    res={}
    for name,d in (('even',even),('odd',odd)):
        b,lam_lo,off,dl=corrected_bound(d['lambda0_certified'],d['eps_C'],d['eps_p'],d['norm_pN'],d['beta_star'],d['eps_D'])
        res[name]=dict(lambda0_lower_endpoint=lam_lo.str(15),off_upper=off.str(6),d_low=dl.str(10),corrected_lower_bound=b.str(15),
                       correction=(lam_lo-b).str(4),advertise_4sig=round_down(b,4),advertise_3sig=round_down(b,3))
        print(name,res[name])
    tests={"T2a odd claimed 5.86e-11 must REJECT":verdict('5.86e-11',corrected_bound(odd['lambda0_certified'],odd['eps_C'],odd['eps_p'],odd['norm_pN'],odd['beta_star'],odd['eps_D'])[0]),
           "T2b odd claimed 5.859e-11 must ACCEPT":verdict('5.859e-11',corrected_bound(odd['lambda0_certified'],odd['eps_C'],odd['eps_p'],odd['norm_pN'],odd['beta_star'],odd['eps_D'])[0]),
           "T2c even claimed 1.031e-13 must ACCEPT":verdict('1.031e-13',corrected_bound(even['lambda0_certified'],even['eps_C'],even['eps_p'],even['norm_pN'],even['beta_star'],even['eps_D'])[0]),
           "T2d even claimed 1.032e-13 must REJECT":verdict('1.032e-13',corrected_bound(even['lambda0_certified'],even['eps_C'],even['eps_p'],even['norm_pN'],even['beta_star'],even['eps_D'])[0])}
    ok=True
    for k,v in tests.items():
        want=k.split("must ")[1]; got=v.split(":")[0]; ok&=(want==got); print("PASS" if want==got else "FAIL","|",k,"->",v)
    res['tests_ok']=ok; json.dump(res,open('d6_constants.json','w'),indent=1); print("D6 CHECKER",("OK" if ok else "BROKEN"))
