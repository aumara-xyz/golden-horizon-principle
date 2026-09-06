"""Reuse unchanged D7 only for preregistered candidate selection, own output directory."""
from pathlib import Path
import runpy, sys, os, json, hashlib

root = Path(__file__).resolve().parent
source = root.parent / 'weil_hidden_modes' / 'opus_d7_rebuild.py'
parity = sys.argv[1]
assert parity in ('even','odd')
os.chdir(root)
sys.argv = [str(source), parity, '80', '1']
d = runpy.run_path(str(source), run_name='__main__')
mp = d['mp']
out = dict(parity=parity, L='0.7', selection='unchanged D7 R_T minimizer; T=120, NE=80',
           source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
           degrees=d['ns'], coefficients=[mp.nstr(d['Vmp'][i,0],40) for i in range(80)])
(root / ('frozen_'+parity+'.json')).write_text(json.dumps(out,indent=2)+'\n')
print('FROZEN',parity,flush=True)
