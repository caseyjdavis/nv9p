"""Checks against the built site. Run `zensical build` first, then
`python -m unittest tests.test_build -v`."""

import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"

POST = "blog/2018/04/16/high-altitude-balloon-part-1-cameras/index.html"


def read(path):
    file = SITE / path
    if not file.is_file():
        raise AssertionError(f"missing built file: site/{path}")
    return file.read_text(encoding="utf-8")


class BaselineTest(unittest.TestCase):
    """Existing behavior that the theme must not break."""

    def test_search_index_exists(self):
        self.assertGreater(len(read("search.json")), 100)

    def test_homepage_lists_three_recent_posts(self):
        links = re.findall(r'href="/(blog/20\d\d/\d\d/\d\d/[^"]+/)"', read("index.html"))
        self.assertGreaterEqual(len(links), 3)
        for link in links[:3]:
            self.assertTrue((SITE / link / "index.html").is_file(), link)

    def test_blog_index_and_post_urls(self):
        read("blog/index.html")
        read(POST)

    def test_glightbox_present(self):
        html = read(POST)
        self.assertIn("<img", html)
        self.assertIn("glightbox", html)


PAGES = [
    "index.html",
    "about/index.html",
    "logbook/index.html",
    "qsl-cards/index.html",
    "blog/index.html",
    POST,
]

SATELLITE_PATH = 'd="M199 7c9.4-9.4 24.6-9.4 33.9 0l89.4 89.4'


def header(html):
    match = re.search(r"<header\b.*?</header>", html, re.S)
    if not match:
        raise AssertionError("no <header> element")
    return match.group(0)


class ChromeTest(unittest.TestCase):
    """Dusk palette, satellite logo, header tabs and wordmark."""

    def test_logo_is_satellite(self):
        logo = re.search(r'class="md-header__button md-logo".*?</a>', read("index.html"), re.S).group(0)
        self.assertIn(SATELLITE_PATH, logo)
        self.assertNotIn("tower-broadcast", logo)

    def test_wordmark_and_title(self):
        html = read("index.html")
        topic = re.search(r'<div class="md-header__topic">\s*<span class="md-ellipsis">(.*?)</span>', html, re.S)
        self.assertEqual(topic.group(1).strip(), "NV9P")
        self.assertIn("NV9P Amateur Radio", re.search(r"<title>(.*?)</title>", html, re.S).group(1))

    def test_stylesheet_linked(self):
        for page in PAGES:
            self.assertIn("stylesheets/nv9p.css", read(page), page)

    def test_tabs_in_header(self):
        head = header(read("index.html"))
        self.assertIn("md-tabs", head)
        for label in ["Home", "Blog", "Logbook", "QSL Cards", "About"]:
            self.assertRegex(head, rf">\s*{label}\s*<", label)

    def test_favicon_is_satellite(self):
        href = re.search(r'<link rel="icon" href="([^"]+)"', read("index.html")).group(1)
        self.assertTrue(href.endswith("img/satellite.svg"), href)


def banner_copy(html):
    match = re.search(r'<div class="nv-banner__copy">(.*?)</div>\s*</section>', html, re.S)
    if not match:
        raise AssertionError("no .nv-banner__copy")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))).strip()


