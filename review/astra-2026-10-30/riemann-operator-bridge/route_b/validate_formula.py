#!/usr/bin/env python3
"""Independent Fourier-domain numerical cross-check plus ball moment check.

The Fourier bounds here are evaluated in float64 and are validation only.
The mathematical certificates are the Arb scripts and their analytic bounds.
"""
from pathlib import Path
import json, math, sys, time
HERE=Path(__file__).resolve().parent
if (HERE/'_deps').exists():sys.path.insert(0,str(HERE/'_deps'))
import numpy as np
from scipy.special import digamma,spherical_jn
from numpy.polynomial.legendre import leggauss,legval,legder
from flint import arb,acb,ctx
from weil_schur import arch_moments,kernel_series,enclosure

def main():
    data=np.load(HERE/'finite_matrices.npz');rows=[]
    xg,wg=leggauss(32);xu,wu=leggauss(16)
    for L,key in [(.4,'2_5'),(.7,'7_10')]:
        A=data['arch_'+key]
        for label,v in [('e0',np.array([1.])),('e1',np.array([0.,1.])),
                        ('even_mix',np.array([1.,0.,1.])/math.sqrt(2)),
                        ('odd_mix',np.array([0.,1.,0.,1.])/math.sqrt(2))]:
            coeff=v*np.sqrt((2*np.arange(len(v))+1)/(2*L))
            endpoints=abs(legval(-1,coeff))+abs(legval(1,coeff))
            D=L*np.sum(wu*(legval(xu,legder(coeff))/L)**2)
            exact=float(v@A[:len(v),:len(v)]@v)
            for T in [512,1024]:
                ts=(np.arange(T)[:,None]+(xg+1)[None,:]/2).ravel();ws=np.tile(wg/2,T)
                F=sum(v[n]*np.sqrt(L*(2*n+1)/math.pi)*(-1)**(n//2)*spherical_jn(n,L*ts) for n in range(len(v)))
                aa=digamma(.25+.5j*ts).real-math.log(math.pi)
                prefix=float(2*np.sum(ws*aa*F*F));mass=float(1-2*np.sum(ws*F*F))
                C=(endpoints/math.sqrt(math.pi)+math.sqrt(D/T))**2
                M0=min(mass,C/T);assert M0>0
                low=(digamma(.25+.5j*T).real-math.log(math.pi))*M0
                high=M0*(math.log(T/(2*math.pi))+math.log(C/(M0*T))+1+math.pi/T+1/(8*T*T))
                passed=bool(prefix+low<exact<prefix+high)
                assert passed
                rows.append({'L':L,'wave':label,'T':T,'time_domain_Arb_midpoint':exact,
                     'Fourier_prefix':prefix,'remaining_mass_numeric':mass,
                     'predicted_full_arch_lower_numeric':prefix+low,
                     'predicted_full_arch_upper_numeric':prefix+high,'bracket_contains_time_domain_value':passed})
    ctx.dps=100
    L=arb(7)/10;M,stat=arch_moments(L,1,kernel_series(512))
    direct=acb.integral(lambda z,analytic:(-z/2).exp()/(-2*z).hypgeom_1f1(1,2),0,2*L,
                        rel_tol=arb('1e-85'),abs_tol=arb('1e-90')).real
    series=L*M[1];assert direct.overlaps(series)
    out={'Fourier_crosschecks':rows,'Fourier_arithmetic':'float64; not interval certificates',
         'independent_moment_check':{'L':'7/10','k':1,'Acb_integral':enclosure(direct,80),
            'rational_Taylor_Cauchy_enclosure':enclosure(series,80),'overlap':bool(direct.overlaps(series))}}
    (HERE/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'Fourier_checks':len(rows),'all_pass':True,'moment_overlap':True},indent=2))

if __name__=='__main__':main()
