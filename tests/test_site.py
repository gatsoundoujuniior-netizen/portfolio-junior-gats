import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a)
        if tag == "h1":
            self.h1 += 1


page = Collector()
page.feed(HTML)


class TestStructure(unittest.TestCase):
    def test_language_and_viewport(self):
        self.assertIn('<html lang="en">', HTML)
        self.assertIn('name="viewport"', HTML)

    def test_single_h1(self):
        self.assertEqual(page.h1, 1)

    def test_required_sections(self):
        for section in ("projects", "experience", "stack", "pipeline", "contact"):
            self.assertIn(section, page.ids)

    def test_ids_are_unique(self):
        self.assertEqual(len(page.ids), len(set(page.ids)))

    def test_anchor_links_have_targets(self):
        for link in page.links:
            href = link["href"]
            if href.startswith("#"):
                self.assertIn(href[1:], page.ids, f"broken anchor {href}")

    def test_external_links_use_noopener(self):
        for link in page.links:
            if link["href"].startswith("http"):
                self.assertIn("noopener", link.get("rel", ""), link["href"])

    def test_stylesheet_exists(self):
        self.assertTrue((ROOT / "css" / "style.css").is_file())
        self.assertIn('href="css/style.css"', HTML)

    def test_no_long_dashes(self):
        self.assertNotIn("—", HTML)
        self.assertNotIn("–", HTML)

    def test_cv_is_linked_and_present(self):
        self.assertIn('href="assets/CV_Junior_Gatsoundou_EN.pdf"', HTML)
        self.assertTrue((ROOT / "assets" / "CV_Junior_Gatsoundou_EN.pdf").is_file())

    def test_no_placeholders_left(self):
        self.assertNotIn("REPLACE_WITH", HTML)

    def test_github_profile_linked(self):
        self.assertIn("github.com/gatsoundoujuniior-netizen", HTML)


if __name__ == "__main__":
    unittest.main()
