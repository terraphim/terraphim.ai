"""Real-filesystem admission tests for the website's editor bundle."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("import_editor", Path(__file__).with_name("import-editor.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ImportEditorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        files = {"index.html": b"<!doctype html><title>Editor</title>",
                 "roles/default.json": b'{"name":"test","data":{}}',
                 "vendor/manifest.json": b'{"files":[]}'}
        for name, data in files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.manifest = self.root / "assets.json"
        self.manifest.write_text(json.dumps({"schema": 1, "sourceHead": "a" * 40,
            "assets": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}))
        self.expected = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.destination = self.root / "website" / "static" / "editor"

    def test_copies_only_admitted_bytes_and_records_identity(self):
        (self.source / "private-log.txt").write_text("not a website asset")
        MODULE.stage(self.source, self.manifest, self.expected, self.destination)
        self.assertFalse((self.destination / "private-log.txt").exists())
        self.assertEqual((self.destination / "index.html").read_bytes(), (self.source / "index.html").read_bytes())
        receipt = json.loads((self.destination / "release.json").read_text())
        self.assertEqual(receipt["manifestSha256"], self.expected)
        self.assertEqual(receipt["sourceHead"], "a" * 40)
        self.assertFalse(receipt["fullParityAccepted"])
        self.assertEqual(MODULE.verify(self.destination, self.expected), receipt)
        (self.destination / "index.html").write_text("changed after import")
        with self.assertRaises(ValueError):
            MODULE.verify(self.destination, self.expected)

    def test_verify_rejects_receipt_changes_and_extra_files(self):
        MODULE.stage(self.source, self.manifest, self.expected, self.destination)
        receipt_path = self.destination / "release.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["sourceHead"] = "b" * 40
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            MODULE.verify(self.destination, self.expected)
        receipt["sourceHead"] = "a" * 40
        receipt_path.write_text(json.dumps(receipt))
        (self.destination / "unexpected.txt").write_text("not admitted")
        with self.assertRaises(ValueError):
            MODULE.verify(self.destination, self.expected)

    def test_verify_rejects_coherent_replacement_against_external_digest(self):
        MODULE.stage(self.source, self.manifest, self.expected, self.destination)
        (self.destination / "index.html").write_text("replacement")
        manifest_path = self.destination / "assets-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["assets"]["index.html"] = hashlib.sha256(b"replacement").hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        receipt_path = self.destination / "release.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["manifestSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            MODULE.verify(self.destination, self.expected)

    def test_hash_failure_leaves_no_destination(self):
        (self.source / "index.html").write_text("corrupt")
        with self.assertRaises(ValueError):
            MODULE.stage(self.source, self.manifest, self.expected, self.destination)
        self.assertFalse(self.destination.exists())

    def test_refuses_unverified_manifest_and_existing_destination(self):
        with self.assertRaises(ValueError):
            MODULE.stage(self.source, self.manifest, "0" * 64, self.destination)
        self.destination.mkdir(parents=True)
        (self.destination / "draft.md").write_text("preserve")
        with self.assertRaises(ValueError):
            MODULE.stage(self.source, self.manifest, self.expected, self.destination)
        self.assertEqual((self.destination / "draft.md").read_text(), "preserve")

    def test_refuses_traversal_and_symlink(self):
        d = json.loads(self.manifest.read_text())
        d["assets"]["../outside"] = "0" * 64
        self.manifest.write_text(json.dumps(d))
        with self.assertRaises(ValueError):
            MODULE.stage(self.source, self.manifest, hashlib.sha256(self.manifest.read_bytes()).hexdigest(), self.destination)
        d["assets"].pop("../outside")
        self.manifest.write_text(json.dumps(d))
        (self.source / "index.html").unlink()
        (self.root / "other.html").write_text("not admitted")
        (self.source / "index.html").symlink_to(self.root / "other.html")
        with self.assertRaises(ValueError):
            MODULE.stage(self.source, self.manifest, hashlib.sha256(self.manifest.read_bytes()).hexdigest(), self.destination)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
