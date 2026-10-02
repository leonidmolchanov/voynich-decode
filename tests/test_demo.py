import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_demo import apply_example,verify

class DemoTests(unittest.TestCase):
    def test_sealed_demo(self):self.assertEqual(verify()['sample_cells'],19)
    def test_preserves_separators(self):
        self.assertEqual(apply_example('<f1r.1,+P0>  a,b.c',1,'b','d'),'<f1r.1,+P0>  a,d.c')
    def test_rejects_wrong_original(self):
        with self.assertRaises(ValueError):apply_example('<f1r.1,+P0> a.b',1,'x','d')
    def test_rejects_wrong_position(self):
        with self.assertRaises(ValueError):apply_example('<f1r.1,+P0> a.b',5,'b','d')

if __name__=='__main__':unittest.main()
