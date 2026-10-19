"""Checks against the built site. Run `zensical build` first, then
`python -m unittest tests.test_build -v`."""

import math
import re
import shutil
import subprocess
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
            "logbook/index.html": "Logbook",
            "blog/index.html": "Blog",
            POST: "High Altitude Balloon Part 1 Cameras",
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
        self.assertIn(".md-container:has(.nv-banner) .md-content__inner > h1:first-of-type", css)
        self.assertIn("<h1", read(POST))


ROOT = SITE.parent
ZENSICAL = ROOT / ".venv" / "bin" / "zensical"


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
            subprocess.run([str(ZENSICAL), "build"], cwd=tmp, check=True, capture_output=True)
            self.assertNotIn("nv-now", (tmp / "site" / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
