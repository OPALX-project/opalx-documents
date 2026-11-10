"""Standalone frame-adapter validation; not registered with native CTest.

Run with ~/.venv-h6/bin/python. Existing simulation products are read only;
all generated fixtures and CLI outputs use an automatically removed directory.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

import h5py
import numpy as np
import pandas as pd

ROOT = Path('/Users/adelmann/git/opalx-master')
TASK = ROOT/'tmp/ffa-probes-implementation-20261107'
UTILITY = ROOT/'tools/probe_frame_adapter.py'
spec = importlib.util.spec_from_file_location('probe_adapter', UTILITY)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
checks = []


def check(name, fn):
    fn()
    checks.append(name)


def reject(fn):
    try:
        fn()
    except (ValueError, OSError):
        return
    raise AssertionError('Invalid input was accepted')


def require(value):
    if not value:
        raise AssertionError('Condition is false')


def cli(*args):
    return subprocess.run([sys.executable, str(UTILITY), *map(str, args)],
                          text=True, capture_output=True, check=False)


def identity_equal(a, b):
    pd.testing.assert_frame_equal(a[['id', 'turn', 'bunchNumber', 'time']],
                                  b[['id', 'turn', 'bunchNumber', 'time']],
                                  check_exact=True)


with tempfile.TemporaryDirectory(prefix='probe-frame-adapter-') as directory:
    work = Path(directory)
    source = work/'native.loss'
    source.write_text(adapter.HEADER+'\n'
                      '-4.42 0.003 4.7 0.01 0.02 0.03 9007199254740993 0 3 2e-9\n'
                      '-4.40 -0.002 4.8 0.04 0.05 0.06 7 1 1 3e-9\n')
    native = adapter.read_probe(source)
    original = native.copy(deep=True)
    check('large_noncontiguous_ids_exact', lambda: np.testing.assert_array_equal(
        native.id, [7, 9007199254740993]))
    check('identity_exact', lambda: pd.testing.assert_frame_equal(
        adapter.transform_frame(native), native, check_exact=True))

    # Rational entries of the quaternion (1,2,3,4)/sqrt(30) rotation.
    rational = [[Fraction(-2, 3), Fraction(2, 15), Fraction(11, 15)],
                [Fraction(2, 3), Fraction(-1, 3), Fraction(2, 3)],
                [Fraction(1, 3), Fraction(14, 15), Fraction(2, 15)]]
    basis = np.asarray(rational, dtype=float)
    origin = np.array([0.7, -0.2, 1.3])
    transformed = adapter.transform_frame(native, origin, basis)
    # Independent scalar exact-rational calculation, rather than repeating
    # the production matrix expression as the expected value.
    expected_positions, expected_momenta = [], []
    for row in native.itertuples():
        r = [Fraction(str(value)) - Fraction(str(offset))
             for value, offset in zip((row.x, row.y, row.z), origin)]
        p = [Fraction(str(value)) for value in (row.px, row.py, row.pz)]
        expected_positions.append([float(sum(a*b for a, b in zip(axis, r)))
                                   for axis in rational])
        expected_momenta.append([float(sum(a*b for a, b in zip(axis, p)))
                                 for axis in rational])
    check('arbitrary_rotation_translation_exact_rational_oracle', lambda:
          np.testing.assert_allclose(transformed[['x', 'y', 'z']], expected_positions,
                                     rtol=0, atol=2e-15))
    check('polar_momentum_rotation_without_translation', lambda:
          np.testing.assert_allclose(transformed[['px', 'py', 'pz']], expected_momenta,
                                     rtol=0, atol=3e-17))
    check('ids_bunch_turn_time_preserved_exactly', lambda: identity_equal(transformed, native))
    check('source_dataframe_unchanged', lambda:
          pd.testing.assert_frame_equal(native, original, check_exact=True))
    inverse = adapter.transform_frame(transformed, -basis @ origin, basis.T)
    check('inverse_frame_round_trip', lambda: np.testing.assert_allclose(
        inverse[['x', 'y', 'z', 'px', 'py', 'pz']],
        native[['x', 'y', 'z', 'px', 'py', 'pz']], rtol=0, atol=2e-15))
    check('momentum_norm_preserved', lambda: np.testing.assert_allclose(
        np.linalg.norm(transformed[['px', 'py', 'pz']], axis=1),
        np.linalg.norm(native[['px', 'py', 'pz']], axis=1), rtol=0, atol=2e-17))
    check('distance_from_origin_preserved', lambda: np.testing.assert_allclose(
        np.linalg.norm(transformed[['x', 'y', 'z']], axis=1),
        np.linalg.norm(native[['x', 'y', 'z']].to_numpy()-origin, axis=1),
        rtol=0, atol=2e-15))
    permutation = ((1, 0, 0), (0, 0, 1), (0, 1, 0))
    permuted = adapter.transform_frame(native, (-4.42, 0, 0), permutation)
    check('handedness_changing_axis_permutation', lambda: np.testing.assert_allclose(
        permuted[['x', 'y', 'z', 'px', 'py', 'pz']],
        [[0.02, 4.8, -0.002, 0.04, 0.06, 0.05],
         [0, 4.7, 0.003, 0.01, 0.03, 0.02]], rtol=0, atol=1e-15))
    check('negative_coordinate_and_origin_supported', lambda: np.testing.assert_allclose(
        adapter.transform_frame(native, (-8, 5, -2))[['x', 'y', 'z']],
        native[['x', 'y', 'z']].to_numpy() + [8, -5, 2], rtol=0, atol=0))
    check('repeated_same_turn_crossings_preserved', lambda: require(len(
        adapter.transform_frame(pd.concat([native, native], ignore_index=True),
                                origin, basis)) == 4))

    for name, options in [
        ('origin_shape', {'origin_m': (1, 2)}),
        ('origin_nonfinite', {'origin_m': (0, np.nan, 0)}),
        ('basis_shape', {'basis': (1, 0, 0)}),
        ('basis_nonfinite', {'basis': [[np.inf, 0, 0], [0, 1, 0], [0, 0, 1]]}),
        ('basis_scaling', {'basis': np.diag([1.01, 1, 1])}),
        ('basis_shear', {'basis': [[1, 0.1, 0], [0, 1, 0], [0, 0, 1]]}),
        ('basis_singular', {'basis': np.zeros((3, 3))}),
    ]:
        check(name+'_rejected', lambda options=options:
              reject(lambda: adapter.transform_frame(native, **options)))
    bad = native.copy()
    bad.loc[0, 'x'] = np.nan
    check('nonfinite_record_rejected', lambda: reject(lambda: adapter.transform_frame(bad)))
    float_ids = native.copy()
    float_ids['id'] = float_ids.id.astype(float)
    check('floating_point_ids_rejected', lambda:
          reject(lambda: adapter.transform_frame(float_ids)))
    huge = native.copy()
    huge['id'] = [2**63, 7]
    check('out_of_range_ids_rejected', lambda: reject(lambda: adapter.transform_frame(huge)))
    overflow = native.copy()
    overflow['x'] = np.finfo(float).max
    check('position_overflow_rejected', lambda: reject(lambda:
          adapter.transform_frame(overflow, (-np.finfo(float).max, 0, 0))))
    output = work/'converted.loss'
    adapter.write_probe_ascii(transformed, output)
    check('ascii_output_ten_columns', lambda: require(all(
        len(line.split()) == 10 for line in output.read_text().splitlines()
        if not line.startswith('#'))))
    restored = adapter.read_probe(output)
    check('ascii_round_trip_integer_metadata_exact', lambda: identity_equal(restored, transformed))
    check('ascii_round_trip_coordinates', lambda: np.testing.assert_array_equal(
        restored[list(adapter.FLOAT_COLUMNS)], transformed[list(adapter.FLOAT_COLUMNS)]))
    before = output.read_bytes()
    check('exclusive_output_rejects_overwrite', lambda:
          reject(lambda: adapter.write_probe_ascii(native, output)))
    check('existing_output_unchanged', lambda: require(output.read_bytes() == before))

    hdf = work/'native.h5'
    with h5py.File(hdf, 'w') as file:
        for key, index in [('Step#10', 0), ('Step#2', 1)]:
            group = file.create_group(key)
            for column in adapter.COLUMNS:
                group[column] = native[column].iloc[[index]].to_numpy()
    check('all_hdf5_flush_batches_equal_ascii', lambda: pd.testing.assert_frame_equal(
        adapter.read_probe(hdf), native, check_exact=True))
    check('hdf5_ascii_transforms_equal', lambda: pd.testing.assert_frame_equal(
        adapter.transform_frame(adapter.read_probe(hdf), origin, basis), transformed,
        check_exact=True))
    empty = work/'empty.loss'
    empty.write_text(adapter.HEADER+'\n')
    converted_empty = adapter.transform_frame(adapter.read_probe(empty), origin, basis)
    empty_output = work/'empty-converted.loss'
    adapter.write_probe_ascii(converted_empty, empty_output)
    check('header_only_ascii_conversion', lambda: require(
        empty_output.read_text() == adapter.HEADER+'\n'))
    with h5py.File(work/'empty.h5', 'w') as file:
        group = file.create_group('Step#0')
        for column in adapter.COLUMNS:
            group[column] = np.array([], dtype='i8' if column in adapter.INTEGER_COLUMNS else 'f8')
    check('empty_hdf5_batch_supported', lambda: require(
        len(adapter.transform_frame(adapter.read_probe(work/'empty.h5'), origin, basis)) == 0))
    malformed = work/'bad.loss'
    malformed.write_text('1 2 3\n')
    check('malformed_ascii_width_rejected', lambda: reject(lambda: adapter.read_probe(malformed)))
    check('missing_input_rejected', lambda: reject(lambda: adapter.read_probe(work/'missing.loss')))
    with h5py.File(work/'bad.h5', 'w') as file:
        file.create_group('Step#0')['x'] = [1.]
    check('missing_hdf5_columns_rejected', lambda:
          reject(lambda: adapter.read_probe(work/'bad.h5')))
    with h5py.File(work/'unequal.h5', 'w') as file:
        group = file.create_group('Step#0')
        for column in adapter.COLUMNS:
            group[column] = native[column].to_numpy()[:1 if column == 'x' else 2]
    check('unequal_hdf5_lengths_rejected', lambda:
          reject(lambda: adapter.read_probe(work/'unequal.h5')))
    with h5py.File(work/'float-ids.h5', 'w') as file:
        group = file.create_group('Step#0')
        for column in adapter.COLUMNS:
            values = native[column].to_numpy()
            group[column] = values.astype(float) if column == 'id' else values
    check('float_hdf5_ids_rejected', lambda:
          reject(lambda: adapter.read_probe(work/'float-ids.h5')))

    result = cli('--help')
    check('cli_help', lambda: require(result.returncode == 0 and '--basis' in result.stdout))
    cli_output = work/'cli.loss'
    result = cli(source, cli_output, '--origin-m', *origin, '--basis', *basis.ravel())
    check('cli_arbitrary_transform_succeeds', lambda: require(result.returncode == 0))
    check('cli_matches_api_exact_file', lambda: require(cli_output.read_bytes() == output.read_bytes()))
    cli_identity = work/'cli-identity.loss'
    result = cli(hdf, cli_identity)
    check('cli_default_identity', lambda: require(result.returncode == 0))
    check('cli_identity_metadata_exact', lambda: identity_equal(adapter.read_probe(cli_identity), native))
    check('cli_identity_coordinates', lambda: np.testing.assert_array_equal(
        adapter.read_probe(cli_identity)[list(adapter.FLOAT_COLUMNS)],
        native[list(adapter.FLOAT_COLUMNS)]))
    same_input = source.read_bytes()
    result = cli(source, source)
    check('cli_same_input_output_rejected', lambda: require(
        result.returncode == 1 and 'Input and output must be different' in result.stderr
        and source.read_bytes() == same_input))
    result = cli(source, cli_output)
    check('cli_existing_output_rejected', lambda: require(
        result.returncode == 1 and cli_output.read_bytes() == before))
    invalid_output = work/'invalid-output.loss'
    result = cli(source, invalid_output, '--basis', 2, 0, 0, 0, 1, 0, 0, 0, 1)
    check('cli_invalid_basis_no_output', lambda: require(
        result.returncode == 1 and 'orthonormal' in result.stderr and not invalid_output.exists()))
    result = cli(malformed, invalid_output)
    check('cli_invalid_data_no_output', lambda: require(
        result.returncode == 1 and 'ten probe columns' in result.stderr and not invalid_output.exists()))

# Read immutable, already-completed FFA runs; no simulator launch or data rewrite.
real_hdf_root = TASK/'native-16-cell-matched-hdf5-r1'
real_ascii_root = TASK/'native-16-cell-matched-ascii-r1'
real_hits = 0
real_files = []
for station in range(1, 17):
    hdf_path = real_hdf_root/f'PROBE{station}.h5'
    ascii_path = real_ascii_root/f'PROBE{station}.loss'
    hdf = adapter.read_probe(hdf_path)
    ascii_frame = adapter.read_probe(ascii_path)
    pd.testing.assert_frame_equal(hdf[list(adapter.INTEGER_COLUMNS)],
                                  ascii_frame[list(adapter.INTEGER_COLUMNS)], check_exact=True)
    # The writer's six-significant-digit ASCII is a lossy representation;
    # compare its exact decimal tokens with rounded HDF5 values.
    tokens = [line.split() for line in ascii_path.read_text().splitlines()
              if line.strip() and not line.startswith('#')]
    for column in adapter.FLOAT_COLUMNS:
        index = adapter.COLUMNS.index(column)
        expected = [float(format(value, '.6g')) for value in hdf[column]]
        actual = [float(row[index]) for row in tokens]
        np.testing.assert_array_equal(actual, expected)
    converted = adapter.transform_frame(hdf, origin, basis)
    identity_equal(converted, hdf)
    np.testing.assert_allclose(
        np.linalg.norm(converted[['px', 'py', 'pz']], axis=1),
        np.linalg.norm(hdf[['px', 'py', 'pz']], axis=1), rtol=1e-15, atol=1e-17)
    real_hits += len(hdf)
    real_files.append({'station': station, 'hits': len(hdf),
                       'hdf5_sha256': hashlib.sha256(hdf_path.read_bytes()).hexdigest(),
                       'ascii_sha256': hashlib.sha256(ascii_path.read_bytes()).hexdigest()})
check('real_ffa_all_stations_57_hits_preserved', lambda: require(real_hits == 57))
check('real_ffa_ascii_hdf5_metadata_exact', lambda: require(len(real_files) == 16))
check('real_ffa_arbitrary_rotation_norms_metadata', lambda: require(len(real_files) == 16))
report = {'checks': checks, 'passed': len(checks), 'failed': 0,
          'adapter_sha256': hashlib.sha256(UTILITY.read_bytes()).hexdigest(),
          'validator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'real_ffa_hits': real_hits, 'real_ffa_files': real_files,
          'note': 'Standalone analysis utility validation only; native C++ and GPU tracking unchanged. '
                  'Rational rotation oracle and inverse checks use absolute 2e-15 m / 3e-17 p/(mc) '
                  'roundoff tolerances. No simulation, reference-data or physics-tolerance changes.'}
Path(__file__).with_name('validation-general.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({key: value for key, value in report.items() if key != 'real_ffa_files'}, indent=2))
