"""D10: rigorous finite, pole-directed Schur diagnostics; no full-W claim.

Predictions precede this script. Input matrices contain interval-enclosed H,
where R=H+kappa*p*p^T. Frozen midpoint eigenvectors are certification aids,
never accepted as eigenvalue certificates by themselves.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import mpmath as mp
from flint import arb, arb_mat, ctx

ctx.prec = 320
mp.mp.dps = 70
ROOT = Path(__file__).resolve().parent


def textball(x):
    return x.str(85)


def endpoints(x):
    assert x.is_finite(), 'Refuse non-finite exported enclosure'
    out = dict(ball=textball(x), lower_enclosure=textball(arb(x.lower())),
               upper_enclosure=textball(arb(x.upper())))
    # Reparse each complete enclosure rather than trusting a displayed decimal.
    if x > 0:
        assert arb(out['lower_enclosure']) > 0
    if x < 0:
        assert arb(out['upper_enclosure']) < 0
    return out


def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), arb(0))


def col(A, j):
    return [A[i,j] for i in range(A.nrows())]


def mv(A, x):
    return col(A * arb_mat([[v] for v in x]), 0)


def norm(x):
    # Generic interval products of a residual with itself may extend below
    # zero. Bound each magnitude first; never sqrt that spurious negative ball.
    lo = sum((arb(z.abs_lower())*arb(z.abs_lower()) for z in x),arb(0))
    hi = sum((arb(z.abs_upper())*arb(z.abs_upper()) for z in x),arb(0))
    return hull(lo.sqrt().lower(),hi.sqrt().upper())


def hull(lo, hi):
    return arb(lo).union(arb(hi))


def midpoint(A):
    return mp.matrix([[mp.mpf(A[i,j].mid().str(95, radius=False))
                       for j in range(A.ncols())] for i in range(A.nrows())])


def spectral_certificate(A):
    """Congruence/Gershgorin + Gram norm and independent Rayleigh upper."""
    n = A.nrows()
    E, Vm = mp.eigsy(midpoint(A))
    frozen_v = [[mp.nstr(Vm[i,j],75) for j in range(n)] for i in range(n)]
    V = arb_mat([[arb(z) for z in row] for row in frozen_v])
    D = V.transpose()*A*V
    G = V.transpose()*V
    gl = min((G[i,i] - sum((G[i,j].abs_upper() for j in range(n) if i != j), arb(0))).lower() for i in range(n))
    gu = max((G[i,i] + sum((G[i,j].abs_upper() for j in range(n) if i != j), arb(0))).upper() for i in range(n))
    gl, gu = arb(gl), arb(gu)
    assert gl > 0, 'Frozen congruence basis is not certified invertible'
    dl, du = [], []
    for i in range(n):
        rad = sum((arb(D[i,j].abs_upper()) for j in range(n) if i != j), arb(0))
        dl.append(arb((D[i,i]-rad).lower()))
        du.append(arb((D[i,i]+rad).upper()))
    dmin = min(dl)
    low = dmin/gu if dmin > 0 else dmin/gl
    v = col(V, 0)
    rq = dot(v, mv(A,v))/dot(v,v)
    interval = hull(low.lower(), rq.upper())
    assert interval.is_finite()
    inertia = None
    distance = None
    if all(l > 0 or u < 0 for l,u in zip(dl,du)):
        pos = sum(l > 0 for l in dl)
        neg = sum(u < 0 for u in du)
        inertia = dict(positive=pos, negative=neg, zero=0)
        distance = min(l if l > 0 else -u for l,u in zip(dl,du))/gu
        assert distance > 0
    out = dict(lambda_min=endpoints(interval), gram_lower=endpoints(gl),
               gram_upper=endpoints(gu), inertia=inertia,
               first_four_midpoint_eigenvalues=[mp.nstr(E[i],25) for i in range(min(4,n))],
               midpoint_count_below_1e_3=sum(E[i] < mp.mpf('0.001') for i in range(n)),
               finite_rayleigh=endpoints(rq),
               finite_witness_coefficients=[frozen_v[i][0] for i in range(n)] if rq < 0 else None,
               negative_finite_witness=bool(rq < 0))
    return out, interval, distance, inertia


def pole_axis(H, p):
    """An exact Householder identity fixes the geometrically chosen axis.

    q=p/||p||, v=q+e0, U=-(I-2vv^T/(v^Tv)); Ue0=q.
    U is orthogonal for every exact p represented by the input balls.
    """
    n = len(p)
    np2 = dot(p,p)
    assert np2 > 0
    q = [x/np2.sqrt() for x in p]
    v = q[:]
    v[0] += 1
    den = dot(v,v)
    assert den > 0
    U = arb_mat([[2*v[i]*v[j]/den - (1 if i==j else 0)
                  for j in range(n)] for i in range(n)])
    G = U.transpose()*U
    for i in range(n):
        assert (U[i,0]-q[i]).contains(0)
        for j in range(n):
            assert (G[i,j]-(1 if i==j else 0)).contains(0)
    J = U.transpose()*H*U
    C = arb_mat([[J[i,j] for j in range(1,n)] for i in range(1,n)])
    b = [J[i,0] for i in range(1,n)]
    return U, J[0,0], b, C, np2


def schur_case(H, p, kappa, label):
    n = len(p)
    R = arb_mat([[H[i,j]+kappa*p[i]*p[j] for j in range(n)] for i in range(n)])
    full_out, full_gap, _, _ = spectral_certificate(R)
    U,a,b,C,np2 = pole_axis(H,p)
    c_out,c_gap,distance,inertia = spectral_certificate(C)
    out = dict(label=label, N=n, kappa=str(kappa), full=full_out,
               complement=c_out, pole_norm_squared=endpoints(np2),
               axis_entry=endpoints(a), householder_identity_checks='PASS')
    if full_gap > 0 and c_gap > 0:
        out['complement_to_full_gap_ratio'] = endpoints(c_gap/full_gap)
    else:
        out['complement_to_full_gap_ratio'] = None
    if distance is None:
        out['schur_status'] = 'UNVERIFIED: complement invertibility unresolved'
        return out

    # Freeze one approximate solve, then bound the exact quadratic via its
    # residual. This does not require interval Gaussian elimination to succeed.
    bm = mp.matrix([mp.mpf(z.mid().str(95, radius=False)) for z in b])
    xm = mp.lu_solve(midpoint(C), bm)
    x = [arb(mp.nstr(z,75)) for z in xm]
    Cx = mv(C,x)
    r = [bi-ci for bi,ci in zip(b,Cx)]
    rnorm = norm(r)
    rupper = arb(rnorm.upper())
    err = rupper/distance
    correction = rupper*rupper/distance
    base = 2*dot(b,x)-dot(x,Cx)
    if inertia['negative'] == 0:
        qform = hull(base.lower(), (base+correction).upper())
    elif inertia['positive'] == 0:
        qform = hull((base-correction).lower(), base.upper())
    else:
        qform = hull((base-correction).lower(), (base+correction).upper())
    response = hull(max(arb(0), arb((norm(x)-err).lower())), (norm(x)+err).upper())
    sigma = a+kappa*np2-qform
    critical = (qform-a)/np2
    cancellation = (abs(a)+abs(kappa*np2)+abs(qform))/abs(sigma) if not sigma.contains(0) else None

    # Verify the completion algebra on a frozen exact-decimal test vector,
    # retaining residual terms instead of pretending x is the exact solve.
    t = arb('0.37')
    g = [arb((i%5)-2)/10 for i in range(n-1)]
    y = [g[i]+t*x[i] for i in range(n-1)]
    coordinate_score = dot(g,mv(C,g))+2*t*dot(g,b)+(a+kappa*np2)*t*t
    residual_identity = dot(y,mv(C,y))+(a+kappa*np2-dot(x,Cx))*t*t+2*t*dot(g,r)
    assert (coordinate_score-residual_identity).contains(0)
    physical = mv(U,[t]+g)
    physical_score = dot(physical,mv(R,physical))
    assert (physical_score-coordinate_score).contains(0)

    out.update(schur_status='MEASURED interval enclosure; positivity criterion requires C>0',
               sigma=endpoints(sigma), kappa_critical=endpoints(critical),
               response_norm=endpoints(response), inverse_distance_lower=endpoints(distance),
               residual_norm=endpoints(rnorm), residual_quadratic_error_upper=endpoints(correction),
               cancellation_factor=endpoints(cancellation) if cancellation is not None else None,
               schur_identity_check='PASS', physical_coordinate_score_check='PASS',
               complement_positive=bool(c_gap > 0), sigma_positive=bool(sigma > 0),
               finite_positive_by_schur=bool(c_gap > 0 and sigma > 0))
    return out


def controls():
    checks = []
    for name,A,expected in [
        ('positive', [[2,1],[1,2]], (2,0)),
        ('indefinite', [[1,2],[2,1]], (1,1)),
        ('negative', [[-2,1],[1,-2]], (0,2))]:
        out,_,_,iner = spectral_certificate(arb_mat(A))
        assert (iner['positive'],iner['negative']) == expected
        if expected[1]: assert out['negative_finite_witness']
        checks.append(name+' inertia and independent Rayleigh PASS')
    out,gap,dist,iner = spectral_certificate(arb_mat([[1,0],[0,0]]))
    assert gap.contains(0) and dist is None and iner is None
    checks.append('singular: refuses invertibility PASS')
    out,gap,dist,iner = spectral_certificate(arb_mat([[1,0],[0,arb('0 +/- 0.001')]]))
    assert gap.contains(0) and dist is None and iner is None
    checks.append('ambiguous interval: refuses sign PASS')
    case = schur_case(arb_mat([[2,1],[1,3]]),[arb(2),arb(1)],-1,'planted Schur')
    assert case['complement_positive'] and not case['sigma_positive']
    assert case['full']['negative_finite_witness']
    checks.append('Schur identity and negative finite witness PASS')
    positive = schur_case(arb_mat([[2,1],[1,3]]),[arb(2),arb(1)],1,'planted positive')
    assert positive['finite_positive_by_schur']
    checks.append('positive Schur completion PASS')
    return checks


def verify_saved(parity):
    """Reparse exact exported witnesses and independently re-score originals."""
    source = (ROOT/f'input_{parity}.json').read_bytes()
    data = json.loads(source)
    result = json.loads((ROOT/f'schur_{parity}.json').read_text())
    assert hashlib.sha256(source).hexdigest() == result['input_sha256']
    count = 0
    for row in result['rows']:
        coeffs = row['full']['finite_witness_coefficients']
        if coeffs is None:
            continue
        model = 'authentic' if row['label']=='authentic pole sign flip' else row['label']
        n = row['N']
        v = [arb(z) for z in coeffs]
        H = arb_mat([[arb(data['models'][model][i][j]) for j in range(n)] for i in range(n)])
        p = [arb(z) for z in data['p'][:n]]
        kappa = arb(row['kappa'])
        score = (dot(v,mv(H,v))+kappa*dot(p,v)*dot(p,v))/dot(v,v)
        assert score < 0
        assert score.overlaps(arb(row['full']['finite_rayleigh']['ball']))
        count += 1
    return dict(parity=parity, exact_decimal_negative_witnesses_rechecked=count,
                status='PASS')


def run(parity):
    started = time.time()
    passed = controls()
    path = ROOT/f'input_{parity}.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    pfull = [arb(z) for z in data['p']]
    kap = arb(2 if parity=='even' else -2)
    rows = []
    # Hostile models run BEFORE authentic tables are accepted.
    for model in ['arch_only','weight_reverse','authentic']:
        Hfull = data['models'][model]
        for n in [20,40,80]:
            H = arb_mat([[arb(Hfull[i][j]) for j in range(n)] for i in range(n)])
            row = schur_case(H,pfull[:n],kap,model)
            rows.append(row)
            print(parity,model,n,'C positive',row.get('complement_positive'),
                  'sigma',row.get('sigma',{}).get('ball'),flush=True)
    Hfull = data['models']['authentic']
    H = arb_mat([[arb(z) for z in row] for row in Hfull])
    rows.append(schur_case(H,pfull,-kap,'authentic pole sign flip'))
    out = dict(parity=parity,precision_bits=ctx.prec,midpoint_dps=mp.mp.dps,
               input_sha256=hashlib.sha256(raw).hexdigest(), controls_first=passed,
               scope='Finite R_120 principal blocks only. Negative witnesses are not full-W negatives.',
               rows=rows,runtime_seconds=time.time()-started)
    (ROOT/f'schur_{parity}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(verify_saved(parity),flush=True)
    print('saved',parity,'seconds',out['runtime_seconds'],flush=True)


if __name__=='__main__':
    if sys.argv[1:] == ['controls']:
        print(json.dumps(controls(),indent=2))
    elif sys.argv[1:] == ['verify']:
        print(json.dumps([verify_saved(p) for p in ['even','odd']],indent=2))
    else:
        assert sys.argv[1] in ('even','odd')
        run(sys.argv[1])
