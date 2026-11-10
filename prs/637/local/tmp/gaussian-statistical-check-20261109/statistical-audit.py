#!/usr/bin/env python3
"""Audit the Gaussian tail bounds; analysis artifact, not a unit-test dependency."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import scipy
from scipy.stats import binom

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checkout", type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
args = parser.parse_args()
out = args.output_dir
out.mkdir(parents=True, exist_ok=True)
manifest = json.loads((Path(__file__).parent / "intended-file.json").read_text())
source_path = args.checkout / manifest["changed_file"]
source = source_path.read_text()
original = (Path(__file__).parent / "original-TestGaussian.cpp").read_text()
assert hashlib.sha256(source_path.read_bytes()).hexdigest() == manifest["after_sha256"]
assert hashlib.sha256(original.encode()).hexdigest() == manifest["before_sha256"]
start = "TEST_F(GaussianTest, largeCutoffDisablesTruncation)"
end = "// Without the phase-space adjustment"
def case(text):
    return text[text.index(start):text.index(end)]
def compact(text):
    return re.sub(r"\s+", "", text)
old_case, new_case = case(original), case(source)
rms_marker = "    auto Rview = pc->R.getView();"
assert old_case[old_case.index(rms_marker):] == new_case[new_case.index(rms_marker):]
config = [
    "const Vector_t<double, 3> sigmaR = 1.0;",
    "const Vector_t<double, 3> sigmaP = 1.0;",
    "const double avrgpz = 0.0;",
    "const double noCut = std::numeric_limits<double>::max();",
    "const Vector_t<double, 3> cutoffR(noCut, noCut, 3.0);",
    "const Vector_t<double, 3> cutoffP(noCut, noCut, noCut);",
    "Gaussian sampler(pc, sigmaR, sigmaP, avrgpz, cutoffR, false, cutoffP);",
]
assert all(compact(x) in compact(old_case) and compact(x) in compact(new_case) for x in config)
# Only the selected case and its required <array> include changed.
old_rest = original.replace(old_case, "CASE_PLACEHOLDER")
new_rest = source.replace(new_case, "CASE_PLACEHOLDER").replace("#include <array>\n", "")
assert compact(old_rest) == compact(new_rest)
assert subprocess.check_output([
    "git", "-C", str(args.checkout), "diff", "--",
    "src/Distribution/Gaussian.cpp", "src/Utilities/Options.cpp", "src/Utilities/Options.h"
], text=True) == ""

n, dimensions, alpha = 100000, 5, 1e-6
cutoff = 3.0
p = math.erfc(cutoff / math.sqrt(2.0))
mu = n * p
variance = n * p * (1.0 - p)
L = math.log(4.0 * dimensions / alpha)
margin = L / 3.0 + math.sqrt(2.0 * variance * L + L * L / 9.0)
lower = math.ceil(mu - margin)
upper = math.floor(mu + margin)
maximum = math.sqrt(2.0 * (L + math.log(n)))
# Bernstein and the normal tail inequality each spend alpha/2.
count_theoretical = 2.0 * dimensions * math.exp(-L)
maximum_theoretical = 2.0 * dimensions * n * math.exp(-maximum * maximum / 2.0)
combined_theoretical = count_theoretical + maximum_theoretical
assert math.isclose(combined_theoretical, alpha, rel_tol=1e-12)
assert (lower, upper) == (170, 370)
assert mu > margin
single_count_lower = float(binom.cdf(lower - 1, n, p))
single_count_upper = float(binom.sf(upper, n, p))
count_numerical_union = dimensions * (single_count_lower + single_count_upper)
maximum_numerical_union = dimensions * n * math.erfc(maximum / math.sqrt(2.0))
assert count_numerical_union <= count_theoretical
assert maximum_numerical_union <= maximum_theoretical
power = []
for sigma in (0.9, 0.95, 1.0, 1.05, 1.1, 1.2):
    q = math.erfc(cutoff / (math.sqrt(2.0) * sigma))
    rejection = float(binom.cdf(lower - 1, n, q) + binom.sf(upper, n, q))
    power.append({"sigma": sigma, "true_tail_probability": q,
                  "expected_tail_count": n * q,
                  "one_axis_count_rejection_probability": rejection})
clipping_rejected = abs(0 - mu) > margin
outlier_rejected = 40.0 > maximum
observed_maximum_accepted = 5.5717775960503042 <= maximum
assert clipping_rejected and outlier_rejected and observed_maximum_accepted
report = {
    "source": str(source_path), "source_sha256": manifest["after_sha256"],
    "source_checks": {"original_hash_verified": True, "rms_block_byte_identical": True,
        "sampling_configuration_unchanged": True,
        "other_test_cases_unchanged_ignoring_whitespace": True,
        "production_gaussian_and_seed_options_have_no_git_diff": True},
    "model": {"n": n, "uncut_dimensions": dimensions, "threshold_sigma": cutoff,
        "family_tail_failure_budget": alpha, "binomial_p": p,
        "mean_count": mu, "variance_count": variance, "log_failure": L},
    "acceptance": {"bernstein_count_margin": margin, "integer_count_lower": lower,
        "integer_count_upper": upper, "maximum_sigma": maximum},
    "probability_bounds": {"count_family_theoretical": count_theoretical,
        "maximum_family_theoretical": maximum_theoretical,
        "combined_family_theoretical": combined_theoretical,
        "binomial_rejection_lower_one_axis": single_count_lower,
        "binomial_rejection_upper_one_axis": single_count_upper,
        "count_family_numerical_union_upper": count_numerical_union,
        "maximum_family_normal_union_upper": maximum_numerical_union,
        "combined_family_numerical_union_upper": count_numerical_union + maximum_numerical_union},
    "analytic_mutation_checks": {"complete_3sigma_clipping_rejected": clipping_rejected,
        "one_40sigma_finite_outlier_rejected_by_maximum": outlier_rejected,
        "previous_5_571777596_maximum_accepted": observed_maximum_accepted,
        "scale_change_count_power": power},
    "assumptions": ["IID Gaussian sampling model; this does not prove the RNG itself is IID",
        "fixMeanR=false avoids centering-induced sample dependence",
        "rejection on independent z alone preserves the other five normal marginals",
        "union bounds do not require independence across coordinates or between checks"],
    "scope_limits": ["The 1e-6 bound covers new count and maximum checks only",
        "Existing four-standard-error RMS checks are unchanged and have a separate false-alarm budget",
        "Power and clipping/outlier results here are analytic models, not native C++ mutation runs",
        "SciPy is used only for this audit; native unit tests require no scripts or external data"],
    "versions": {"scipy": scipy.__version__}, "native_tests_run_by_this_audit": False,
}
(out / "statistical-audit.json").write_text(json.dumps(report, indent=2) + "\n")
md = f"""# Gaussian tail-check statistical audit

