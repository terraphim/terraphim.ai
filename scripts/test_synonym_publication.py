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
        self.assertIn("v0.1.0-rc.1", self.html)
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


if __name__ == "__main__":
    unittest.main()
