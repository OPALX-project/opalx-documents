# DBA space-charge laptop feasibility pilot — completed

User authorized a bounded pilot only. No full-turn campaign started.

Only ~/git/opalx/build-omp/src/opalx, unchanged SHA4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb. Source patch SHA885e59c8a4fe5c3751b0077db53051f7467667af1a4d0fee77b799b68ef6764a also unchanged. No C++ edits/rebuilds/commits/pushes.

Setup: full-ring matchedKV100000particles,5.602212333965894nC,64x64x512,64mm transverse widths,FFT2D5 ORIGINAL,PIPEMODE NONE (transverseSC; longitudinalforce off as plannedcoastingKV/PyORBIT setup),closed referencepath2607points,3ps fixed Boris/PIC,MIDPOINTSCupdates,1MPIrank. Independent design reference and100karrays inserted into CURRENTbinary-native checkpoint schema. Aperture deletionFALSE; fieldaperturesunchanged. Same sourceNPZ SHA97943097cf785f64019b7092bd52bbf57eca77bdfbe07cdef288d9ac5732d923 as earlier preparation. No archived binary executed.

Completed100steps each:
- OMP1 SC:167.813s wall; steady(native main - OrbitThreader)/100=1.659975s/step; logtimestampfit1.663333.
- OMP4 SC:75.424s wall; steady.735932s/step; logfit.738333. Nativeexit0; getrusagepeak130138112bytes.
- OMP4 ZeroSC timingcontrol:5.009s wall; steady.031187s/step. Same charged-matched source, onlyFSNONE; not zero-currentmatchedtune study. Nativeexit0; peak291160064bytes.

Feasibility:16turns require6291834steps at3ps. OMP4 estimated53.59days perchargecase (40.19days at4ps). OMP1~120.88days at3ps. Thus NOT practical with current settings. These are extrapolations from0.000254turns; no long-run physicsvalidation, no thermal/output/evolvedbeamguarantee.12.268nC notrun; comparablecost expected butnotmeasured. Difference versusZeroSC indicatesFFT2D5pathdominates, not whichkernel; profilebeforeclaiming specificbottleneck. Never silentlyincreaseDT orreduceSCfrequencywithoutconvergencevalidation.

Audits: all100000IDs/count, total5.602212nC, finite R/P, final300ps/globalstep99,100nativeTIntegration2calls for all3pilots. ChargedOMP1 vs4 max labmomentum difference7.79e-13 beta-gamma. Charged vsZeroSC max5.38e-8,median3.55e-8: nonzeroSCactionconfirmed. No tune or long-termagreementclaimed.

Failures handled: initialunquotedTYPEFFT2D5 parseerror correctedtoquotedstring; failedinputpreservedunderinput-parse-error-omp1-100steps. SuccessfulOMP1 waswrappedin/usr/bin/time-l; wrapperclockratesysctl denied AFTER nativecompleted100steps, returning1. Manifest retainswrapperreturncode1,native_returncodeunknown,trackingcompletionverifiedfromH5/timercounts.4threadrunsdirectnativeexit0. No physics tolerancechanged.

Raw: /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-sc-feasibility, withrunner/analyzer/archive scripts inparent. Alltaskjobsfinished.
Curated: /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/dba-sc-feasibility-2026-11-04 (14catalogedassets:inputs,logs,manifests,CSV/JSON/readme/scripts). Largeparticle/checkpointdata retainedraw withhashes. Archivedscripts explicitlypointtorawstudyroot andguardfrozenbinary;pilotrunnercaps1000steps. All14hashesverified,Pythonparsechecks pass,manifestdiffwhitespaceclean. Fullrepositorydocumentvalidator stillfailsONLY pre-existinguncatalogedmovie movies/2026-10-30-mue4_analytical-trails.mp4; leftuntouched.

Next: report infeasibility and measuredrates. Furtherprofiling, acceleration ormultirate/boundaryhandlingexperiments require newtaskscope. Do notstart16turns automatically.
