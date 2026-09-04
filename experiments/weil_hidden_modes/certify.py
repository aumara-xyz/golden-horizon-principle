"""Ball-enclosed finite Weil form. See CERTIFICATE.md for cutoff bound."""
import json
from pathlib import Path
from flint import arb, acb, ctx
import flint


def corr(i, j, u, L):
    # Analytic continuation of the positive-shift formula, not piecewise support.
    if (i+j) % 2:
        return u*0
    a, b, length = i*arb.pi()/(2*L), j*arb.pi()/(2*L), 2*L-u
    def directed(a,b,equal):
        first = length*(a*u).cos() if equal else (
            ((a-b)*length+a*u).sin()-(a*u).sin())/(a-b)
        second = (((a+b)*length+a*u).sin()-(a*u).sin())/(a+b)
        return (first-second)/(2*L)
    return (directed(a,b,i==j)+directed(b,a,i==j))/2


def pole(i,c,L):
    a = i*arb.pi()/(2*L)
    return (-c*L).exp()/L.sqrt()*a*(1-(-1)**i*(2*c*L).exp())/(a*a+c*c)


def archimedean(L,N,eps):
    w = [[arb(0) for j in range(N)] for i in range(N)]
    cutoff = eps*(N*arb.pi()/(2*L)+(eps/2).exp()/2)
    for i in range(1,N+1):
        for j in range(i,N+1):
            if (i+j) % 2:
                continue
            d = int(i==j)
            def integrand(u,analytic):
                # Meromorphic expression: poles produce nonfinite balls.
                return (d-(u/2).exp()*corr(i,j,u,L))/u.sinh()
            integral = acb.integral(integrand,acb(eps),acb(2*L),
                                    abs_tol=arb('1e-35'),rel_tol=arb('1e-35'),
                                    eval_limit=100000,depth_limit=300)
            if not integral.is_finite() or not integral.imag.contains(0):
                raise ArithmeticError('unresolved integral')
            v = pole(i,arb('1/2'),L)*pole(j,arb('-1/2'),L)
            v += pole(j,arb('1/2'),L)*pole(i,arb('-1/2'),L)
            v -= (arb.const_euler()+(4*arb.pi()).log()+L.tanh().log())*d
            v += integral.real+arb(0,cutoff.abs_upper())
            w[i-1][j-1] = w[j-1][i-1] = v
        print('integrated row',i,flush=True)
    return w,cutoff


def prime_terms(L,shift):
    if shift is None:
        return []
    # For L=.7 and shifts .9,1,1.1, exp(2L/shift)<5.
    assert (2*L/shift).exp() < 5
    out=[]
    for p in [2,3]:
        for k in range(1,4):
            u = k*arb(p).log()*shift
            if u < 2*L:
                out.append((u,2*arb(p).log()/(arb(p)**k).sqrt()))
            else:
                assert u > 2*L
        assert 4*arb(p).log()*shift > 2*L
    return out


def ldl(w,lower='0'):
    n=len(w)
    a=[[w[i][j]-(arb(lower) if i==j else 0) for j in range(n)] for i in range(n)]
    pivots=[]
    for k in range(n):
        pivot=a[k][k]
        pivots.append(pivot)
        if pivot.contains(0):
            return dict(status='UNVERIFIED',pivots=[str(v) for v in pivots])
        for i in range(k+1,n):
            for j in range(i,n):
                a[i][j] -= a[i][k]*a[j][k]/pivot
                a[j][i] = a[i][j]
    return dict(status='MEASURED',positive=all(v>0 for v in pivots),
                negative_direction=any(v<0 for v in pivots),
                pivots=[v.str(40) for v in pivots])


def run():
    ctx.prec=384
    L,N,eps=arb('7/10'),16,arb('1e-40')
    arch,cutoff=archimedean(L,N,eps)
    rows=[]
    for name,shift in [('arch_only',None),('shift_plus',arb('11/10')),
                       ('shift_minus',arb('9/10')),('authentic',arb(1))]:
        w=[row.copy() for row in arch]
        for u,weight in prime_terms(L,shift):
            for i in range(1,N+1):
                for j in range(i,N+1):
                    w[i-1][j-1] -= weight*corr(i,j,u,L)
                    w[j-1][i-1] = w[i-1][j-1]
        row=dict(model=name,restrictions={str(n):ldl([r[:n] for r in w[:n]]) for n in (8,12,16)},
                 entries=[[v.str(45) for v in r] for r in w],
                 max_entry_radius=str(max(v.rad() for r in w for v in r)))
        if name=='authentic':
            row['lower_bound_1e_minus_12']=ldl(w,'1e-12')
        rows.append(row)
        print(name,{n:r['status']+':'+str(r.get('positive')) for n,r in row['restrictions'].items()},flush=True)
    result=dict(python_flint=flint.__version__,precision_bits=ctx.prec,
                cutoff_bound=str(cutoff),rows=rows)
    Path(__file__).with_name('certified_results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    run()
