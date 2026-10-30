#!/usr/bin/env python3
"""One adaptive all-function lower certificate at L=2/5,T=32,N=48.

Uses the valid Fourier lower envelope R_T <= W, rigorous Arb quadrature,
an analytic Gauss remainder, and a complete Legendre-complement bound.
"""
import sys,json,math,time,hashlib
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
if (HERE/'_deps').exists():sys.path.insert(0,str(HERE/'_deps'))
from flint import arb,acb,arb_mat,ctx
import numpy as np
from weil_schur import enclosure,certified_floor,sub,basis_pole,tail_bound_attempt,ldl_positive


def run():
    ctx.dps=100
    N=48;T=32;L=arb(2)/5;order=32;rho=arb(2);h=arb(1)/2;imag_h=arb(3)/8
    start=time.monotonic()
    # The ellipse over a unit panel has real semiaxis5/8 and imaginary semiaxis3/8.
    # Digamma arguments have Re>=1/4-3/16=1/16, away from their poles.
    assert arb(1)/4-imag_h/2==arb(1)/16
    logpi=arb.pi().log();weight=2*arb(2).log()/arb(2).sqrt();shift=arb(2).log()
    def arch(z):
        iz=acb(0,1)*z/2
        return ((acb(arb(1)/4)+iz).digamma()+(acb(arb(1)/4)-iz).digamma())/2-logpi
    aT=arch(acb(T)).real;beta=aT-weight
    g=[arb.legendre_p_root(order,k,weight=True) for k in range(order)]
    ts=[];qs=[];per_panel=[]
    # Entry-independent analytic Fourier basis bound: sqrt(L/pi)exp(L|Im z|).
    F_product_bound=L/arb.pi()*(2*L*imag_h).exp()
    for panel in range(T):
        center=arb(panel)+h
        # Direct wide-box Acb digamma returned indeterminate in the first attempt.
        # Instead use the exact analytic derivative bound |psi'(z)|<=eta^-2+eta^-1
        # for Re z>=eta=1/16, from its absolutely convergent reciprocal-square series.
        # Each digamma argument differs from its center by at most sqrt(34)/16.
        eta=arb(1)/16;argument_radius=arb(34).sqrt()/16
        psi_center=acb(arb(1)/4,center/2).digamma().abs_upper()
        arch_bound=psi_center+argument_radius*(eta**-2+eta**-1)+logpi.abs_upper()
        symbol_bound=(arch_bound+beta.abs_upper()+weight*(shift*imag_h).cosh()).abs_upper()
        M=(symbol_bound*F_product_bound).abs_upper()
        error=(h*64*M/(15*(1-rho**-2)*rho**(2*order))).abs_upper()
        per_panel.append(error)
        for node,w in g:
            t=center+h*node
            sym=arch(acb(t)).real-weight*(shift*t).cos()-beta
            ts.append(t);qs.append(h*w*sym)
    entry_error=(2*sum(per_panel,arb(0))).abs_upper()
    p=[basis_pole(L,n) for n in range(N)]
    basis=[]
    for n in range(N):
        df=math.prod(range(1,2*n+2,2))
        norm=(L*(2*n+1)/arb.pi()).sqrt()*(-1)**(n//2)
        basis.append([norm*(L*t)**n/df*(-(L*t)**2/4).hypgeom_0f1(arb(n)+arb(3)/2) for t in ts])
    tail=tail_bound_attempt('2/5',N=N,T=T)
    # Recompute exact balls rather than parsing the shortened display strings for decisions.
    x=L*T;df=math.prod(range(1,2*N+2,2));hn2=L*(2*N+1)/arb.pi()*x**(2*N)/arb(df)**2
    r=x*x/((2*N+1)*(2*N+3));assert r<1
    tau=(2*T*hn2/(1-r)).abs_upper()
    a0=(arb(1)/4).digamma()-logpi
    Mtail=max((aT-a0).abs_upper(),(2*weight).abs_upper())
    y=L/2;pt2=2*L*(2*N+1)*(2*y).exp()*y**(2*N)/arb(df)**2
    pr=y*y/((2*N+1)*(2*N+3));pt2=(pt2/(1-pr)).abs_upper()
    gap=beta-Mtail*tau-2*pt2
    # ||P_N p||<=||exp(x/2)||; this works for either parity's cosh/sinh vector.
    pole_norm_upper=(2*L).sqrt()*(L/2).exp()
    coupling=(Mtail*tau.sqrt()+2*pole_norm_upper*pt2.sqrt()).abs_upper()
    out={'profile':'pentora.research.all-function-window.v1','L':'2/5','T':T,'N':N,
         'basis':'normalized Legendre degrees0..47, both parities','no_zero_inputs':True,
         'precision_decimal_digits':100,'quadrature_points_per_unit_panel':order,
         'ellipse_rho':'2','ellipse_imaginary_semiaxis':'3/8','digamma_real_part_lower':'1/16',
         'Gauss_error_formula':'64 M h / (15 (1-rho^-2) rho^(2*order))',
         'total_two_sided_entry_error':enclosure(entry_error),
         'beta':enclosure(beta),'tail_tau':enclosure(tau),'tail_pole_norm_squared':enclosure(pt2),
         'complement_gap_lower':enclosure(gap),'coupling_upper':enclosure(coupling),
         'parities':{},'scope':'All L2 functions supported on[-2/5,2/5] in the Weil form domain; no larger L or RH claim.'}
    for parity in [0,1]:
        deg=list(range(parity,N,2));F=arb_mat([basis[n] for n in deg]);Fq=arb_mat([[x*q for x,q in zip(basis[n],qs)] for n in deg])
        R=2*Fq*F.transpose()
        for i,n in enumerate(deg):
            for j,m in enumerate(deg):
                R[i,j]+=arb(0,entry_error)+(beta if i==j else 0)+(2 if parity==0 else -2)*p[n]*p[m]
        floor=certified_floor(R)
        # A fixed conservative decimal target, chosen after the earlier failedT160bound,
        # is certified by a shifted full-space block determinant.
        mu=arb('0.0001') if parity==0 else arb('0.009')
        finite_ok,pivots=ldl_positive(R,mu)
        # Strengthen by selecting mA from certified_floor, then rigorously checking the2x2bound.
        mA=arb(floor['certified_lower_bound']) if floor['certified_lower_bound'] is not None else None
        determinant=(mA-mu)*(gap-mu)-coupling**2 if mA is not None else None
        passed=bool(mA is not None and mA>mu and gap>mu and determinant>0 and finite_ok)
        rational_mA=Fraction(10106,100000000) if parity==0 else Fraction(9283,1000000)
        rational_mu=Fraction(1,10000) if parity==0 else Fraction(9,1000)
        rational_gap=Fraction(64755,100000);rational_c=Fraction(101,10**23)
        rational_det=(rational_mA-rational_mu)*(rational_gap-rational_mu)-rational_c**2
        rational_pass=bool(mA is not None and mA>arb(str(rational_mA)) and gap>arb(str(rational_gap))
                          and coupling<arb(str(rational_c)) and rational_det>0)
        A=sub(R,[0,1,2],[0,1,2]);C=sub(R,list(range(3,len(deg))),list(range(3,len(deg))));B=sub(R,[0,1,2],list(range(3,len(deg))))
        try:
            S=A-B*C.solve(B.transpose())
            schur=certified_floor(S)
        except ZeroDivisionError:
            schur={'certification_failed':'Arb could not enclose the finite complement inverse'}
        out['parities']['even' if parity==0 else 'odd']={
            'finite_R_floor':floor,'finite_R_Schur':schur,
            'requested_global_lower_bound':enclosure(mu),'shifted_block_determinant':None if determinant is None else enclosure(determinant),
            'all_function_positive_certificate':passed,
            'simplified_rational_certificate':{'finite_block_lower':str(rational_mA),
                'complement_lower':str(rational_gap),'coupling_upper':str(rational_c),
                'target_mu':str(rational_mu),'shifted_determinant':str(rational_det),
                'certified_by_ball_enclosures':rational_pass},
            'finite_LDL_min_pivot_at_mu':enclosure(min(pivots,key=lambda a:float(a.mid()))),
        }
        print('parity',parity,'pass',passed,'finite_min',floor['numeric_eigenvalue'],flush=True)
    out['elapsed_seconds']=time.monotonic()-start
    out['all_functions_both_parities_certified']=all(r['all_function_positive_certificate'] and r['simplified_rational_certificate']['certified_by_ball_enclosures'] for r in out['parities'].values())
    (HERE/'small_window_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)


if __name__=='__main__':run()
