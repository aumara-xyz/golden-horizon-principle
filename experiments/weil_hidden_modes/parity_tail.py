"""Preregistered finite parity-sector audit, no infinite-tail inference."""
import json
from pathlib import Path
from flint import arb, ctx
import flint
from certify import archimedean, corr, prime_terms, ldl


def sector(w,N,parity):
    ids=range(parity,N,2)  # zero-index even is spatially even
    return [[w[i][j] for j in ids] for i in ids]


def run():
    ctx.prec=512
    L,N,eps=arb('7/10'),32,arb('1e-65')
    arch,cutoff=archimedean(L,N,eps,tolerance='1e-55')
    rows=[]
    previous=json.loads(Path(__file__).with_name('certified_results.json').read_text())
    for name,shift in [('arch_only',None),('shift_plus',arb('11/10')),
                       ('shift_minus',arb('9/10')),('authentic',arb(1))]:
        w=[r.copy() for r in arch]
        for u,weight in prime_terms(L,shift):
            for i in range(1,N+1):
                for j in range(i,N+1):
                    w[i-1][j-1] -= weight*corr(i,j,u,L)
                    w[j-1][i-1] = w[i-1][j-1]
        old=next(r for r in previous['rows'] if r['model']==name)
        overlap=all(w[i][j].overlaps(arb(old['entries'][i][j])) for i in range(16) for j in range(16))
        assert overlap
        assert all(w[i][j].is_zero() for i in range(N) for j in range(N) if (i+j)%2)
        checks={}
        for n in (16,24,32):
            checks[str(n)]={}
            for parity,label in [(0,'even'),(1,'odd')]:
                block=sector(w,n,parity)
                result=ldl(block)
                if name=='authentic':
                    result['lower_bound_tests']={str(k):ldl(block,'1e-'+str(k)) for k in (8,12,16,20,24,28,32,36,40)}
                checks[str(n)][label]=result
        row=dict(model=name,restrictions=checks,previous_N16_overlap=overlap,
                 cross_parity_exact_zero=True,entries=[[v.str(90) for v in r] for r in w],
                 max_entry_radius=str(max(v.rad() for r in w for v in r)))
        rows.append(row)
        print(name,{n:{p:(v['status'],v.get('positive')) for p,v in r.items()} for n,r in checks.items()},flush=True)
    result=dict(python_flint=flint.__version__,precision_bits=ctx.prec,N=N,L='7/10',
                epsilon='1e-65',cutoff_bound=str(cutoff),rows=rows)
    Path(__file__).with_name('parity_tail_results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    run()
