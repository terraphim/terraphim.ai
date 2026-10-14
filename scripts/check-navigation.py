#!/usr/bin/env python3
"""Check real rendered navigation against a built site, preview or production."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright


WIDTHS = (320, 390, 768, 899, 900, 1024, 1200, 1279, 1280, 1366, 1440,
          1799, 1800, 1920, 2560)
PAGES = ("/", "/how-tos/synonym-search/", "/how-tos/command-rewriting-howto/")
DESTINATIONS = (
    ("Home", "/"), ("Editor", "/editor/"),
    ("Capabilities", "/capabilities"), ("How-tos", "/how-tos"),
    ("Docs", "https://docs.terraphim.ai/"), ("Rust", "https://terraphim.rs/"),
    ("Releases", "/releases"), ("Install", "/docs/installation"),
    ("Community", "/#community"), ("Donate", "/docs/donate"),
)

GEOMETRY = """() => {
  const rect = el => {
    const r = el.getBoundingClientRect();
    return {x:r.x, y:r.y, right:r.right, bottom:r.bottom, w:r.width, h:r.height};
  };
  const shown = el => !!el && getComputedStyle(el).display !== 'none'
    && el.getBoundingClientRect().width > 0;
  const desktop = shown(document.querySelector('.topbar'));
  const mobile = shown(document.querySelector('.mobile-nav'));
  const selector = desktop
    ? '.topbar-brand, .topbar-link, .topbar-status, .topbar-search'
    : '.mobile-nav-brand, .nav-search-btn, .nav-burger';
  const controls = [...document.querySelectorAll(selector)].map(el => {
    const range = document.createRange(); range.selectNodeContents(el);
    const textRects = el.matches('.topbar-link') ? [...range.getClientRects()]
      .filter(r => r.width > 0).map(r => ({x:r.x,y:r.y,right:r.right,bottom:r.bottom})) : [];
    const r = rect(el);
    const hit = document.elementFromPoint((r.x+r.right)/2, (r.y+r.bottom)/2);
    return {text:el.textContent.trim(), rect:r, textRects,
      lines: new Set(textRects.map(r => Math.round(r.y))).size,
      hit:!!hit && (hit === el || el.contains(hit))};
  });
  const links = selector => [...document.querySelectorAll(selector)]
    .map(el => ({text:el.textContent.trim(), href:el.href}));
  const inlineCode = [...document.querySelectorAll('.article-box .prose code')]
    .filter(el => !el.closest('pre')).map(el => ({text:el.textContent,
      fragments:[...el.getClientRects()].map(r => ({left:r.left,right:r.right}))}));
  return {width:innerWidth, clientWidth:document.documentElement.clientWidth,
    scrollWidth:document.documentElement.scrollWidth, inlineCode,
    desktop, mobile, controls, desktopLinks:links('.topbar-link'),
    mobileLinks:links('.nav-mobile-menu a'),
    version:document.querySelector('.status-label').textContent.trim(),
    stylesheet:[...document.styleSheets].map(s => s.href).find(h => h && h.includes('/css/warp.css')),
    fonts:[...document.fonts].map(f => ({family:f.family,status:f.status}))};
}"""


def geometry_errors(data, base_url):
    """Assert observable layout rather than CSS declarations."""
    errors = []
    if data["scrollWidth"] > data["clientWidth"] + 1:
        errors.append("Page content extends beyond the viewport")
    for code in data["inlineCode"]:
        if any(r["left"] < -1 or r["right"] > data["clientWidth"] + 1
               for r in code["fragments"]):
            errors.append(f"Inline code extends beyond the viewport: {code['text']}")
    if data["desktop"] != (data["width"] >= 1280) or data["mobile"] == data["desktop"]:
        errors.append("Wrong header mode or multiple visible headers")
    previous = None
    for control in data["controls"]:
        r = control["rect"]
        name = control["text"] or "icon control"
        if r["x"] < -0.6 or r["right"] > data["clientWidth"] + 0.6:
            errors.append(f"{name} extends beyond the viewport")
        if r["y"] < -0.6 or r["bottom"] > 52.6:
            errors.append(f"{name} extends beyond the header height")
        if previous is not None and r["x"] < previous - 0.6:
            errors.append(f"{name} overlaps the previous control")
        previous = r["right"]
        if control["lines"] > 1:
            errors.append(f"{name} wraps onto {control['lines']} lines")
        for text in control["textRects"]:
            if text["y"] < 0 or text["bottom"] > 52:
                errors.append(f"{name} text is vertically clipped")
        if not control["hit"]:
            errors.append(f"{name} is obscured or offscreen")
    if not data["version"].startswith("Clients v"):
        errors.append("Client release badge missing")
    for kind in ("desktopLinks", "mobileLinks"):
        actual = [(link["text"], link["href"]) for link in data[kind]]
        expected = [(label, urljoin(base_url, destination)) for label, destination in DESTINATIONS]
        if actual != expected:
            errors.append(f"{kind} changed destinations or labels: {actual}")
    return errors


def settle(page):
    page.evaluate("() => document.fonts.ready")
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


def tab_to(page, selector):
    """Reach a control with actual Tab presses, including WebKit's full tab mode."""
    for _ in range(50):
        if page.evaluate("s => document.activeElement.matches(s)", selector):
            return
        mac_webkit = sys.platform == "darwin" and page.context.browser.browser_type.name == "webkit"
        page.keyboard.press("Alt+Tab" if mac_webkit else "Tab")
    raise AssertionError(f"Keyboard cannot reach {selector}")


