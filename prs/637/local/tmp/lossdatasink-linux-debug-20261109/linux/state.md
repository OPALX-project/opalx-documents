# Linux Debug/OpenMP investigation: complete

9 November 2026. The exact original HDF5 rewind test fails in the first concurrent Linux pair and passes in isolation. Root's one-file owned-directory fixture fix passes five relevant targets and 100 concurrent pairs (200 CTest target executions). Source verification covers all 1,072 files, with only the intended loss-sink test differing from the frozen baseline. The production library is unchanged.

Full suite: 136/137 pass. Separate unchanged Gaussian maximum-bound test fails at 5.5717775960503042 versus 5.5, and the one isolated rerun repeats it. No Gaussian code, seed or tolerance changes. This limitation must remain explicit.

Final relevant job355093 is COMPLETED 0:0 (6m39s). All task jobs are terminal; no active monitor or allocation remains. Earlier metadata/stale-binary harness attempts and the broader Gaussian failure are preserved in the report and raw logs. No source edits by this worker, no staging, commit or push.

Evidence: REPORT.md, audit.json, validation-evidence.json and validation-evidence.tgz (SHA2563260c12c40b93741ad335e48b5f908d860db4c0cc6f88c04f85df9988e793bb2), raw remote-evidence/. Next: root independent review and final user report; no further test runs.
