"""Exercise the built page and the downloadable reproduction kit."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "static/demos/synonym-search"
OBSIDIAN = ROOT / "static/demos/obsidian-synonym-search"


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name"))] = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs["href"])


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = tempfile.TemporaryDirectory()
        built = Path(cls.output.name) / "site"
        subprocess.run(["zola", "build", "--output-dir", str(built)], cwd=ROOT, check=True, text=True)
        cls.html = (built / "how-tos/synonym-search/index.html").read_text()

    @classmethod
    def tearDownClass(cls):
        cls.output.cleanup()

    def test_production_metadata_and_privacy_wording(self):
        head = HeadParser()
        head.feed(self.html)
        url = "https://terraphim.ai/how-tos/synonym-search/"
        self.assertEqual(head.canonicals, [url])
        self.assertEqual(head.meta["og:url"], url)
        self.assertEqual(head.meta["og:title"], "Different words. The same idea.")
        self.assertEqual(head.meta["og:image"], "https://terraphim.ai/demos/synonym-search/poster.jpg")
        self.assertEqual(head.meta["twitter:card"], "summary_large_image")
        self.assertNotIn("All data processed locally", self.html)
        self.assertIn("Optional synthesis uses your configured model provider", self.html)
        self.assertNotIn("editor graph-sharing candidate", self.html)
        self.assertIn("v1.21.19", self.html)

    def test_released_evidence_and_bundle_match_actual_files(self):
        receipt = json.loads((MEDIA / "reproduction.json").read_text())
        self.assertEqual(receipt["grepVersion"], "1.21.19")
        self.assertEqual(receipt["editorVersion"], "0.1.0-rc.1")
        before = json.loads((MEDIA / "released-before-sharing.json").read_text())
        off = json.loads((MEDIA / "released-without-synthesis.json").read_text())
        on = json.loads((MEDIA / "released-with-synthesis.json").read_text())
        self.assertEqual(before["chunks"], [])
        self.assertEqual(off["chunks"], on["chunks"])
        self.assertEqual(len(off["chunks"]), 3)
        self.assertIsNone(off["answer"])
        self.assertTrue(on["answer"]["answer"])
        self.assertEqual(len(on["answer"]["citations"]), 3)
        with zipfile.ZipFile(MEDIA / "synonym-search-example.zip") as bundle:
            self.assertEqual(set(bundle.namelist()), set(receipt["bundleFiles"]))
            for name in receipt["bundleFiles"]:
                self.assertEqual(bundle.read(name), (MEDIA / name).read_bytes())
        for item in receipt["files"]:
            self.assertEqual(hashlib.sha256((MEDIA / item["file"]).read_bytes()).hexdigest(), item["sha256"])
        for name in ["reproduction.json", "synonym-search-example.zip", "captions.srt"]:
            self.assertIn("/demos/synonym-search/" + name, self.html)

    def test_obsidian_synonyms_belong_to_knowledge_note(self):
        note = (OBSIDIAN / "vault/Notes/Risk.md").read_text()
        results = (OBSIDIAN / "vault/Search results/Concern search.md").read_text()
        brief = (OBSIDIAN / "vault/Notes/Projects/Community garden launch.md").read_text()
        self.assertTrue(note.startswith("synonyms:: Risk, Concern\n"))
        self.assertNotIn("synonyms::", results)
        self.assertNotIn("concern", brief.lower())
        self.assertEqual(brief, (MEDIA / "project-brief.md").read_text())
        graph = json.loads((OBSIDIAN / "vault/Knowledge graph/knowledge-graph.json").read_text())
        self.assertEqual(graph, json.loads((MEDIA / "knowledge-graph.json").read_text()))
        self.assertEqual(graph["data"]["risk"]["id"], graph["data"]["concern"]["id"])

    def test_obsidian_outputs_are_actual_project_passages(self):
        before = json.loads((OBSIDIAN / "evidence/before-sharing.json").read_text())
        after = json.loads((OBSIDIAN / "evidence/with-synonym.json").read_text())
        receipt = json.loads((OBSIDIAN / "evidence/verification.json").read_text())
        lines = (OBSIDIAN / "vault/Notes/Projects/Community garden launch.md").read_text().splitlines()
        self.assertEqual(before["chunks"], [])
        self.assertIsNone(after["answer"])
        self.assertEqual([chunk["line_start"] for chunk in after["chunks"]], [7, 10, 13])
        for chunk in after["chunks"]:
            self.assertEqual(chunk["source"], "Community garden launch.md")
            self.assertEqual(chunk["content"], "\n".join(lines[chunk["line_start"] - 1:chunk["line_end"]]))
        self.assertEqual(receipt["version"], "terraphim-grep 1.21.19")
        for run in receipt["runs"]:
            command = run["command"]
            self.assertEqual(command[command.index("--paths") + 1], "Notes/Projects")
            self.assertEqual(run["exitCode"], 0)

    def test_obsidian_vault_bundle_matches_reviewed_files(self):
        manifest = json.loads((OBSIDIAN / "manifest.json").read_text())
        files = {item["file"]: item for item in manifest["files"]}
        self.assertIn("screenshots/03-synonyms-in-knowledge-note.jpg", files)
        with zipfile.ZipFile(OBSIDIAN / "obsidian-synonym-search-example.zip") as bundle:
            expected = {"obsidian-demo/" + name for name in files} | {"obsidian-demo/manifest.json"}
            self.assertEqual(set(bundle.namelist()), expected)
            self.assertTrue(all(".obsidian" not in name and ".." not in Path(name).parts for name in expected))
            for name, item in files.items():
                raw = (OBSIDIAN / name).read_bytes()
                self.assertEqual(bundle.read("obsidian-demo/" + name), raw)
                self.assertEqual(len(raw), item["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256"])
            self.assertEqual(bundle.read("obsidian-demo/manifest.json"), (OBSIDIAN / "manifest.json").read_bytes())

    def test_obsidian_screenshot_has_jpeg_content(self):
        raw = (OBSIDIAN / "screenshots/03-synonyms-in-knowledge-note.jpg").read_bytes()
        self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
        self.assertTrue(raw.endswith(b"\xff\xd9"))

    def test_obsidian_section_explains_scope_and_links_downloads(self):
        for name in ["obsidian-synonym-search-example.zip", "screenshots/03-synonyms-in-knowledge-note.jpg",
                     "evidence/before-sharing.json", "evidence/with-synonym.json", "manifest.json"]:
            self.assertIn("/demos/obsidian-synonym-search/" + name, self.html)
        self.assertIn('id="try-it-with-an-obsidian-vault"', self.html)
        self.assertIn("Obsidian displays saved CLI results", self.html)
        self.assertIn("does not automatically rebuild the graph", self.html)
        self.assertIn("Logseq-compatible Markdown property syntax", self.html)
        self.assertIn('alt="Obsidian with synonyms in the Risk knowledge note', self.html)


if __name__ == "__main__":
    unittest.main()
