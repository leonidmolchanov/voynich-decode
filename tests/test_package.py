"""Integration and rejection tests using isolated temporary package copies."""
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_manifest import build, disallowed
from verify_demo import apply_example, verify
from verify_artifact import read_registry


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.package, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, '-B', str(self.package / 'scripts' / name), *args],
                              cwd=self.temp.name, capture_output=True, text=True,
                              env={'PYTHONIOENCODING': 'utf-8'}, timeout=20)

    def test_clean_copy_cli(self):
        result = self.run_script('verify_demo.py')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)

    def test_manifest_rebuild_cli(self):
        before = (self.package / 'MANIFEST.json').read_bytes()
        result = self.run_script('build_manifest.py')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, (self.package / 'MANIFEST.json').read_bytes())
        self.assertEqual(self.run_script('verify_demo.py').returncode, 0)

    def test_changed_file_rejected(self):
        file = self.package / 'data/cells_sample.tsv'
        file.write_bytes(file.read_bytes() + b'\n')
        self.assertNotEqual(self.run_script('verify_demo.py').returncode, 0)

    def test_missing_file_rejected(self):
        (self.package / 'data/cells_sample.tsv').unlink()
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_extra_file_rejected(self):
        (self.package / 'data/unlisted.json').write_text('{}')
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_article_and_cache_rejected(self):
        self.assertTrue(disallowed(Path('article')))
        self.assertTrue(disallowed(Path('article/article.html')))
        (self.package / 'data/cache').mkdir()
        with self.assertRaises(ValueError):
            build(self.package)

    def test_symlink_rejected(self):
        (self.package / 'data/linked.tsv').symlink_to(self.package / 'data/cells_sample.tsv')
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_resealed_incorrect_correction_rejected(self):
        file = self.package / 'data/transcription_excerpts.tsv'
        file.write_text(file.read_text().replace('checkhy', 'checthy'))
        build(self.package)
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_resealed_duplicate_provenance_rejected(self):
        file = self.package / 'data/cell_provenance.tsv'
        lines = file.read_text().splitlines()
        file.write_text('\n'.join(lines + [lines[1]]) + '\n')
        build(self.package)
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_resealed_ambiguity_promotion_rejected(self):
        file = self.package / 'data/ambiguities.tsv'
        file.write_text(file.read_text().replace('EXCLUDE_FROM_ZERO_CORE', 'ACCEPTED', 1))
        build(self.package)
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_resealed_provenance_count_rejected(self):
        file = self.package / 'data/provenance.json'
        obj = json.loads(file.read_text())
        obj['sample_cells'] = 20
        file.write_text(json.dumps(obj))
        build(self.package)
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_duplicate_manifest_entry_rejected(self):
        file = self.package / 'MANIFEST.json'
        obj = json.loads(file.read_text())
        obj['files'].append(obj['files'][0])
        file.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):
            verify(self.package)

    def test_invalid_positions_and_tokens_rejected(self):
        for position in [-1, 0.5, 'x', '01']:
            with self.subTest(position=position), self.assertRaises(ValueError):
                apply_example('<f1r.1,+P0> a.b', position, 'b', 'c')
        for new in ['', 'a.b', 'a,b', 'a b']:
            with self.subTest(new=new), self.assertRaises(ValueError):
                apply_example('<f1r.1,+P0> a.b', 1, 'b', new)

    def test_artifact_cli_match_tamper_and_unknown(self):
        registry = read_registry()
        payload = Path(self.temp.name) / 'artifact.bin'
        payload.write_bytes(b'reproducible')
        item = copy.deepcopy(registry['artifacts'][0])
        item.update(bytes=12, sha256=hashlib.sha256(b'reproducible').hexdigest())
        registry['artifacts'] = [item]
        file = Path(self.temp.name) / 'registry.json'
        file.write_text(json.dumps(registry))
        args = ['--registry', str(file), '--id', item['id'], '--file', str(payload)]
        self.assertEqual(self.run_script('verify_artifact.py', *args).returncode, 0)
        payload.write_bytes(b'not-the-same')
        self.assertNotEqual(self.run_script('verify_artifact.py', *args).returncode, 0)
        args[3] = 'unknown'
        self.assertNotEqual(self.run_script('verify_artifact.py', *args).returncode, 0)

    def test_registry_invalid_shapes(self):
        original = read_registry()
        file = Path(self.temp.name) / 'registry.json'
        cases = [[], {}, {'schema': original['schema'], 'artifacts': []}]
        duplicate = copy.deepcopy(original)
        duplicate['artifacts'].append(duplicate['artifacts'][0])
        cases.append(duplicate)
        for field, value in [('sha256', 'not-a-hash'), ('bytes', True), ('project_path', '../private')]:
            obj = copy.deepcopy(original)
            obj['artifacts'][0][field] = value
            cases.append(obj)
        for obj in cases:
            file.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                read_registry(file)
        file.write_text('{invalid')
        with self.assertRaises(ValueError):
            read_registry(file)

    def test_english_docs_and_resolving_links(self):
        for path in [ROOT / 'README.md', ROOT / 'CITATION.cff', *sorted((ROOT / 'docs').glob('*.md'))]:
            content = path.read_text(encoding='utf-8')
            self.assertIsNone(re.search(r'[\u0400-\u04ff]', content), str(path))
            for target in re.findall(r'\]\(([^)]+)\)', content):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).is_file(), target)


if __name__ == '__main__':
    unittest.main()
