"""Governed effects. The broker hashes the SOURCE of each tool at statement time and again at dispatch (check-at-use)."""
import os, hashlib
def write_note(governed_dir, text):
    os.makedirs(os.path.join(governed_dir,"notes"),exist_ok=True)
    p=os.path.join(governed_dir,"notes",hashlib.sha256(text.encode()).hexdigest()[:16]+".txt")
    open(p,"w").write(text); return {"path":p,"sha256":hashlib.sha256(text.encode()).hexdigest()}
def read_note(governed_dir, sha_prefix):
    p=os.path.join(governed_dir,"notes",sha_prefix+".txt"); return {"text":open(p).read()}
TOOLS={"write_note":write_note,"read_note":read_note}
