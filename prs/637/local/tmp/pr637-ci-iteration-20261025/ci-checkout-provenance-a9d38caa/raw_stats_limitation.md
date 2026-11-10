# Raw-stat artifact coverage limitation

The current a9 OpenMP regression job 17451990959 and MI300 job 17451990683 public artifacts were inspected read-only after completion. Their exact source and regression checkout SHAs are independently preserved in the adjacent XML/provenance records.

For both jobs:

- `regression-results-ARCH/` contains only `overview/`, `regressionTests/`, and `unitTests/` directories, with no root files.
- The specific branch/architecture regression report directory contains eight files: report XML, two HTML files, CSS, JavaScript, XSLT and two status-icon PNGs.
- The current timestamped `plots_.../` directory contains exactly 430 raw files, all PNG images.
- No `.stat`, `.smb`, `.csv` or `.dat` files are present in those regression report or plot listings. Actual FODO/Scaling simulation `.stat` files are unavailable.

The complete public directory listings and SHA256 hashes of fetched HTML are preserved in `openmp-{root,arch,plots}-artifact-listing.{json,html}` and equivalent `mi300-...` files. `check_raw_stat_artifacts.py` reproduces this read-only inventory.

This agrees with the checked runner source `/tmp/pr637-nightlybuildx-20261025/scripts/OpalRegressionTests/regressiontest.py:679` (`RegressionTest.publish` copies only `*.png`) and exact a9 CI source `ci/cscs/regression-common.yml:267` (artifact paths include only `regression-results-$BUILD_ARCH`). The external runner full SHA remains unavailable; its precise revision is not inferred from this local source inspection.

Consequently the five failing/broken checks cannot be reevaluated against our local reviewed reference draft using the unchanged NightlyBuildX metric and tolerances from these public artifacts. No pass against that draft is inferred from the plot pixels, XML failure deltas, or approximate CPU/GPU agreement. This remains a validation limitation. No extra simulations, test cases, CI changes, publication or reruns were launched.
