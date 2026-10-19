"""Checks against the built site. Run `zensical build` first, then
`python -m unittest tests.test_build -v`."""

import re
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


if __name__ == "__main__":
    unittest.main()
