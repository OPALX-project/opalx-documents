"""Qualify agreed fine frozen-field results separately from coarse convergence."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROFILES=['uniform','triangle']
PRIMARY={profile:f'{profile}-cell-z8192-final' for profile in PROFILES}
SERIES={profile:[f'{profile}-cell-z{nz}-final' for nz in [2048,4096,8192]] for profile in PROFILES}
CONTROLS=[
    dict(case_a=PRIMARY['uniform'],case_b='uniform-control-source96-final',label='Uniform source refinement',kind='source'),
    dict(case_a='uniform-control-source96-final',case_b='uniform-control-mesh96-final',label='Uniform transverse field mesh',kind='field mesh'),
    dict(case_a=PRIMARY['triangle'],case_b='triangle-control-source96-final',label='Triangular source refinement',kind='source'),
    dict(case_a='triangle-control-source96-final',case_b='triangle-control-mesh96-final',label='Triangular transverse field mesh',kind='field mesh'),
    dict(case_a=PRIMARY['uniform'],case_b='uniform-control-path01-final',label='Reference-path refinement',kind='path')]
QUALIFIED=list(PRIMARY.values())+[item['case_b'] for item in CONTROLS]
CASES=[case for series in SERIES.values() for case in series]+[item['case_b'] for item in CONTROLS]
FINAL_BINARY='70383ff72345d869db40d42d2ff5aee8ceaa2f1f4fa656fcf2e8fc75e35647c1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_clean(value):
    if isinstance(value,dict):
        return {key:json_clean(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):
        return [json_clean(item) for item in value]
    if isinstance(value,np.generic):
        return json_clean(value.item())
    if isinstance(value,float) and not np.isfinite(value):
        return None
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-analysis',action='store_true',help='use already verified combined CSV instead of rereading H5')
    args=parser.parse_args()
    manifests={case:json.loads((ROOT/'runs'/case/'manifest.json').read_text()) for case in CASES}
    for case,manifest in manifests.items():
        if manifest.get('returncode')!=0 or manifest['binary_sha256']!=FINAL_BINARY:
            raise ValueError('Case is incomplete or differs from frozen binary: '+case)
        companion=json.loads((ROOT/'runs'/(case+'-probes')/'manifest.json').read_text())
        if companion.get('returncode')!=0 or companion['binary_sha256']!=FINAL_BINARY:
            raise ValueError('Companion is incomplete or differs from frozen binary: '+case)
    for profile,series in SERIES.items():
        if len({manifests[case]['source']['sha256'] for case in series})!=1:
            raise ValueError('Longitudinal series must hold its physical source fixed')
        if len({manifests[case]['reference_path_sha256'] for case in series})!=1:
            raise ValueError('Longitudinal series must hold its reference path fixed')
    for control in CONTROLS:
        aa,bb=manifests[control['case_a']],manifests[control['case_b']]
        if control['kind']=='source' and aa['mesh']!=bb['mesh']:
            raise ValueError('Source control changes the field mesh')
        if control['kind'] in ['field mesh','path'] and aa['source']['sha256']!=bb['source']['sha256']:
            raise ValueError('Field/path control changes its physical source')
        if control['kind']!='path' and aa['reference_path_sha256']!=bb['reference_path_sha256']:
            raise ValueError('A non-path control changes the path')
    if not args.skip_analysis:
        subprocess.run([sys.executable,str(ROOT/'analyze_fields.py'),'--cases',*CASES],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/'export_source_quadratures.py')],cwd=ROOT,check=True)
    fields=pd.read_csv(ROOT/'analysis/field_comparison.csv',float_precision='round_trip')
    if set(fields.case.unique())!=set(CASES):
        raise ValueError('Combined native comparison CSV has a different selected-case set')
    summary=pd.read_csv(ROOT/'analysis/field_summary.csv')
    integrity=pd.read_csv(ROOT/'analysis/run_integrity_checks.csv')
    metrics=[]
    for case in QUALIFIED:
        for component in ['r','y','s']:
            data=fields[(fields.case==case)&(fields.component==component)&fields.original_target]
            relative=data.relative_pointwise_error.abs().dropna()
            worst=data.loc[data.relative_pointwise_error.abs().idxmax()]
            metrics.append(dict(case=case,profile=manifests[case]['profile'],component=component,points=len(data),
                max_abs_relative_pointwise_error=float(relative.max()),
                max_abs_error_over_component_scale=float(data.error_over_component_scale.abs().max()),
                worst_nonzero_point=worst.point_id,
                passed=bool(relative.max()<.01 and data.error_over_component_scale.abs().max()<.01)))
    controls=[]
    for control in CONTROLS:
        aa=fields[(fields.case==control['case_a'])&fields.original_target]
        bb=fields[(fields.case==control['case_b'])&fields.original_target]
        merged=aa.merge(bb,on=['point_id','component'],suffixes=('_a','_b'),validate='one_to_one')
        for component,data in merged.groupby('component',sort=False):
            difference=data.E_fft_V_m_b-data.E_fft_V_m_a
            reference=data.E_sacr_V_m_b
            scale=data.component_scale_V_m_b
            nonzero=reference.abs()>scale*1e-10
            rel=(difference[nonzero]/reference[nonzero]).abs()
            scaled=(difference/scale).abs()
            controls.append(control|dict(component=component,
                max_abs_relative_nonzero_component_change=float(rel.max()),
                max_abs_change_over_component_scale=float(scaled.max()),
                passed=bool(rel.max()<.01 and scaled.max()<.01)))
    # Analyzer has already verified the complete q/m arrays by ID; these flags
    # preserve that strict native-data audit in the scoped final qualification.
    selected_integrity=integrity[integrity.case.isin(QUALIFIED+[case+'-probes' for case in QUALIFIED])]
    integrity_flags=['input_hashes_passed','output_checkpoint_q_attributes_passed','output_checkpoint_m_attributes_passed']
    attributes_passed=bool(len(selected_integrity)==2*len(QUALIFIED)
        and all(selected_integrity[key].eq(True).all() for key in integrity_flags))
    charge=[]
    for case in QUALIFIED:
        aa=selected_integrity[selected_integrity.case==case].iloc[0]
        bb=selected_integrity[selected_integrity.case==case+'-probes'].iloc[0]
        actual=float(aa.authoritative_q_sum_C-bb.authoritative_q_sum_C)
        charge.append(dict(case=case,actual_source_charge_C=actual,relative_error=actual/1e-11-1,
                           passed=abs(actual/1e-11-1)<1e-11))
    extras=summary[(summary.case.isin(QUALIFIED))&(summary.selection=='extra_diagnostic')]
    centre=summary[(summary.case.isin(QUALIFIED))&(summary.selection=='weak_centre_radial')]
    selection=dict(cases=CASES,mesh_series=SERIES,primary=PRIMARY,controls=CONTROLS,
        qualified_cases=QUALIFIED,coarse_refinement_cases=[case for case in CASES if case not in QUALIFIED],
        frozen_binary_sha256=FINAL_BINARY,
        field_operator='finite curved OPEN electrostatic, gamma=1; direct companion subtraction',
        original_target_count=43,additional_diagnostic_target_count=8)
    result=dict(passed=bool(all(row['passed'] for row in metrics+controls+charge) and attributes_passed),
        target_relative_accuracy=.01,selected_fine_cases=QUALIFIED,primary=PRIMARY,
        spatial_scope='43 agreed interior targets; closest uniform-end targets are5mm from the source end',
        geometry=dict(full_length_m=5.,radius_m=2.,radial_semiaxis_m=.005,vertical_semiaxis_m=.0005,
                      source_charge_C=1e-11,beta=.001,time_step_s=1e-17),
        field_metrics=metrics,control_changes=controls,actual_charge_audits=charge,
        all_native_q_m_attributes_preserved_by_ID=attributes_passed,
        weak_centre_radial_metrics=centre.to_dict(orient='records'),
        additional_eight_diagnostics=extras.to_dict(orient='records'),
        original_nonzero_reference_threshold='1e-10 times that direction maximum at the43 agreed targets',
        coarse_levels_enter_fine_pass_status=False,
        limits=['Frozen low-beta electrostatic fields, not finite-step curved tracking or relativistic dynamics.',
                'The8 extra near-cusp/1mm/0.1mm-end diagnostics remain explicit and do not enter the43-point1% criterion.',
                'Weighted-source CHARGE header is not authoritative; complete native q datasets and output-checkpoint q/m arrays were audited instead.'],
        frozen_binary_sha256=FINAL_BINARY,
        evidence_sha256={name:sha(ROOT/name) for name in ['analysis/field_comparison.csv','analysis/field_summary.csv',
            'analysis/run_integrity_checks.csv','analysis/convergence_changes.csv','reference/acceptance.json',
            'reference/cell_source_quadrature_checks.csv','qualify_results.py']})
    (ROOT/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    (ROOT/'final-acceptance.json').write_text(json.dumps(json_clean(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(passed=result['passed'],qualified_cases=QUALIFIED,
                         max_nonzero_point_error=max(row['max_abs_relative_pointwise_error'] for row in metrics)),indent=2))
    if not result['passed']:
        raise SystemExit('Scoped fine-field qualification failed')


if __name__=='__main__':
    main()
