"""Midpoint spectral diagnostics only; certified signs live in ball output."""
import json
from pathlib import Path
import mpmath as m


def midpoint(s):
    return m.mpf(s.strip('[]').split(' +/- ')[0])


def run():
    m.mp.dps=100
    root=Path(__file__).parent
    data=json.loads((root/'parity_tail_results.json').read_text())
    output=[]
    for row in data['rows']:
        for N in (16,24,32):
            for p,name in [(0,'even'),(1,'odd')]:
                ids=list(range(p,N,2))
                w=m.matrix([[midpoint(row['entries'][i][j]) for j in ids] for i in ids])
                ev,vec=m.eigsy(w)
                interval=row['restrictions'][str(N)][name]
                lower=next((k for k,v in interval.get('lower_bound_tests',{}).items() if v.get('positive')),None)
                out=dict(model=row['model'],N=N,sector=name,
                         midpoint_minimum=m.nstr(ev[0],40),
                         midpoint_eigen_residual=m.nstr(m.norm(w*vec[:,0]-ev[0]*vec[:,0]),10),
                         interval_positive=interval.get('positive'),
                         certified_lower_power=lower)
                output.append(out)
                print(json.dumps(out),flush=True)
    (root/'parity_diagnostics.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':
    run()
