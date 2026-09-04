"""boundary-min activator + test runner. The activator is the only party that can create a statement/epoch."""
import os, sys, json, time, subprocess, socket, tempfile, shutil, inspect, importlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
import tools
PY=sys.executable; HERE=os.path.dirname(os.path.abspath(__file__))
run=os.path.realpath(tempfile.mkdtemp(prefix="bmin-")); keys=os.path.join(run,"keys"); os.makedirs(keys,mode=0o700)
governed=os.path.join(run,"governed"); os.makedirs(governed); anchor_dir=os.path.join(run,"anchor"); os.makedirs(anchor_dir)
issuer_sock=os.path.join(run,"issuer.sock"); anchor_sock=os.path.join(run,"anchor.sock"); log_path=os.path.join(run,"aura.jsonl")
profile=os.path.join(run,"guest.sb"); open(profile,"w").write(f'''(version 1)
(deny default)
(allow process-exec) (allow process-fork) (allow sysctl-read) (allow mach-lookup)
(allow file-read*)
(deny file-read* (subpath "{keys}"))
(deny file-write*)
(deny network*)
''')
results=[]
def rec(test,claim,ok,evidence): results.append({"test":test,"claim":claim,"status":"PASS" if ok else "FAIL","evidence":evidence}); print(("PASS" if ok else "FAIL"),test,claim,"|",evidence,flush=True)
# ---- Merkle self-test (the anchor's whole job) ----
L=[leaf_hash(f"leaf{i}".encode()) for i in range(23)]
okc=all(verify_consistency(m,n,mth(L[:m]),mth(L[:n]),consistency_proof(m,L[:n])) for n in range(1,24) for m in range(1,n+1))
bad=verify_consistency(5,9,mth(L[:5]),mth(L[:8]+[leaf_hash(b"evil")]),consistency_proof(5,L[:8]+[leaf_hash(b"evil")]))  # proof for evil tree vs claim: consistent (it IS an extension) -> should be True; real tamper test below
tam=verify_consistency(5,9,mth(L[:5]),mth([leaf_hash(b"x")]+L[1:9]),consistency_proof(5,L[:9]))
rec("T0","RFC6962 consistency proofs verify for all 1<=m<=n<=23 and reject an edited prefix",okc and not tam,f"all-pairs={okc} edited-prefix-detected={not tam}")
# ---- activator: statement + keys + issuer/anchor ----
act_key=keygen(); iss_key=keygen(); open(os.path.join(keys,"issuer.pem"),"wb").write(priv_pem(iss_key)); os.chmod(os.path.join(keys,"issuer.pem"),0o600)
def make_statement(epoch):
    importlib.reload(tools)
    body={"epoch":epoch,"allowlist":{n:h(inspect.getsource(f).encode()) for n,f in tools.TOOLS.items()},"issuer_pub":pub_hex(iss_key),"activator_pub":pub_hex(act_key)}
    st={"body":body,"signature":sign(act_key,canon(body))}; p=os.path.join(run,f"statement-{epoch}.json"); json.dump(st,open(p,"w")); return p,h(canon(body))
st_path,sd=make_statement(1)
procs=[]
def start(args,ready):
    p=subprocess.Popen([PY]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=HERE); procs.append(p)
    line=p.stdout.readline(); assert ready in line, line; return p
issuer=start([os.path.join(HERE,"issuer.py"),issuer_sock,os.path.join(keys,"issuer.pem"),sd,os.path.join(keys,"nonces.txt")],"ISSUER READY")
anchor=start([os.path.join(HERE,"anchor.py"),anchor_sock,os.path.join(anchor_dir,"state.json")],"ANCHOR READY")
def broker(scenario,statement=None):
    out=subprocess.run([PY,os.path.join(HERE,"broker.py"),statement or st_path,issuer_sock,anchor_sock,governed,log_path,scenario,profile,keys],capture_output=True,text=True,cwd=HERE,timeout=60)
    try: return json.loads(out.stdout.strip().splitlines()[-1])
    except Exception: return {"error":out.stdout[-800:]+out.stderr[-800:]}
def steps(r): return {s["name"]:s["result"] for s in (r.get("report") or {}).get("steps",[])}
# T1 confinement
s=steps(broker("confinement"))
ctrl=subprocess.run([PY,"-c","open('/tmp/boundary-min-ctrl.txt','w').write('x');print('ok')"],capture_output=True,text=True).stdout.strip()
rec("T1","guest cannot write files, open sockets, or read the issuer key; no key in env (control: same write outside sandbox succeeds)",
    all(str(s.get(k,"")).startswith("REFUSED") for k in ("direct_write","direct_net","read_issuer_key")) and s.get("env_has_key")==False and ctrl=="ok", s)
# T2 allowlist
s=steps(broker("allowlist"))
rec("T2","tool outside the statement is refused before the issuer is contacted; allowed tool is granted, executed, anchored",
    s["bad_tool"]["ok"]==False and s["bad_tool"]["reason"]=="not-in-allowlist" and s["good_tool"]["ok"] and s["good_tool"]["anchored"] and os.path.exists(s["good_tool"]["effect"]["path"]), {k:(v.get("reason") or "ok") for k,v in s.items()})
