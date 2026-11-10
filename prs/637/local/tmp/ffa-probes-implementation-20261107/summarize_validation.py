#!/usr/bin/env python3
"""Reproduce the school-probe matrix summary from saved native outputs."""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def write(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def compare_snapshots(driver,reference,candidate):
    a,b=driver.final_snapshot(HERE/reference),driver.final_snapshot(HERE/candidate)
    fields={key:dict(exact=bool(np.array_equal(value,b[key])),
                     max_abs_delta=float(np.max(np.abs(value-b[key]))))
            for key,value in a.items()}
    return dict(reference=reference,candidate=candidate,exact=all(v['exact'] for v in fields.values()),
                fields=fields)


def compare_probe_files(adapter,reference,candidate,stations,ascii_rounding=False):
    maximum={name:0. for name in adapter.COLUMNS};exact=True;rounding=True;count=0
    for j in range(1,stations+1):
        a=adapter.read_probe(HERE/reference/f'PROBE{j}.h5')
        suffix='.loss' if ascii_rounding else '.h5'
        b=adapter.read_probe(HERE/candidate/f'PROBE{j}{suffix}')
        ascii_tokens=None
        if ascii_rounding:
            ascii_tokens=[line.split() for line in (HERE/candidate/f'PROBE{j}{suffix}').read_text().splitlines()
                          if line.strip() and not line.lstrip().startswith('#')]
            ascii_tokens.sort(key=lambda row:(int(row[8]),int(row[6]),float(row[9])))
        if len(a)!=len(b):raise ValueError('Unequal hit counts')
        count+=len(a)
        for name in adapter.COLUMNS:
            x,y=a[name].to_numpy(),b[name].to_numpy()
            maximum[name]=max(maximum[name],float(np.max(np.abs(x-y))))
            exact=exact and np.array_equal(x,y)
            expected=(np.asarray([float(format(v,'.6g')) for v in x])
                      if name in adapter.FLOAT_COLUMNS else x)
            # Compare file tokens through correctly rounded Python float conversion.
            # pandas.to_numeric can differ by one ULP for tiny subnormal-scale
            # values, which is reader arithmetic rather than writer precision.
            written=(np.asarray([float(row[adapter.COLUMNS.index(name)]) for row in ascii_tokens])
                     if ascii_rounding and name in adapter.FLOAT_COLUMNS else y)
            rounding=rounding and np.array_equal(expected,written)
    return dict(reference=reference,candidate=candidate,crossings=count,exact=bool(exact),
                max_abs_deltas=maximum,
                exact_after_six_significant_digit_rounding=bool(rounding) if ascii_rounding else None)


def main():
    driver=load('school_validation_driver',HERE/'check_school_probes.py')
    adapter=load('school_validation_adapter',HERE.parents[1]/'tools/probe_frame_adapter.py')
    names=sorted(path.name for path in HERE.glob('native-*-matched*')
                 if (path/'analysis.json').exists())
    analyses={}
    for name in names:
        analyses[name]=driver.analyze(HERE/name)
    controls=[]
    for case in ['16-cell','fourfold']:
        for variant in ['ascii-r1','hdf5-r1']:
            controls.append(compare_snapshots(driver,f'native-{case}-matched-off-r1',
                                               f'native-{case}-matched-{variant}'))
    controls.append(compare_snapshots(driver,'native-16-cell-matched-off-r1','native-16-cell-matched-hdf5-r2'))
    controls.append(compare_snapshots(driver,'native-fourfold-matched-off-r2','native-fourfold-matched-hdf5-r2-repeat'))
    outlier=compare_snapshots(driver,'native-fourfold-matched-hdf5-r2-repeat','native-fourfold-matched-hdf5-r2')
    repeats=[compare_snapshots(driver,'native-fourfold-matched-off-r2','native-fourfold-matched-off-r2-repeat'),
             outlier]
    formats=[compare_probe_files(adapter,f'native-{case}-matched-hdf5-r1',f'native-{case}-matched-ascii-r1',stations,True)
             for case,stations in [('16-cell',16),('fourfold',4)]]
    mpi=[compare_probe_files(adapter,'native-16-cell-matched-hdf5-r1','native-16-cell-matched-hdf5-r2',16),
         compare_probe_files(adapter,'native-fourfold-matched-hdf5-r1','native-fourfold-matched-hdf5-r2-repeat',4),
         compare_probe_files(adapter,'native-fourfold-matched-hdf5-r1','native-fourfold-matched-hdf5-r2',4)]
    first=HERE/'native-fourfold-matched-hdf5-r2';repeat=HERE/'native-fourfold-matched-hdf5-r2-repeat'
    a,b=[json.loads((path/'manifest.json').read_text()) for path in [first,repeat]]
    provenance=dict(input_bytes_identical=(first/'school.in').read_bytes()==(repeat/'school.in').read_bytes(),
                    particle_bytes_identical=(first/'particles.dat').read_bytes()==(repeat/'particles.dat').read_bytes(),
                    executable_sha256_identical=a['executable_sha256']==b['executable_sha256'],
                    executable_sha256=a['executable_sha256'],
                    enforced_environment=dict(OMP_NUM_THREADS='1',IPPL_OPENMP_THREADS='1',OMP_PROC_BIND='false'),
                    inherited_environment_captured=False,
                    concurrent_load='First ON ran concurrently with other independent comparisons; repeat was sequential after OFF.',
                    diagnosis='Unresolved isolated subdivision-schedule difference; no deterministic probe effect established. No generic baseline-nondeterminism claim.')
    launch=adapter.read_probe(HERE/'native-fourfold-turn-label-debug/launch-section.h5')
    radial=adapter.read_probe(HERE/'native-fourfold-turn-label-debug/PROBE1.h5')
    label_report=dict(launch_time_s=launch.time.tolist(),launch_labels=launch.turn.tolist(),
                      radial_time_s=radial.time.tolist(),radial_labels=radial.turn.tolist(),
                      radial_after_launch_ps=((radial.time-launch.time)*1e12).tolist(),
                      interpretation='Second launch/radial crossings share one accepted interval. The observer records its step-start reference count before updating the reference counter; labels need not equal per-station passage indices.')
    metrics=[];source_provenance={}
    for name,analysis in analyses.items():
        path=HERE/name;manifest=json.loads((path/'manifest.json').read_text())
        source_provenance[name]={key:manifest.get(key) for key in
                                ['executable','executable_sha256','input_sha256','particle_sha256',
                                 'native_template_sha256','school_module_sha256','mass_GeV',
                                 'initial_native_x_px_y_py_z_pz','dt_s','steps','ranks','geometry_correction']}
        old=manifest['old_reference']
        source_provenance[name]['old']={key:old.get(key) for key in
                                      ['binary','binary_sha256','binary_OPAL_revision','source_sha256',
                                       'input_sha256','distribution_sha256','physical_mass_MeV',
                                       'initial_old_x_y_z_px_py_pz','dt_s','integrator']}
        if analysis['variant']=='off':continue
        data=pd.read_csv(path/'crossing-comparison.csv')
        r={suffix:np.hypot(data['x_'+suffix],data['y_'+suffix]) for suffix in ['old','native']}
        pr={suffix:(data['x_'+suffix]*data['px_'+suffix]+data['y_'+suffix]*data['py_'+suffix])/r[suffix]
            for suffix in ['old','native']}
        metrics.append(dict(native_run=name,old_run=manifest['old_run'],
                            physical_hits=analysis['matched_hits'],
                            old_initial_hits_excluded=analysis['old_initial_hits_excluded'],
                            unmatched_old=analysis['unmatched_old'],unmatched_native=analysis['unmatched_native'],
                            max_coordinate_delta_m=max(analysis['max_abs_deltas'][key] for key in ['x','y','z']),
                            max_radial_delta_m=float(np.max(np.abs(r['native']-r['old']))),
                            max_radial_momentum_delta_mc=float(np.max(np.abs(pr['native']-pr['old']))),
                            max_vertical_delta_m=float(np.max(np.abs(data.z_native-data.z_old))),
                            max_vertical_momentum_delta_mc=float(np.max(np.abs(data.pz_native-data.pz_old))),
                            max_time_delta_s=analysis['max_abs_deltas']['time'],
                            final_charge_C=analysis['final_charge_C'],nominal_steps=manifest['steps'],
                            accepted_steps=analysis['global_steps'],dt_s=manifest['dt_s'],ranks=manifest['ranks']))
    summary=dict(analyses=analyses,metrics=metrics,source_provenance=source_provenance,
                 probe_passivity_controls=controls,
                 all_listed_passivity_controls_exact=all(c['exact'] for c in controls),
                 format_comparisons=formats,mpi_probe_comparisons=mpi,
                 fourfold_repeats=repeats,outlier_provenance=provenance,
                 turn_label_diagnostic=label_report,
                 limitations=['Few-turn, one-particle, no-space-charge comparisons; not beam/high-current validation.',
                              'No fresh GPU run is part of this local integration matrix.',
                              'Native boundary control subdivides nominal dt; halving nominal dt need not halve accepted dt.',
                              'Old ASCII has six significant digits; old records current-step momentum at an extrapolated event.',
                              'Two old initial-plane t=0 records per case are reported and excluded; native suppresses them.',
                              'Old RF-step turn labels are not native reference launch-plane counts.',
                              'One first fourfold two-rank ON run differs by 15 subdivisions; all raw evidence retained.'])
    write(HERE/'comparison-summary.json',summary)
    lines=['# Native/old school PROBE integration validation','',
           'The first implementation uses native OPALX laboratory output and the school adapter. All original school files remain unchanged. Source-derived geometry reflection and spiral reversal are applied only to copied comparison inputs. See the driver and old-school field-transform audit.','',
           '## Raw crossing comparison','',
           '| Native case | Physical hits | Unmatched old/native | Maximum coordinate difference [m] |',
           '|---|---:|---:|---:|']
    for name in ['native-16-cell-matched-hdf5-r1','native-16-cell-matched-refined-hdf5-r1',
                 'native-16-cell-matched-quarter-hdf5-r1','native-16-cell-matched-vertical-hdf5-r1',
                 'native-fourfold-matched-hdf5-r1','native-fourfold-matched-refined-hdf5-r1',
                 'native-55deg-d-off-matched-hdf5-r1','native-55deg-d-off-matched-refined-hdf5-r1']:
        if name not in analyses:continue
        d=analyses[name];delta=d.get('max_abs_deltas',{})
        maximum=max(delta.get(key,0) for key in ['x','y','z'])
        lines.append(f'| {name} | {d.get("matched_hits")} | {d.get("unmatched_old")}/{d.get("unmatched_native")} | {maximum:.6g} |')
    lines.extend(['','All cases use one particle with no losses; two initial old t=0 records are excluded explicitly. Time, particle IDs and chronological station passage define the join, while both native and old turn labels remain available.','',
                  '## Passivity, output and MPI','',
                  '- The listed one-rank OFF/ASCII/HDF5 controls are bitwise identical in final particle state, charge, reference state, time, path length and accepted-step count.',
                  '- Sixteen-station one/two-rank outputs are identical. The repeated fourfold two-rank ON run is also identical to its OFF control and to the one-rank case.',
                  '- Native ASCII and HDF5 format consistency is checked against six-significant-digit ASCII rounding; exact detail is in comparison-summary.json.',
                  '- FFA output has no misleading lab-origin .hist/.peaks products.','',
                  '## Retained two-rank outlier','',
                  'The first fourfold HDF5 two-rank run used 63,158 accepted subdivisions; OFF and repeated ON runs used 63,143. The repeated ON is exactly identical to OFF. Initial input bytes, particle bytes and binary hash are identical across the two ON runs. The driver fixes OMP/IPPL thread counts to one and disables binding, but the complete inherited environment was not captured. The first run overlapped independent jobs; this is context, not an established cause.',
                  f'The outlier has identical final time, ID and charge. Maximum local position difference is {max(outlier["fields"][key]["max_abs_delta"] for key in ["x","y","z"]):.6g} m; reference-position difference is {outlier["fields"]["RefPartR"]["max_abs_delta"]:.6g} m. Cause remains unresolved; no blanket bitwise MPI or general baseline-nondeterminism claim is made.','',
                  '## Reference labels','',
                  'In the fourfold diagnostic, radial PROBE1 returns occur 132.05, 18.84 and 98.80 ps after returns through the initial reference plane. Their native labels are 1,1,3, whereas launch-plane probe labels are 0,1,2. The second pair shares one accepted interval, so its station record retains the previous step-start count. This is the documented counter/observation ordering, not a new particle or station turn definition.','',
                  '## Numerical limits','',
                  'Old OPAL uses RK4 and extrapolated event positions with current-step momentum; native tracking uses its existing boundary-controlled particle transport and coherent endpoint interpolation. Old raw ASCII has six significant digits. Nominal timestep refinement is reported without claiming uniform accepted-step refinement. No tolerances or physics references were changed.','',
                  'Plots and standalone CSV/JSON are in plots/. The validation is a few-turn detector comparison, not space-charge, convergence, long-term stability or fresh GPU validation.'])
    lines.extend(['','## Geometry and provenance','',
                  'Legacy RingDefinition LAT_PHIINIT is clockwise from old +Y. The existing native school template had treated the accumulated angle as counterclockwise from +X. Copied physical magnet placements are corrected by theta_entrance = PI/2 - phi_template - L/R0, TAN_DELTA is negated, and the existing axial B0 sign conversion is retained. Native AsymmetricEnge already reverses the old scalar coordinate with the same start/end names; no additional endpoint swap is applied. Zero-field geometry arcs are retained. No original school template or production field calculation was changed.',
                  'The independent source-derived field transformation check covers 450 points, off-plane fields, and symmetric/asymmetric fringe profiles, with maximum error 8.05e-15 T: [script](old-school/check_field_transform.py), [results](old-school/check_field_transform.json).',
                  'Native executable hashes are b13e9e5354a4434826ebf9844b05ebed6c3e6534a2b48fcc867dd6329cd80ef5 (frozen first implementation) and 58bd5db212d2dc3e62c8fdf62a51fb2dca456580eabf9452c595ea448777f9d5 (final linked source). Old executable hash, exact revision, input/distribution/template hashes, full initial states and corrected physical masses/timesteps are retained for each run in comparison-summary.json and each manifest.json. Both binaries are preserved under bin/.',
                  '', '## Coordinate observables and refinement', '',
                  '| Native run | Max radial difference (µm) | Max radial momentum difference p/(mc) | Max vertical difference (µm) | Max vertical momentum difference p/(mc) |',
                  '|---|---:|---:|---:|---:|'])
    selected=['native-16-cell-matched-hdf5-r1','native-16-cell-matched-refined-hdf5-r1',
              'native-16-cell-matched-quarter-hdf5-r1','native-16-cell-matched-vertical-hdf5-r1',
              'native-fourfold-matched-hdf5-r1','native-fourfold-matched-refined-hdf5-r1',
              'native-55deg-d-off-matched-hdf5-r1','native-55deg-d-off-matched-refined-hdf5-r1']
    for metric in metrics:
        if metric['native_run'] not in selected:continue
        lines.append(f"| {metric['native_run']} | {metric['max_radial_delta_m']*1e6:.5g} | {metric['max_radial_momentum_delta_mc']:.5g} | {metric['max_vertical_delta_m']*1e6:.5g} | {metric['max_vertical_momentum_delta_mc']:.5g} |")
    lines.extend(['','The 16-cell radial momentum difference decreases from 9.66e-6 to 3.44e-6 to 2.29e-6 p/(mc) across nominal coarse/half/quarter budgets. Quarter-step radial-position maximum decreases from about13.6 to8.71µm. The 55-degree D-off radial momentum difference approximately halves from1.48e-4 to7.30e-5 p/(mc). These observations support the expected legacy event/momentum sampling difference; they do not establish a uniform integrator convergence order because native boundary subdivision and old ASCII rounding both intervene.','',
                  '## Artifacts and reproduction','',
                  '- [Matched native preparation/run/comparison driver](check_school_probes.py)',
                  '- [Summary reproduction script](summarize_validation.py)',
                  '- [Plot reproduction script](plot_school_probe_comparison.py)',
                  '- [Old run provenance and accepted cases](old-school/REPORT.md)',
                  '- [Structured complete comparison summary](comparison-summary.json)'])
    for name in ['16-cell-radial','16-cell-vertical','fourfold-radial','fourfold-vertical','55deg-d-off-radial','55deg-d-off-vertical']:
        lines.append(f'- {name}: [PNG](plots/{name}.png), [PDF](plots/{name}.pdf), [CSV](plots/{name}.csv), [metrics JSON](plots/{name}.json)')
    (HERE/'SCHOOL_COMPARISON.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(native_runs=len(analyses),listed_controls_exact=summary['all_listed_passivity_controls_exact'],
                          format_rounding=[entry['exact_after_six_significant_digit_rounding'] for entry in formats],
                          matrix=str(HERE/'comparison-summary.json')),indent=2))

if __name__=='__main__':main()