class BannerTest(unittest.TestCase):
    """Front Range banner: large on the homepage, slim elsewhere."""

    def test_home_banner(self):
        html = read("index.html")
        self.assertIn("nv-banner--home", html)
        copy = re.search(r'<div class="nv-banner__copy">.*?</section>', html, re.S).group(0)
        self.assertIn(">NV9P<", copy)
        self.assertIn("Working satellites from the Colorado Rockies", copy)
        for tag in ["DM79", "ITU 7", "CQ 4", "Rocky Mountain Div."]:
            self.assertIn(f">{tag}<", copy, tag)
        self.assertIn('id="nv-sat"', html)
        self.assertIn('id="nv-sonde"', html)

    def test_slim_banner_on_inner_pages(self):
        titles = {
            "about/index.html": "About",
            "logbook/index.html": "My digital logbook",
            "blog/index.html": "Blog",
            POST: "High Altitude Balloon Part 1: Cameras",
            "404.html": "404 - Not found",
        }
        for page, title in titles.items():
            html = read(page)
            self.assertIn("nv-banner--slim", html, page)
            self.assertNotIn("nv-banner--home", html, page)
            self.assertEqual(banner_copy(html), title, page)
            self.assertNotIn('id="nv-sat"', html, page)
            self.assertNotIn('id="nv-sonde"', html, page)

    def test_satellite_on_orbit(self):
        html = read("index.html")
        orbit = re.search(r'<ellipse id="nv-orbit"[^>]*>', html).group(0)
        cx, cy, rx, ry = (float(re.search(rf'\b{k}="([\d.]+)"', orbit).group(1)) for k in ("cx", "cy", "rx", "ry"))
        sat = re.search(r'<g id="nv-sat" transform="translate\(([\d.]+) ([\d.]+)\) rotate\((-?[\d.]+)\)"', html)
        x, y, angle = (float(v) for v in sat.groups())
        self.assertAlmostEqual(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2, 1, delta=0.01)
        t = math.acos((x - cx) / rx)
        tangent = math.degrees(math.atan2(ry * math.cos(t), rx * math.sin(t)))
        self.assertAlmostEqual(angle, tangent, delta=1)

    def test_duplicate_h1_hidden_by_css(self):
        css = (SITE / "stylesheets/nv9p.css").read_text()
        rule = re.search(r"\.md-container:has\(\.nv-banner\) \.md-content__inner > h1:first-of-type \{(.*?)\}", css, re.S)
        self.assertIsNotNone(rule)
        # Visually hidden only, so screen readers keep the page heading
        self.assertNotIn("display: none", rule.group(1))
        self.assertIn("clip", rule.group(1))
        self.assertIn("<h1", read(POST))

    def test_banner_title_matches_hidden_h1(self):
        for page in ["about/index.html", "logbook/index.html", "qsl-cards/index.html",
                     "blog/index.html", "blog/archive/2018/index.html", POST, "404.html"]:
            html = read(page)
            content = html[html.index('class="md-content__inner'):]
            h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S).group(1)).strip()
            self.assertEqual(banner_copy(html), h1, page)


ROOT = SITE.parent


class NowPanelTest(unittest.TestCase):
    """Homepage "What I'm working on right now" panel, driven by config."""

    def test_panel_on_homepage(self):
        html = read("index.html")
        panel = re.search(r'<section class="nv-now".*?</section>', html, re.S).group(0)
        self.assertRegex(panel, r"What I(&#39;|')m working on right now")
        self.assertIn("updated October 2026", panel)
        titles = ["Portable satellite tower", "Front Range sonde chasing", "Weather balloon launches"]
        positions = [panel.index(t) for t in titles]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(len(re.findall(r'<li class="nv-now__item">\s*<span class="nv-now__icon">\s*<svg', panel)), 3)

    def test_panel_before_intro(self):
        html = read("index.html")
        self.assertLess(html.index('class="nv-now"'), html.index("Welcome to the website of radio station NV9P"))

    def test_panel_only_on_homepage(self):
        for page in ["about/index.html", "blog/index.html", POST]:
            self.assertNotIn("nv-now", read(page), page)

    def test_empty_items_renders_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for name in ["docs", "overrides", "ext", "hooks"]:
                if (ROOT / name).exists():
                    shutil.copytree(ROOT / name, tmp / name)
            shutil.copy(ROOT / "main.py", tmp)
            config = (ROOT / "zensical.toml").read_text()
            config = re.sub(r"\n\[\[project\.extra\.now\.items\]\]\n(?:[^\[\n].*\n?)*", "\n", config)
            config = config.replace("[project.extra.now]\n", "[project.extra.now]\nitems = []\n")
            (tmp / "zensical.toml").write_text(config)
            subprocess.run([sys.executable, "-m", "zensical", "build"], cwd=tmp, check=True, capture_output=True)
            self.assertNotIn("nv-now", (tmp / "site" / "index.html").read_text())


CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

