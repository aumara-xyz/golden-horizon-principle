"""D10 P1: interval checks of an exact local-kernel obstruction and its scope.

No zero ordinates, eigenvalue fitting, or optimization enter this experiment.
The 3x3 control is not a discretization of the Weil form.
"""
import hashlib
import itertools
import json
from pathlib import Path

from flint import arb, ctx
import flint

ctx.prec = 320
ROOT = Path(__file__).resolve().parent
L = arb(7) / 10
EPS = arb(1) / 100
EDGES = [(0, 1), (1, 2), (0, 2)]


def ends(x):
    assert x.is_finite()
    return {
        "lower_enclosure": arb(x.lower()).str(75),
        "upper_enclosure": arb(x.upper()).str(75),
    }


def sign(x):
    if not x.is_finite():
        return "UNVERIFIED"
    if x > 0:
        return "POSITIVE"
    if x < 0:
        return "NEGATIVE"
    return "UNVERIFIED"


def record(x):
    return {"display": x.str(30), "sign": sign(x), "endpoints": ends(x)}


def kernel(r):
    assert r > 0
    return 2 * (r / 2).cosh() - (r / 2).exp() / (2 * r.sinh())


def pole_free(r):
    assert r > 0
    return -(r / 2).exp() / (2 * r.sinh())


def gauges(values):
    output = []
    for signs in itertools.product((-1, 1), repeat=3):
        transformed = [
            signs[i] * signs[j] * value
            for (i, j), value in zip(EDGES, values)
        ]
        output.append({
            "gauge": list(signs),
            "edge_signs": [sign(v) for v in transformed],
            "all_nonpositive": all(v <= 0 for v in transformed),
            "strictly_positive_edges": [
                list(edge) for edge, value in zip(EDGES, transformed) if value > 0
            ],
        })
    return output


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), arb(0)) for row in matrix]


def quadratic(matrix, vector):
    return sum((x * y for x, y in zip(vector, matvec(matrix, vector))), arb(0))


def verify_exported_record(item):
    lo = arb(item["endpoints"]["lower_enclosure"]).lower()
    hi = arb(item["endpoints"]["upper_enclosure"]).upper()
    restored = "POSITIVE" if lo > 0 else "NEGATIVE" if hi < 0 else "UNVERIFIED"
    assert restored == item["sign"]


