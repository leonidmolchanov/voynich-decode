import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_artifact import read_registry, verify_artifact
from build_manifest import disallowed

class ArtifactTests(unittest.TestCase):
    def test_private_paths_rejected(self):
        for name in ['data/weights.pt', 'data/a.safetensors', 'data/.env.local',
                     'scripts/__pycache__/a.pyc', 'article/cache/image.png', 'data/private.key']:
            self.assertTrue(disallowed(Path(name)), name)
        self.assertFalse(disallowed(Path('data/artifact-commitments-2026-10-02-v2.json')))

    def test_registry_metadata_only(self):
        rows = read_registry()['artifacts']
        self.assertEqual(sum(r['kind'] == 'weights' for r in rows), 15)
        self.assertTrue(all(r['payload_in_demo'] is False for r in rows))
        for row in rows:
            self.assertFalse(Path(row['project_path']).is_absolute())
            self.assertNotIn('..', Path(row['project_path']).parts)

    def test_match_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'example.bin'
            path.write_bytes(b'example')
            entry = {'bytes': 7, 'sha256': hashlib.sha256(b'example').hexdigest()}
            self.assertTrue(verify_artifact(path, entry))
            path.write_bytes(b'Example')
            with self.assertRaises(ValueError):
                verify_artifact(path, entry)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                verify_artifact(Path(tmp) / 'missing.bin', {})

    def test_wrong_size_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'example.bin'
            path.write_bytes(b'example')
            entry = {'bytes': 8, 'sha256': hashlib.sha256(b'example').hexdigest()}
            with self.assertRaises(ValueError):
                verify_artifact(path, entry)
            link = Path(tmp) / 'link.bin'
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                verify_artifact(link, entry)

if __name__ == '__main__':
    unittest.main()
