"""Verify exported signs and a higher-node scalar cross-check; no selection."""
import json
from score import ROOT, L, arb, compact

out={}
for name,par in [('even',0),('odd',1)]:
    frozen=json.loads((ROOT/('frozen_'+name+'.json')).read_text())
    b=[arb(0)]*(max(frozen['degrees'])+1)
    for n,c in zip(frozen['degrees'],frozen['coefficients']):
        b[n]=arb(c)*((2*n+1)/(2*L)).sqrt()
    v64=compact(b,par,2,64)
    v80=compact(b,par,2,80)
    assert v64[0].overlaps(v80[0]) and v64[1].overlaps(v80[1])
    data=json.loads((ROOT/('scores_'+name+'.json')).read_text())
    for trial in data['trials']:
        for th,ep in trial['score_endpoints'].items():
            lower=arb(ep['lower_enclosure']).lower()
            upper=arb(ep['upper_enclosure']).upper()
            verdict='POSITIVE' if lower>0 else 'NEGATIVE' if upper<0 else 'UNVERIFIED'
            assert verdict==trial['signs'][th],(name,th,verdict)
    out[name]={'all_exported_signs_reverified':True,'candidate_small_interval_64_80_overlap':True}
    print(name)
    for label,e in data['trials'][-1]['component_endpoints'].items():
        print(label,arb(e['lower_enclosure']).lower().str(12),arb(e['upper_enclosure']).upper().str(12))
(ROOT/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('VERIFIED',out)
