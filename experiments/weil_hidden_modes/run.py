"""Geometric Weil form; no spectral-zero input. Numerical diagnostics, not certification."""
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import roots_legendre

BASE = Path(__file__).resolve().parent

def basis(x, L, N):
    return np.sin(np.outer(x+L, np.arange(1,N+1)*np.pi/(2*L)))/np.sqrt(L)

def quad(a,b,order):
    x,w=roots_legendre(order)
    return a+(b-a)*(x+1)/2, w*(b-a)/2

def corr(u,L,N,order):
    if u>=2*L:
        return np.zeros((N,N))
    x,w=quad(-L,L-u,order)
    a,b=basis(x+u,L,N),basis(x,L,N)
    g=np.einsum('xi,x,xj->ij',a,w,b)
    return (g+g.T)/2

def terms(L,shift):
    out=[]
    for p in range(2,math.ceil(math.exp(2*L/shift))+1):
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)):
            continue
        m=1
        while m*math.log(p)*shift<2*L:
            out.append((m*math.log(p)*shift,2*math.log(p)/p**(m/2)))
            m+=1
    return out

def assemble(L,order,shift):
    N=16; eye=np.eye(N)
    x,w=quad(-L,L,order)
    b=basis(x,L,N)
    plus=np.einsum('xi,x->i',b,w*np.exp(x/2))
    minus=np.einsum('xi,x->i',b,w*np.exp(-x/2))
    pole=np.outer(plus,minus)+np.outer(minus,plus)
    arch=-(np.euler_gamma+math.log(4*np.pi))*eye
    other=-(np.euler_gamma+math.log(np.pi))*eye
    u,weights=quad(0,2*L,order)
    for t,wt in zip(u,weights):
        g=corr(t,L,N,order)
        arch+=wt*(eye-np.exp(t/2)*g)/np.sinh(t)
        other+=wt*2*(np.exp(-2*t)*eye-np.exp(-t/2)*g)/(-np.expm1(-2*t))
    arch-=math.log(math.tanh(L))*eye
    other-=math.log1p(-math.exp(-4*L))*eye
    arithmetic=np.zeros((N,N))
    if shift is not None:
        for t,weight in terms(L,shift):
            arithmetic+=weight*corr(t,L,N,order)
    return pole+arch-arithmetic, float(np.linalg.norm(arch-other,2))

def invsqrt(a):
    v,u=np.linalg.eigh(a)
    return np.einsum('ik,k,jk->ij',u,1/np.sqrt(v),u)

def diagnose(w,uncertainty):
    ev=np.linalg.eigvalsh(w)
    out={'minimum':float(ev[0]),'resolution_proxy':uncertainty,
         'status':'MEASURED positive finite approximation' if ev[0]>uncertainty else 'UNVERIFIED sign'}
    if len(w)==4: return out
    a,c,d=w[:4,:4],w[:4,4:],w[4:,4:]
    out['hidden_minimum']=float(np.linalg.eigvalsh(d)[0])
    if min(np.linalg.eigvalsh(a)[0],out['hidden_minimum'])<=uncertainty: return out
    correction=np.einsum('ik,kj->ij',c,np.linalg.solve(d,c.T))
    schur=a-correction
    coupling=np.einsum('ik,kl,lj->ij',invsqrt(a),c,invsqrt(d))
    out.update(visible_minimum=float(np.linalg.eigvalsh(a)[0]),
               schur_minimum=float(np.linalg.eigvalsh(schur)[0]),
               coupling_norm=float(np.linalg.norm(coupling,2)),
               correction_norm=float(np.linalg.norm(correction,2)))
    return out

def main():
    result={'source':'https://alainconnes.org/wp-content/uploads/Selecta.pdf',
            'zero_input':False,'rigorous_bounds':False,'runs':[]}
    lines=['# Weil hidden modes — numerical report','',
           'Full prime-side form, including pole and archimedean terms. No zero input.',
           'Quadrature differences are diagnostics, not certified error bounds.','',
           '| Model | L | N | Minimum | Schur minimum | Coupling norm |',
           '|---|---:|---:|---:|---:|---:|']
    for name,shift in [('arch_only',None),('shift_plus',1.1),('shift_minus',.9),('authentic',1.)]:
        for L in [.4,.7,1.]:
            matrices=[]; discrepancies=[]
            for order in [96,192,384]:
                w,check=assemble(L,order,shift)
                matrices.append(w); discrepancies.append(check)
            for N in [4,8,12,16]:
                errors=[float(np.linalg.norm(matrices[i+1][:N,:N]-matrices[i][:N,:N],2)) for i in range(2)]
                proxy=max(errors[-1]*10,1e-11)
                row={'model':name,'L':L,'N':N,'quadrature_differences':errors,
                     'arch_formula_disagreement':max(discrepancies),**diagnose(matrices[-1][:N,:N],proxy)}
                result['runs'].append(row)
                s=row.get('schur_minimum'); c=row.get('coupling_norm')
                lines.append(f"| {name} | {L} | {N} | {row['minimum']:.6g} | {s if s is not None else 'unresolved / N=4'} | {c if c is not None else '—'} |")
    (BASE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (BASE/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    for r in result['runs']:
        if r['model']=='authentic': print(r)

if __name__=='__main__': main()
