#!/usr/bin/env python3
"""Independent exact-rational check of exported scalar certificate endpoints.

This verifies the final scalar implication, not the construction of the matrix
or analytic remainder. Those are handled by the accompanying Arb computation.
"""
from fractions import Fraction as F
from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent

def endpoints(s):
    s=s.strip()
    if s.startswith('['):
        m=re.fullmatch(r'\[\s*([^ ]+)\s*\+/-\s*([^ ]+)\s*\]',s)
        if not m:raise ValueError('unsupported or non-finite enclosure')
        mid,rad=map(F,m.groups());assert rad>=0
        return mid-rad,mid+rad
    return F(s),F(s)

def main():
    d=json.loads((HERE/'small_window_certificate.json').read_text());out={}
    gap_lo,_=endpoints(d['complement_gap_lower']);_,c_hi=endpoints(d['coupling_upper'])
    for parity,row in d['parities'].items():
        a_lo,_=endpoints(row['finite_R_floor']['certified_lower_bound'])
        cert=row['simplified_rational_certificate']
        a,g,c,mu=map(F,[cert['finite_block_lower'],cert['complement_lower'],cert['coupling_upper'],cert['target_mu']])
        assert a_lo>a and gap_lo>g and c_hi<c
        det=(a-mu)*(g-mu)-c*c
        assert a>mu and g>mu and det>0 and det==F(cert['shifted_determinant'])
        out[parity]={'target_mu':str(mu),'determinant_exact':str(det),'PASS':True}
    (HERE/'scalar_certificate_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
