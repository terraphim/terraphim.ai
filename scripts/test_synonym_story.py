"""Verify actual editor exports, CLI results and publication media identities."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'static/demos/synonym-search'


class SynonymStoryTests(unittest.TestCase):
    def test_export_is_used_for_search_and_synthesis(self):
        graph = json.loads((MEDIA / 'knowledge-graph.json').read_text())
        self.assertEqual(graph['data']['risk']['id'], graph['data']['concern']['id'])
        self.assertNotIn('concern', (MEDIA / 'project-brief.md').read_text().lower())
        off = json.loads((MEDIA / 'without-synthesis.json').read_text())
        on = json.loads((MEDIA / 'with-synthesis.json').read_text())
        self.assertIsNone(off['answer'])
        self.assertEqual(off['chunks'], on['chunks'])
        self.assertEqual(len(off['chunks']), 3)
        lines = (MEDIA / 'project-brief.md').read_text().splitlines()
        for chunk in off['chunks']:
            self.assertEqual(chunk['source'], 'project-brief.md')
            self.assertEqual(chunk['content'], '\n'.join(lines[chunk['line_start'] - 1:chunk['line_end']]))
        for citation in on['answer']['citations']:
            self.assertEqual(citation['source'], 'project-brief.md')
            self.assertEqual(citation['excerpt'], lines[citation['line'] - 1])
        self.assertTrue(on['answer']['answer'])
        self.assertEqual(len(on['answer']['citations']), 3)

    def test_media_and_outputs_match_reviewed_manifest(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertGreaterEqual(manifest['durationSeconds'], 60)
        self.assertLessEqual(manifest['durationSeconds'], 90)
        self.assertTrue(manifest['voice']['synthetic'])
        self.assertTrue(manifest['voice']['speechRateUnchanged'])
        for entry in manifest['files']:
            data = (MEDIA / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), entry['bytes'])
        self.assertEqual(manifest['checks']['pageErrors'], [])
        self.assertTrue(manifest['checks']['sameRetrievedChunks'])
        self.assertTrue(manifest['checks']['sameGraphAndTextAsPriorVerifiedRun'])

    def test_main_story_is_linked_and_scope_is_clear(self):
        page = (ROOT / 'content/how-tos/synonym-search.md').read_text()
        home = (ROOT / 'themes/WarpDrive/templates/index.html').read_text()
        self.assertIn('href="/how-tos/synonym-search/"', home)
        for text in ['synonyms:: Risk, Concern', '--answer', 'sample project brief',
                     'synthetic British English']:
            self.assertIn(text, page)
        for file in ['synonym-search-story.mp4', 'knowledge-graph.json', 'project-brief.md', 'without-synthesis.json', 'with-synthesis.json']:
            self.assertIn('/demos/synonym-search/' + file, page)


if __name__ == '__main__':
    unittest.main()
