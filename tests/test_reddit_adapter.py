from __future__ import annotations

import unittest

from reddit_adapter import _extract_rapidsave_download_url


class RapidSaveHTMLParserTests(unittest.TestCase):
    def test_extracts_download_button_anchor(self):
        page = (
            '<html><a class="btn download-button" '
            'href="/download.php?token=abc123">Download</a></html>'
        )
        self.assertEqual(
            _extract_rapidsave_download_url(page),
            "https://rapidsave.com/download.php?token=abc123",
        )

    def test_extracts_download_php_link_without_button_class(self):
        page = '<a href="https://rapidsave.com/download.php?token=abc">Download</a>'
        self.assertEqual(
            _extract_rapidsave_download_url(page),
            "https://rapidsave.com/download.php?token=abc",
        )

    def test_ignores_external_or_non_download_links(self):
        page = (
            '<a class="download-button" href="https://attacker.invalid/file.mp4">bad</a>'
            '<a href="/about">about</a>'
        )
        self.assertIsNone(_extract_rapidsave_download_url(page))

    def test_returns_none_for_static_site_shell(self):
        self.assertIsNone(_extract_rapidsave_download_url("<html><body>Paste URL</body></html>"))


if __name__ == "__main__":
    unittest.main()
