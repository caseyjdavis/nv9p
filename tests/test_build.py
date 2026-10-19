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


if __name__ == "__main__":
    unittest.main()
