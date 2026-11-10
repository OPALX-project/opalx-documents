# Scaling FFA additive-field independent review

Read-only review of source/test diff; no builds, source edits or reference edits
performed by this reviewer during this pass.

## Corrected concrete issue

The first candidate put KOKKOS_LAMBDA launches in private static member
ScalingFFAMagnet::evaluateField. NVCC forbids a private/protected enclosing
member for an extended lambda. This matches the earlier task's actual
`bad_private_testbody.log` compiler reproduction and NVIDIA's current guide:
https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/cpp-language-support.html#extended-lambda-restrictions

The implementation agent corrected this to namespace-scope internal
scaling_ffa_detail::FieldEvaluator with public static evaluate. Existing private
coordinate/rotation math helpers remain private via friendship. The enclosing
function/type and all captured config/view types are now accessible; no private
payload type was introduced. Actual CUDA compilation/runtime is still required.

## Reviewed final contract

- Public raw scalar/batch getFieldValue signatures and overwrite semantics remain.
  Its helper uses accumulate=false; all outputs become this element's field,
  including zero outside existing support.
- apply(pc) uses accumulate=true; scalar apply computes an independent local
  Cartesian contribution then adds it. applyToReferenceParticle delegates to
  this scalar addition. E is untouched. Units remain metres/tesla.
- Existing ParallelTracker per-element transformBunch rotates R/P/E/B to local
  coordinates before apply and back after; thus existing self/external fields
  are in the same frame during addition. Host reference code independently
  zeroes each local field and rotates/adds the result into the common frame.
- Existing cylindrical formulas, fringe evaluation, support predicates,
  coefficients and public signatures are unchanged.
- Same four temporary device views and three explicit kernels plus existing
  fringe-model evaluation; no extra allocations, launches, copies, fences,
  atomics or MPI. The new local contribution vector and uniform bool only
  change the final store. This intentionally changes overlapping-field
  arithmetic from replacement to physical superposition.
- Native test uses actual particle device views, host/device transfers, seeded
  nonzero B/E, two magnets and overlapping support. It checks outside vertical,
  radial and azimuthal support, scalar/reference parity, untouched E and raw
  overwrite after nonzero initialization. The new test adds no external input
  data, Python scripts or OPALX execution. The 1e-12T assertion is justified as
  a picotesla absolute allowance for O(1T) summation; existing epsilons unchanged.
- No remaining concrete issue found in final read-only diff. This is not a CUDA
  runtime validation or a claim that all FFA tracking errors are resolved.

Reviewed diff SHA256: 04c68ac0cec7d8695011bc325221f59ef078cfe5a8658c1b6b14eedc50faf765

## Other completed evidence

Independent named-master FODO comparison is in
fodo-multipolet/baseline-master-8c1a862-independent/. It preserves all four input
hashes, uses one rank/OMP1, and compares47numeric columns over2001rows with the
existing candidate. Reference coordinates/momenta are exact; maxRMS difference
1.5e-16m, max emittance difference3.94e-14m, energy1.02e-12MeV. All seven existing
avg checks pass against current results. Largest overall numeric delta6.46e-10
is dimensionless zpz correlation. No references were edited.

Manual physics/overview/index.qmd now documents the field-sum contract with
common-frame B_total=B_self+sum(B_j), tesla units, no erasure outside one support
and external-only reference transport. The prior cyclotron manual draft was
preserved. Source58-chapter validation, focused Overview render,64-page rendered
link validator, focused formula/anchor/link checks and whitespace checks pass.
No full book/PDF/browser-interaction test or visual preview claim.
