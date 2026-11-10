"""Collect independently audited initialization, field errors, and mesh changes."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    cases, audits, metrics, snapshots = {}, [], [], {}
    for path in sorted(HERE.glob('*.json')):
        item = json.loads(path.read_text())
        if 'initialization_valid' not in item or 'full' not in item:
            continue
        case = item['case']
        full = item['full']
        manifest = json.loads((HERE.parent/'runs'/case/'manifest.json').read_text())
        for label, filename in manifest['source'].get('generator_snapshots', {}).items():
            snapshot = Path(filename)
            actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
            assert actual == snapshot.stem
            snapshots[str(snapshot)] = dict(label=label, sha256=actual, passed=True)
        audits.append(dict(case=case, initialization_valid=item['initialization_valid'],
            comparison_interpretable=item['comparison_interpretable'],
            binary_sha256=full['binary_sha256'], source_particles=full['source_particles'],
            source_q_C=full['output_source_q_C'], q_max_relative_change=full['q_max_relative_change'],
            m_max_relative_change=full['m_max_relative_change'],
            max_frozen_motion_residual_m=full['max_frozen_motion_residual_m']))
        if not item['initialization_valid']:
            continue
        cases[case] = pd.read_csv(HERE/(case+'-fields.csv'), float_precision='round_trip')
        for row in item['field_metrics']:
            metrics.append(dict(case=case, **row))
    pd.DataFrame(audits).to_csv(HERE/'audit-summary.csv', index=False)
    pd.DataFrame(metrics).to_csv(HERE/'field-error-summary.csv', index=False)
    (HERE/'generator-snapshot-checks.json').write_text(json.dumps(snapshots, indent=2)+'\n')
    points = pd.read_csv(HERE.parent/'reference/points_extended.csv', float_precision='round_trip')
    pairs = []
    for profile in ['uniform', 'triangle']:
        primary = profile+'-cell-z8192-final'
        source = profile+'-control-source96-final'
        mesh = profile+'-control-mesh96-final'
        for first, second, kind in [
            (profile+'-cell-z2048-final', profile+'-cell-z4096-final', 'longitudinal_2048_to_4096'),
            (profile+'-cell-z4096-final', primary, 'longitudinal_4096_to_8192'),
            (primary, source, 'source_refinement_64_to_96'),
            (source, mesh, 'transverse_mesh_64_to_96'),
            (primary, profile+'-control-path01-final', 'path_step_002_to_001'),
        ]:
            if first not in cases or second not in cases:
                continue
            d = cases[first].merge(cases[second], on='point_id', suffixes=('_a', '_b'), validate='one_to_one')
            d = d.merge(points[['point_id', 'original_target']], on='point_id', validate='one_to_one')
            for target_set, selected in [('original43', d.original_target), ('all51', np.ones(len(d), dtype=bool))]:
                for component in ['r', 'y', 's']:
                    ref = d[f'SACR_E_{component}_V_m_a']
                    assert np.array_equal(ref, d[f'SACR_E_{component}_V_m_b'])
                    delta = d[f'native_E_{component}_V_m_b']-d[f'native_E_{component}_V_m_a']
                    nonzero = selected & (ref.abs()>1e-8)
                    zero = selected & ~nonzero
                    pairs.append(dict(profile=profile, kind=kind, case_a=first, case_b=second,
                        target_set=target_set, component=component,
                        max_change_percent_of_local_SACR=float((100*delta[nonzero]/ref[nonzero]).abs().max()),
                        max_change_at_symmetry_zero_V_m=float(delta[zero].abs().max()) if zero.any() else 0.))
    pd.DataFrame(pairs).to_csv(HERE/'independent-control-changes.csv', index=False)
    print(f'{len(audits)} audited cases; {len(metrics)} field-error rows; {len(pairs)} convergence rows')


if __name__ == '__main__':
    main()
