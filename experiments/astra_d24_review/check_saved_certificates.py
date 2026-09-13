"""Exact-rational D24 audit of saved D22 certificate scalars.

This does NOT rerun matrix assembly, quadrature, eigensolvers, or Fourier tails.
It conditionally repairs the saved D5/D22 quadrature constant by rho**2 = 4:
the stored maxq bounds one-sided quadrature error before M = 2*(S +/- err).
The extra error per symmetric matrix entry is at most 6*maxq, hence its
operator norm is at most 6*N*maxq. We deduct that from the saved finite-block
lower endpoint, then test the SHIFTED Schur inequality in exact rationals.

Inputs remain evidence supplied by the original implementation: this checker
does not prove its Bessel, ellipse-supremum, pole, or discarded-space bounds.
See Hale--Trefethen (2008), Theorem 2.1, equation (2.3), for the n-point rule:
64*M / (15*(1-rho**(-2))*rho**(2*n)). D5 uses (rho**2-1) in the denominator
without the compensating rho**2 numerator. D7's independent rebuild avoided
that constant and is not invalidated by this repair.

Default: JSON on stdout only. --output writes only within this script's own
review directory. No dependencies beyond the Python standard library.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
from fractions import Fraction


REVIEW = Path(__file__).resolve().parent
REPO = REVIEW.parent.parent
EXPECTED_SOURCE_SHA256 = {
    "experiments/fable_d22_test2/d22_certify.py":
        "c94e4a1de435082c5bea2feecc601d3fdd2486e0f15b40694264cb51e34f7cbb",
    "experiments/weil_hidden_modes/d5_certify.py":
        "43f947310afce68a4975929b4b706a82002d46e0251cb2bc48cebc7c897cddf8",
    "experiments/weil_hidden_modes/d4_checker.py":
        "a1cea1c6afae50825d58aa2cfb083f3f85387c708a3831358c04d8b5206e410d",
    "experiments/weil_hidden_modes/certify.py":
        "756eb8327d42943210a3c72075103d7310ff6e98690a0d31c85b8b39d0c3adb8",
}

SAFE_MU = {
    ("even", "0.4", 160): "1.44919e-4",
    ("even", "0.5", 160): "7.14785e-7",
    ("even", "0.6", 160): "1.10135e-9",
    ("even", "0.7", 160): "2.67167e-13",
    ("even", "0.7", 240): "3.37581e-13",
    ("odd", "0.4", 160): "1.24019e-2",
    ("odd", "0.5", 160): "1.42134e-4",
    ("odd", "0.6", 160): "4.12866e-7",
    ("odd", "0.7", 160): "1.58596e-10",
    ("odd", "0.7", 240): "2.03304e-10",
}


def endpoints(value):
    """Parse a printed Arb enclosure OUTWARD, using exact decimal fractions."""
    text = str(value).strip()
    if any(token in text.lower() for token in ("nan", "inf")):
        raise ValueError("Nonfinite certificate input")
    if text.startswith("["):
        if not text.endswith("]"):
            raise ValueError("Malformed enclosure")
        mid, radius = text[1:-1].split("+/-")
        m = Fraction(mid.strip() or "0")
        r = Fraction(radius.strip())
        if r < 0:
            raise ValueError("Negative radius")
        return m-r, m+r
    x = Fraction(text)
    return x, x


def upper_nonnegative(data, name):
    lo, hi = endpoints(data[name])
    # A display interval may cross zero for a tiny nonnegative bound. Its
    # upper endpoint remains usable; reject a genuinely negative upper bound.
    if hi < 0:
        raise ValueError("Negative bound: " + name)
    return hi


def repaired_scalars(data):
    if data.get("rho") != 2:
        raise ValueError("The frozen factor-four repair requires rho = 2")
    n = data["NE"]
    if not isinstance(n, int) or n < 1:
        raise ValueError("Invalid matrix dimension")
    finite_old = endpoints(data["lambda0_certified"])[0]
    maxq = upper_nonnegative(data, "max_quadrature_error_bound")
    extra_error = 6*n*maxq
    finite_repaired = finite_old-extra_error
    eps_d = upper_nonnegative(data, "eps_D")
    eps_c = upper_nonnegative(data, "eps_C")
    eps_p = upper_nonnegative(data, "eps_p")
    norm_p = upper_nonnegative(data, "norm_pN")
    beta = endpoints(data["beta_star"])[0]
    discarded = beta-eps_d-2*eps_p*eps_p
    coupling = eps_c+2*norm_p*eps_p
    return finite_repaired, discarded, coupling, extra_error


def shifted_schur(data, advertised):
    """Certify R >= mu I by positivity of its two-block bound AFTER shift."""
    mu = Fraction(advertised)
    finite, discarded, coupling, extra = repaired_scalars(data)
    a, d = finite-mu, discarded-mu
    accepted = mu > 0 and a > 0 and d > 0 and a*d > coupling*coupling
    return {
        "advertised_mu": advertised,
        "accepted": accepted,
        "finite_block_minus_mu_positive": a > 0,
        "discarded_block_minus_mu_positive": d > 0,
        "shifted_determinant_positive": a*d > coupling*coupling,
        # These have moderate size. Do not serialize huge squared tail
        # denominators merely to prove they were not converted to floats.
        "extra_quadrature_operator_error_exact_rational": str(extra),
        "repaired_finite_lower_exact_rational": str(finite),
        "nonzero_pole_tail_preserved": upper_nonnegative(data, "eps_p") > 0,
    }


def synthetic(**overrides):
    row = {
        "rho": 2, "NE": 2, "lambda0_certified": "1",
        "max_quadrature_error_bound": "0", "eps_D": "0",
        "eps_C": "0", "eps_p": "0", "norm_pN": "0",
        "beta_star": "2",
    }
    row.update(overrides)
    return row


def controls():
    tests = {}
    tests["exact_decimal_enclosure"] = endpoints("[1e-13 +/- 1e-25]") == (
        Fraction("1e-13")-Fraction("1e-25"),
        Fraction("1e-13")+Fraction("1e-25"))
    tests["crossing_enclosure_rejected"] = not shifted_schur(
        synthetic(lambda0_certified="[+/- 1e-13]"), "1e-15")["accepted"]
    tests["upward_rounded_claim_rejected"] = not shifted_schur(
        synthetic(lambda0_certified="[1e-13 +/- 1e-25]"), "1e-13")["accepted"]
    tests["lower_claim_accepted"] = shifted_schur(
        synthetic(lambda0_certified="[1e-13 +/- 1e-25]"), "9.99e-14")["accepted"]
    tiny = Fraction("1e-1000")
    tests["arbitrarily_tiny_tail_not_zero"] = tiny > 0 and tiny*tiny > 0
    # The spectral shift is only 1e-900 below the finite block. A coupling
    # of 1e-400 has a square larger than that slack and must not underflow.
    almost_one = str(Fraction(1)-Fraction("1e-900"))
    tests["tiny_coupling_can_reject_near_endpoint"] = not shifted_schur(
        synthetic(eps_C="1e-400"), almost_one)["accepted"]
    tests["pole_tail_retained_in_discarded_bound"] = (
        repaired_scalars(synthetic(eps_p="1e-1000"))[1]
        < Fraction(2))
    # Finite-block positivity is not full-block positivity when coupling
    # overwhelms the determinant.
    tests["excess_coupling_rejected"] = not shifted_schur(
        synthetic(lambda0_certified="1e-13", eps_C="1e-3"),
        "1e-14")["accepted"]
    if not all(tests.values()):
        raise AssertionError(tests)
    return tests


def effective_source_hash(source, data):
    """Reproduce wrapper substitutions as TEXT ONLY; never execute them."""
    original = "L=arb('7/10'); T=120;"
    if source.count(original) != 1:
        raise ValueError("Unexpected parameter-substitution target count")
    source = source.replace(original, f"L=arb('{data['L']}'); T={data['T']};")
    source, count = re.subn(
        r"for k in \(12,13,14,15,16,17,18\):\n.*?\n.*?\n",
        "", source, flags=re.S)
    if count != 1:
        raise ValueError("Unexpected LDL-loop substitution count")
    replacements = (
        ("r0=ldl(A,'0')", "r0={'positive':None}"),
        ('out={"run":5,',
         'out={"run":22,"L":LSTR,"T":TVAL,"minimizer_frozen_40dig":'
         '[mp.nstr(Vmp[i,0],40) for i in range(NE)],'
         '"modes":[int(n) for n in ns],'),
        ('open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w")',
         'open(f"d22_cert_{PAR}_L{LSTR}_T{TVAL}_N{NE}.json","w")'),
    )
    for old, new in replacements:
        if source.count(old) != 1:
            raise ValueError("Unexpected wrapper target: " + old)
        source = source.replace(old, new)
    return hashlib.sha256(source.encode()).hexdigest()


def audit():
    test_results = controls()
    hashes = {}
    for name, expected in EXPECTED_SOURCE_SHA256.items():
        actual = hashlib.sha256((REPO/name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Source differs from D24 reviewed snapshot: " + name)
        hashes[name] = actual
    template = (REPO/"experiments/weil_hidden_modes/d5_certify.py").read_text()
    rows = []
    for (parity, width, cutoff), mu in SAFE_MU.items():
        n = 192 if cutoff == 240 else 160
        relative = (f"experiments/fable_d22_test2/"
                    f"d22_cert_{parity}_L{width}_T{cutoff}_N{n}.json")
        raw = (REPO/relative).read_bytes()
        data = json.loads(raw)
        if (data["parity"], data["L"], data["T"], data["NE"]) != (
                parity, width, cutoff, n):
            raise ValueError("Certificate filename/metadata mismatch")
        row = shifted_schur(data, mu)
        row.update({
            "certificate": relative,
            "certificate_sha256": hashlib.sha256(raw).hexdigest(),
            "effective_source_sha256": effective_source_hash(template, data),
            "parameters": {"L": width, "T": cutoff, "N": n,
                           "K": data["GL_nodes_per_unit_panel"], "parity": parity},
        })
        rows.append(row)
    return {
        "status": "MEASURED: exact-rational saved-evidence audit",
        "scope": "Conditional on the saved scalar evidence and analytic bounds; no matrix replay",
        "quadrature_repair": {
            "rho": 2, "factor": 4,
            "extra_operator_error": "6*N*maxq_upper",
            "source": "https://appliedmaths.sun.ac.za/~nhale/publications/HaleTrefethen2008.pdf",
            "location": "Theorem 2.1, equation (2.3), printed page 932",
        },
        "controls": test_results,
        "source_sha256": hashes,
        "certificates": rows,
        "all_safe_constants_accepted": all(row["accepted"] for row in rows),
        "warning": "Original 12-digit midpoint constants are not validated by this replacement certificate.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional JSON output inside this review directory")
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2)+"\n"
    if args.output:
        destination = Path(args.output).resolve()
        if destination.parent != REVIEW:
            raise ValueError("Output must be directly inside " + str(REVIEW))
        destination.write_text(text)
    print(text, end="")
    if not result["all_safe_constants_accepted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
