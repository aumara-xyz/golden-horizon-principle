"""D24 exact-rational checks of SAVED D21.1 witnesses and D22 energy gates.

No integration, matrix assembly, eigensolver, or fresh scalar scoring occurs.
All decimal Arb endpoints are parsed outward through the sibling certificate
checker's Fraction helper. A positive R endpoint can establish W > 0 only
conditional on the analytically identified W >= R route. Negative R never
establishes negative W. One survivor omits its R endpoints; this checker marks
that survivor's route as not independently endpoint-replayed.

Default: stdout JSON. --output may write only directly inside this review
directory. Source/evidence files outside this directory are read-only.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from check_saved_certificates import SAFE_MU, endpoints, shifted_schur


REVIEW = Path(__file__).resolve().parent
REPO = REVIEW.parent.parent
MONOTONE_ROUTE = "monotonicity W>=R_128 (T=128>=T_env)"
D21_RESULT = "experiments/fable_d21_test1/d21_1_results.json"
D21_VECTORS = "experiments/fable_d21_test1/d21_results.json"


def scalar_interval(pair):
    """Outward hull of separately printed lower and upper endpoint balls."""
    lo = endpoints(pair["lower"])[0]
    hi = endpoints(pair["upper"])[1]
    if lo > hi:
        raise ValueError("Reversed saved endpoint pair")
    return lo, hi


def sign(interval):
    lo, hi = interval
    if lo > 0:
        return "POSITIVE"
    if hi < 0:
        return "NEGATIVE"
    return "UNRESOLVED"


def routed_sign(w_interval, r_interval=None, *, w_ge_r=False):
    """Never infer negative W from a lower form's negative value."""
    direct = sign(w_interval)
    if direct != "UNRESOLVED":
        return direct
    if w_ge_r and r_interval is not None and r_interval[0] > 0:
        return "POSITIVE"
    return "UNRESOLVED"


def overlap(left, right):
    return max(left[0], right[0]) <= min(left[1], right[1])


def display_ratio(value):
    # All decisions use Fraction. Decimal is presentation only.
    with localcontext() as context:
        context.prec = 14
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def control_checks():
    tests = {
        "positive_strict_endpoint": sign((Fraction(1), Fraction(2))) == "POSITIVE",
        "negative_strict_endpoint": sign((Fraction(-2), Fraction(-1))) == "NEGATIVE",
        "crossing_zero_rejected": sign((Fraction(-1), Fraction(1))) == "UNRESOLVED",
        "touching_zero_not_strict_positive": sign((Fraction(0), Fraction(1))) == "UNRESOLVED",
        "outward_ball_parsing": scalar_interval({
            "lower": "[1 +/- 0.01]", "upper": "[2 +/- 0.02]"})
            == (Fraction("0.99"), Fraction("2.02")),
        "positive_lower_form_route_accepted": routed_sign(
            (Fraction(-1), Fraction(2)), (Fraction(1), Fraction(2)),
            w_ge_r=True) == "POSITIVE",
        "negative_lower_form_not_negative_witness": routed_sign(
            (Fraction(-2), Fraction(2)), (Fraction(-4), Fraction(-3)),
            w_ge_r=True) == "UNRESOLVED",
        "crossing_lower_form_route_rejected": routed_sign(
            (Fraction(-2), Fraction(2)), (Fraction(-1), Fraction(1)),
            w_ge_r=True) == "UNRESOLVED",
        "missing_monotonicity_assumption_rejected": routed_sign(
            (Fraction(-2), Fraction(2)), (Fraction(1), Fraction(2)),
            w_ge_r=False) == "UNRESOLVED",
        "missing_r_endpoints_route_not_replayed": routed_sign(
            (Fraction(-2), Fraction(2)), None, w_ge_r=True) == "UNRESOLVED",
        "endpoint_only_gate_equality_not_strict_failure": not (
            Fraction("1.1") > Fraction(11, 10) * Fraction(1)),
    }
    try:
        scalar_interval({"lower": "nan", "upper": "2"})
    except ValueError:
        tests["nonfinite_endpoint_rejected"] = True
    else:
        tests["nonfinite_endpoint_rejected"] = False
    if not all(tests.values()):
        raise AssertionError(tests)
    return tests


class Inputs:
    def __init__(self):
        self.hashes = {}

    def raw(self, name):
        path = (REPO / name).resolve()
        if REPO not in path.parents:
            raise ValueError("Input outside repository")
        content = path.read_bytes()
        self.hashes[name] = hashlib.sha256(content).hexdigest()
        return content

    def json(self, name):
        return json.loads(self.raw(name))


