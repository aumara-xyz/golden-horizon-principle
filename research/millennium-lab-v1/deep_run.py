"""Deep run: does the angle stabilize as N and prolate degree grow? x=13 (N=160,200), x=25 (N=200/300, 240/340), x=30 (N=280/380, 320/420)."""
import sys, json, time
sys.path.insert(0,"codex-r5")
import run_prolate_exact_grid as g
cases=[(13,160,240),(13,200,280),(25,200,300),(25,240,340),(30,280,380),(30,320,420)]
out=[]
for x,N,lmax in cases:
    g.PRIMARY_N=N; g.FINAL_FIVE=(); g.PRIMARY_LMAX=lmax; g.MUTATION_LMAX=lmax-40
    t=time.time(); r=g.run_x_family(x); r["wall_s"]=time.time()-t
    for row in r["rows"]: print("RESULT x=%d N=%d lmax=%d sin_angle=%s wall=%.0fs"%(x,row["N"],lmax,str(row["metrics"]["actual_sin_angle"])[:12],r["wall_s"]),flush=True)
    out.append(r); json.dump(out,open("deep-run-angle-convergence.json","w"),indent=1,default=str)
print("DEEP DONE")
