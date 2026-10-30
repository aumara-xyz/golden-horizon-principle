#!/usr/bin/env python3
"""Bounded exact tests; no NumPy, floating arithmetic, or product execution."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import perf_counter_ns
import reference as r

HERE=Path(__file__).resolve().parent
TESTS=[]


def check(name,body):
    start=perf_counter_ns()
    detail=body()
    TESTS.append({'name':name,'status':'PASS','elapsed_ns':perf_counter_ns()-start,
                  'detail':detail if detail is not None else {}})


def rejects(code,body):
    try:body()
    except r.Refusal as error:
        assert str(error)==code,(str(error),code)
        return {'expected_refusal':code}
    raise AssertionError('Expected refusal '+code)


def encoded(request):return r.canonical_json(request)


def request_with(change):
    request=r.make_request();change(request);return encoded(request)


def coeffs_for(terms):
    out=[r.Phi() for _ in r.BASIS]
    for powers,value in terms.items():out[r.BASIS.index(powers)]=r.as_phi(value)
    return out


def test_basis():
    assert len(set(r.BASIS))==36
    assert all(k in (0,1) and i+j+k<=5 for i,j,k in r.BASIS)
    assert [sum(sum(p)==degree for p in r.BASIS) for degree in range(6)]==[1,3,5,7,9,11]
    return {'dimension':36,'degree_shell_dimensions':[1,3,5,7,9,11]}


def test_radicals():
    roots=[r.Radical.generator(1),r.Radical.generator(2),r.Radical.generator(4)]
    for root,n in zip(roots,(2,3,5)):
        assert root*root==r.Radical.from_phi(n)
    a=roots[0]+roots[1]+roots[2]+r.Radical.from_phi(r.Phi(2,3))
    b=roots[0]*roots[1]+r.Radical.from_phi(r.Phi(-1,Fraction(2,7)))
    assert a*b==b*a
    assert a*(b+roots[1])==a*b+a*roots[1]
    assert r.Radical.from_phi(r.Phi(Fraction(3,7),Fraction(-11,13))).to_phi()==r.Phi(Fraction(3,7),Fraction(-11,13))
    rejects('NOT_IN_QPHI',lambda:roots[0].to_phi())
    return {'basis_radicands':[1,2,3,6,5,10,15,30],'sqrt2_Qphi_conversion':'refused'}


def test_normalization():
    _,points,_=r.source_geometry();counts={1:0,2:0,3:0}
    for idx,point in points.items():
        if idx==55:continue
        n=r.normalized(point)
        square=sum((x*x for x in n),r.Radical.from_phi(0))
        assert square==r.Radical.from_phi(1)
        counts[r.radius_squared(point)]+=1
    assert counts=={1:30,2:60,3:20}
    total=sum(Fraction(counts[k]*r.WEIGHT_NUMERATORS[k],r.WEIGHT_DENOMINATOR) for k in counts)
    assert total==1
    return {'unit_directions':110,'shell_counts':counts,'weight_sum':'1'}


def test_norms():
    cases={
        'zero':coeffs_for({}),
        'constant':coeffs_for({(0,0,0):1}),
        'linear_x':coeffs_for({(1,0,0):1}),
        'phi_mixed':coeffs_for({(1,0,0):r.Phi(0,1),(0,1,0):Fraction(1,3),(0,0,1):r.Phi(2,-1)}),
        'invisible_on_dual32_h':coeffs_for({(3,1,1):1,(1,3,1):-1}),
        'dense36':[r.Phi(Fraction(i-17,i+1),Fraction(i%5-2,i+2)) for i in range(36)],
    }
    expected={'zero':r.Phi(),'constant':r.Phi(1),'linear_x':r.Phi(Fraction(1,3)),
              'invisible_on_dual32_h':r.Phi(Fraction(4,3465))}
    output={}
    for name,coeff in cases.items():
        frame=r.evaluate_request(encoded(r.make_request(coeff)))
        value=r.read_phi(frame['norm_squared'])
        assert frame['norm_squared']==frame['sample_norm_squared']
        if name in expected:assert value==expected[name]
        assert value.sign()>=0
        output[name]={'norm_squared':frame['norm_squared'],
                      'arithmetic_operations':frame['arithmetic_operations'],
                      'sample_bytes':len(r.canonical_json(frame))}
        if name=='invisible_on_dual32_h':
            (HERE/'example_frame.json').write_bytes(r.canonical_json(frame)+b'\n')
    return output


def test_hidden_controls():
    data,points,frames=r.source_geometry()
    corners=[points[i] for i in data['double_corner_indices']]
    phi=r.Phi(0,1);base=(r.Phi(),phi,r.Phi(1));dual=[]
    for roll in range(3):
        v=base[-roll:]+base[:-roll] if roll else base
        nz=[i for i,x in enumerate(v) if x!=r.Phi()]
        for signs in product((-1,1),repeat=2):
            p=list(v)
            for i,sign in zip(nz,signs):p[i]=p[i]*sign
            dual.append(tuple(p))
    def h(p):
        x,y,z=p;return x*y*z*(x*x-y*y)
    assert len(set(dual))==12 and all(h(p)==r.Phi() for p in corners+dual)
    true_energy=r.sphere_moment((6,2,2))-2*r.sphere_moment((4,4,2))+r.sphere_moment((2,6,2))
    assert true_energy==Fraction(4,3465)
    def hidden25(point):
        answer=r.Phi(1)
        for axes in frames:
            u,v,w=[r.dot(axis,point) for axis in axes]
            answer=answer*u*v*w*(u*u-v*v)
        return answer
    assert all(hidden25(p)==r.Phi() for i,p in points.items() if i!=55)
    probe=hidden25(tuple(r.Phi(i) for i in (1,2,3)))
    assert probe!=r.Phi()
    assert probe==r.Phi(Fraction(55071306675,262144),Fraction(244124503425,524288))
    frame=r.evaluate_request(encoded(r.make_request(target_kind='external-projection')))
    assert frame['tail']=={'status':'unknown'} and not frame['full_external_norm_certified']
    return {'dual32_raw_samples_zero':32,'h_true_norm_squared':r.q_wire(true_energy),
            'full110_hidden_raw_samples_zero':110,'hidden25_raw_probe_value':r.phi_wire(probe),
            'homogeneous_normalization':'Zeros persist under nonzero radial scaling; generic normalized probe need not lie in the runtime field.',
            'zero_external_projection':'tail remains unknown; no full-field conclusion'}


def test_viviani():
    cases=[1,2,3,5,7,11,243,(1<<256)-1]
    result={}
    for n in cases:
        frame=r.viviani_address(str(n))
        xyz=[Fraction(int(a),int(b)) for a,b in frame['coordinates']]
        assert sum(x*x for x in xyz)==1 and xyz[0]**2+xyz[1]**2==xyz[0]
        assert not frame['primality_checked']
        result[str(n)]=frame['coordinates']
    assert result['2']==[['9','25'],['-12','25'],['4','5']]
    rejects('POSITIVE_INTEGER_REQUIRED',lambda:r.viviani_address('0'))
    rejects('INTEGER_BITS',lambda:r.viviani_address(str(1<<256)))
    return {'checked_count':len(cases),'n2':result['2'],'max_n_bits':256,
            'no_primality_or_time_proof':True}


def test_asserted_tail():
    request=r.make_request(target_kind='external-projection',tail={
        'status':'asserted-upper-bound','upper':['1','100'],'evidence_digest':'a'*64})
    frame=r.evaluate_request(encoded(request))
    assert frame['tail']['verification']=='not-verified-by-this-profile'
    assert not frame['full_external_norm_certified']
    return {'upper':['1','100'],'verification':frame['tail']['verification']}


def test_denominator_budget():
    request=r.make_request()
    for i,(prime,power) in enumerate(((2,200),(3,126),(5,85),(7,71),(11,58),(13,54))):
        request['coefficients'][i]['a']=['1',str(prime**power)]
    return rejects('COMMON_DENOMINATOR_BITS',lambda:r.evaluate_request(encoded(request)))


def main():
    check('basis_dimension',test_basis)
    check('radical_field',test_radicals)
    check('all110_normalized_exactly',test_normalization)
    check('all364_moments_and_degree12_failure',r.all_moment_checks)
    check('six_exact_norm_cases',test_norms)
    check('mandatory_hidden_modes',test_hidden_controls)
    check('rational_viviani_addresses',test_viviani)
    check('asserted_tail_is_not_a_certificate',test_asserted_tail)
    for label,wire in [('unreduced',['2','4']),('zero_not_reduced',['0','2']),('negative_den',['1','-1']),
                       ('leading_zero',['01','2']),('negative_zero',['-0','1']),('plus',['+1','2']),
                       ('numeric_not_string',[1,2]),('decimal',['0.5','1'])]:
        code=('NONCANONICAL_RATIONAL' if label in ('unreduced','zero_not_reduced') else
              'POSITIVE_INTEGER_REQUIRED' if label=='negative_den' else 'NONCANONICAL_INTEGER')
        check('reject_fraction_'+label,lambda wire=wire,code=code:rejects(code,lambda:r.read_q(wire)))
    check('reject_float',lambda:rejects('FLOAT_FORBIDDEN',lambda:r.decode_request(b'{"x":1.0}')))
    check('reject_nan',lambda:rejects('FLOAT_FORBIDDEN',lambda:r.decode_request(b'{"x":NaN}')))
    check('reject_duplicate_key',lambda:rejects('DUPLICATE_KEY',lambda:r.decode_request(b'{"a":1,"a":2}')))
    check('reject_trailing_lf',lambda:rejects('NONCANONICAL_JSON',lambda:r.decode_request(encoded(r.make_request())+b'\n')))
    check('reject_geometry',lambda:rejects('GEOMETRY_PIN',lambda:r.evaluate_request(request_with(lambda q:q.update(geometry_sha256='0'*64)))))
    check('reject_wrong_dimension',lambda:rejects('COEFFICIENT_COUNT',lambda:r.evaluate_request(request_with(lambda q:q['coefficients'].pop()))))
    check('reject_degree25_basis',lambda:rejects('BASIS',lambda:r.evaluate_request(request_with(lambda q:q.update(basis='sphere-degree25')))))
    check('reject_extra_authority',lambda:rejects('REQUEST_SCHEMA',lambda:r.evaluate_request(request_with(lambda q:q.update(authority='owner')))))
    check('reject_external_exact_zero',lambda:rejects('TAIL_SCHEMA',lambda:r.evaluate_request(encoded(r.make_request(target_kind='external-projection',tail={'status':'zero-for-declared-polynomial'})))))
    check('reject_negative_tail',lambda:rejects('NEGATIVE_TAIL_BOUND',lambda:r.evaluate_request(encoded(r.make_request(target_kind='external-projection',tail={'status':'asserted-upper-bound','upper':['-1','10'],'evidence_digest':'a'*64})))))
    check('reject_257bit_input',lambda:rejects('INTEGER_BITS',lambda:r.read_q([str(1<<256),'1'])))
    check('reject_denominator_lcm_growth',test_denominator_budget)
    check('reject_intermediate_growth',lambda:rejects('INTERMEDIATE_BITS',lambda:r.Phi(Fraction(1,1<<3000))**2))
    check('reject_arithmetic_exhaustion',lambda:rejects('ARITHMETIC_BUDGET',lambda:r.evaluate_request(encoded(r.make_request()),max_operations=1)))
    check('reject_center_normalization',lambda:rejects('CENTER_HAS_NO_DIRECTION',lambda:r.normalized((r.Phi(),r.Phi(),r.Phi()))))
    check('reject_input_size',lambda:rejects('INPUT_BYTES',lambda:r.decode_request(b' '*(r.MAX_INPUT_BYTES+1))))
    check('exact_Phi_ordering',lambda:assert_ordering())
    output={'profile':'pentora.research.exact-reference-tests.v1','date':'2026-10-30',
            'geometry_sha256':r.GEOMETRY_SHA256,'plan_sha256':sha256((HERE/'PLAN.md').read_bytes()).hexdigest(),
            'test_count':len(TESTS),'passed':len(TESTS),'failed':0,
            'arithmetic':'Exact integer/Fraction arithmetic; elapsed_ns is diagnostic integer timing',
            'product_build_or_Wasm_tests_run':False,'tests':TESTS}
    (HERE/'results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'passed':len(TESTS),'failed':0,'results':'results.json'},indent=2))


def assert_ordering():
    assert r.Phi(0,1).sign()==1
    assert r.Phi(1,-1).sign()==-1
    assert r.Phi(-1,1).sign()==1
    assert r.Phi(2,-1).sign()==1
    assert r.Phi().sign()==0
    return {'exact_sign_examples':5}


if __name__=='__main__':main()
