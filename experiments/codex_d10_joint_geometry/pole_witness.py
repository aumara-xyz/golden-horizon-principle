"""Exact full-W pole mutations on already frozen D9 waves; no new quadrature."""
import hashlib
import json
from pathlib import Path
from flint import arb, ctx

ctx.prec = 320
HERE = Path(__file__).resolve().parent
D9 = HERE.parent / 'codex_d9_exact_scores'


def endpoints(lo, hi):
    return {'lower_enclosure': arb(lo.lower()).str(85),
            'upper_enclosure': arb(hi.upper()).str(85)}


def verdict(lo, hi):
    if not lo.is_finite() or not hi.is_finite():
        return 'UNVERIFIED'
    return 'POSITIVE' if lo > 0 else 'NEGATIVE' if hi < 0 else 'UNVERIFIED'


def main():
    assert verdict(arb(-1), arb(1)) == 'UNVERIFIED'
    assert verdict(arb(1), arb(2)) == 'POSITIVE'
    assert verdict(arb(-2), arb(-1)) == 'NEGATIVE'
    out = {'scope': 'Fixed D9 waves, FULL W with its already certified entire frequency tail',
           'sign_controls_passed': 3, 'rows': []}
    for parity, k0 in [('even', 2), ('odd', -2)]:
        path = D9 / ('scores_' + parity + '.json')
        data = json.loads(path.read_text())
        comp = data['trials'][-1]['component_endpoints']
        lo = arb(comp['W']['lower_enclosure'])
        hi = arb(comp['W']['upper_enclosure'])
        plo = arb(comp['pole']['lower_enclosure']) / k0
        phi = arb(comp['pole']['upper_enclosure']) / k0
        # Reverse endpoints when dividing by the negative odd coefficient.
        if k0 < 0:
            plo, phi = phi, plo
        assert plo > 0 and phi > 0
        for delta in ['-1e-2', '-1e-4', '0', '1e-4', '1e-2']:
            dd = arb(delta)
            dl, du = (dd * plo, dd * phi) if dd >= 0 else (dd * phi, dd * plo)
            ll, uu = lo + dl, hi + du
            ep = endpoints(ll, uu)
            vv = verdict(ll, uu)
            # Reparse all endpoint balls; never strip a radius to obtain sign.
            assert verdict(arb(ep['lower_enclosure']), arb(ep['upper_enclosure'])) == vv
            out['rows'].append(dict(parity=parity, kappa_authentic=k0,
                                   delta_kappa=delta, score=ep, sign=vv))
        out[parity + '_source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (HERE / 'pole_witness_results.json').write_text(json.dumps(out, indent=2) + '\n')
    for r in out['rows']:
        print(r['parity'], r['delta_kappa'], r['sign'],
              arb(r['score']['lower_enclosure']).str(12),
              arb(r['score']['upper_enclosure']).str(12))


if __name__ == '__main__':
    main()
