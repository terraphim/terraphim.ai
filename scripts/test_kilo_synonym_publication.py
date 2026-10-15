"""Verify the Kilo replay download against the actual saved graph and passages."""
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'static/demos/kilo-synonym-search'


class KiloPublicationTests(unittest.TestCase):
    def test_saved_outputs_match_clean_source_and_shared_graph(self):
        graph = json.loads((MEDIA / 'knowledge-graph.json').read_text())
        self.assertEqual(graph['data']['risk']['id'], graph['data']['concern']['id'])
        brief = (MEDIA / 'corpus/editor-risk-clean.md').read_text()
        self.assertNotIn('concern', brief.lower())
        self.assertIn('"text": "Concern"', (MEDIA / 'annotated.md').read_text())
        off = json.loads((MEDIA / 'without-synthesis.json').read_text())
        on = json.loads((MEDIA / 'with-synthesis.json').read_text())
        self.assertIsNone(off['answer'])
        self.assertEqual(off['chunks'], on['chunks'])
        self.assertEqual([c['line_start'] for c in off['chunks']], [3, 5, 7])
        lines = brief.splitlines()
        for chunk in off['chunks']:
            self.assertEqual(chunk['source'], 'editor-risk-clean.md')
            self.assertEqual(chunk['content'], '\n'.join(lines[chunk['line_start'] - 1:chunk['line_end']]))
        self.assertTrue(on['answer']['answer'])
        self.assertEqual([c['line'] for c in on['answer']['citations']], [3, 5, 7])
        for citation in on['answer']['citations']:
            self.assertEqual(citation['source'], 'editor-risk-clean.md')
            self.assertEqual(citation['excerpt'], lines[citation['line'] - 1])

    def test_bundle_is_exact_and_preserves_recorded_versions(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertEqual(manifest['kind'], 'saved-run replay')
        self.assertFalse(manifest['freshExecution'])
        self.assertFalse(manifest['catalogInstall'])
        self.assertFalse(manifest['narration'])
        self.assertTrue(manifest['burnedCaptions'])
        self.assertEqual(manifest['durationSeconds'], 44)
        self.assertEqual(manifest['versions'], {'kilo': '7.8.8', 'editor': '0.1.3', 'grep': '1.21.20', 'continueMcpAdapter': '0.1.1'})
        entries = {entry['file']: entry for entry in manifest['files']}
        self.assertEqual(len(entries), len(manifest['files']))
        for name, entry in entries.items():
            self.assertFalse(Path(name).is_absolute())
            self.assertNotIn('..', Path(name).parts)
            raw = (MEDIA / name).read_bytes()
            self.assertEqual(len(raw), entry['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
        self.assertEqual(entries['kilo-native-replay-captioned.mp4']['sha256'], '29db304f09b6064d2b7352f23675e146449c7fbafd92cf9eb1053fe8a5a102c8')
        with zipfile.ZipFile(MEDIA / 'kilo-synonym-search-example.zip') as bundle:
            expected = {'kilo-synonym-search/' + name for name in entries} | {'kilo-synonym-search/manifest.json'}
            self.assertEqual(set(bundle.namelist()), expected)
            self.assertEqual(len(bundle.namelist()), len(expected))
            for name in [*entries, 'manifest.json']:
                self.assertEqual(bundle.read('kilo-synonym-search/' + name), (MEDIA / name).read_bytes())

    def test_page_and_download_provide_accessible_honest_replay(self):
        page = (ROOT / 'content/how-tos/synonym-search.md').read_text()
        for name in ['kilo-native-replay-captioned.mp4', 'poster.jpg', 'captions.vtt', 'kilo-synonym-search-example.zip', 'manifest.json']:
            self.assertIn('/demos/kilo-synonym-search/' + name, page)
        self.assertIn('replay of saved tool results', page)
        self.assertIn('with captions and no audio', page)
        self.assertIn('under marketplace review', page)
        self.assertIn('https://marketplace.visualstudio.com/items?itemName=applied-knowledge-systems.terraphim-it', page)
        self.assertIn('/demos/synonym-search/synonym-search-story.mp4', page)
        captions = (MEDIA / 'captions.vtt').read_text()
        self.assertTrue(captions.startswith('WEBVTT\n'))
        self.assertEqual(captions.count(' --> '), 5)
        self.assertIn('00:00:44.000', captions)
        readme = (MEDIA / 'README.md').read_text()
        self.assertIn('--paths corpus -n 3 --search-only --json', readme)
        self.assertIn('--paths corpus -n 3 --answer --json', readme)
        self.assertIn('configured model provider', readme)
        self.assertTrue((MEDIA / 'poster.jpg').read_bytes().startswith(b'\xff\xd8\xff'))


if __name__ == '__main__':
    unittest.main()