def audit_d21(inputs):
    data = inputs.json(D21_RESULT)
    vectors = inputs.json(D21_VECTORS)
    expected_keys = {
        f"{case} {parity} T{cutoff}"
        for case in ("delete_4", "delete_2", "prime_free")
        for parity in ("even", "odd")
        for cutoff in (160, 240)
    }
    if set(data["cases"]) != expected_keys:
        raise ValueError("D21.1 case inventory differs from the frozen twelve cases")
    if not expected_keys.issubset(vectors["cases"]):
        raise ValueError("Missing D21 frozen vector")

    rows = []
    for key in sorted(expected_keys):
        saved = data["cases"][key]
        frozen = vectors["cases"][key]
        case, parity, t_tag = key.split()
        selector_t = int(t_tag[1:])
        expected_w = "POSITIVE" if case == "delete_4" else "NEGATIVE"
        expected_r = "POSITIVE" if case == "delete_4" and parity == "even" else "NEGATIVE"
        w = scalar_interval(saved["W"])
        r = scalar_interval(saved["R128"])
        direct = sign(w)
        route = saved["W_route"]
        if route not in ("direct", MONOTONE_ROUTE):
            raise ValueError("Unknown sign route: " + route)
        # This is source/model validation, not a new quadrature proof. Each
        # frozen case only deletes positive zeta weights at L=0.7. With beta
        # formed using the original full comb, monotonicity of a(t) gives
        # Psi_kept(t) >= beta for |t| >=128, so W >= R128 on that same wave.
        envelope_scope = (
            saved["scoring_cutoff"] == 128 and case in
            ("delete_4", "delete_2", "prime_free"))
        inferred = routed_sign(w, r, w_ge_r=(route == MONOTONE_ROUTE and envelope_scope))
        excess = scalar_interval(saved["excess"])
        i4 = scalar_interval(saved["I4"])
        parity_bit = 0 if parity == "even" else 1
        checks = {
            "selector_cutoff_metadata_matches": saved["selector_T"] == selector_t,
            "scoring_cutoff_is_128": saved["scoring_cutoff"] == 128,
            "coefficient_degree_lengths_match": len(frozen["degrees"]) == len(frozen["frozen_coefficients"]),
            "frozen_degrees_match_parity": all(n % 2 == parity_bit for n in frozen["degrees"]),
            "r_sign_matches_export": sign(r) == saved["R128_sign"],
            "r_sign_matches_printed_d21_1_table": sign(r) == expected_r,
            "w_route_matches_export": inferred == saved["W_sign"],
            "w_route_matches_printed_d21_1_table": inferred == expected_w,
            "direct_reparse_matches_export": direct == saved.get("endpoint_reparse_sign"),
            "excess_nonnegative_flag_matches_endpoints": (excess[0] >= 0) == saved["excess_certain_nonneg"],
            "i4_sign_matches_export": sign(i4) == saved["I4_sign"],
        }
        survivor = saved["survivor_K80_400"]
        sw = scalar_interval(survivor["W"])
        survivor_direct = sign(sw)
        survivor_route = survivor["route"]
        if survivor_route == "direct":
            survivor_status = "MEASURED: direct saved endpoints replayed"
            survivor_replayed = survivor_direct
            checks["survivor_direct_sign_matches_export"] = survivor_direct == survivor["W_sign"]
            checks["survivor_sign_matches_main_route"] = survivor_direct == inferred
        elif survivor_route == MONOTONE_ROUTE:
            # No R128 field was exported by this survivor, so the recorded
            # positive route cannot be independently reconstructed here.
            survivor_status = "UNVERIFIED: survivor R128 endpoints not exported; route not independently endpoint-replayed"
            survivor_replayed = "UNRESOLVED"
            checks["survivor_missing_r_scope_reported"] = (
                "R128" not in survivor and survivor_direct == "UNRESOLVED")
            checks["survivor_reported_sign_agrees_but_not_replayed"] = survivor["W_sign"] == inferred
        else:
            raise ValueError("Unknown survivor route")
        checks["survivor_complete_enclosure_overlaps_main"] = overlap(sw, w)
        vector_bytes = json.dumps({
            "degrees": frozen["degrees"],
            "coefficients": frozen["frozen_coefficients"],
        }, sort_keys=True, separators=(",", ":")).encode()
        rows.append({
            "case": key,
            "expected_table_w_sign": expected_w,
            "direct_endpoint_w_sign": direct,
            "r128_endpoint_sign": sign(r),
            "accepted_w_sign_with_stated_route": inferred,
            "route": route,
            "route_analytic_assumption": "identified W >= R128 inequality; no fresh function scoring" if route != "direct" else None,
            "frozen_vector_sha256": hashlib.sha256(vector_bytes).hexdigest(),
            "survivor_direct_endpoint_sign": survivor_direct,
            "survivor_replayed_sign": survivor_replayed,
            "survivor_status": survivor_status,
            "checks": checks,
            "all_checks_passed": all(checks.values()),
        })
    return rows