# T3 replay incl. issuer restart
s=steps(broker("replay")); first_ok=s["first"]["ok"]; rep1=s["replay_same_nonce"]
issuer.kill(); issuer.wait(); issuer=start([os.path.join(HERE,"issuer.py"),issuer_sock,os.path.join(keys,"issuer.pem"),sd,os.path.join(keys,"nonces.txt")],"ISSUER READY")
sock=socket.socket(socket.AF_UNIX); sock.connect(issuer_sock); f=sock.makefile("rw"); send_line(f,{"operation":{"statement_digest":sd,"nonce":s["first"]["nonce"],"tool":"write_note","args_digest":"x","impl_digest":"x"}}); rep2=recv_line(f); sock.close()
rec("T3","replayed nonce refused; still refused after issuer restart (durable nonce book)", first_ok and rep1["ok"]==False and "nonce-used" in rep1["reason"] and rep2["ok"]==False and rep2["reason"]=="nonce-used", {"first":first_ok,"replay":rep1.get("reason"),"after_restart":rep2.get("reason")})
# T4 tamper
s=steps(broker("tamper"))
rec("T4","one-bit signature change refused; clean grant accepted", s["tampered"]["ok"]==False and s["tampered"]["reason"]=="signature-invalid" and s["clean"]["ok"], {k:(v.get("reason") or "ok") for k,v in s.items()})
# T5 semantic binding: substitute the implementation (same name, same args)
src=open(os.path.join(HERE,"tools.py")).read(); open(os.path.join(HERE,"tools.py"),"w").write(src.replace('open(p,"w").write(text)','open(p,"w").write(text.upper())  # substituted provider'))
s=steps(broker("semantic")); open(os.path.join(HERE,"tools.py"),"w").write(src)
s2=steps(broker("allowlist"))
rec("T5","provider substitution (implementation bytes changed after activation) refused at check-at-use; original accepted", s["substituted_impl"]["ok"]==False and "definition-mismatch" in s["substituted_impl"]["reason"] and s2["good_tool"]["ok"], {"substituted":s["substituted_impl"].get("reason"),"restored":"ok" if s2["good_tool"]["ok"] else "fail"})
# T6 amendment boundary + new epoch by activator only
s=steps(broker("amend")); st2,sd2=make_statement(2)
issuer.kill(); issuer.wait(); issuer=start([os.path.join(HERE,"issuer.py"),issuer_sock,os.path.join(keys,"issuer.pem"),sd2,os.path.join(keys,"nonces.txt")],"ISSUER READY")
r2=steps(broker("allowlist",st2)); last=json.loads(open(log_path).read().splitlines()[-1])
rec("T6","guest amendment refused; allowlist unchanged afterwards; new epoch only via activator, visible as a new statement digest in leaves",
    s["amend"]["ok"]==False and "amendment-boundary" in s["amend"]["reason"] and s["after_amend"]["reason"]=="not-in-allowlist" and r2["good_tool"]["ok"] and last["operation"]["statement_digest"]==sd2 and sd2!=sd, {"amend":s["amend"].get("reason"),"epoch2_digest_in_leaf":last["operation"]["statement_digest"][:12]})
# T7 evidence: log matches anchor; edited leaf detected; fake appended leaf detected
lines=open(log_path).read().splitlines(); leaves=[leaf_hash(l.encode()) for l in lines]
sock=socket.socket(socket.AF_UNIX); sock.connect(anchor_sock); f=sock.makefile("rw"); send_line(f,{"kind":"get"}); anch=recv_line(f); sock.close()
match=anch["size"]==len(leaves) and anch["root"]==mth(leaves).hex()
edited=lines[:]; edited[2]=edited[2].replace("settlement","settIement"); ed_detect=mth([leaf_hash(l.encode()) for l in edited]).hex()!=anch["root"]
fake=lines+[json.dumps({"kind":"settlement","operation":{"tool":"write_note","statement_digest":sd},"forged":True})]; fk_detect=mth([leaf_hash(l.encode()) for l in fake]).hex()!=anch["root"] and len(fake)!=anch["size"]
settle_paths={json.loads(l)["effect"]["path"] for l in lines if '"kind": "settlement"' in l}; disk_paths={os.path.join(governed,"notes",f) for f in os.listdir(os.path.join(governed,"notes"))}
n_settle=len(settle_paths); n_files=len(disk_paths); paths_match=(settle_paths==disk_paths)
rec("T7","every governed file has a settlement leaf and vice versa (content-addressed: same text = same file); anchor root matches log; edited leaf and forged appended leaf both detected against the anchor", match and ed_detect and fk_detect and paths_match, {"anchor":anch,"distinct_effect_paths_in_leaves":n_settle,"files_on_disk":n_files,"sets_equal":paths_match,"edit_detected":ed_detect,"forgery_detected":fk_detect})
# T8 self-issue
s=steps(broker("selfissue"))
rec("T8","hand-minted grant with a random key refused; guest cannot read the issuer key (T1)", s["hand_minted"]["ok"]==False and s["hand_minted"]["reason"]=="signature-invalid", s["hand_minted"].get("reason"))
for p in procs: p.kill()
json.dump({"run_dir":run,"anchor_final":anch,"results":results},open(os.path.join(HERE,"RESULTS.json"),"w"),indent=1)
print("\nSUMMARY:",sum(r["status"]=="PASS" for r in results),"/",len(results),"PASS ; anchor root",anch["root"][:16],"size",anch["size"])
open(os.path.join(HERE,"ANCHOR.txt"),"w").write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} size={anch['size']} root={anch['root']}\n")
