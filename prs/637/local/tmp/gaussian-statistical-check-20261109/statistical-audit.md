# Gaussian tail-check statistical audit

The frozen implementation is `6569cabdd647bd40dcbbeb280819aca92ea724b5f06b30972975b5bf830fa4ce`. Only the selected test case and its required array include changed. Sampling setup and the existing RMS block are preserved; Gaussian production code and seed options have no Git diff.

For each of five uncut unit-normal coordinates, K counts values with |Z| > 3. Thus K is Binomial(N,p), where p = erfc(3/sqrt(2)). Set mu=Np, v=Np(1-p), alpha=1e-6 and L=log(4m/alpha), with m=5.

The two-sided Bernstein inequality is P(|K-mu| >= t) <= 2 exp(-t^2/[2(v+t/3)]). Solving the quadratic for exponent L gives t=L/3+sqrt(2vL+(L/3)^2). Union-bounding over m coordinates spends alpha/2. The normal inequality P(|Z| > u) <= 2 exp(-u^2/2), union-bounded over m*N values, spends the remaining alpha/2 with u=sqrt(2*(L+log(N))). Therefore the combined new-check false-alarm probability is at most alpha under the IID normal sampling model. No independence between the two checks or across coordinates is needed for these union bounds.

At N=100,000, p=0.00269979606326019, mu=269.979606326, and v=269.250716448. The count margin is 100.915238737, accepting integer counts **170–370**. The derived maximum is **7.52650892466 sigma**. This accepts the previously observed 5.571777596 sigma sample.

SciPy's binomial CDF/SF give a numerical count-family union upper bound of 1.61779854755e-08. The normal-tail maximum-family union upper bound is 2.60574596708e-08. Their sum is 4.22354451463e-08, below the analytic 1e-6 guarantee. These are conservative family upper bounds, not an exact combined probability.

Complete clipping at 3 sigma yields zero tails and is rejected deterministically. A 40-sigma finite outlier is rejected by the derived maximum. The count check rejects a 5% inflated width with probability 0.997584278681 per coordinate. These are analytic mutation/power calculations; this audit does not run native tests or alter source.

The 1e-6 budget applies only to the new tail checks. Existing four-standard-error RMS checks remain unchanged and have their own false-alarm probability. Pseudorandom output is modeled as IID Gaussian; this audit does not certify the generator.

Reproduce with:

    /Users/adelmann/.venv-h6/bin/python /Users/adelmann/git/opalx-master/tmp/gaussian-statistical-check-20261109/statistical-audit.py --checkout /Users/adelmann/git/opalx-master

The analysis requires installed SciPy 1.17.1; the native C++ test has no SciPy, Python or external-data dependency. Exact numbers and source checks are in statistical-audit.json.