def interactions(page, url):
    """Check actual controls and keyboard navigation on the rendered page."""
    outcomes = []
    for width in (1024, 1280):
        page.set_viewport_size({"width": width, "height": 480})
        page.goto(url, wait_until="load")
        settle(page)
        desktop = width >= 1280
        search = "#nav-search-ribbon" if desktop else "#nav-search"
        tab_to(page, search)
        page.keyboard.press("Enter")
        page.locator("#search-modal.is-active").wait_for(state="visible")
        assert page.locator("#search").evaluate("el => el === document.activeElement")
        page.keyboard.press("Escape")
        page.locator("#search-modal").wait_for(state="hidden")
        outcomes.append({"width": width, "searchKeyboardAndFocus": True})

        # Reload to start a new keyboard traversal at the document start.
        page.goto(url, wait_until="load")
        if not desktop:
            tab_to(page, ".nav-burger")
            page.keyboard.press("Enter")
            assert page.locator(".nav-burger").get_attribute("aria-expanded") == "true"
            menu = page.locator(".nav-mobile-menu")
            menu.wait_for(state="visible")
            assert menu.locator("a").count() == 10
            tab_to(page, '.nav-mobile-menu a[href$="/docs/donate"]')
            last = menu.locator("a").last
            visible = last.evaluate("""el => {
              const r=el.getBoundingClientRect(), m=el.parentElement.getBoundingClientRect();
              const hit=document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2);
              return r.top >= m.top && r.bottom <= Math.min(m.bottom,innerHeight)+1
                && (hit===el || el.contains(hit));
            }""")
            assert visible, "Last compact-menu destination is not visible after keyboard scroll"
            page.keyboard.press("Enter")
            page.wait_for_url(lambda url: urlparse(url).path.rstrip("/") == "/docs/donate",
                              wait_until="domcontentloaded")
            outcomes.append({"width": width, "lastDestinationKeyboardNavigation": page.url})
            page.goto(url, wait_until="load")
            tab_to(page, ".nav-burger")
            page.keyboard.press("Enter")
            page.set_viewport_size({"width": 1280, "height": 480})
            settle(page)
            assert not page.locator(".nav-mobile-menu").is_visible()
            assert page.locator(".topbar").is_visible()
            page.set_viewport_size({"width": 1024, "height": 480})
            settle(page)
            assert page.locator(".nav-mobile-menu").is_visible()
            assert not page.locator(".topbar").is_visible()
            outcomes.append({"width": width, "resizeRetainsOpenState": True})
        selector = '.topbar-link[href$="/editor/"]' if desktop else '.nav-mobile-menu a[href$="/editor/"]'
        tab_to(page, selector)
        page.keyboard.press("Enter")
        page.wait_for_url("**/editor/", wait_until="domcontentloaded")
        outcomes.append({"width": width, "editorKeyboardNavigation": page.url})
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"), required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    report = {"checkedAt": datetime.now(timezone.utc).isoformat(), "baseUrl": args.base_url,
              "browser": args.browser, "geometry": [], "interactions": [], "errors": []}
    try:
        with sync_playwright() as playwright:
            browser = getattr(playwright, args.browser).launch()
            report["browserVersion"] = browser.version
            for fallback in (False, True):
                context = browser.new_context(viewport={"width": 1280, "height": 800},
                                              reduced_motion="reduce")
                if fallback:
                    context.route("**/*", lambda route: route.abort() if
                                  route.request.resource_type == "font" or
                                  urlparse(route.request.url).netloc in ("fonts.googleapis.com", "fonts.gstatic.com")
                                  else route.continue_())
                page = context.new_page()
                page.set_default_timeout(15000)
                for index, path in enumerate(PAGES):
                    url = urljoin(args.base_url.rstrip("/") + "/", path.lstrip("/"))
                    page.goto(url, wait_until="load")
                    settle(page)
                    if index == 0 and not fallback:
                        css_url = urljoin(args.base_url.rstrip("/") + "/", "css/warp.css")
                        css = page.request.get(css_url)
                        assert css.ok, f"Stylesheet returned HTTP {css.status}"
                        report["stylesheet"] = {"url": css_url,
                                                 "sha256": hashlib.sha256(css.body()).hexdigest()}
                    for width in WIDTHS:
                        page.set_viewport_size({"width": width, "height": 800})
                        settle(page)
                        data = page.evaluate(GEOMETRY)
                        errors = geometry_errors(data, args.base_url)
                        if path == "/how-tos/command-rewriting-howto/" and not any(
                                code["text"] == "evidence/executions/<execution_id>/validation.json"
                                for code in data["inlineCode"]):
                            errors.append("Hooks article execution-path regression fixture is missing")
                        if data["stylesheet"] != urljoin(args.base_url.rstrip("/") + "/", "css/warp.css"):
                            errors.append("Rendered stylesheet is not from the site under test")
                        loaded = any("Space Grotesk" in f["family"] and f["status"] == "loaded"
                                     for f in data["fonts"])
                        if not fallback and not loaded:
                            errors.append("Normal-font run did not load Space Grotesk")
                        data.update({"path": path, "fallbackFonts": fallback, "errors": errors})
                        report["geometry"].append(data)
                        prefix = f"page-{index}-{'fallback' if fallback else 'normal'}-{width}"
                        report["errors"].extend(f"{prefix}: {e}" for e in errors)
                        if width in (1024, 1280, 2560) and index == 0:
                            page.screenshot(path=str(args.artifacts / f"{prefix}.png"))
                    if not fallback:
                        try:
                            report["interactions"].append({"path": path, "outcomes": interactions(page, url)})
                        except Exception as error:
                            report["errors"].append(f"{path} interactions: {error}")
                            page.screenshot(path=str(args.artifacts / f"page-{index}-interaction-failure.png"))
                context.close()
            browser.close()
    except Exception as error:
        report["errors"].append(f"Browser check could not complete: {error}")
    report["passed"] = not report["errors"] and len(report["geometry"]) == len(WIDTHS) * len(PAGES) * 2
    (args.artifacts / "navigation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"browser": args.browser, "passed": report["passed"],
                      "geometryCases": len(report["geometry"]), "errors": report["errors"][:12]}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
