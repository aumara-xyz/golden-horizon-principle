#!/usr/bin/env python3
"""Finite Cayley/Caratheodory test from arithmetic continuation, no zeros.

Only Python standard-library arithmetic constructs the coefficient enclosures.
NumPy eigenvalues are supplementary floating diagnostics, never certificates.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN, getcontext
from fractions import Fraction as F
from math import comb, factorial, prod, isqrt
from pathlib import Path
import hashlib
import json
import time
import numpy as np

HERE=Path(__file__).resolve().parent
PREC=220
getcontext().prec=PREC
LO=Context(prec=PREC,rounding=ROUND_FLOOR)
HI=Context(prec=PREC,rounding=ROUND_CEILING)
NEAR=Context(prec=PREC,rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class I:
    lo:D
    hi:D
    def __add__(self,o):
        o=iv(o);return I(LO.add(self.lo,o.lo),HI.add(self.hi,o.hi))
    __radd__=__add__
    def __neg__(self):return I(self.hi.copy_negate(),self.lo.copy_negate())
    def __sub__(self,o):return self+-iv(o)
    def __rsub__(self,o):return iv(o)+-self
    def __mul__(self,o):
        o=iv(o)
        pairs=[(self.lo,o.lo),(self.lo,o.hi),(self.hi,o.lo),(self.hi,o.hi)]
        return I(min(LO.multiply(x,y) for x,y in pairs),max(HI.multiply(x,y) for x,y in pairs))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=iv(o)
        if o.lo<=0<=o.hi:raise ZeroDivisionError('interval divisor contains zero')
        return self*I(LO.divide(D(1),o.hi),HI.divide(D(1),o.lo))
    def __rtruediv__(self,o):return iv(o)/self
    def __pow__(self,n):
        assert n>=0
        a=iv(1);b=self
        while n:
            if n&1:a=a*b
            b=b*b;n//=2
        return a
    def ln(self):
        assert self.lo>0
        # Decimal ln is correctly nearest-rounded. One adjacent number on
        # either side therefore encloses each exact endpoint logarithm.
        return I(LO.next_minus(NEAR.ln(self.lo)),HI.next_plus(NEAR.ln(self.hi)))
    def mid(self):return NEAR.divide(NEAR.add(self.lo,self.hi),D(2))
    def width(self):return HI.subtract(self.hi,self.lo)
    def record(self):return {'lo':str(self.lo),'hi':str(self.hi),'width':str(self.width())}


def iv(x):
    if isinstance(x,I):return x
    if isinstance(x,F):return I(LO.divide(D(x.numerator),D(x.denominator)),HI.divide(D(x.numerator),D(x.denominator)))
    d=D(x);return I(d,d)


def bernoulli(m):
    # Exact recurrence. Convention B1=-1/2; only even indices enter EM.
    b=[F(1)]
    for n in range(1,m+1):b.append(-sum(F(comb(n+1,k))*b[k] for k in range(n))/F(n+1))
    return b


def arctan_fraction(q,n):
    s=sum((F((-1)**k,(2*k+1)*q**(2*k+1)) for k in range(n)),F(0))
    nxt=F((-1)**n,(2*n+1)*q**(2*n+1))
    return iv(s)+I(min(D(0),iv(nxt).lo),max(D(0),iv(nxt).hi))


def pi_interval():return 16*arctan_fraction(5,170)-4*arctan_fraction(239,55)


def em_bound_half_disk(N,K):
    # |s-1|<=1/2; |(s)_(2K)|<=prod(j+1/2,j=1..2K).
    # zeta(2K)<=1+1/(2K-1); 2*pi>6; sqrt(N)<=ceil(sqrt(N)).
    rt=isqrt(N)+(isqrt(N)**2!=N)
    return (F(2)*(1+F(1,2*K-1))*prod(F(2*j+1,2) for j in range(1,2*K+1))
            *F(rt,N**(2*K))/(F(6)**(2*K)*F(4*K-1,2)))


def em_bound_integer(s,N,K):
    return (F(2)*(1+F(1,2*K-1))*prod(range(s,s+2*K))
            / (F(6)**(2*K)*N**(s+2*K-1)*(s+2*K-1)))


def multiply(a,b,m):
    out=[iv(0) for _ in range(m+1)]
    for i,x in enumerate(a[:m+1]):
        if x.lo==x.hi==0:continue
        for j,y in enumerate(b[:m+1-i]):
            if y.lo==y.hi==0:continue
            out[i+j]=out[i+j]+x*y
    return out


def exp_jet(x,m):
    c=[iv(1)]
    for k in range(1,m+1):c.append(c[-1]*x/k)
    return c


def divide_series(num,den,m):
    out=[]
    for n in range(m+1):
        v=num[n] if n<len(num) else iv(0)
        for k in range(1,min(n,len(den)-1)+1):v=v-den[k]*out[n-k]
        out.append(v/den[0])
    return out


def zeta_integer(s,N,K,B):
    # Rational EM main expression; interval remainder is analytic.
    value=sum((F(1,n**s) for n in range(1,N)),F(0))
    value+=F(1,(s-1)*N**(s-1))+F(1,2*N**s)
    rising=1
    for j in range(1,2*K):
        rising*=s+j-1
        if j%2:
            k=(j+1)//2
            value+=B[2*k]*F(rising,factorial(2*k)*N**(s+2*k-1))
    r=iv(em_bound_integer(s,N,K))
    return iv(value)+I(-r.hi,r.hi)


def regularized_zeta_jet(m,N,K,B):
    eN=exp_jet(-iv(N).ln(),m)
    rest=[iv(0) for _ in range(m)]
    for n in range(1,N):
        ee=exp_jet(-iv(n).ln(),m-1)
        for k in range(m):rest[k]=rest[k]+ee[k]/n
    for k in range(m):rest[k]=rest[k]+eN[k]/(2*N)
    rising=[iv(1)]
    for j in range(1,2*K):
        rising=multiply(rising,[iv(j),iv(1)],min(j,m-1))
        if j%2:
            k=(j+1)//2
            fact=iv(B[2*k]/F(factorial(2*k)*N**(2*k)))
            product=multiply(rising,eN,m-1)
            for r in range(m):rest[r]=rest[r]+fact*product[r]
    out=[iv(1)]+[eN[j]+rest[j-1] for j in range(1,m+1)]
    # G(h)=h*zeta(1+h). Cauchy on |h|=1/2 gives coefficient
    # remainder <= (R_zeta/2)*2^j. Its constant term is identically zero.
    bound=em_bound_half_disk(N,K)
    for j in range(1,m+1):
        error=iv(bound*F(2)**(j-1))
        out[j]=out[j]+I(-error.hi,error.hi)
    return out,bound


def cayley_coefficients(M,N,K):
    B=bernoulli(2*K)
    G,bound=regularized_zeta_jet(M+1,N,K,B)
    gamma=G[1]
    lnpi=pi_interval().ln()
    logG=divide_series([(k+1)*G[k+1] for k in range(M+1)],G,M)
    q=[]
    q.append(iv(1)-lnpi/2-gamma/2-iv(2).ln()+logG[0])
    for k in range(1,M+1):
        gam=((-1)**(k+1))*iv(1-F(1,2**(k+1)))*zeta_integer(k+1,N,K,B)
        q.append(iv((-1)**k)+gam+logG[k])
    a=[q[0]]
    for n in range(1,M+1):a.append(sum((comb(n-1,k-1)*q[k] for k in range(1,n+1)),iv(0)))
    closed=iv(1)+gamma/2-iv(2).ln()-lnpi/2
    return a,{'N':N,'K':K,'precision':PREC,'degree':M,
              'zeta_half_disk_remainder_upper':str(iv(bound).hi),
              'a0_closed_form_overlap':max(a[0].lo,closed.lo)<=min(a[0].hi,closed.hi),
              'max_coefficient_interval_width':str(max(z.width() for z in a))}


def toeplitz_ldl(a,N):
    moments=[a[0]]+[z/2 for z in a[1:N]]
    A=[[moments[abs(i-j)] for j in range(N)] for i in range(N)]
    L=[[iv(0) for j in range(N)] for i in range(N)]
    pivots=[];status='positive_definite_certified'
    for j in range(N):
        d=A[j][j]-sum((L[j][k]*L[j][k]*pivots[k] for k in range(j)),iv(0))
        pivots.append(d);L[j][j]=iv(1)
        if d.lo<=0:
            status='indefinite_certified' if d.hi<0 else 'unresolved'
            break
        for i in range(j+1,N):
            L[i][j]=(A[i][j]-sum((L[i][k]*L[j][k]*pivots[k] for k in range(j)),iv(0)))/d
    arr=np.array([[float(x.mid()) for x in row] for row in A])
    eig=np.linalg.eigvalsh(arr)
    return {'dimension':N,'status':status,'resolved_positive_pivots':sum(z.lo>0 for z in pivots),
            'pivots':[z.record() for z in pivots],
            'float64_min_eigenvalue_not_certificate':float(eig[0]),
            'float64_max_eigenvalue':float(eig[-1])}


def schur_parameters(a,count):
    # S=(H-a0)/(H+a0), so S(0)=0 identically.
    num=[iv(0)]+a[1:]
    den=[2*a[0]]+a[1:]
    f=divide_series(num,den,len(a)-1)
    rows=[]
    for k in range(count):
        alpha=f[0]
        inside=alpha.lo>-1 and alpha.hi<1
        rows.append({'index':k,'alpha':alpha.record(),'strictly_inside_unit_disk_certified':inside})
        if not inside:break
        if len(f)<=1:break
        # f_next=(f-alpha)/(w*(1-alpha*f)). The numerator's constant
        # vanishes identically, so divide its shifted coefficients.
        denominator=[iv(1)-alpha*f[0]]+[-alpha*x for x in f[1:]]
        f=divide_series(f[1:],denominator,len(f)-2)
    return rows


def ratmul(a,b,M):
    out=[F(0)]*(M+1)
    for i,x in enumerate(a[:M+1]):
        for j,y in enumerate(b[:M+1-i]):out[i+j]+=x*y
    return out


def rational_control(delta,M):
    A=[F(5,4)-delta**2,F(1),F(1)]
    P=ratmul(A,A,4);P[0]+=4*delta**2
    dP=[(j+1)*P[j+1] for j in range(4)]
    q=[]
    for n in range(M+1):
        v=dP[n] if n<len(dP) else F(0)
        v-=sum((P[k]*q[n-k] for k in range(1,min(n,4)+1)),F(0))
        q.append(v/P[0])
    a=[q[0]]+[sum((F(comb(n-1,k-1))*q[k] for k in range(1,n+1)),F(0)) for n in range(1,M+1)]
    return a


def exact_ldl_control(a,N):
    c=[a[0]]+[x/2 for x in a[1:N]]
    L=[[F(0)]*N for _ in range(N)];ds=[]
    for j in range(N):
        d=c[0]-sum((L[j][k]**2*ds[k] for k in range(j)),F(0));ds.append(d)
        if d<=0:
            out={'dimension':N,'first_nonpositive_pivot_index':j,'pivot':str(d),
                 'status':'indefinite_exact' if d<0 else 'zero_pivot_exact'}
            if d<0:
                witness=[F(0)]*(j+1);witness[j]=1
                for i in range(j-1,-1,-1):
                    witness[i]=-sum((L[k][i]*witness[k] for k in range(i+1,j+1)),F(0))
                score=sum((witness[i]*c[abs(i-k)]*witness[k]
                           for i in range(j+1) for k in range(j+1)),F(0))
                assert score==d
                out['leading_block_negative_vector']=[str(x) for x in witness]
                out['exact_quadratic_score']=str(score)
            return out
        L[j][j]=1
        for i in range(j+1,N):L[i][j]=(c[i-j]-sum((L[i][k]*L[j][k]*ds[k] for k in range(j)),F(0)))/d
    return {'dimension':N,'status':'positive_definite_exact','last_pivot':str(ds[-1])}


def mobius(x,n):return ((n-1)+(n+1)*x)/((n+1)+(n-1)*x)


def main():
    start=time.monotonic()
    M=24
    primary,meta=cayley_coefficients(M,256,48)
    smaller,meta2=cayley_coefficients(M,128,40)
    overlap=all(max(x.lo,y.lo)<=min(x.hi,y.hi) for x,y in zip(primary,smaller))
    tests=[toeplitz_ldl(primary,n) for n in [2,4,6,8,10,12,14,16]]
    schur=schur_parameters(primary,16)
    controls={}
    for delta in [F(0),F(1,5)]:
        aa=rational_control(delta,M)
        controls[str(delta)]={'coefficients':[str(x) for x in aa],
            'sections':[exact_ldl_control(aa,n) for n in range(1,17)]}
    for x in [F(-2,7),F(0),F(2,7)]:
        for n,m in [(2,3),(3,5),(4,7),(11,13)]:
            assert mobius(mobius(x,n),m)==mobius(x,n*m)
            assert -mobius(-x,n)==mobius(x,F(1,n))
    result={'profile':'pentora.research.cayley-finite.v1','authority':'none',
        'plan_sha256':hashlib.sha256((HERE/'PLAN.md').read_bytes()).hexdigest(),
        'definition':'H(w)=(xi_prime/xi)(1/(1-w)); c0=a0, cn=an/2',
        'construction':'Arithmetic Euler-Maclaurin continuation of regularized zeta plus Gamma Taylor expansion; no zeros',
        'not_literal_prime_product':True,'no_zero_ordinates':True,
        'primary':meta,'secondary':meta2,'coefficient_enclosures_overlap':overlap,
        'coefficients':[x.record() for x in primary],
        'toeplitz_sections':tests,'schur_parameters':schur,'polynomial_controls':controls,
        'on_line_control_measure':'delta=0: c_n=(8/5)Re((3/5+4i/5)^n); positive two-atom measure; rank2 for N>=2',
        'mobius_exact_cases':12,'RH_proof':False,'seconds':time.monotonic()-start}
    (HERE/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'primary':meta,'secondary':meta2,'overlap':overlap,
        'a0':str(primary[0].mid()),'sections':[{k:v for k,v in x.items() if k!='pivots'} for x in tests],
        'bad_control_first_nonpositive':next(x for x in controls['1/5']['sections'] if x['status']!='positive_definite_exact'),
        'seconds':result['seconds']},indent=2))


if __name__=='__main__':main()
