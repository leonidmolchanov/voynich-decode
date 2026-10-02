"""Verify the selected transcription data and the package inventory."""
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from verify_artifact import read_registry
from build_manifest import inventory

ROOT = Path(__file__).resolve().parents[1]


def rows(root, name):
    with (root / 'data' / name).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('Invalid table header: ' + name)
        result = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in result):
            raise ValueError('Malformed table row: ' + name)
        return result


def apply_example(line, position, old, new):
    if not re.fullmatch(r'0|[1-9][0-9]*', str(position)):
        raise ValueError('Position must be a nonnegative integer')
    if not old or not new or re.search(r'[.,\s]', old + new):
        raise ValueError('Expected individual nonempty tokens')
    match = re.fullmatch(r'(<[^>]+>\s+)(.*)', line)
    if not match:
        raise ValueError('Invalid example line')
    prefix, body = match.groups()
    parts = re.split(r'([.,])', body)
    at = 2 * int(position)
    if at >= len(parts) or parts[at] != old:
        raise ValueError('Old token mismatch')
    parts[at] = new
    return prefix + ''.join(parts)


def verify(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('schema') != 'voynich-minimal-files-v1':
        raise ValueError('Invalid package manifest')
    expected = manifest.get('files')
    if not isinstance(expected, list) or expected != inventory(root):
        raise ValueError('Manifest mismatch: changed, missing, duplicate or unexpected files')
    corrections = rows(root, 'corrections.tsv')
    excerpts = rows(root, 'transcription_excerpts.tsv')
    correction_ids = {'ZL3B-0001', 'ZL3B-0003'}
    if len(corrections) != 2 or {r['correction_id'] for r in corrections} != correction_ids:
        raise ValueError('Wrong correction selection')
    if len(excerpts) != 2 or {r['correction_id'] for r in excerpts} != correction_ids:
        raise ValueError('Wrong excerpt selection')
    for correction in corrections:
        ex = next(r for r in excerpts if r['correction_id'] == correction['correction_id'])
        address = correction['locus'] + ':' + correction['position_zero_based']
        if ex['record_id'] != address or not ex['source_line'].startswith('<' + correction['locus'] + ','):
            raise ValueError('Correction address mismatch')
        if apply_example(ex['source_line'], correction['position_zero_based'],
                         correction['original_surface'], correction['corrected_surface']) != ex['corrected_line']:
            raise ValueError('Correction reproduction failed')
    ambiguous = rows(root, 'ambiguities.tsv')
    if (len(ambiguous) != 7 or len({r['ambiguity_id'] for r in ambiguous}) != 7
            or any(r['action'] != 'EXCLUDE_FROM_ZERO_CORE' for r in ambiguous)):
        raise ValueError('Ambiguity policy changed')
    cells = rows(root, 'cells_sample.tsv')
    refs = rows(root, 'cell_provenance.tsv')
    ids = {r['record_id'] for r in cells}
    if len(cells) != 19 or len(ids) != 19 or len(refs) != 19 or ids != {r['record_id'] for r in refs}:
        raise ValueError('Cell/provenance selection mismatch')
    tiers = {'STRICT_ACCEPTED', 'ENSEMBLE_OR_CHAIN_CANDIDATE', 'FORCED_TRANSCRIPTION_SYMBOLIC'}
    for cell in cells:
        if cell['record_id'].split(':')[0] not in {'f108r.10', 'f115r.23'}:
            raise ValueError('Cell outside selected lines')
        if cell['assignment_tier'] not in tiers:
            raise ValueError('Unrecognized assignment tier')
        ref = next(r for r in refs if r['record_id'] == cell['record_id'])
        if cell['folio'] != ref['folio'] or cell['folio'] != cell['record_id'].split('.')[0]:
            raise ValueError('Cell/provenance folio mismatch')
    for correction in corrections:
        address = correction['locus'] + ':' + correction['position_zero_based']
        if next(r for r in cells if r['record_id'] == address)['surface'] != correction['corrected_surface']:
            raise ValueError('Cell disagrees with corrected reading')
    provenance = json.loads((root / 'data/provenance.json').read_text(encoding='utf-8'))
    for key, count in [('corrections_in_demo', 2), ('open_ambiguities', 7), ('sample_cells', 19)]:
        if provenance.get(key) != count:
            raise ValueError('Provenance count mismatch: ' + key)
    registry = read_registry(root / 'data/artifact-commitments-2026-10-02-v2.json')
    if any(row.get('payload_in_demo') is not False for row in registry['artifacts']):
        raise ValueError('Future payload incorrectly marked as distributed')
    return {'files': len(expected), 'corrections': 2, 'ambiguities': 7,
            'sample_cells': 19, 'future_artifact_commitments': len(registry['artifacts'])}


if __name__ == '__main__':
    try:
        print('PASS:', json.dumps(verify()), '— package checks, not full-study replication')
    except (ValueError, KeyError, OSError, StopIteration) as exc:
        raise SystemExit('FAIL: ' + str(exc))
