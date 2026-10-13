"""Bind hook claims to actual captured failures, correction and executed output."""
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'static/demos/agent-hooks'


class AgentHooksPublicationTests(unittest.TestCase):
    def test_media_matches_reviewed_manifest(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertEqual(manifest['qualification'], 'released-binary')
        self.assertEqual(manifest['durationSeconds'], 75)
        self.assertTrue(manifest['manualPromotion'])
        self.assertTrue(manifest['adapterRequired'])
        self.assertTrue(manifest['voice']['speechRateUnchanged'])
        for entry in manifest['files']:
            data = (MEDIA / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), entry['bytes'])

    def test_bundle_proves_hook_result_and_execution_separately(self):
        with zipfile.ZipFile(MEDIA / 'harbour-hooks-example.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist()))
            load = lambda n: json.loads(z.read('recorded/evidence/' + n))
            result = load('verification.json')
            self.assertTrue(result['pass'])
            self.assertEqual(result['baseline_exit'], 2)
            self.assertEqual(result['corrected_exit'], 0)
            self.assertTrue(result['manual_promotion'])
            self.assertTrue(result['native_adapter_required'])
            off = json.loads(load('rewrite-disabled.json')['stdout'])
            on = json.loads(load('rewrite-enabled.json')['stdout'])
            self.assertEqual(off['tool_input']['command'], result['host_attempted'])
            self.assertEqual(on['tool_input']['command'], result['host_executed'])
            events = [json.loads(line) for line in z.read('recorded/evidence/host-events.jsonl').decode().splitlines()]
            after = [e['data'] for e in events if e['type'] == 'native-after']
            self.assertEqual(after[0]['result']['metadata']['exit'], 2)
            self.assertEqual(after[-1]['input']['command'], result['host_executed'])
            self.assertEqual(after[-1]['result']['metadata']['exit'], 0)
            self.assertEqual(json.loads(after[-1]['result']['output']['output']), json.loads(z.read('recorded/validation.json')))
            learning = z.read('recorded/evidence/learning-before-correction.md').decode()
            self.assertIn(result['host_attempted'], learning)
            self.assertIn('exit_code: 2', learning)
            self.assertIn('Compiled 0 correction(s)', load('learning-only-compile.json')['stdout'])
            self.assertIn('Compiled 1 correction(s)', load('compile-corrections.json')['stdout'])
            for row in z.read('SHA256SUMS').decode().splitlines():
                digest, name = row.split('  ', 1)
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), digest)

    def test_article_preserves_scope_and_downloads(self):
        page = (ROOT / 'content/how-tos/command-rewriting-howto.md').read_text()
        self.assertIn('date=2026-04-15', page)
        self.assertIn('updated=2026-10-13', page)
        for name in ['agent-hooks.mp4','captions.vtt','transcript.txt','harbour-hooks-example.zip']:
            self.assertIn('/demos/agent-hooks/' + name, page)
            self.assertTrue((MEDIA / name).is_file())
        self.assertIn('explicit human review', page)
        self.assertIn('included project-local adapter', page)
        self.assertIn('It has not executed Python', page)
        self.assertIn('redaction gaps', page)
        self.assertIn('synonyms:: python3 validate-brief.py --chek', page)


if __name__ == '__main__':
    unittest.main()
