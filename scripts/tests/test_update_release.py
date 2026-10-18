#!/usr/bin/env python3
"""Regression tests for scripts/update_release.py using real filesystem
inputs captured from actual source revisions and recorded release/channel
JSON. No mocked services."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import update_release as u  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "release-update"


def tree(name: str, dest: Path) -> Path:
    src = FIX / "source" / name
    target = dest / name
    shutil.copytree(src, target)
    return target


def snapshot(name: str) -> u.ReleaseSnapshot:
    return u.load_snapshot(FIX / "snapshot" / name)


class AdmissionTests(unittest.TestCase):
    def test_complete_snapshot_admits_all_seven(self):
        snap = snapshot("complete.json")
        self.assertEqual(
            set(snap.components),
            {"core", "clients", "editor", "vscode", "cursor", "zed", "continue"})
        self.assertEqual(str(snap.components["clients"].version), "1.21.22")
        self.assertEqual(str(snap.components["core"].version), "1.21.3")
        # prefixed selectors resolve their own series inside terraphim-ai
        self.assertEqual(snap.components["vscode"].tag, "terraphim_vscode-v0.1.7")
        self.assertEqual(snap.components["continue"].tag, "terraphim_continue-v0.1.1")
        # core selector excludes prefixed tags in the same repository
        self.assertEqual(snap.components["core"].tag, "v1.21.3")

    def test_incomplete_channels_skip_clients_only(self):
        snap = snapshot("incomplete-channels.json")
        self.assertNotIn("clients", snap.components)
        self.assertIn("cursor", snap.components)
        self.assertIn("core", snap.components)

    def test_downgrade_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = tree("terraphim.ai", Path(d))
            with self.assertRaises(u.RejectedInput):
                u.plan_updates(root, u.TargetRepository.WEBSITE,
                               snapshot("downgrade.json"))


class WebsiteFieldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = tree("terraphim.ai", Path(self.tmp.name))
        self.snap = snapshot("complete.json")

    def read(self, rel):
        return (self.root / rel).read_text()

    def test_no_drift_on_current_source(self):
        # fixture source already displays the admitted versions
        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        changed = [f.path for f in plan.files
                   if f.original_sha256 != f.proposed_sha256]
        # README migrates (markers inserted); all other fields already current
        self.assertEqual(changed, ["README.md"])

    def test_stale_fields_repaired_and_history_preserved(self):
        # deliberately stale the active fields back to 1.21.20/9 October
        for rel in ("config.toml", "content/releases.md",
                    "content/docs/installation.md",
                    "themes/WarpDrive/templates/index.html",
                    "themes/WarpDrive/static/js/site.js"):
            p = self.root / rel
            p.write_text(p.read_text().replace("1.21.22", "1.21.20"))
        releases = self.root / "content/releases.md"
        releases.write_text(
            releases.read_text().replace("15 October 2026", "9 October 2026", 1))
        history_before = releases.read_text().split("## Previous Release")[1]

        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        receipt = u.apply_plan(plan, self.root)

        self.assertIn('release_version = "1.21.22"', self.read("config.toml"))
        self.assertIn('version = "1.21.16"', self.read("config.toml"))  # dev version kept
        self.assertIn("## Latest Release: v1.21.22", self.read("content/releases.md"))
        self.assertIn("**Released:** 15 October 2026", self.read("content/releases.md"))
        self.assertIn("**Latest Stable:** v1.21.22", self.read("content/releases.md"))
        self.assertIn("terraphim-agent-1.21.22-", self.read("content/releases.md"))
        self.assertIn("v1.21.22 ships across", self.read("content/releases.md"))
        # pre-1.21.15 inside the active block must not be rewritten
        self.assertIn("pre-1.21.15", self.read("content/releases.md"))
        # historical block byte-identical
        self.assertEqual(
            self.read("content/releases.md").split("## Previous Release")[1],
            history_before)
        # installation.md slots
        self.assertIn("--version 1.21.22", self.read("content/docs/installation.md"))
        self.assertIn("VERSION=1.21.22", self.read("content/docs/installation.md"))
        self.assertIn("terraphim-agent 1.21.22", self.read("content/docs/installation.md"))
        self.assertIn("1.85.0", self.read("content/docs/installation.md"))
        # index.html fallbacks and site.js
        self.assertIn("default(value='1.21.22')",
                      self.read("themes/WarpDrive/templates/index.html"))
        self.assertIn("|| '1.21.22'",
                      self.read("themes/WarpDrive/static/js/site.js"))
        self.assertEqual(receipt["outcome"], "applied")

    def test_idempotent_second_run(self):
        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        u.apply_plan(plan, self.root)
        snapshot_bytes = {p: (self.root / p).read_bytes()
                          for p in ("config.toml", "content/releases.md",
                                    "README.md")}
        plan2 = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        u.apply_plan(plan2, self.root)
        for p, b in snapshot_bytes.items():
            self.assertEqual((self.root / p).read_bytes(), b)


class ReadmeRegionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = tree("terraphim.ai", Path(self.tmp.name))
        self.snap = snapshot("complete.json")

    def test_first_run_inserts_markers(self):
        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        u.apply_plan(plan, self.root)
        text = self.readme()
        self.assertEqual(text.count(u.README_MARKER_START), 1)
        self.assertEqual(text.count(u.README_MARKER_END), 1)
        self.assertIn("| Cursor plugin | [v0.2.7]", text)
        self.assertIn("| VS Code extension | [0.1.7]", text)
        self.assertIn("| Continue integration | [0.1.1]", text)
        self.assertIn("official Zed catalogue submission remains pending", text)
        # content outside the region preserved
        self.assertIn("# Terraphim website", text)
        self.assertIn("releases/latest", text)

    def readme(self):
        return (self.root / "README.md").read_text()

    def test_marked_region_rewritten_only(self):
        u.apply_plan(
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap),
            self.root)
        # corrupt a row inside the region; run again
        p = self.root / "README.md"
        p.write_text(p.read_text().replace("[v0.2.7]", "[v0.2.5]"))
        u.apply_plan(
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap),
            self.root)
        self.assertIn("[v0.2.7]", self.readme())

    def test_unadmitted_row_preserved(self):
        u.apply_plan(
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap),
            self.root)
        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE,
                              snapshot("incomplete-channels.json"))
        u.apply_plan(plan, self.root)
        self.assertIn("| CLI clients | [v1.21.22]", self.readme())

    def test_unexpected_marker_free_structure_rejected(self):
        p = self.root / "README.md"
        p.write_text(p.read_text().replace("## Current downloads",
                                           "## Downloads overview"))
        with self.assertRaises(u.RejectedInput):
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)

    def test_duplicate_markers_rejected(self):
        u.apply_plan(
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap),
            self.root)
        p = self.root / "README.md"
        p.write_text(p.read_text() + "\n" + u.README_MARKER_START + "\n"
                     + u.README_MARKER_END + "\n")
        with self.assertRaises(u.RejectedInput):
            u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)


class ApplySafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = tree("terraphim.ai", Path(self.tmp.name))
        self.snap = snapshot("complete.json")

    def test_original_hash_conflict_aborts(self):
        plan = u.plan_updates(self.root, u.TargetRepository.WEBSITE, self.snap)
        readme = self.root / "README.md"
        before = readme.read_bytes()
        readme.write_bytes(before + b"\nlocal edit\n")
        with self.assertRaises(u.OperationalFailure):
            u.apply_plan(plan, self.root)
        self.assertEqual(readme.read_bytes(), before + b"\nlocal edit\n")

    def test_other_repo_targets_only_touch_readme(self):
        for name, target in (("terraphim-ai", u.TargetRepository.TERRAPHIM_AI),
                             ("terraphim-clients", u.TargetRepository.TERRAPHIM_CLIENTS)):
            root = tree(name, Path(self.tmp.name))
            plan = u.plan_updates(root, target, self.snap)
            self.assertEqual({f.path for f in plan.files}, {"README.md"})
            u.apply_plan(plan, root)
            text = (root / "README.md").read_text()
            self.assertEqual(text.count(u.README_MARKER_START), 1)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = tree("terraphim.ai", Path(self.tmp.name))
        self.snap_path = str(FIX / "snapshot" / "complete.json")

    def run_cli(self, *argv):
        return u.main(["--snapshot", self.snap_path, "--root", str(self.root),
                       "--target", "website", *argv])

    def test_check_reports_drift(self):
        self.assertEqual(self.run_cli("--check"), u.EXIT_DRIFT)

    def test_check_clean_after_apply(self):
        self.assertEqual(self.run_cli(), u.EXIT_OK)
        self.assertEqual(self.run_cli("--check"), u.EXIT_OK)

    def test_rejected_exit_code(self):
        code = u.main(["--snapshot", str(FIX / "snapshot" / "downgrade.json"),
                       "--root", str(self.root), "--target", "website"])
        self.assertEqual(code, u.EXIT_REJECTED)

    def test_receipt_written(self):
        receipt = Path(self.tmp.name) / "receipt.json"
        self.run_cli("--check", "--receipt", str(receipt))
        body = json.loads(receipt.read_text())
        self.assertEqual(body["receiptType"], "discovery")
        self.assertIn("admitted", body)

        receipt2 = Path(self.tmp.name) / "receipt2.json"
        u.main(["--root", str(self.root), "--target", "website",
                "--snapshot", self.snap_path, "--receipt", str(receipt2)])
        body2 = json.loads(receipt2.read_text())
        self.assertEqual(body2["receiptType"], "update")
        self.assertIn(body2["outcome"], ("applied", "unchanged"))


class VersionTests(unittest.TestCase):
    def test_ordering(self):
        a = u.Version.parse("1.21.22")
        b = u.Version.parse("1.21.3")
        rc4 = u.Version.parse("0.1.0-rc.4")
        rc5 = u.Version.parse("0.1.0-rc.5")
        stable = u.Version.parse("0.1.0")
        self.assertGreater(a, b)
        self.assertGreater(rc5, rc4)
        self.assertGreater(stable, rc5)  # stable > prerelease of same version
        self.assertIsNone(u.Version.parse("not-a-version"))


if __name__ == "__main__":
    unittest.main()
