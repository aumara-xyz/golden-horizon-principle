"""Mutation for the x=36 uptick: larger N and prolate degree."""
import sys, json, time
sys.path.insert(0,"codex-r5")
import run_prolate_exact_grid as g
out=[]
for x,N,lmax in [(36,280,380),(30,240,340)]:
    g.PRIMARY_N=N; g.FINAL_FIVE=(); g.PRIMARY_LMAX=lmax; g.MUTATION_LMAX=lmax-40
    t=time.time(); r=g.run_x_family(x); r["wall_s"]=time.time()-t
    for row in r["rows"]: print("RESULT x=%d N=%d lmax=%d sin_angle=%s"%(x,row["N"],lmax,row["metrics"]["actual_sin_angle"]),flush=True)
    out.append(r); json.dump(out,open("followup2b-mutation.json","w"),indent=1,default=str)
print("DONE")
