# GH200 build silence: comparison with prior successful jobs

The current quiet249K checkpoint is consistent with the previous successful GH200 output pattern. It is not evidence by itself that the build has failed or stalled. Both preceding23f builds were silent between the249K and299K checkpoints for about27 minutes, then completed successfully. This is a timing comparison only; current success remains unverified until the live CI monitor observes a terminal result.

## Exact prior successful timings

All timestamps below areUTC, from public GitLab pipeline-job metadata and the corresponding completed raw build logs. The old jobs built exact23f04f6c8e57f497e6f1a722038f9e1cef010803 in pipeline2987093893. The pipeline's later aggregate status is canceled, but **both individual build jobs are success** and have finished timestamps; do not confuse those states.

|Prior build|Release17451643237|Debug17451643236|
|---|---|---|
|GitLab started|20:09:29.279|20:09:29.227|
|Compiler build began|20:13:06.098|20:13:15.549|
|249K output checkpoint|20:19:24.414|20:19:34.536|
|Next299K checkpoint|20:46:20.504|20:47:13.145|
|Quiet249K→299K gap|**26m56.090s**|**27m38.609s**|
|Compiler build completed|20:49:07.794|20:49:26.371|
|249K→compiler completion|29m43.380s|29m51.834s|
|GitLab job finished/success|20:50:33.634|20:51:25.507|
|249K→job success|31m09.220s|31m50.971s|
|Entire GitLab job duration|41m04.355s|41m56.280s|
|Compiler build duration|36m01.696s|36m10.822s|

Both raw logs report0 compiler errors and2 warnings. The compiler-completion event is distinct from subsequent cleanup/artifact work and the final GitLab finished_at timestamp.

Sources: [old Release job](https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757981/-/jobs/17451643237), [old Debug job](https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757981/-/jobs/17451643236), [public pipeline jobs metadata](https://gitlab.com/api/v4/projects/82981356/pipelines/2987093893/jobs?per_page=100). Exact metadata, machine-readable interval calculations and safe phase excerpts are adjacent.

## Comparison with the current a9 jobs

The live CI monitor owns current polling and concrete-error checks; this diagnostic did not duplicate current job metadata/raw polling. Its provided observations are:

|Current a9 build|Release17451990420|Debug17451990419|
|---|---|---|
|Compiler build began|about20:59:41|about20:59:42|
|249K checkpoint|about21:05:55|about21:05:58|
|Build start→249K|about6m14s|about6m16s|

Those initial intervals closely match the previous successful builds'6m18.316s and6m18.988s. At the21:26 observation, the new checkpoints had been quiet for only about20 minutes, shorter than both prior successful27-minute gaps. The live monitor subsequently confirmed both remained running without a concrete error. Their exact current started_at/duration values will be attached only if supplied by its regular poll; no new poll was requested for this report.

CTest explicitly prints `Each symbol represents 1024 bytes of output`, then emits a checkpoint every50 symbols. The reported249K is an **output-volume counter**, not a completion percentage or a heartbeat of individual compiler processes. The completed raw traces are only about20KiB because build output is aggregated in this display. A long gap therefore cannot establish process inactivity. The prior observed pattern supports continuing to wait for the existing jobs and their actual terminal status; it does not guarantee the new source takes the same time.

## Bounds and limitations

`ci/cscs/cuda/build_sm90.yml` configures a45-minute Slurm allocation cap. The prior GitLab jobs took41–42 minutes including setup, cleanup and artifact operations. GitLab duration and Slurm allocation time are not identical clocks, so these observations do not determine the exact current allocation deadline. No scheduler credentials, process-level visibility, or cscs-ci CLI were available. Public individual-job metadata/trace APIs return401; the public pipeline-jobs endpoint and web `/raw` succeed.

There is no concrete build error in this diagnostic and no source change, test, rerun, restart, timeout override or external action was performed. Continue the existing CI monitor; act on its first real error or terminal status rather than an apparent log timeout. The user's local-only reference decision is unchanged.