PROBE = """<!doctype html><body><iframe id="f" src="/" width="%(w)d" height="1000"></iframe><pre id="out"></pre>
<script>
const f = document.getElementById("f");
f.onload = () => setTimeout(() => {
  const d = f.contentDocument, win = f.contentWindow;
  const box = (sel) => { const e = d.querySelector(sel); if (!e) return null;
    const r = e.getBoundingClientRect(); return {l: r.left, r: r.right, t: r.top, b: r.bottom}; };
  const sidebar = d.querySelector(".md-sidebar--primary");
  document.getElementById("out").textContent = JSON.stringify({
    banner: box(".nv-banner"), art: box(".nv-banner__art"), copy: box(".nv-banner__copy"),
    sat: box("#nv-sat"), sonde: box("#nv-sonde"),
    sidebar: sidebar ? win.getComputedStyle(sidebar).display : null,
    scroll: d.documentElement.scrollWidth,
  });
}, 500);
</script>"""


@unittest.skipUnless(CHROME.exists(), "Google Chrome not installed")
class BrowserLayoutTest(unittest.TestCase):
    """Homepage banner layout measured in headless Chrome at real widths."""

    WIDTHS = [375, 720, 1280, 1920, 2560]

    @classmethod
    def setUpClass(cls):
        import functools
        import http.server
        import threading
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

        handler = functools.partial(Quiet, directory=str(SITE))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.results = {}
        for width in cls.WIDTHS:
            probe = SITE / f"_probe-{width}.html"
            probe.write_text(PROBE % {"w": width})
            try:
                dom = subprocess.run(
                    [str(CHROME), "--headless=new", "--disable-gpu", "--window-size=2700,1100",
                     "--virtual-time-budget=5000", "--dump-dom",
                     f"http://127.0.0.1:{cls.server.server_port}/{probe.name}"],
                    capture_output=True, text=True, timeout=60).stdout
            finally:
                probe.unlink()
            match = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
            cls.results[width] = json.loads(match.group(1).replace("&quot;", '"')) if match else None

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def inside(self, inner, outer):
        return (inner["l"] >= outer["l"] - 0.5 and inner["r"] <= outer["r"] + 0.5
                and inner["t"] >= outer["t"] - 0.5 and inner["b"] <= outer["b"] + 0.5)

    def overlaps(self, a, b):
        return a["l"] < b["r"] and b["l"] < a["r"] and a["t"] < b["b"] and b["t"] < a["b"]

    def test_satellite_and_balloon_fully_in_banner(self):
        for width, m in self.results.items():
            with self.subTest(width=width):
                self.assertTrue(self.inside(m["sat"], m["banner"]), m)
                self.assertTrue(self.inside(m["sonde"], m["banner"]), m)

    def test_art_clear_of_copy(self):
        for width, m in self.results.items():
            with self.subTest(width=width):
                self.assertFalse(self.overlaps(m["sat"], m["copy"]), m)
                self.assertFalse(self.overlaps(m["sonde"], m["copy"]), m)

    def test_art_covers_banner_width(self):
        for width, m in self.results.items():
            with self.subTest(width=width):
                self.assertLessEqual(m["art"]["l"], m["banner"]["l"] + 0.5, m)
                self.assertGreaterEqual(m["art"]["r"], m["banner"]["r"] - 0.5, m)
                self.assertEqual(m["scroll"], width, m)

    def test_homepage_sidebar_hidden_on_desktop_only(self):
        self.assertEqual(self.results[1280]["sidebar"], "none")
        self.assertEqual(self.results[1920]["sidebar"], "none")
        self.assertNotEqual(self.results[375]["sidebar"], "none")


class ProjectHeadingTest(unittest.TestCase):
    def test_project_headings_use_left_bar(self):
        css = (SITE / "stylesheets/nv9p.css").read_text()
        rule = re.search(r"\.md-container:has\(\.nv-banner--home\) \.md-typeset h3 \{(.*?)\}", css, re.S).group(1)
        self.assertIn("border-left", rule)
        self.assertNotIn("border-top", rule)


if __name__ == "__main__":
    unittest.main()
