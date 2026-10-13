"""Check published bytes, actual execution evidence and bundled regressions in CI."""
import hashlib,json,subprocess,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'static/demos/hooks-execution-evidence'
class HooksExecutionEvidenceTests(unittest.TestCase):
    def test_manifest_matches_every_asset(self):
        manifest=json.loads((ASSETS/'manifest.json').read_text())
        self.assertEqual(manifest['durationSeconds'],65.6)
        self.assertEqual(manifest['qualification'],'released-binary-with-included-adapter-source')
        for entry in manifest['files']:
            data=(ASSETS/entry['file']).read_bytes()
            self.assertEqual(len(data),entry['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'])
    def test_public_receipt_proves_actual_output(self):
        receipt=json.loads((ASSETS/'execution-receipt.json').read_text())
        output=(ASSETS/'validation.json').read_bytes()
        self.assertEqual(receipt['original_input']['command'],'python3 validate-brief.py --chek')
        self.assertEqual(receipt['executed_input']['command'],'python3 validate-brief.py --check')
        self.assertEqual(receipt['tool_result']['exit_code'],0)
        self.assertEqual(receipt['execution_id'],json.loads(output)['execution_id'])
        self.assertEqual(json.loads(receipt['tool_result']['combined_output']),json.loads(output))
        self.assertEqual(hashlib.sha256(output).hexdigest(),receipt['artifact']['sha256'])
    def test_extracted_example_and_regressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(ASSETS/'terraphim-hooks-execution-evidence-v2.zip') as z:
                self.assertIsNone(z.testzip())
                self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist()))
                z.extractall(tmp)
            for args in [['node','reproduction/verify.mjs','recorded-run'],['node','--test','tests/execution-trace.test.mjs','tests/verify-evidence.test.mjs']]:
                run=subprocess.run(args,cwd=tmp,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
    def test_page_explains_execution_and_downloads(self):
        page=(ROOT/'content/how-tos/command-rewriting-howto.md').read_text()
        for name in ['hooks-execution-evidence.mp4','captions.vtt','transcript.txt','terraphim-hooks-execution-evidence-v2.zip','execution-receipt.json','validation.json','verification.json']:
            self.assertIn('/demos/hooks-execution-evidence/'+name,page)
        self.assertIn('not a built-in approval gate',page)
        self.assertIn('OpenCode executes it',page)
        self.assertIn('blocked call',page)
        self.assertIn('node reproduction/verify.mjs',page)
if __name__=='__main__':unittest.main()
