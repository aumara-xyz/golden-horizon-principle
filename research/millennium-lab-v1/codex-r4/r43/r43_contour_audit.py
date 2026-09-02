#!/usr/bin/env python3
"""Registered-mesh contour audit for r43_polymath.py output.

This reuses the already refined real roots but reevaluates every contour from
the defining Phi integral.  Conjugation symmetry is used only to avoid doing
the same quadrature twice.  Results remain numerical, not interval-certified.
"""

import hashlib
import importlib.util
import json
import time
from pathlib import Path

from mpmath import mp


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r43_polymath", HERE / "r43_polymath.py")
R43 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R43)


def symmetric_values(q, t, points):
    cache = {}
    values = []
    for z in points:
        z = mp.mpc(z)
        upper = mp.conj(z) if z.imag < 0 else z
        key = (mp.nstr(upper.real, 45), mp.nstr(upper.imag, 45))
        if key not in cache:
            cache[key] = q.scaled_h(upper, t)
        values.append(mp.conj(cache[key]) if z.imag < 0 else cache[key])
    return values


def one_audit(q, t, roots, edge_mesh, local_mesh):
    start = time.time()
    boundary = R43.contour_rectangle(210, 300, 1, edge_mesh)
    bw, braw, bmin, bstep = R43.winding(symmetric_values(q, t, boundary))
    local = []
    for i, root in enumerate(roots):
        nearest = min(
            root - (roots[i - 1] if i else mp.mpf(210)),
            (roots[i + 1] if i + 1 < len(roots) else mp.mpf(300)) - root,
        )
        radius = min(mp.mpf("0.2"), mp.mpf("0.3") * nearest)
        pts = R43.contour_circle(root, radius, local_mesh)
        lw, lraw, lmin, lstep = R43.winding(symmetric_values(q, t, pts))
        local.append(
            {
                "root": mp.nstr(root, 45),
                "winding": lw,
                "winding_raw": mp.nstr(lraw, 25),
                "radius": mp.nstr(radius, 20),
                "min_scaled_abs": mp.nstr(lmin, 16),
                "max_arg_step": mp.nstr(lstep, 16),
                "abs_integral_derivative": mp.nstr(abs(q.derivative(root, t)), 20),
            }
        )
    return {
        "t": mp.nstr(t, 8),
        "quadrature": {
            "dps": q.dps,
            "degree": q.degree,
            "nodes": len(q.u),
            "u_max": mp.nstr(q.u_max, 8),
            "phi_terms": q.nphi,
        },
        "edge_mesh_per_edge": edge_mesh,
        "local_mesh": local_mesh,
        "rectangle_winding": bw,
        "rectangle_winding_raw": mp.nstr(braw, 25),
        "rectangle_min_scaled_abs": mp.nstr(bmin, 16),
        "rectangle_max_arg_step": mp.nstr(bstep, 16),
        "local_winding_sum": sum(row["winding"] for row in local),
        "all_local_windings_one": all(row["winding"] == 1 for row in local),
        "all_derivatives_nonzero_numerically": all(mp.mpf(row["abs_integral_derivative"]) > 0 for row in local),
        "roots": local,
        "elapsed_seconds": round(time.time() - start, 3),
    }


def main():
    # Preserve the serialized arbitrary-precision root centers.  Parsing before
    # setting mp.dps would silently round them at mpmath's default precision.
    mp.dps = 100
    source = json.loads((HERE / "r43_results.json").read_text())
    by_label = {case["label"]: case for case in source["cases"]}
    roots20 = [mp.mpf(row["root"]) for row in by_label["primary_t_0.2"]["roots"]]
    roots19 = [mp.mpf(row["root"]) for row in by_label["mutation_t_0.19"]["roots"]]
    roots0 = [mp.mpf(row["root"]) for row in by_label["control_t_0"]["roots"]]

    q70 = R43.PhiQuadrature(70, 8)
    cases = {}
    cases["primary_registered_48"] = one_audit(q70, mp.mpf(".2"), roots20, 48, 32)
    print("finished primary_registered_48", flush=True)
    cases["primary_same_quadrature_96"] = one_audit(q70, mp.mpf(".2"), roots20, 96, 48)
    print("finished primary_same_quadrature_96", flush=True)
    cases["mutation_registered_48"] = one_audit(q70, mp.mpf(".19"), roots19, 48, 24)
    print("finished mutation_registered_48", flush=True)
    cases["mutation_double_96"] = one_audit(q70, mp.mpf(".19"), roots19, 96, 48)
    print("finished mutation_double_96", flush=True)
    cases["control_registered_48"] = one_audit(q70, mp.mpf("0"), roots0, 48, 24)
    print("finished control_registered_48", flush=True)
    cases["control_double_96"] = one_audit(q70, mp.mpf("0"), roots0, 96, 48)
    print("finished control_double_96", flush=True)

    q100 = R43.PhiQuadrature(100, 9)
    cases["primary_high_precision_96"] = one_audit(q100, mp.mpf(".2"), roots20, 96, 48)
    print("finished primary_high_precision_96", flush=True)

    result = {
        "schema": "codex-r4-r43-contour-audit-v1",
        "status": "MEASURED",
        "source_results_sha256": hashlib.sha256((HERE / "r43_results.json").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "method": "Defining-Phi-integral contour winding; conjugation symmetry; no interval arithmetic.",
        "cases": cases,
        "interpretation": {
            "registered_rectangle": "210 <= Re(z) <= 300, |Im(z)| <= 1",
            "stable_counts": {
                "t_0.2": [cases["primary_registered_48"]["rectangle_winding"], cases["primary_same_quadrature_96"]["rectangle_winding"], cases["primary_high_precision_96"]["rectangle_winding"]],
                "t_0.19": [cases["mutation_registered_48"]["rectangle_winding"], cases["mutation_double_96"]["rectangle_winding"]],
                "t_0": [cases["control_registered_48"]["rectangle_winding"], cases["control_double_96"]["rectangle_winding"]],
            },
            "certification": "UNVERIFIED: meshes and quadrature convergence are numerical, not interval/Rouche bounds on all arcs.",
        },
    }
    (HERE / "r43_contour_audit.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
