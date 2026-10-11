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
        expected = {'manifest.json', 'narration.json'}
        for entry in manifest['media']:
            self.assertTrue(entry['publicDelivery'])
            expected.add(entry['file'])
            data = (MEDIA / entry['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), int(entry['probe']['format']['size']))
        self.assertEqual({p.name for p in MEDIA.iterdir()}, expected)

    def test_all_six_demos_have_synchronized_british_narration(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        narration = manifest['narration']
        self.assertEqual(narration['voiceId'], 'bf_emma')
        self.assertEqual(narration['language'], 'en-gb')
        self.assertTrue(narration['syntheticVoice'])
        raw_script = (MEDIA / narration['script']).read_bytes()
        self.assertEqual(hashlib.sha256(raw_script).hexdigest(), narration['scriptSha256'])
        script = json.loads(raw_script)
        self.assertEqual(script['quality']['status'], 'PASS')
        self.assertGreaterEqual(script['quality']['normalizedMean'], 0.97)
        self.assertGreaterEqual(script['quality']['normalizedMinimum'], 0.90)
        videos = {e['file']: e for e in manifest['media']}
        self.assertEqual({e['file'] for e in script['videos']}, set(videos))
        for output in narration['outputs']:
            self.assertTrue(output['videoBitstreamUnchanged'])
            self.assertTrue(output['noTempoOrPitchChanges'])
            self.assertLessEqual(output['peakDbfs'], -3)
        for video in script['videos']:
            entry = videos[video['file']]
            audio = [s for s in entry['probe']['streams'] if s['codec_type'] == 'audio']
            self.assertEqual(len(audio), 1)
            self.assertEqual(audio[0]['codec_name'], 'aac')
            duration = float(entry['probe']['format']['duration'])
            previous_end = 0
            for beat in video['beats']:
                self.assertTrue(beat['fits'])
                self.assertGreaterEqual(beat['audioStart'], previous_end)
                self.assertLessEqual(beat['audioEnd'], min(beat['end'], duration))
                self.assertAlmostEqual(beat['audioEnd'] - beat['audioStart'], beat['take']['duration'], delta=0.000002)
                previous_end = beat['audioEnd']

    def test_unavailable_windows_download_is_not_advertised(self):
        for name in ['themes/WarpDrive/templates/index.html', 'themes/WarpDrive/static/js/site.js', 'content/docs/installation.md']:
            self.assertNotIn('x86_64-pc-windows-msvc.zip', (ROOT / name).read_text())
        self.assertNotIn('terraphim-server_{{ rv }}-1_amd64.deb', (ROOT / 'themes/WarpDrive/templates/index.html').read_text())
        self.assertIn("var base = 'https://downloads.terraphim.ai/terraphim-agent/'", (ROOT / 'themes/WarpDrive/static/js/site.js').read_text())
        self.assertIn('Native Windows archives are unavailable', (ROOT / 'content/docs/installation.md').read_text())

    def test_paced_walkthroughs_are_short_and_continuously_captioned(self):
        manifest = json.loads((MEDIA / 'manifest.json').read_text())
        self.assertIn('paced-v2', manifest['edition'])
        durations = {e['file']: float(e['probe']['format']['duration']) for e in manifest['media']}
        self.assertLess(durations['grammarly-for-knowledge-work-preview.mp4'], 90)
        self.assertLess(durations['grep-live-execution-public.mp4'], 25)
        for entry in manifest['edits']:
            if 'segments' not in entry:
                continue
            cursor = 0
            source_end = 0
            for segment in entry['segments']:
                self.assertAlmostEqual(segment['start'], cursor, places=5)
                self.assertTrue(segment['text'])
                self.assertGreater(segment['end'], segment['start'])
                self.assertGreaterEqual(segment['sourceStart'], source_end)
                self.assertGreaterEqual(segment['speed'], 1)
                self.assertLessEqual(segment['speed'], 3)
                cursor = segment['end']
                source_end = segment['sourceEnd']
            self.assertAlmostEqual(cursor, durations[entry['output']], delta=0.1)
            if entry['output'] != 'grep-live-execution-public.mp4':
                self.assertLess(durations[entry['output']], 70)

    def test_editor_is_listed_as_a_homepage_capability(self):
        home = (ROOT / 'themes/WarpDrive/templates/index.html').read_text()
        section = home.split('id="waypoints"', 1)[1].split('</section>', 1)[0]
        self.assertIn("@/capabilities/terraphim-editor.md", section)
        self.assertIn('Terraphim Editor', section)
        self.assertIn('Intelligent editor', section)
        self.assertIn('alternative suggestions', section)
        self.assertIn('knowledge graph and roles', section)
        self.assertEqual(section.count('class="waypoint-link"'), 10)
        self.assertNotIn('Nine capabilities', section)
        page = (ROOT / 'content/capabilities/terraphim-editor.md').read_text()
        for target in ['/editor/', '/how-tos/knowledge-work-editor/']:
            self.assertIn(target, page)
        self.assertIn('document-scoped synonyms', page)
        self.assertIn('preview', page)

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
