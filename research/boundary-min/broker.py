"""Broker: spawns the sandboxed guest, mediates every effect, mints via issuer, appends Merkle leaves, anchors roots."""
import sys, os, json, socket, subprocess, hashlib, inspect, importlib, secrets
from common import *
statement_path, issuer_sock, anchor_sock, governed_dir, log_path, scenario, sandbox_profile, keys_dir = sys.argv[1:9]
statement=json.load(open(statement_path)); sdigest=h(canon(statement["body"]))
import tools
def impl_digest(name): return h(inspect.getsource(tools.TOOLS[name]).encode())
leaves=[leaf_hash(l.encode()) for l in open(log_path).read().splitlines()] if os.path.exists(log_path) else []
def rpc(sock,o):
    s=socket.socket(socket.AF_UNIX); s.connect(sock); f=s.makefile("rw"); send_line(f,o); r=recv_line(f); s.close(); return r
def append_leaf(record):
    line=json.dumps(record,sort_keys=True); open(log_path,"a").write(line+"\n"); leaves.append(leaf_hash(line.encode()))
    proof=consistency_proof(len(leaves)-1,leaves); return rpc(anchor_sock,{"kind":"put","size":len(leaves),"root":mth(leaves).hex(),"proof":[p.hex() for p in proof]})
def refuse(reason,extra=None):
    rec={"kind":"refusal","statement_digest":sdigest,"reason":reason}; rec.update(extra or {}); a=append_leaf(rec); return {"ok":False,"reason":reason,"anchored":a.get("ok")}
def handle(p):
    kind=p.get("kind")
    if kind=="amend": return refuse("amendment-boundary: only the activator can start a new epoch")
    if kind=="raw_grant":
        op=p["operation"]; sig=p["signature"]
        if not verify(statement["body"]["issuer_pub"],canon(op),sig): return refuse("signature-invalid")
        return refuse("unreachable")
    if kind=="replay":
        op=dict(last_op); r=rpc(issuer_sock,{"operation":op})
        return refuse("issuer-refused:"+r["reason"]) if not r["ok"] else {"ok":True,"BUG":"replay minted"}
    tool=p.get("tool"); args=p.get("args",{})
    if tool not in statement["body"]["allowlist"]: return refuse("not-in-allowlist",{"tool":tool})
    importlib.reload(tools); d=impl_digest(tool)
    if d!=statement["body"]["allowlist"][tool]: return refuse("definition-mismatch: implementation digest changed since activation",{"tool":tool})
    op={"statement_digest":sdigest,"tool":tool,"args_digest":h(canon(args)),"impl_digest":d,"nonce":secrets.token_hex(8)}
    r=rpc(issuer_sock,{"operation":op})
    if not r["ok"]: return refuse("issuer-refused:"+r["reason"])
    sig=r["signature"]
    if p.get("_test_tamper"): sig=("0" if sig[0]!="0" else "1")+sig[1:]
    if not verify(statement["body"]["issuer_pub"],canon(op),sig): return refuse("signature-invalid")
    importlib.reload(tools)
    if impl_digest(tool)!=op["impl_digest"]: return refuse("check-at-use: implementation changed between grant and dispatch")
    effect=tools.TOOLS[tool](governed_dir,**args)
    globals()["last_op"]=op
    a=append_leaf({"kind":"settlement","operation":op,"signature":sig,"effect":effect})
    return {"ok":True,"nonce":op["nonce"],"effect":effect,"anchored":a.get("ok"),"anchor_size":a.get("size")}
last_op=None
env={"PATH":"/usr/bin:/bin","KEY_DIR_HINT":keys_dir}
cmd=["/usr/bin/sandbox-exec","-f",sandbox_profile,sys.executable,os.path.join(os.path.dirname(__file__),"guest.py"),scenario]
g=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
report=None
while True:
    line=g.stdout.readline()
    if not line: break
    msg=json.loads(line)
    if msg.get("kind")=="report": report=msg["report"]; break
    send_line(g.stdin,handle(msg))
g.wait(timeout=10); err=g.stderr.read()
print(json.dumps({"report":report,"guest_stderr":err[-500:],"leaves":len(leaves),"root":mth(leaves).hex()}))
