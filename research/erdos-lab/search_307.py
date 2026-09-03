"""Erdős #307 structured search. Given Q, P is forced: B=numerator(sum 1/q) must be squarefree with prime factors outside Q, P=factors, then A_P must equal prod(Q)."""
import sys, json, time, itertools, math
from fractions import Fraction
from sympy import primerange, factorint, isprime
NPR=int(sys.argv[1]); KMAX=int(sys.argv[2]); ALLOW_ONE=int(sys.argv[3]); out=sys.argv[4]
primes=list(primerange(2,400))[:NPR]; base=([1] if ALLOW_ONE else [])+primes
t0=time.time(); hits=[]; stats={"sets":0,"B_squarefree_disjoint":0}
def numer_and_prod(S):
    P=1
    for s in S: P*=s
    A=sum(P//s for s in S); return A,P
for k in range(1,KMAX+1):
    for Q in itertools.combinations(base,k):
        stats["sets"]+=1
        B,PQ=numer_and_prod(Q)
        g=math.gcd(B,PQ); Bred=B//g; PQred=PQ//g            # lowest terms (g>1 only possible when 1 in Q)
        if Bred==1: continue
        f=factorint(Bred)
        if any(e>1 for e in f.values()): continue
        Pset=sorted(f.keys())
        if set(Pset)&set(Q): continue
        stats["B_squarefree_disjoint"]+=1
        A,PP=numer_and_prod(Pset)
        # exact check: (sum_P 1/p)(sum_Q 1/q) == 1
        SP=sum(Fraction(1,p) for p in Pset); SQ=sum(Fraction(1,q) for q in Q)
        if SP*SQ==1: hits.append({"Q":list(Q),"P":Pset}); print("HIT",Q,Pset,flush=True)
    print(f"k={k} done sets={stats['sets']} sqfree_disjoint={stats['B_squarefree_disjoint']} hits={len(hits)} t={time.time()-t0:.0f}s",flush=True)
json.dump({"n_primes":NPR,"kmax":KMAX,"allow_one":ALLOW_ONE,"stats":stats,"hits":hits,"runtime_s":time.time()-t0},open(out,"w"),indent=1)
