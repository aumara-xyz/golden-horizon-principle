#!/usr/bin/env python3
"""Exact polynomial correlations and rigorous finite full-Weil matrices.

No zeta zeros or prior matrix coefficients are inputs. Float eigensolvers select
candidate bounds only; every advertised finite lower bound is checked with Arb
LDL pivots. This does not certify the infinite-dimensional complement.
"""
import sys, json, math, time, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
if (HERE/'_deps').exists(): sys.path.insert(0,str(HERE/'_deps'))
import numpy as np
from scipy.special import digamma, spherical_jn
from scipy.integrate import quad
from flint import arb, arb_mat, arb_poly, fmpq, fmpq_poly, fmpq_series, ctx

MAX_DEGREE=47
MOMENT_TERMS=512
DPS=170

def enclosure(v,digits=32):
    return str(v.str(digits))

def midmatrix(M):
    return np.array([[float(M[i,j].mid()) for j in range(M.ncols())] for i in range(M.nrows())])

def sub(M,rows,cols):
    return arb_mat([[M[i,j] for j in cols] for i in rows])

def ldl_positive(M,mu=arb(0)):
    n=M.nrows(); a=[[M[i,j]-(mu if i==j else 0) for j in range(n)] for i in range(n)]
    piv=[]
    for k in range(n):
        d=a[k][k]
        if not d>0: return False,piv+[d]
        piv.append(d)
        for i in range(k+1,n):
            for j in range(i,n):
                a[j][i]=a[i][j]=a[i][j]-a[i][k]*a[j][k]/d
    return True,piv

def certified_floor(M):
    evals, evecs=np.linalg.eigh(midmatrix(M));est=float(evals[0])
    v=arb_mat([[arb(float(x))] for x in evecs[:,0]])
    rayleigh=(v.transpose()*M*v)[0,0]/(v.transpose()*v)[0,0]
    witness={'selected_vector_Rayleigh':enclosure(rayleigh),
             'negative_witness_certified':bool(rayleigh<0)}
    if rayleigh<0:witness['negative_witness_binary64_vector']=[float(x) for x in evecs[:,0]]
    # The chosen exact decimal candidate is independently validated by Arb LDL.
    # This can certify a negative floor, too; a positive floor is the useful case.
    slack=max(abs(est)*.01,1e-16)
    candidate=arb(format(est-slack,'.17g'))
    for attempt in range(12):
        good,p=ldl_positive(M,candidate)
        if good:
            return {'numeric_eigenvalue':est,'certified_lower_bound':enclosure(candidate),**witness,
                    'positive_lower_bound':bool(candidate>0),
                    'LDL_min_pivot':enclosure(min(p,key=lambda z:float(z.mid()))),
                    'candidate_attempts':attempt+1}
        slack*=4
        candidate=arb(format(est-slack,'.17g'))
    return {'numeric_eigenvalue':est,'certified_lower_bound':None,'positive_lower_bound':False,**witness,
            'candidate_attempts':12}

def legendre_polys(N):
    x=fmpq_poly([0,1]);P=[fmpq_poly([1]),x]
    for n in range(1,N-1):P.append(((2*n+1)*x*P[n]-n*P[n-1])/(n+1))
    return P[:N]

def correlation_polys(N):
    """Unnormalized integral[-1,1-r] P_n(x) P_m(x+r) dx."""
    P=legendre_polys(N);x=fmpq_poly([0,1]);J=[]
    for k in range(2*N):J.append(((1-x)**(k+1)-(-1)**(k+1))/(k+1))
    F=[[sum((P[n][i]*J[i+k] for i in range(n+1)),fmpq_poly()) for k in range(N)] for n in range(N)]
    B=[[fmpq_poly([P[m][j]*math.comb(j,k) for j in range(k,m+1)]) for k in range(m+1)] for m in range(N)]
    result={}
    for n in range(N):
        for m in range(n,N):
            if (n+m)%2:continue
            p=sum((B[m][k]*F[n][k] for k in range(m+1)),fmpq_poly())
            assert p[0] == (fmpq(2,2*n+1) if n==m else 0)
            result[n,m]=p
    return P,result