def audit_d22(inputs):
    rows = []
    for parity in ("even", "odd"):
        for width in ("0.4", "0.5", "0.6", "0.7"):
            name = ("experiments/fable_d22_test2/"
                    f"d22_score_cand2_{parity}_L{width}.json")
            data = inputs.json(name)
            cutoff = 240 if (parity, width) == ("even", "0.5") else 512
            trial = next(row for row in data["trials"] if row["cutoff"] == cutoff)
            low, high = scalar_interval(trial["W"])
            mu_text = SAFE_MU[(parity, width, 160)]
            mu = Fraction(mu_text)
            cert_name = ("experiments/fable_d22_test2/"
                         f"d22_cert_{parity}_L{width}_T160_N160.json")
            cert = inputs.json(cert_name)
            repaired = shifted_schur(cert, mu_text)
            checks = {
                "metadata_matches_filename": (data["L"], data["parity"]) == (width, parity),
                "repaired_safe_mu_accepted_by_sibling_checker": repaired["accepted"],
                "strict_positive_scalar_endpoint": low > 0,
                "same_candidate_cannot_close_ten_percent": low > Fraction(11, 10) * mu,
                "saved_lower_does_not_exceed_saved_upper": low <= high,
            }
            row = {
                "L": width,
                "parity": parity,
                "score_file": name,
                "scoring_cutoff": cutoff,
                "safe_mu": mu_text,
                "safe_mu_source": cert_name,
                "scalar_lower_outward_exact": str(low),
                "scalar_lower_over_mu_exact": str(low / mu),
                "scalar_lower_over_mu_approx_display_only": display_ratio(low / mu),
                "clearance_above_1_1_mu_exact": str(low - Fraction(11, 10) * mu),
                "checks": checks,
                "all_checks_passed": all(checks.values()),
            }
            if width == "0.7":
                stronger_mu_text = SAFE_MU[(parity, width, 240)]
                stronger_mu = Fraction(stronger_mu_text)
                stronger_name = ("experiments/fable_d22_test2/"
                                 f"d22_cert_{parity}_L0.7_T240_N192.json")
                stronger_cert = inputs.json(stronger_name)
                stronger_repaired = shifted_schur(stronger_cert, stronger_mu_text)
                stronger_rejected = low > Fraction(11, 10) * stronger_mu
                row["stronger_t240_operator_bound"] = {
                    "safe_mu": stronger_mu_text,
                    "certificate": stronger_name,
                    "safe_mu_repair_accepted": stronger_repaired["accepted"],
                    "candidate_still_fails_ten_percent_gate": stronger_rejected,
                    "ratio_display_only": display_ratio(low / stronger_mu),
                }
                row["all_checks_passed"] &= stronger_repaired["accepted"] and stronger_rejected
            rows.append(row)
    return rows


def audit():
    controls = control_checks()
    inputs = Inputs()
    for source in (
        "experiments/astra_d24_review/check_saved_witnesses.py",
        "experiments/astra_d24_review/check_saved_certificates.py",
        "experiments/fable_d21_test1/d21_1.py",
        "experiments/fable_d21_test1/d21.py",
        "experiments/fable_d21_test1/RESULTS.md",
        "experiments/fable_d21_test1/d9_score_copy.py",
        "experiments/fable_d22_test2/RESULTS.md",
        "experiments/fable_d22_test2/d22_score.py",
        "experiments/fable_d22_test2/d22_candidates2.py",
        "experiments/fable_d22_test2/d22_certify.py",
        "experiments/weil_hidden_modes/d5_certify.py",
    ):
        inputs.raw(source)
    d21 = audit_d21(inputs)
    d22 = audit_d22(inputs)
    return {
        "status": "MEASURED: exact-rational audit of saved endpoints only",
        "scope": "No new integration, spectral solve, candidate selection, or full certificate replay",
        "controls": controls,
        "source_and_input_sha256": inputs.hashes,
        "d21_1_cases": d21,
        "d21_1_summary": {
            "cases": len(d21),
            "direct_signs_endpoint_replayed": sum(row["direct_endpoint_w_sign"] != "UNRESOLVED" for row in d21),
            "main_positive_routes_using_saved_r128": sum(row["route"] == MONOTONE_ROUTE for row in d21),
            "survivor_direct_signs_endpoint_replayed": sum(row["survivor_replayed_sign"] != "UNRESOLVED" for row in d21),
            "survivor_routes_not_independently_endpoint_replayed": sum(row["survivor_replayed_sign"] == "UNRESOLVED" for row in d21),
        },
        "d22_fixed_candidate_energy_gates": d22,
        "all_asserted_endpoint_checks_pass": all(row["all_checks_passed"] for row in d21 + d22),
        "limitations": [
            "Saved enclosures are assumed to arise from the identified valid scalar scorer; no quadrature rerun here.",
            "Positive fixed-wave scores do not prove positivity on all waves.",
            "The monotonicity survivor omits R128 endpoints, so only its reported route—not its independent route evidence—is available.",
            "D22 safe operator constants are conditional on the sibling checker's corrected analytic/scalar certificate assumptions.",
            "An energy-gate failure excludes only this candidate paired with this lower bound; it does not determine the full infimum.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional output JSON directly inside the review directory")
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        destination = Path(args.output).resolve()
        if destination.parent != REVIEW:
            raise ValueError("Output must be directly inside " + str(REVIEW))
        destination.write_text(rendered)
    print(rendered, end="")
    if not result["all_asserted_endpoint_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
