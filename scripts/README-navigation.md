# Responsive navigation checks

These checks exercise the generated site in Chromium, Firefox and WebKit on the
homepage and synonym-search tutorial at 15 widths from 320 to 2,560 CSS pixels,
with web fonts loaded and with font downloads blocked.

Use **Zola 0.22.1**, matching CI. Newer Zola versions may require a separate
template migration.

```sh
python3 -m venv /tmp/terraphim-navigation-venv
/tmp/terraphim-navigation-venv/bin/python -m pip install -r scripts/requirements-browser.txt
/tmp/terraphim-navigation-venv/bin/python -m playwright install chromium firefox webkit
zola build --base-url http://127.0.0.1:8879
python3 -m http.server 8879 --bind 127.0.0.1 --directory public
```

In another terminal, run each engine:

```sh
/tmp/terraphim-navigation-venv/bin/python scripts/check-navigation.py --base-url http://127.0.0.1:8879 --browser chromium --artifacts /tmp/navigation-chromium
/tmp/terraphim-navigation-venv/bin/python scripts/check-navigation.py --base-url http://127.0.0.1:8879 --browser firefox --artifacts /tmp/navigation-firefox
/tmp/terraphim-navigation-venv/bin/python scripts/check-navigation.py --base-url http://127.0.0.1:8879 --browser webkit --artifacts /tmp/navigation-webkit
```

The build base URL must match the server. Otherwise absolute asset URLs could
load production CSS instead of the patch. The checker rejects a stylesheet from
another origin and records the served stylesheet SHA-256 in `navigation.json`.
It also checks exact navigation destinations, including their origins.

Checks cover single-line desktop text, visible non-overlapping controls,
compact/desktop selection, preserved links and actual keyboard actions: search
input focus, Escape to close search, opening and scrolling the compact menu to
Donate, and navigating to Editor. The open compact menu is resized to desktop
and back. WebKit uses Option+Tab to include links in keyboard traversal on macOS.

Runs exit nonzero on failure and save JSON plus representative screenshots.
The normal-font run requires Space Grotesk to load; a font CDN failure is not
silently relabelled as success. A separate fallback run blocks font downloads.
CI runs all three engines and uploads evidence even when a check fails.
Its `site-public` artifact is a localhost test build; production deployment
builds separately using the production base URL.

To verify a deployment, use `--base-url https://terraphim.ai`. Manual acceptance
also includes actual 200% browser zoom: viewport/device-scale overrides are not
browser zoom, and Playwright WebKit is not native Safari.
