"""
Synchronize Apple Light Theme and Theme Switcher
"""
from pathlib import Path
import re

DOCS_DIR = Path("docs")
HTML_PATH = DOCS_DIR / "index.html"
CSS_PATH = DOCS_DIR / "styles.css"

css_content = CSS_PATH.read_text(encoding="utf-8")
html_content = HTML_PATH.read_text(encoding="utf-8")

# Replace <style>...</style>
updated_html = re.sub(r"<style>.*?</style>", f"<style>\n{css_content}\n  </style>", html_content, flags=re.DOTALL)

# Add Theme Toggle Button
old_btn = '<button id="btn-fullscreen" class="btn-secondary" type="button">\n        Full Screen\n      </button>'
new_btn = '<button id="btn-theme-toggle" class="btn-secondary" type="button">\n        Theme: Light\n      </button>\n      <button id="btn-fullscreen" class="btn-secondary" type="button">\n        Full Screen\n      </button>'

if old_btn in updated_html:
    updated_html = updated_html.replace(old_btn, new_btn)
    print("Added Theme: Light button to header")

HTML_PATH.write_text(updated_html, encoding="utf-8")
print("Updated docs/index.html with Apple Light Theme")