def run():
    controls = {}
    # Implementations must not turn an interval crossing zero into a sign.
    controls["positive_sign"] = sign(arb(1)) == "POSITIVE"
    controls["negative_sign"] = sign(arb(-1)) == "NEGATIVE"
    controls["singular_sign"] = sign(arb(0)) == "UNVERIFIED"
    controls["ambiguous_sign"] = sign(arb(0, 1)) == "UNVERIFIED"

    # Exact nonlocal sum of squares, with the same frustrated triangle.
    v = [arb(1), arb(-1), arb(1)]
    positive = [[v[i] * v[j] + (arb(1) / 2 if i == j else 0)
                 for j in range(3)] for i in range(3)]
    comparison = [[positive[i][j] if i == j else -abs(positive[i][j])
                   for j in range(3)] for i in range(3)]
    eigenvectors = [([arb(1), arb(1), arb(0)], arb(1) / 2),
                    ([arb(1), arb(0), arb(-1)], arb(1) / 2),
                    (v, arb(7) / 2)]
    controls["positive_exact_eigenpairs"] = all(
        all(a == value * b for a, b in zip(matvec(positive, vector), vector))
        for vector, value in eigenvectors
    )
    controls["positive_joint_sos_identity"] = all(
        positive[i][j] - (arb(1) / 2 if i == j else 0) == v[i] * v[j]
        for i in range(3) for j in range(3)
    )
    ones = [arb(1)] * 3
    comparison_rayleigh = quadratic(comparison, ones) / 3
    controls["comparison_negative_witness"] = comparison_rayleigh == -arb(1) / 2
    positive_edges = [positive[i][j] for i, j in EDGES]
    controls["positive_control_has_same_frustration"] = (
        [sign(x) for x in positive_edges] == ["NEGATIVE", "NEGATIVE", "POSITIVE"]
        and not any(x["all_nonpositive"] for x in gauges(positive_edges))
    )
    assert all(controls.values()), controls

    a = (arb(5) / 4).log()
    radii = [a + arb(0, 2 * EPS), 2 * a + arb(0, 2 * EPS)]
    controls["bumps_disjoint"] = 2 * EPS < a
    controls["bumps_inside_support"] = a + EPS < L
    controls["all_bump_cross_distances_below_first_prime_shift"] = radii[1] < arb(2).log()

    free_edges = [pole_free(radii[0]), pole_free(radii[0]), pole_free(radii[1])]
    free_gauges = gauges(free_edges)
    controls["pole_free_all_edges_negative"] = all(x < 0 for x in free_edges)
    controls["pole_free_unfrustrated"] = any(x["all_nonpositive"] for x in free_gauges)
    assert all(controls.values()), controls

    # Authentic kernel is accepted only after the scope controls above.
    point_values = [kernel(a), kernel(2 * a)]
    exact_values = [-arb(19) / (18 * arb(5).sqrt()), arb(5129) / 7380]
    exact_agreement = [x.overlaps(y) and (x - y).contains(0)
                       for x, y in zip(point_values, exact_values)]
    assert all(exact_agreement)
    neighborhood_values = [kernel(r) for r in radii]
    assert point_values[0] < 0 and point_values[1] > 0
    assert neighborhood_values[0] < 0 and neighborhood_values[1] > 0
    authentic_edges = [neighborhood_values[0], neighborhood_values[0], neighborhood_values[1]]
    authentic_gauges = gauges(authentic_edges)
    assert not any(x["all_nonpositive"] for x in authentic_gauges)
    assert all(x["strictly_positive_edges"] for x in authentic_gauges)

    mutation_gauges = gauges([authentic_edges[0], authentic_edges[1], -authentic_edges[2]])
    controls["long_edge_reversal_unfrustrated"] = any(
        x["all_nonpositive"] for x in mutation_gauges
    )
    assert all(controls.values()), controls

    output = {
        "status": "MEASURED",
        "prediction": "P1 held",
        "precision_bits": ctx.prec,
        "python_flint": flint.__version__,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "predictions_sha256": hashlib.sha256((ROOT / "PREDICTIONS.md").read_bytes()).hexdigest(),
        "support_half_width": "7/10",
        "bump_radius": "1/100",
        "center_shift": record(a),
        "exact_formulae": ["-19/(18*sqrt(5))", "5129/7380"],
        "point_kernel_values": [record(x) for x in point_values],
        "independent_algebraic_values": [record(x) for x in exact_values],
        "exact_formula_agreement": exact_agreement,
        "bump_distance_intervals": [record(x) for x in radii],
        "neighborhood_kernel_values": [record(x) for x in neighborhood_values],
        "gauge_edge_order": EDGES,
        "authentic_gauges": authentic_gauges,
        "pole_free_gauges": free_gauges,
        "long_edge_reversal_gauges": mutation_gauges,
        "positive_joint_sos_control": {
            "matrix": [[x.str(20) for x in row] for row in positive],
            "eigenvalues_exact": ["1/2", "1/2", "7/2"],
            "comparison_negative_rayleigh": record(comparison_rayleigh),
            "comparison_eigenvalues_exact": ["-1/2", "5/2", "5/2"],
            "note": "Independent toy matrix, not a restriction or discretization of W.",
        },
        "controls": controls,
        "scope": "Obstruction only to diagonal-gauge nonnegative-conductance pairwise-square representations. Not an obstruction to general SOS or positivity.",
    }
    records = [output["center_shift"], output["positive_joint_sos_control"]["comparison_negative_rayleigh"]]
    for key in ("point_kernel_values", "independent_algebraic_values", "bump_distance_intervals", "neighborhood_kernel_values"):
        records.extend(output[key])
    for item in records:
        verify_exported_record(item)
    output["endpoint_reparse_checks"] = len(records)
    target = ROOT / "kernel_results.json"
    target.write_text(json.dumps(output, indent=2) + "\n")
    reloaded = json.loads(target.read_text())
    assert all(reloaded["controls"].values())
    print("P1 held;", len(controls), "controls;", len(records), "endpoint reparses.")
    for label, value in zip(("K(a)", "K(2a)"), point_values):
        print(label, value.str(25))
    for label, value in zip(("short neighborhoods", "long neighborhood"), neighborhood_values):
        print(label, value.str(25))
    print("Authentic all-nonpositive gauges:", sum(x["all_nonpositive"] for x in authentic_gauges), "/ 8")
    print("Long-edge mutation all-nonpositive gauges:", sum(x["all_nonpositive"] for x in mutation_gauges), "/ 8")


if __name__ == "__main__":
    run()
