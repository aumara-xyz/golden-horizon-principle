"""boundary-min shared primitives: canonical JSON, Ed25519, RFC 6962 Merkle with consistency proofs."""
import json, hashlib, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
def canon(o): return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
def h(b): return hashlib.sha256(b).hexdigest()
def keygen(): return Ed25519PrivateKey.generate()
def priv_pem(k): return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
def pub_hex(k): return k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
def load_priv(pem): return serialization.load_pem_private_key(pem, password=None)
def sign(k, b): return k.sign(b).hex()
def verify(pub_hex_, b, sig_hex):
    try: Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex_)).verify(bytes.fromhex(sig_hex), b); return True
    except Exception: return False
# ---- RFC 6962 ----
def leaf_hash(b): return hashlib.sha256(b"\x00"+b).digest()
def node(l,r): return hashlib.sha256(b"\x01"+l+r).digest()
def mth(leaves):
    if not leaves: return hashlib.sha256(b"").digest()
    if len(leaves)==1: return leaves[0]
    k=1
    while k*2<len(leaves): k*=2
    return node(mth(leaves[:k]), mth(leaves[k:]))
def _subproof(m, leaves, b):
    n=len(leaves)
    if m==n: return [] if b else [mth(leaves)]
    k=1
    while k*2<n: k*=2
    if m<=k: return _subproof(m, leaves[:k], b)+[mth(leaves[k:])]
    return _subproof(m-k, leaves[k:], False)+[mth(leaves[:k])]
def consistency_proof(m, leaves):
    if m==0 or m>len(leaves): return []
    return _subproof(m, leaves, True)
def verify_consistency(m, n, old_root, new_root, proof):
    """RFC 6962 §2.1.4.2."""
    if m==n: return proof==[] and old_root==new_root
    if m==0 or m>n: return False
    return _verify_core(m,n,old_root,new_root,list(proof))
def _verify_core(m,n,old_root,new_root,proof):
    fn,sn=m-1,n-1
    while fn&1: fn>>=1; sn>>=1
    if (m & (m-1))==0: fr=sr=old_root; rest=proof
    else:
        if not proof: return False
        fr=sr=proof[0]; rest=proof[1:]
    for c in rest:
        if sn==0: return False
        if fn&1 or fn==sn:
            fr=node(c,fr); sr=node(c,sr)
            while fn&1==0 and fn!=0: fn>>=1; sn>>=1
        else:
            sr=node(sr,c)
        fn>>=1; sn>>=1
    return sn==0 and fr==old_root and sr==new_root
def recv_line(f):
    line=f.readline()
    return json.loads(line) if line else None
def send_line(f,o): f.write(json.dumps(o)+"\n"); f.flush()
