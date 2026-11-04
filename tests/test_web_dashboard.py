"""
Unit Tests for Web Dashboard Assets
===================================
Verifies file completeness, zero-emoji enforcement, data integrity,
and absence of interview Q&A leakage.
"""

import json
import re
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"


class TestWebDashboard(unittest.TestCase):
    """Test suite validating web dashboard assets and compliance."""

    def test_required_web_files_exist(self):
        for fname in ["index.html", "styles.css", "app.js", "data.js"]:
            fpath = DOCS_DIR / fname
            self.assertTrue(fpath.exists(), f"Missing required web asset: {fname}")
            self.assertGreater(fpath.stat().st_size, 100, f"Asset {fname} is empty or too small")

    def test_no_emojis_in_web_assets(self):
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
        for fpath in DOCS_DIR.glob("*.*"):
            content = fpath.read_text(encoding="utf-8")
            emojis = emoji_pattern.findall(content)
            self.assertEqual(
                len(emojis),
                0,
                f"Prohibited emojis detected in {fpath.name}: {set(emojis)}",
            )

    def test_no_interview_qa_in_web_assets(self):
        prohibited_terms = [
            "interview question",
            "candidate persona",
            "q&a",
            "roche's maxim",
            "support engineer background help",
        ]
        for fpath in DOCS_DIR.glob("*.*"):
            content = fpath.read_text(encoding="utf-8").lower()
            for term in prohibited_terms:
                self.assertNotIn(
                    term,
                    content,
                    f"Interview text leak detected in {fpath.name} ('{term}')",
                )

    def test_data_js_payload_integrity(self):
        data_js = (DOCS_DIR / "data.js").read_text(encoding="utf-8")
        self.assertIn("const STUDENT_RECORDS =", data_js)
        self.assertIn("const FEATURE_IMPORTANCES =", data_js)
        self.assertIn("const MODEL_METRICS =", data_js)

        # Extract student records count
        match = re.search(r"const STUDENT_RECORDS = (\[.*?\]);", data_js)
        self.assertIsNotNone(match, "Could not extract STUDENT_RECORDS JSON")
        records = json.loads(match.group(1))
        self.assertEqual(len(records), 4464, "Web payload must contain all 4,464 students")

    def test_html_includes_chartjs_and_scripts(self):
        html = (DOCS_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn("chart.umd.min.js", html)
        self.assertIn("data.js", html)
        self.assertIn("app.js", html)
        self.assertIn("styles.css", html)
        self.assertIn("Kishor Prajapati", html)


if __name__ == "__main__":
    unittest.main()