def kernel_series(K):
    # q(x)=x exp(x/2)/sinh(x)=exp(3x/2)/exprel(2x).
    ctx.cap=K
    denominator=fmpq_series([fmpq(2)**m/fmpq(math.factorial(m+1)) for m in range(K)])
    numerator=fmpq_series([0,fmpq(3,2)]).exp()
    q=(numerator/denominator).coeffs()
    assert q[0]==1 and q[1]==fmpq(1,2) and q[2]==fmpq(-1,24)
    return q

def arch_moments(L,max_k,qcoeff):
    # Cauchy bound on |z|=rho<pi:
    # |sinh(z)/z| >= sin(rho)/rho, hence |q(z)|<=rho exp(rho/2)/sin(rho).
    # rho=14/5 and 2L<=7/5 give a geometric ratio <=1/2.
    rho=arb(14)/5; M=rho*(rho/2).exp()/rho.sin();ratio=2*L/rho
    assert ratio<1
    rem=(M*ratio**len(qcoeff)/(1-ratio)).abs_upper()
    terms=[arb(q)*((2*L)**m) for m,q in enumerate(qcoeff)]
    out=[arb(0)]
    for k in range(1,max_k+1):
        s=sum((v/(k+m) for m,v in enumerate(terms)),arb(0))*2**k
        err=(rem*2**k/k).abs_upper()
        out.append(s+arb(0,err))
    return out,{'terms':len(qcoeff),'rho':'14/5','uniform_kernel_tail_bound':enclosure(rem),
                'maximum_moment_radius':enclosure(max((x.rad() for x in out),key=float))}

def basis_pole(L,n):
    z=L/2
    i_n=(arb.pi()/(2*z)).sqrt()*z.bessel_i(arb(n)+arb(1)/2)
    return (2*L*(2*n+1)).sqrt()*i_n

def coefficient_mode(n,sigma,mode):
    ln=arb(n).log()
    if mode=='authentic':return (-ln/2).exp()
    if mode=='unsym':return (-sigma*ln).exp()
    if mode=='bounce':return (-ln/2).exp()*((sigma-arb(1)/2)*ln).cosh()
    raise ValueError(mode)

def matrices(L_string,P,Cpoly,qcoeff):
    L=arb(L_string);N=len(P)
    mom,mstat=arch_moments(L,2*N-1,qcoeff)
    z=(-L).exp()
    constant=(arb(1)/4).digamma()-arb.pi().log()+2*(z.atanh()+z.atan())
    arch=arb_mat(N,N);pole=arb_mat(N,N)
    p=[basis_pole(L,n) for n in range(N)]
    shifts=[2] if L_string=='2/5' else [2,3,4]
    primemats={n:arb_mat(N,N) for n in shifts}
    for (n,m),pol in Cpoly.items():
        norm=(arb((2*n+1)*(2*m+1))).sqrt()/2
        value=(constant if n==m else arb(0))-norm*sum((arb(pol[k])*mom[k] for k in range(1,len(pol))),arb(0))
        arch[n,m]=arch[m,n]=value
        pole[n,m]=pole[m,n]=(2 if n%2==0 else -2)*p[n]*p[m]
        ap=arb_poly(pol)
        for pp in shifts:
            r=arb(pp).log()/L
            primemats[pp][n,m]=primemats[pp][m,n]=norm*ap(r)
    variants={}
    for mode,sigma in [('authentic','1/2'),('unsym','9/20'),('unsym','11/20'),('bounce','9/20'),('bounce','11/20')]:
        Q=arch+pole
        for pp,C in primemats.items():
            prime=2 if pp==4 else pp
            weight=2*arb(prime).log()*coefficient_mode(pp,arb(sigma),mode)
            Q=Q-C*weight
        variants[f'{mode}_{sigma}']=Q
    # The bounce controls must be identical under sigma -> 1-sigma, as balls overlap.
    assert all(variants['bounce_9/20'][i,j].overlaps(variants['bounce_11/20'][i,j]) for i in range(N) for j in range(N))
    return arch,pole,primemats,variants,mstat,mom

