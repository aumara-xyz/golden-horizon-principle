#!/usr/bin/env python3
"""Exact PENTORA research oracle. Standard library only; no float arithmetic.

This is a reference contract, not an adopted X2 ABI or a Wasm implementation.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEOMETRY_SHA256 = '96b27c9b4de41cd961612be5b1e88d40e973a2fded16bd320415b3e15e3b8c61'
PROFILE = 'pentora.research.sphere.exact.v1-proposal'
MAX_INPUT_BYTES = 65536
MAX_OUTPUT_BYTES = 262144
INPUT_BITS = 256
INTERMEDIATE_BITS = 4096
COMMON_DENOMINATOR_BITS = 1024
DEFAULT_ARITHMETIC_BUDGET = 20000000
WEIGHT_NUMERATORS = {1:800, 2:512, 3:729}
WEIGHT_DENOMINATOR = 69300
BASIS = tuple((i, d-z-i, z) for d in range(6)
              for z in (0,1) if z <= d for i in range(d-z+1))
assert len(BASIS) == 36
ACTIVE_BUDGET = None


class Refusal(ValueError):
    pass


@dataclass
class Budget:
    maximum: int = DEFAULT_ARITHMETIC_BUDGET
    used: int = 0

    def charge(self, amount=1):
        self.used += amount
        if self.used > self.maximum:
            raise Refusal('ARITHMETIC_BUDGET')


@contextmanager
def bounded(maximum=DEFAULT_ARITHMETIC_BUDGET):
    global ACTIVE_BUDGET
    previous = ACTIVE_BUDGET
    current = Budget(maximum)
    ACTIVE_BUDGET = current
    try:
        yield current
    finally:
        ACTIVE_BUDGET = previous


def checked(q):
    if ACTIVE_BUDGET is not None:
        ACTIVE_BUDGET.charge()
    if type(q) is int:
        q = Fraction(q)
    if not isinstance(q,Fraction):
        raise Refusal('RATIONAL_TYPE')
    if max(abs(q.numerator).bit_length(),q.denominator.bit_length()) > INTERMEDIATE_BITS:
        raise Refusal('INTERMEDIATE_BITS')
    return q


def qadd(a,b):
    return checked(a+b)


def qmul(a,b):
    return checked(a*b)


@dataclass(frozen=True)
class Phi:
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __post_init__(self):
        object.__setattr__(self,'a',checked(self.a))
        object.__setattr__(self,'b',checked(self.b))

    def __add__(self,other):
        other=as_phi(other)
        return Phi(qadd(self.a,other.a),qadd(self.b,other.b))

    __radd__=__add__

    def __neg__(self):
        return Phi(-self.a,-self.b)

    def __sub__(self,other):
        return self+-as_phi(other)

    def __mul__(self,other):
        other=as_phi(other)
        bb=qmul(self.b,other.b)
        return Phi(qadd(qmul(self.a,other.a),bb),
                   qadd(qadd(qmul(self.a,other.b),qmul(self.b,other.a)),bb))

    __rmul__=__mul__

    def __truediv__(self,q):
        if type(q) is int:q=Fraction(q)
        if not isinstance(q,Fraction) or q==0:raise Refusal('RATIONAL_DIVISOR')
        return Phi(checked(self.a/q),checked(self.b/q))

    def __pow__(self,n):
        if type(n) is not int or n<0:raise Refusal('EXPONENT')
        out=Phi(1)
        for _ in range(n):out=out*self
        return out

    def sign(self):
        # 2*(a+b*phi)=(2a+b)+b*sqrt(5). Compare exact rational squares.
        c=qadd(qmul(Fraction(2),self.a),self.b);b=self.b
        if b==0:return (c>0)-(c<0)
        if c==0:return (b>0)-(b<0)
        if c>0 and b>0:return 1
        if c<0 and b<0:return -1
        difference=qadd(qmul(c,c),-qmul(Fraction(5),qmul(b,b)))
        result=(difference>0)-(difference<0)
        return result if c>0 else -result


def as_phi(value):
    return value if isinstance(value,Phi) else Phi(value)


@dataclass(frozen=True)
class Radical:
    # Mask bits select sqrt(2),sqrt(3),sqrt(5), in that order.
    # Basis order: 1,sqrt2,sqrt3,sqrt6,sqrt5,sqrt10,sqrt15,sqrt30.
    c: tuple

    def __post_init__(self):
        if len(self.c)!=8:raise Refusal('RADICAL_DIMENSION')
        object.__setattr__(self,'c',tuple(checked(q) for q in self.c))

    @staticmethod
    def from_phi(p):
        p=as_phi(p);c=[Fraction(0)]*8
        c[0]=p.a+p.b/2;c[4]=p.b/2
        return Radical(tuple(c))

    @staticmethod
    def generator(mask,q=1):
        c=[Fraction(0)]*8;c[mask]=Fraction(q)
        return Radical(tuple(c))

    def __add__(self,other):
        if not isinstance(other,Radical):other=Radical.from_phi(other)
        return Radical(tuple(qadd(a,b) for a,b in zip(self.c,other.c)))

    __radd__=__add__

    def __neg__(self):
        return Radical(tuple(-q for q in self.c))

    def __sub__(self,other):return self+-other

    def __mul__(self,other):
        if not isinstance(other,Radical):other=Radical.from_phi(other)
        out=[Fraction(0)]*8
        for i,a in enumerate(self.c):
            if not a:continue
            for j,b in enumerate(other.c):
                if not b:continue
                repeated=i&j;factor=1
                for bit,radicand in enumerate((2,3,5)):
                    if repeated&(1<<bit):factor*=radicand
                out[i^j]=qadd(out[i^j],qmul(qmul(a,b),Fraction(factor)))
        return Radical(tuple(out))

    __rmul__=__mul__

    def __pow__(self,n):
        if type(n) is not int or n<0:raise Refusal('EXPONENT')
        out=Radical.from_phi(1)
        for _ in range(n):out=out*self
        return out

    def to_phi(self):
        if any(self.c[i] for i in (1,2,3,5,6,7)):
            raise Refusal('NOT_IN_QPHI')
        return Phi(self.c[0]-self.c[4],2*self.c[4])


def decimal_integer(s,bits=INPUT_BITS,positive=False):
    if not isinstance(s,str) or not re.fullmatch(r'0|-?[1-9][0-9]*',s):
        raise Refusal('NONCANONICAL_INTEGER')
    if len(s.lstrip('-')) > (bits*30103//100000)+1:
        raise Refusal('INTEGER_BITS')
    n=int(s)
    if abs(n).bit_length()>bits:raise Refusal('INTEGER_BITS')
    if positive and n<=0:raise Refusal('POSITIVE_INTEGER_REQUIRED')
    return n


def read_q(wire,bits=INPUT_BITS):
    if not isinstance(wire,list) or len(wire)!=2:raise Refusal('RATIONAL_SCHEMA')
    numerator=decimal_integer(wire[0],bits)
    denominator=decimal_integer(wire[1],bits,positive=True)
    q=Fraction(numerator,denominator)
    if (q.numerator,q.denominator)!=(numerator,denominator):
        raise Refusal('NONCANONICAL_RATIONAL')
    return checked(q)


def q_wire(q):return [str(q.numerator),str(q.denominator)]


def phi_wire(p):return {'a':q_wire(p.a),'b':q_wire(p.b)}


def read_phi(wire):
    if not isinstance(wire,dict) or set(wire)!={'a','b'}:raise Refusal('QPHI_SCHEMA')
    return Phi(read_q(wire['a']),read_q(wire['b']))


def canonical_json(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def unique_object(items):
    result={}
    for k,v in items:
        if k in result:raise Refusal('DUPLICATE_KEY')
        result[k]=v
    return result


def refuse_float(_):raise Refusal('FLOAT_FORBIDDEN')


def decode_request(raw):
    if not isinstance(raw,bytes) or len(raw)>MAX_INPUT_BYTES:raise Refusal('INPUT_BYTES')
    try:
        result=json.loads(raw,object_pairs_hook=unique_object,
                          parse_float=refuse_float,parse_constant=refuse_float)
    except Refusal:raise
    except (ValueError,RecursionError,UnicodeError):raise Refusal('JSON')
    if canonical_json(result)!=raw:raise Refusal('NONCANONICAL_JSON')
    return result


def source_geometry():
    path=HERE/'data/geometry_index_table_v1.json';raw=path.read_bytes()
    if sha256(raw).hexdigest()!=GEOMETRY_SHA256:raise Refusal('GEOMETRY_BYTES')
    data=json.loads(raw)
    def coord(wire):return Phi(Fraction(*wire['a']),Fraction(*wire['b']))
    points={p['global_index']:tuple(coord(c) for c in p['coordinates']) for p in data['points']}
    frames=[[tuple(coord(c) for c in axis) for axis in cube['axes']] for cube in data['cubes']]
    return data,points,frames


def dot(a,b):return sum((x*y for x,y in zip(a,b)),Phi())


def radius_squared(raw):
    q=dot(raw,raw)
    for r in (0,1,2,3):
        if q==Phi(r):return r
    raise Refusal('GEOMETRY_RADIUS')


def normalized(raw):
    r=radius_squared(raw)
    if not r:raise Refusal('CENTER_HAS_NO_DIRECTION')
    scale=(Radical.from_phi(1) if r==1 else
           Radical.generator(1,Fraction(1,2)) if r==2 else
           Radical.generator(2,Fraction(1,3)))
    return tuple(Radical.from_phi(x)*scale for x in raw)


def double_factorial(n):
    answer=1
    for k in range(n,0,-2):answer*=k
    return answer


def sphere_moment(powers):
    if any(p%2 for p in powers):return Fraction(0)
    numerator=1
    for p in powers:numerator*=double_factorial(p-1)
    return Fraction(numerator,double_factorial(sum(powers)+1))


def polynomial_value(coefficients,point):
    powers=[]
    for coordinate in point:
        row=[Radical.from_phi(1)]
        for _ in range(5):row.append(row[-1]*coordinate)
        powers.append(row)
    result=Radical.from_phi(0)
    for coeff,(i,j,k) in zip(coefficients,BASIS):
        if coeff==Phi():continue
        result=result+Radical.from_phi(coeff)*powers[0][i]*powers[1][j]*powers[2][k]
    return result


def integrated_norm(coefficients):
    answer=Phi()
    for i,a in enumerate(coefficients):
        if a==Phi():continue
        for j in range(i,len(coefficients)):
            b=coefficients[j]
            if b==Phi():continue
            moment=sphere_moment(tuple(x+y for x,y in zip(BASIS[i],BASIS[j])))
            if moment:answer=answer+a*b*moment*(1 if i==j else 2)
    return answer


def validated_tail(target,wire):
    if not isinstance(wire,dict):raise Refusal('TAIL_SCHEMA')
    if target=='declared-polynomial':
        if wire!={'status':'zero-for-declared-polynomial'}:raise Refusal('TAIL_TARGET_MISMATCH')
        return dict(wire)
    if target!='external-projection':raise Refusal('TARGET_KIND')
    if wire=={'status':'unknown'}:return dict(wire)
    if set(wire)!={'status','upper','evidence_digest'} or wire['status']!='asserted-upper-bound':
        raise Refusal('TAIL_SCHEMA')
    upper=read_q(wire['upper'])
    if upper<0:raise Refusal('NEGATIVE_TAIL_BOUND')
    if not isinstance(wire['evidence_digest'],str) or not re.fullmatch('[0-9a-f]{64}',wire['evidence_digest']):
        raise Refusal('EVIDENCE_DIGEST')
    return {**wire,'verification':'not-verified-by-this-profile'}


def evaluate_request(raw,max_operations=DEFAULT_ARITHMETIC_BUDGET):
    with bounded(max_operations) as budget:
        request=decode_request(raw)
        keys={'profile','geometry_sha256','basis','coefficients','target_kind','tail','source_digest'}
        if not isinstance(request,dict) or set(request)!=keys:raise Refusal('REQUEST_SCHEMA')
        if request['profile']!=PROFILE:raise Refusal('PROFILE')
        if request['geometry_sha256']!=GEOMETRY_SHA256:raise Refusal('GEOMETRY_PIN')
        if request['basis']!='sphere-z-reduced-degree5-v1':raise Refusal('BASIS')
        if not isinstance(request['coefficients'],list) or len(request['coefficients'])!=36:
            raise Refusal('COEFFICIENT_COUNT')
        if not isinstance(request['source_digest'],str) or not re.fullmatch('[0-9a-f]{64}',request['source_digest']):
            raise Refusal('SOURCE_DIGEST')
        coefficients=[read_phi(x) for x in request['coefficients']]
        common_denominator=1
        for coefficient in coefficients:
            for q in (coefficient.a,coefficient.b):
                common_denominator=(common_denominator//gcd(common_denominator,q.denominator))*q.denominator
                if common_denominator.bit_length()>COMMON_DENOMINATOR_BITS:
                    raise Refusal('COMMON_DENOMINATOR_BITS')
        tail=validated_tail(request['target_kind'],request['tail'])
        _,points,_=source_geometry()
        samples=[];sample_norm=Radical.from_phi(0)
        for i,point in sorted(points.items()):
            if i==55:continue
            r=radius_squared(point);value=polynomial_value(coefficients,normalized(point))
            weight=Fraction(WEIGHT_NUMERATORS[r],WEIGHT_DENOMINATOR)
            sample_norm=sample_norm+value*value*weight
            samples.append({'global_index':i,'value':[q_wire(q) for q in value.c]})
        integral=integrated_norm(coefficients)
        if sample_norm!=Radical.from_phi(integral) or integral.sign()<0:
            raise Refusal('NORM_INVARIANT')
        frame={
            'profile':PROFILE,'geometry_sha256':GEOMETRY_SHA256,
            'definition':'sphere-z-reduced-degree5-v1','bandlimit':5,
            'measure':'dOmega/(4*pi)','basis_dimension':36,
            'arithmetic':'Q(sqrt2,sqrt3,sqrt5), canonical rational coefficients',
            'coefficient_domain':'Q(phi)','weight_denominator':WEIGHT_DENOMINATOR,
            'shell_weight_numerators':{str(k):v for k,v in WEIGHT_NUMERATORS.items()},
            'input_digest':sha256(b'pentora.research.sphere.v1\0'+raw).hexdigest(),
            'source_digest':request['source_digest'],'source_authenticated':False,
            'target_kind':request['target_kind'],'tail':tail,
            'norm_squared':phi_wire(integral),'sample_norm_squared':phi_wire(sample_norm.to_phi()),
            'samples':samples,'product_authority':'none',
            'full_external_norm_certified':False,'Weil_energy_computed':False,
            'arithmetic_operations':budget.used,
        }
        output=canonical_json(frame)
        if len(output)>MAX_OUTPUT_BYTES:raise Refusal('OUTPUT_BYTES')
        return frame


def make_request(coefficients=None,target_kind='declared-polynomial',tail=None):
    if coefficients is None:coefficients=[Phi() for _ in BASIS]
    if tail is None:
        tail={'status':'zero-for-declared-polynomial'} if target_kind=='declared-polynomial' else {'status':'unknown'}
    return {'profile':PROFILE,'geometry_sha256':GEOMETRY_SHA256,
            'basis':'sphere-z-reduced-degree5-v1','coefficients':[phi_wire(p) for p in coefficients],
            'target_kind':target_kind,'tail':tail,'source_digest':'0'*64}


def viviani_address(n_text):
    n=decimal_integer(n_text,INPUT_BITS,positive=True)
    d=n*n+1
    x=Fraction((n*n-1)**2,d*d)
    y=Fraction(-2*n*(n*n-1),d*d)
    z=Fraction(2*n,d)
    if x*x+y*y+z*z!=1 or x*x+y*y!=x:raise Refusal('CURVE_INVARIANT')
    return {'profile':'pentora.research.viviani-address.v1-proposal',
            'n':n_text,'parameter':'t=log(n), not numerically evaluated',
            'coordinates':[q_wire(q) for q in (x,y,z)],
            'primality_checked':False,'product_authority':'none'}


def monomial_value(point,powers):
    value=Phi(1)
    for x,power in zip(point,powers):value=value*(x**power)
    return value


def all_moment_checks():
    _,points,_=source_geometry()
    shells={r:[p for p in points.values() if radius_squared(p)==r] for r in (1,2,3)}
    records=[]
    for degree in range(12):
        for i in range(degree+1):
            for j in range(degree-i+1):
                powers=(i,j,degree-i-j);got=Phi()
                for r,vertices in shells.items():
                    raw_sum=sum((monomial_value(p,powers) for p in vertices),Phi())
                    if degree%2:
                        if raw_sum!=Phi():raise Refusal('ODD_SHELL_MOMENT')
                    else:
                        got=got+raw_sum*Fraction(WEIGHT_NUMERATORS[r],WEIGHT_DENOMINATOR*r**(degree//2))
                want=Phi(sphere_moment(powers))
                if got!=want:raise Refusal('MOMENT_IDENTITY')
                records.append(list(powers))
    got=Phi()
    for r,vertices in shells.items():
        got=got+sum((p[0]**12 for p in vertices),Phi())*Fraction(WEIGHT_NUMERATORS[r],WEIGHT_DENOMINATOR*r**6)
    error=got-Phi(Fraction(1,13))
    if error!=Phi(Fraction(29,640640)):raise Refusal('DEGREE12_CONTROL')
    return {'moment_count':len(records),'all_exact':True,'degree12_x12_error':phi_wire(error),
            'shell_counts':{str(r):len(v) for r,v in shells.items()}}


if __name__=='__main__':
    import sys
    try:
        frame=evaluate_request(sys.stdin.buffer.read(MAX_INPUT_BYTES+1))
        sys.stdout.buffer.write(canonical_json(frame)+b'\n')
    except Refusal as error:
        sys.stdout.buffer.write(canonical_json({'status':'refused','code':str(error),'product_authority':'none'})+b'\n')
        raise SystemExit(1)
