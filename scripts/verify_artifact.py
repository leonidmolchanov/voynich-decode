"""Check a supplied file against a registered SHA-256 without executing it."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / 'data/artifact-commitments-2026-10-02-v2.json'


def read_registry(path=DEFAULT_REGISTRY):
    registry = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(registry, dict) or registry.get('schema') != 'voynich-artifact-commitments-v1':
        raise ValueError('Unsupported registry schema')
    rows = registry.get('artifacts')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Empty or invalid artifact list')
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid artifact entry')
        ident = row.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', ident) or ident in ids:
            raise ValueError('Invalid or duplicate artifact ID')
        ids.add(ident)
        if not isinstance(row.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid SHA-256')
        if type(row.get('bytes')) is not int or row['bytes'] < 0:
            raise ValueError('Invalid byte count')
        name = row.get('project_path')
        if not isinstance(name, str) or not name or '\\' in name:
            raise ValueError('Invalid archive path')
        archive_path = PurePosixPath(name)
        if archive_path.is_absolute() or '..' in archive_path.parts:
            raise ValueError('Invalid archive path')
    return registry


def verify_artifact(path, entry):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Supply a regular file, not a symlink')
    before = path.stat()
    digest = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            count += len(block)
            digest.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError('File changed during verification')
    if count != entry['bytes'] or digest.hexdigest() != entry['sha256']:
        raise ValueError('File does not match registered bytes/SHA-256')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument('--id', required=True)
    parser.add_argument('--file', required=True, type=Path)
    args = parser.parse_args()
    try:
        registry = read_registry(args.registry)
        entry = next((r for r in registry['artifacts'] if r['id'] == args.id), None)
        if entry is None:
            raise ValueError('Unknown artifact ID')
        verify_artifact(args.file, entry)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    print('PASS: bytes match', args.id, '— identity only, not scientific validation')


if __name__ == '__main__':
    main()
