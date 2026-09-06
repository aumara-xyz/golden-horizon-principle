"""Reparse endpoints and directly replay saved negative finite witnesses."""
import hashlib
import json
from pathlib import Path
from flint import arb, ctx

ctx.prec = 384
HERE = Path(__file__).resolve().parent


def scalar(ep):
    lo, hi = arb(ep['lower_enclosure']), arb(ep['upper_enclosure'])
    assert lo.is_finite() and hi.is_finite()
    assert lo.lower() <= hi.upper()
    return lo, hi


def main():
    verified = {'scope': 'Independent endpoint reparse and direct scalar finite-witness replay, same Arb stack',
                'scalar_endpoint_records': 0, 'negative_finite_witnesses': 0, 'authentic_schur_certificates': 0}
    for par in ('even', 'odd'):
        ipath = HERE / ('input_' + par + '.json')
        raw = ipath.read_bytes()
        data = json.loads(raw)
        results = json.loads((HERE / ('schur_' + par + '.json')).read_text())
        assert results['input_sha256'] == hashlib.sha256(raw).hexdigest()
        for row in results['rows']:
            for container in (row, row['full'], row['complement']):
                for value in container.values():
                    if isinstance(value, dict) and 'lower_enclosure' in value:
                        scalar(value)
                        verified['scalar_endpoint_records'] += 1
            if row.get('finite_positive_by_schur'):
                assert scalar(row['sigma'])[0] > 0
                assert scalar(row['complement']['lambda_min'])[0] > 0
            if row['label'] == 'authentic':
                assert row['finite_positive_by_schur']
                verified['authentic_schur_certificates'] += 1
                if row['N'] == 80:
                    assert scalar(row['complement_to_full_gap_ratio'])[0] > 1000
                    assert scalar(row['complement']['lambda_min'])[1] < arb('1e-3')
                # Critical strength uses the SAME normalization and sign.
                sigma = arb(row['sigma']['ball'])
                nrm = arb(row['pole_norm_squared']['ball'])
                crit = arb(row['kappa_critical']['ball'])
                assert (arb(row['kappa']) - crit - sigma / nrm).contains(0)
            if row['full']['negative_finite_witness']:
                label = row['label']
                model = 'authentic' if label == 'authentic pole sign flip' else label
                n = row['N']
                p = [arb(x) for x in data['p'][:n]]
                v = [arb(x) for x in row['full']['finite_witness_coefficients']]
                # Scalar pair summation, separate from the matrix product
                # used by the generating code; no decimal eigenvalue accepted.
                hq = sum((v[i]*arb(data['models'][model][i][j])*v[j]
                          for i in range(n) for j in range(n)), arb(0))
                pv = sum((p[i]*v[i] for i in range(n)), arb(0))
                nn = sum((x*x for x in v), arb(0))
                score = (hq + arb(row['kappa'])*pv*pv)/nn
                assert score < 0
                assert score.overlaps(arb(row['full']['finite_rayleigh']['ball']))
                verified['negative_finite_witnesses'] += 1
    pw = json.loads((HERE / 'pole_witness_results.json').read_text())
    for row in pw['rows']:
        lo, hi = scalar(row['score'])
        sign = 'POSITIVE' if lo > 0 else 'NEGATIVE' if hi < 0 else 'UNVERIFIED'
        assert row['sign'] == sign
    verified['full_W_fixed_vector_endpoints'] = len(pw['rows'])
    (HERE / 'verification.json').write_text(json.dumps(verified, indent=2) + '\n')
    print(json.dumps(verified, indent=2))


if __name__ == '__main__':
    main()
