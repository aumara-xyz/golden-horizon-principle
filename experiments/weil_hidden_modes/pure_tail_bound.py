"""Evaluate the explicit infinite pure-tail inequality; not a full certificate."""
import json
from pathlib import Path
from flint import arb, acb, ctx
from certify import prime_terms


def run():
    ctx.prec=384
    L,R=arb('7/10'),arb(256)
    pi=arb.pi()
    a0=-arb.const_euler()-pi/2-3*arb(2).log()-pi.log()
    aR=acb(arb('1/4'),R/2).digamma().real-pi.log()
    odd_penalty=2*(L.sinh()-L)
    rows=[]
    for model,shift in [('arch_only',None),('shift_plus',arb('11/10')),
                        ('shift_minus',arb('9/10')),('authentic',arb(1))]:
        mass=sum((weight for u,weight in prime_terms(L,shift)),arb(0))
        for N in (4096,8192):
            omega=(N+1)*pi/(2*L)
            assert R<omega
            eta=16*L*R/(pi**3*N*(1-(R/omega)**2)**2)
            assert eta<1
            even=aR-(aR-a0)*eta-mass
            odd=even-odd_penalty
            row=dict(model=model,N=N,R=256,L='7/10',
                     eta=eta.str(40),mass=mass.str(40),
                     even_lower=even.str(40),odd_lower=odd.str(40),
                     even_gt_half=even>arb('1/2'),odd_gt_three_tenths=odd>arb('3/10'))
            rows.append(row)
            print(json.dumps(row),flush=True)
    Path(__file__).with_name('pure_tail_results.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':
    run()