The frozen implementation is `{manifest['after_sha256']}`. Only the selected test case and its required array include changed. Sampling setup and the existing RMS block are preserved; Gaussian production code and seed options have no Git diff.

For each of five uncut unit-normal coordinates, K counts values with |Z| > 3. Thus K is Binomial(N,p), where p = erfc(3/sqrt(2)). Set mu=Np, v=Np(1-p), alpha=1e-6 and L=log(4m/alpha), with m=5.

The two-sided Bernstein inequality is P(|K-mu| >= t) <= 2 exp(-t^2/[2(v+t/3)]). Solving the quadratic for exponent L gives t=L/3+sqrt(2vL+(L/3)^2). Union-bounding over m coordinates spends alpha/2. The normal inequality P(|Z| > u) <= 2 exp(-u^2/2), union-bounded over m*N values, spends the remaining alpha/2 with u=sqrt(2*(L+log(N))). Therefore the combined new-check false-alarm probability is at most alpha under the IID normal sampling model. No independence between the two checks or across coordinates is needed for these union bounds.

At N={n:,}, p={p:.15g}, mu={mu:.12g}, and v={variance:.12g}. The count margin is {margin:.12g}, accepting integer counts **{lower}–{upper}**. The derived maximum is **{maximum:.12g} sigma**. This accepts the previously observed 5.571777596 sigma sample.

SciPy's binomial CDF/SF give a numerical count-family union upper bound of {count_numerical_union:.12g}. The normal-tail maximum-family union upper bound is {maximum_numerical_union:.12g}. Their sum is {count_numerical_union + maximum_numerical_union:.12g}, below the analytic 1e-6 guarantee. These are conservative family upper bounds, not an exact combined probability.

Complete clipping at 3 sigma yields zero tails and is rejected deterministically. A 40-sigma finite outlier is rejected by the derived maximum. The count check rejects a 5% inflated width with probability {next(x['one_axis_count_rejection_probability'] for x in power if x['sigma']==1.05):.12g} per coordinate. These are analytic mutation/power calculations; this audit does not run native tests or alter source.

The 1e-6 budget applies only to the new tail checks. Existing four-standard-error RMS checks remain unchanged and have their own false-alarm probability. Pseudorandom output is modeled as IID Gaussian; this audit does not certify the generator.

Reproduce with:

    /Users/adelmann/.venv-h6/bin/python {Path(__file__).resolve()} --checkout {args.checkout}

The analysis requires installed SciPy {scipy.__version__}; the native C++ test has no SciPy, Python or external-data dependency. Exact numbers and source checks are in statistical-audit.json.
"""
(out / "statistical-audit.md").write_text(md)
print(json.dumps({"source_sha256": report["source_sha256"], "acceptance": report["acceptance"],
    "probability_bounds": report["probability_bounds"], "source_checks": report["source_checks"],
    "complete_clipping_rejected": clipping_rejected,
    "sigma_1_05_one_axis_count_power": next(x["one_axis_count_rejection_probability"] for x in power if x["sigma"]==1.05)}, indent=2))