def finite_summary(M,degrees):
    A=sub(M,list(range(3)),list(range(3)))
    C=sub(M,list(range(3,M.nrows())),list(range(3,M.nrows())))
    B=sub(M,list(range(3)),list(range(3,M.nrows())))
    Af=certified_floor(A);Cf=certified_floor(C);Qf=certified_floor(M)
    bfloat=float(np.linalg.norm(midmatrix(B),2))
    bf=sum((B[i,j]**2 for i in range(B.nrows()) for j in range(B.ncols())),arb(0)).sqrt().abs_upper()
    simple=None
    if Af['certified_lower_bound'] is not None and Cf['positive_lower_bound']:
        simple=arb(Af['certified_lower_bound'])-bf**2/arb(Cf['certified_lower_bound'])
    S=A-B*C.solve(B.transpose())
    Sf=certified_floor(S)
    return {'degrees':degrees,'visible_degrees':degrees[:3],
            'A':Af,'C_finite':Cf,'B_operator_norm_numeric':bfloat,'B_frobenius_upper_bound':enclosure(bf),
            'simple_sufficient_margin_using_Frobenius':None if simple is None else enclosure(simple),
            'finite_Schur':Sf,'full_finite_matrix':Qf,
            'largest_entry_radius':enclosure(max((M[i,j].rad() for i in range(M.nrows()) for j in range(M.ncols())),key=float)),
            'infinite_complement_certified':False}

def first_negative_degrees(variants):
    out={}
    for name,Q in variants.items():
        if name=='bounce_11/20':continue
        row={}
        for parity in [0,1]:
            first=None;checked=[]
            for maximum in range(parity,Q.nrows(),2):
                deg=list(range(parity,maximum+1,2));M=sub(Q,deg,deg)
                vals,V=np.linalg.eigh(midmatrix(M))
                if vals[0]<0:
                    v=arb_mat([[arb(float(x))] for x in V[:,0]])
                    score=(v.transpose()*M*v)[0,0]/(v.transpose()*v)[0,0]
                    if score<0:
                        first={'maximum_degree':maximum,'Rayleigh_enclosure':enclosure(score),
                               'Legendre_degrees':deg,'exact_binary64_vector':[float(x) for x in V[:,0]]}
                        break
                passed,_=ldl_positive(M)
                checked.append({'maximum_degree':maximum,'positive_definite_certified':passed})
            row['even' if parity==0 else 'odd']={'first_negative_finite_degree':first,
                    'earlier_compressions':checked,'full_infinite_form_claim':False}
        out[name]=row
    return out

def tail_bound_attempt(L_string,N=48,T=160):
    L=arb(L_string);Tarb=arb(T)
    shifts=[2] if L_string=='2/5' else [2,3,4]
    B=sum((2*arb(2 if n==4 else n).log()/arb(n).sqrt() for n in shifts),arb(0))
    # Complex digamma is required for a(T).
    from flint import acb
    a0=(arb(1)/4).digamma()-arb.pi().log()
    aT=acb(arb(1)/4,Tarb/2).digamma().real-arb.pi().log()
    beta=aT-B; M=max((aT-a0).abs_upper(),(2*B).abs_upper())
    # Exact Bessel envelope; use all degrees >=N (a parity-specific sum is smaller).
    # h_n^2 = L(2n+1)/pi (LT)^(2n)/((2n+1)!!)^2.
    x=L*Tarb;df=math.prod(range(1,2*N+2,2))
    h2=L*(2*N+1)/arb.pi()*x**(2*N)/(arb(df)**2)
    r=x*x/((2*N+1)*(2*N+3))
    geometric_valid=bool(r<1)
    # When the initial ratio >=1, sum finitely until a decreasing geometric tail applies.
    hsum=arb(0);hn=h2;n=N
    while True:
        hsum+=hn
        ratio=x*x/((2*n+1)*(2*n+3))
        if ratio<arb(1)/2:
            hsum+=hn*ratio/(1-ratio);break
        hn*=ratio;n+=1
        if n>2000: raise RuntimeError('tail envelope did not contract')
    trace_bound=2*Tarb*hsum
    # Restriction of Fourier transform is a contraction, so replacing trace bound by1
    # yields a valid, sometimes sharper operator norm bound.
    restriction_bound=min(trace_bound.abs_upper(),arb(1))
    y=L/2;pdf=math.prod(range(1,2*N+2,2))
    pn2=2*L*(2*N+1)*(2*y).exp()*y**(2*N)/(arb(pdf)**2)
    pratio=y*y/((2*N+1)*(2*N+3))
    pole_tail2=pn2/(1-pratio)
    complement=beta-M*restriction_bound-2*pole_tail2
    return {'N_first_omitted_degree':N,'frequency_cutoff':T,'beta':enclosure(beta),
            'symbol_absolute_bound_M':enclosure(M),'Fourier_tail_HS_squared_bound':enclosure(trace_bound),
            'initial_geometric_ratio_below_one':geometric_valid,'pole_tail_norm_squared_bound':enclosure(pole_tail2),
            'all_function_complement_lower_bound':enclosure(complement),
            'positive_gap_certified':bool(complement>0),
            'claim':'Valid analytic lower bound for compression of R_T to all Legendre degrees >=N; W>=R_T. Not a full-space certificate.'}

