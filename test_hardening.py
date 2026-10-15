"""Adversarial CLI regressions. All fixtures are synthetic, local and temporary."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tool_diff import MAX_BYTES, MAX_DEPTH, load

class Hardening(unittest.TestCase):
    def check_invalid(self, raw):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'before.json',Path(d)/'after.json'
            a.write_text('{"tools":[]}');b.write_bytes(raw)
            r=subprocess.run([sys.executable,str(Path(__file__).with_name('tool_diff.py')),str(a),str(b)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,2,r.stderr)
            self.assertEqual(r.stderr,'')
            self.assertTrue(json.loads(r.stdout)['review_required'])
    def test_deep_parser(self):self.check_invalid(b'['*2000+b'0'+b']'*2000)
    def test_depth_limit(self):self.check_invalid(b'['*(MAX_DEPTH+1)+b'0'+b']'*(MAX_DEPTH+1))
    def test_oversized(self):self.check_invalid(b' '*(MAX_BYTES+1))
    def test_non_utf8(self):self.check_invalid(b'\xff')
    def test_truncated(self):self.check_invalid(b'{"tools":[')
    def test_duplicate_nested_key(self):self.check_invalid(b'{"tools":[{"name":"x","inputSchema":{"type":"object","type":"array"}}]}')
    def test_nonfinite(self):self.check_invalid(b'{"tools":[{"name":"x","inputSchema":{"x":NaN}}]}')
    def test_exact_byte_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'ok';base=b'{"tools":[]}';p.write_bytes(base+b' '*(MAX_BYTES-len(base)))
            self.assertEqual(load(p),{'tools':[]})

if __name__=='__main__':unittest.main()
