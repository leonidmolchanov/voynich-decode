"""Build a SHA-256 inventory for the explicitly scoped code/data package."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {'.gitignore', '.gitattributes', 'README.md', 'LICENSE', 'CITATION.cff', 'MANIFEST.json'}
DIRECTORIES = {'data': {'.tsv', '.json'}, 'docs': {'.md'},
               'scripts': {'.py'}, 'tests': {'.py'}}


def disallowed(rel):
    forbidden = {'__pycache__', '.DS_Store', '.pytest_cache', '.venv', 'node_modules',
                 'WORKING', 'PRIVATE_RECORDS', 'web_cache', 'cache', '.cache', 'wandb', 'runs'}
    if rel.is_absolute() or '..' in rel.parts:
        return True
    if any(x in forbidden or x.startswith('rendered') or x.startswith('.env') for x in rel.parts):
        return True
    if len(rel.parts) == 1:
        return str(rel) not in ROOT_FILES and str(rel) not in DIRECTORIES
    return rel.parts[0] not in DIRECTORIES or rel.suffix not in DIRECTORIES[rel.parts[0]]


def inventory(root=ROOT):
    entries = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if rel.parts[0] == '.git':
            continue
        if path.is_symlink():
            raise ValueError('Symlink not allowed: ' + str(rel))
        if disallowed(rel):
            raise ValueError('Unexpected package path: ' + str(rel))
        if not path.is_file() or str(rel) == 'MANIFEST.json':
            continue
        before = path.stat()
        payload = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise ValueError('File changed while hashing: ' + str(rel))
        entries.append({'path': rel.as_posix(), 'bytes': len(payload),
                        'sha256': hashlib.sha256(payload).hexdigest()})
    return entries


def build(root=ROOT):
    result = {'schema': 'voynich-minimal-files-v1', 'files': inventory(root)}
    (root / 'MANIFEST.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    try:
        print('Manifest:', len(build()['files']), 'files')
    except (ValueError, OSError) as exc:
        raise SystemExit('FAIL: ' + str(exc))
