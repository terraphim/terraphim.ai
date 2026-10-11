"""Check real publication bytes and links without browser mocks."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'static/demos/knowledge-work'


class PublicationMediaTests(unittest.TestCase):
    def test_published_bytes_match_reviewed_inventory(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertEqual(len(manifest['media']), 6)
        expected = {'manifest.json'}
        for entry in manifest['media']:
            self.assertTrue(entry['publicDelivery'])
            expected.add(entry['file'])
            data = (MEDIA / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), int(entry['probe']['format']['size']))
        self.assertEqual({p.name for p in MEDIA.iterdir()}, expected)

    def test_unavailable_windows_download_is_not_advertised(self):
        for name in ['themes/WarpDrive/templates/index.html', 'themes/WarpDrive/static/js/site.js', 'content/docs/installation.md']:
            self.assertNotIn('x86_64-pc-windows-msvc.zip', (ROOT / name).read_text())
        self.assertNotIn('terraphim-server_{{ rv }}-1_amd64.deb', (ROOT / 'themes/WarpDrive/templates/index.html').read_text())
        self.assertIn("var base = 'https://downloads.terraphim.ai/terraphim-agent/'", (ROOT / 'themes/WarpDrive/static/js/site.js').read_text())
        self.assertIn('Native Windows archives are unavailable', (ROOT / 'content/docs/installation.md').read_text())

    def test_walkthrough_links_and_disclosures(self):
        page = (ROOT / 'content/how-tos/knowledge-work-editor.md').read_text()
        for entry in json.loads((MEDIA / 'manifest.json').read_text())['media']:
            self.assertIn('/demos/knowledge-work/' + entry['file'], page)
        for text in ['41 requirements', 'zero cuts', 'overstates', 'document-scoped synonym', 'Zed fork is separate', 'normalization repair']:
            self.assertIn(text, page)
        home = (ROOT / 'themes/WarpDrive/templates/index.html').read_text()
        self.assertIn("get_url(path='editor/')", home)
        self.assertIn("get_url(path='@/how-tos/knowledge-work-editor.md')", home)


if __name__ == '__main__':
    unittest.main()
