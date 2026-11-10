# School adapter status

Implemented tools/ffa_school_probe_adapter.py and tools/ffa_school_probe_adapter.md. No C++ or original school source edits. API: read_native_probe(path), to_school_frame(frame,r0_m,turn_offset=0), write_school_loss(frame,path). CLI uses explicit --r0-m and optional --turn-offset. Native ASCII/HDF5 inputs are unchanged, ten-column school output is exclusively created. Exact int64 IDs and labels retained; missing/malformed records fail.

Validation: validate_adapter.py passes all21 synthetic/real-record checks, report validation.json. Real20-hit cyclotron ASCII/HDF5 files validate parsing and source precision only, not FFA physics. Additional CLI smoke passes and output is accepted by original FFA25-school/read_dat.py read_probe; existing-output refusal returns1.

Limits: transformation applies only to existing unrotated school centre (-R0,0); +1 offset changes label base without recreating legacy initial-plane/boundary semantics. No contiguous-ID or one-hit/turn assumption. HDF5 q/m are deliberately outside the school ten-column export. No files pushed or committed.
