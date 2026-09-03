"""Follow-up 2: angle vs x at larger x with N scaled ~ 6-7x. Reuses Codex's exact-projection pipeline unchanged."""
import sys, json, time, mpmath as mp
sys.path.insert(0, "codex-r5")
import run_prolate_exact_grid as g
cases=[(25,160,260),(30,200,300),(36,240,340)]
out=[]
for x,N,lmax in cases:
    g.PRIMARY_N=N; g.FINAL_FIVE=(); g.PRIMARY_LMAX=lmax; g.MUTATION_LMAX=lmax-40
    t=time.time(); r=g.run_x_family(x); r["N_used"]=N; r["lmax"]=lmax; r["wall_s"]=time.time()-t
    for row in r["rows"]: print("RESULT x=%d N=%d sin_angle=%s gap=%s r/gap=%s"%(x,row["N"],row["metrics"]["actual_sin_angle"],row["metrics"]["gap"],row["metrics"]["residual_over_gap"]),flush=True)
    out.append(r); json.dump(out,open("followup2-angle-vs-x.json","w"),indent=1,default=str)
print("FOLLOWUP2 DONE")