def polynomial_controls(L_string,P,variants):
    L=arb(L_string);a=arb(2).log()
    # Coefficients in physical x, then convert via exact monomial moments against Legendre.
    raw=[['even_constant',[arb(1)]],['odd_linear',[arb(0),arb(1)]],
         ['even_quadratic',[-a*a/4,arb(0),arb(1)]],
         ['odd_cubic',[arb(0),-a*a/4,arb(0),arb(1)]]]
    out=[]
    for name,coef in raw:
        vec=[]
        for n in range(len(coef)):
            val=arb(0)
            for j,c in enumerate(coef):
                for k,q in enumerate(P[n].coeffs()):
                    if (j+k)%2==0:val+=c*L**(j+1)*arb(q)*2/(j+k+1)
            vec.append(val*((2*n+1)/(2*L)).sqrt())
        norm=sum((v*v for v in vec),arb(0))
        scores={}
        for key,M in variants.items():
            v=arb_mat([[x] for x in vec])
            scores[key]=enclosure((v.transpose()*sub(M,list(range(len(vec))),list(range(len(vec))))*v)[0,0]/norm)
        out.append({'name':name,'normalized_scores':scores})
    return out

def main():
    ctx.dps=DPS
    started=time.monotonic();N=MAX_DEGREE+1
    P,C=correlation_polys(N);print('Exact correlation polynomials ready',time.monotonic()-started,flush=True)
    q=kernel_series(MOMENT_TERMS)
    output={'profile':'pentora.research.weil-schur.v1','no_zero_inputs':True,
            'product_authority':'none','precision_decimal_digits':DPS,
            'plan_sha256':hashlib.sha256((HERE/'PLAN.md').read_bytes()).hexdigest(),
            'matrix_definition':'Complete authentic W; controls alter prime weights only',
            'finite_ball_arithmetic':True,'infinite_complement_certified':False,'cases':{}}
    numeric={}
    for Ls in ['2/5','7/10']:
        arch,pole,primes,variants,mstat,mom=matrices(Ls,P,C,q)
        case={'moments':mstat,'variants':{},'nodal_controls':polynomial_controls(Ls,P,variants),
              'first_negative_finite_degrees':first_negative_degrees(variants),
              'all_function_tail_attempt':tail_bound_attempt(Ls)}
        numeric['arch_'+Ls.replace('/','_')]=midmatrix(arch)
        for key,Q in variants.items():
            if key=='bounce_11/20':
                case['variants'][key]={'same_as':'bounce_9/20','reason':'cosh symmetry, ball overlap checked'};continue
            rows=[]
            for parity in [0,1]:
                for cutoff in [11,19,31,47]:
                    deg=list(range(parity,cutoff+1,2));M=sub(Q,deg,deg)
                    row=finite_summary(M,deg);row['parity']='even' if parity==0 else 'odd';row['maximum_degree']=cutoff
                    rows.append(row)
            case['variants'][key]=rows
            numeric[Ls.replace('/','_')+'_'+key.replace('/','_')]=midmatrix(Q)
        output['cases'][Ls]=case
        (HERE/'results.json').write_text(json.dumps(output,indent=2)+'\n')
        print('Completed L',Ls,'seconds',time.monotonic()-started,flush=True)
    np.savez_compressed(HERE/'finite_matrices.npz',**numeric)
    output['elapsed_seconds']=time.monotonic()-started
    (HERE/'results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'elapsed_seconds':output['elapsed_seconds'],'output':'results.json'}),flush=True)


if __name__=='__main__':main()
