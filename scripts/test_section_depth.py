#!/usr/bin/env python3
"""Guard: the json.html / json-ad.html templates expand sections to a fixed
depth (root + two subsection levels). If a deeper _index.md appears in
content/, its pages would be silently omitted from /json/ and /json-ad/ —
fail here instead of losing them quietly."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent / "content"
MAX_DEPTH = 3  # content/a/b/_index.md is the deepest expanded level


class TestSectionDepth(unittest.TestCase):
    def test_no_section_deeper_than_expansion(self):
        deep = [
            p for p in ROOT.rglob("_index.md")
            if len(p.relative_to(ROOT).parts) > MAX_DEPTH
        ]
        self.assertEqual(
            [],
            deep,
            "Sections deeper than the JSON templates' expansion depth: "
            + ", ".join(str(p) for p in deep)
            + " — extend templates/json.html and templates/json-ad.html",
        )


if __name__ == "__main__":
    unittest.main()
