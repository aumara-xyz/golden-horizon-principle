"""Issuer: holds the root key. Mints a grant only for the configured statement digest and an unused nonce (durable nonce book)."""
import sys, os, socket, json
from common import *
sock_path, key_path, statement_digest, nonce_book = sys.argv[1:5]
priv=load_priv(open(key_path,"rb").read())
used=set(open(nonce_book).read().split()) if os.path.exists(nonce_book) else set()
if os.path.exists(sock_path): os.remove(sock_path)
srv=socket.socket(socket.AF_UNIX); srv.bind(sock_path); srv.listen(8); print("ISSUER READY",flush=True)
while True:
    c,_=srv.accept(); f=c.makefile("rw")
    req=recv_line(f)
    if not req: c.close(); continue
    op=req.get("operation",{})
    if op.get("statement_digest")!=statement_digest: send_line(f,{"ok":False,"reason":"statement-mismatch"})
    elif op.get("nonce") in used: send_line(f,{"ok":False,"reason":"nonce-used"})
    else:
        used.add(op["nonce"]); open(nonce_book,"a").write(op["nonce"]+"\n"); os.fsync(os.open(nonce_book,os.O_RDONLY)) if False else None
        send_line(f,{"ok":True,"signature":sign(priv,canon(op))})
    c.close()
