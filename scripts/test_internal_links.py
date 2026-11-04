"""Every same-site link in the built site must resolve to a generated file.

`zola build` validates only `@/` links, so root-relative links in Markdown and
templates can point at draft or renamed pages without failing the build.
"""
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlparse

REPO = Path(__file__).resolve().parent.parent
BUILD_URL = "http://127.0.0.1:8879"
SITE_HOSTS = {"127.0.0.1:8879", "terraphim.ai", "www.terraphim.ai"}
# These two pages hold JSON documents, not markup, so their contents are not links.
JSON_PAGES = {"json/index.html", "json-ad/index.html"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src", "poster"} and value:
                self.links.append(value)


def redirect_sources():
    lines = (REPO / "static" / "_redirects").read_text().splitlines()
    return {line.split()[0] for line in lines if line.strip() and not line.startswith("#")}


def resolves(site, path, redirects):
    if path in redirects:
        return True
    target = site / unquote(path).lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def broken_links(site):
    redirects = redirect_sources()
    broken = {}
    for page in site.rglob("*.html"):
        relative = page.relative_to(site).as_posix()
        if relative in JSON_PAGES:
            continue
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        page_url = f"{BUILD_URL}/{relative}"
        for link in parser.links:
            url = urlparse(urldefrag(urljoin(page_url, link.strip())).url)
            if url.scheme not in {"http", "https"} or url.netloc not in SITE_HOSTS:
                continue
            if not resolves(site, url.path, redirects):
                broken.setdefault(url.path, set()).add(relative)
    return broken


class InternalLinkTest(unittest.TestCase):
    def test_same_site_links_resolve(self):
        zola = shutil.which("zola")
        self.assertIsNotNone(zola, "zola is required to build the site")
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp) / "site"
            subprocess.run(
                [zola, "build", "--base-url", BUILD_URL, "--output-dir", str(site)],
                cwd=REPO,
                check=True,
                capture_output=True,
            )
            broken = broken_links(site)
        report = "\n".join(f"{path} <- {sorted(pages)[:3]}" for path, pages in sorted(broken.items()))
        self.assertEqual(broken, {}, f"Broken same-site links:\n{report}")


if __name__ == "__main__":
    unittest.main()
