"""Bind the memory walkthrough and download to actual released-binary outputs."""
import hashlib
import json
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'static/demos/agent-memory'


class AgentMemoryPublicationTests(unittest.TestCase):
    def test_media_inventory_is_complete_and_unchanged(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertEqual(manifest['qualification'], 'released-binary')
        self.assertGreaterEqual(manifest['durationSeconds'], 60)
        self.assertLessEqual(manifest['durationSeconds'], 90)
        self.assertTrue(manifest['voice']['synthetic'])
        self.assertTrue(manifest['voice']['speechRateUnchanged'])
        for entry in manifest['files']:
            data = (MEDIA / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), entry['bytes'])
        self.assertFalse(manifest['render']['candidatePreview'])

    def test_download_proves_exact_content_and_negative_controls(self):
        with zipfile.ZipFile(MEDIA / 'harbour-memory-example.zip') as bundle:
            self.assertIsNone(bundle.testzip())
            self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in bundle.namelist()))
            load = lambda n: json.loads(bundle.read(n))
            verification = load('recorded/verification.json')
            self.assertEqual(verification['qualification'], 'released-binary')
            self.assertEqual(verification['status'], 'PASS')
            self.assertTrue(all(verification['checks'].values()))
            ids = load('released-binaries.json')
            self.assertIn(verification['binarySha256'], [b['binarySha256'] for b in ids['binaries']])
            lesson = bundle.read('fixture/lesson.md').decode()
            shown = load('recorded/outputs/reopened.stdout.json')
            found = load('recorded/outputs/retrieved.stdout.json')
            self.assertEqual(shown['memory_item']['content'], lesson)
            self.assertEqual(found['items'][0]['content'], lesson)
            self.assertEqual(found['items'][0]['id'], verification['memoryId'])
            self.assertEqual(found['count'], 1)
            for name in ['unrelated-query', 'other-role', 'separate-store']:
                self.assertEqual(load(f'recorded/outputs/{name}.stdout.json')['count'], 0)
            for row in bundle.read('SHA256SUMS').decode().splitlines():
                digest, name = row.split('  ', 1)
                self.assertEqual(hashlib.sha256(bundle.read(name)).hexdigest(), digest)
            self.assertIn('--prepare-only', bundle.read('README.md').decode())

    def test_reader_has_setup_media_and_reproduction_links(self):
        page = (ROOT / 'content/posts/cold-start-tax-agentic-memory.md').read_text()
        self.assertLess(page.index('export TERRAPHIM_DEFAULT_DATA_PATH'), page.index('memory capture'))
        self.assertIn('updated=2026-10-13', page)
        for name in ['agent-memory.mp4','captions.vtt','transcript.txt','harbour-memory-example.zip','manifest.json']:
            self.assertIn('/demos/agent-memory/' + name, page)
            self.assertTrue((MEDIA / name).is_file())
        self.assertIn('synthetic British female narration', page)
        for obsolete in ['42 agents', 'all eight stages shipped', '89%']:
            self.assertNotIn(obsolete, page)
        for target in re.findall(r'(?:src|poster)="(/demos/agent-memory/[^"]+)"', page):
            self.assertTrue((ROOT / 'static' / target.lstrip('/')).is_file())


if __name__ == '__main__':
    unittest.main()
