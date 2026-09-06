"""D5 part 2: Halmos unitary dilation of a contraction. Finite-dimensional, no physics claimed. numpy only."""
import numpy as np, json
from scipy.linalg import sqrtm
np.set_printoptions(precision=6, suppress=True)
def halmos(A):
    n=A.shape[0]; I=np.eye(n)
    DA=sqrtm(I-A.conj().T@A); DAs=sqrtm(I-A@A.conj().T)   # (I-A*A)^{1/2}, (I-AA*)^{1/2}: PSD roots (A contraction)
    U=np.block([[A,DAs],[DA,-A.conj().T]])
    return U,DA,DAs
def report(name,A):
    U,DA,DAs=halmos(A); n=A.shape[0]; P=np.zeros((2*n,2*n)); P[:n,:n]=np.eye(n)
    evA=np.linalg.eigvals(A); evU=np.linalg.eigvals(U)
    intertw=np.linalg.norm(A@DA-DAs@A)
    unit=np.linalg.norm(U.conj().T@U-np.eye(2*n))
    powdev={k:float(np.linalg.norm((np.linalg.matrix_power(U,k))[:n,:n]-np.linalg.matrix_power(A,k))) for k in (1,2,3,5)}
    lhs=(np.linalg.matrix_power(U,2))[:n,:n]; rhs=A@A+DAs@DA
    out={"name":name,"norm_A":float(np.linalg.norm(A,2)),"eig_A":[complex(v) for v in evA],"eig_A_abs":[float(abs(v)) for v in evA],
         "eig_A_imag_max":float(max(abs(v.imag) for v in evA)),"eig_U_abs":[float(abs(v)) for v in evU],
         "unitarity_defect":float(unit),"intertwining_defect":float(intertw),"compression_of_U^k_minus_A^k":powdev,
         "U2_block_identity_defect":float(np.linalg.norm(lhs-rhs)),
         "nonnormality":float(np.linalg.norm(A@A.conj().T-A.conj().T@A))}
    print(json.dumps({k:(str(v) if isinstance(v,list) else v) for k,v in out.items()},indent=1)); return out
control=np.diag([0.5,-0.3]).astype(complex)                     # diagonal real contraction
mut=np.array([[0.5,0.6],[-0.3,0.4]],dtype=complex)                # nonnormal, complex eigenvalues inside the disk
assert np.linalg.norm(mut,2)<1 and np.linalg.norm(control,2)<1
mut3=np.array([[0.2,0.7,0.1],[-0.4,0.1,0.3],[0.0,-0.5,0.3]],dtype=complex); assert np.linalg.norm(mut3,2)<1
res=[report("control_diag_real",control),report("mutation_nonnormal_2x2",mut),report("mutation_nonnormal_3x3",mut3)]
json.dump(res,open("d5_dilation_results.json","w"),indent=1,default=str)
