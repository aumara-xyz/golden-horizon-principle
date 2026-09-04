"""Anchor: holds only (size, root). Accepts a new root only with a valid RFC 6962 consistency proof from the retained one."""
import sys, os, socket, json
from common import *
sock_path, state_path = sys.argv[1:3]
state=json.load(open(state_path)) if os.path.exists(state_path) else {"size":0,"root":None}
if os.path.exists(sock_path): os.remove(sock_path)
srv=socket.socket(socket.AF_UNIX); srv.bind(sock_path); srv.listen(8); print("ANCHOR READY",flush=True)
while True:
    c,_=srv.accept(); f=c.makefile("rw"); req=recv_line(f)
    if not req: c.close(); continue
    if req.get("kind")=="get": send_line(f,state); c.close(); continue
    m,n=state["size"],req["size"]; new_root=bytes.fromhex(req["root"]); proof=[bytes.fromhex(p) for p in req["proof"]]
    old_root=bytes.fromhex(state["root"]) if state["root"] else None
    ok = (m==0 and n>=1) or (n>m and verify_consistency(m,n,old_root,new_root,proof))
    if ok:
        state={"size":n,"root":req["root"]}; json.dump(state,open(state_path,"w")); send_line(f,{"ok":True,"size":n})
    else: send_line(f,{"ok":False,"reason":"consistency-proof-failed","retained":state})
    c.close()
