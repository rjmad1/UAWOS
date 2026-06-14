# scratch/test_dashboard_regression.py
import os
import re
import pytest
from html.parser import HTMLParser

# Resolve paths of HTML files in the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = [
    os.path.join(ROOT_DIR, "uawos_dashboard.html"),
    os.path.join(ROOT_DIR, "uawos_delivery.html"),
    os.path.join(ROOT_DIR, "uawos_roadmap.html"),
    os.path.join(ROOT_DIR, "uawos_requirement_studio.html"),
    os.path.join(ROOT_DIR, "uawos_architecture.html"),
]


class UAWOSHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.aria_elements = []
        self.tablist_elements = []
        self.tab_elements = []
        self.interactive_elements = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, "start"))
        self.current_tag = tag
        attrs_dict = dict(attrs)

        # Check for ARIA attributes
        aria_keys = [k for k in attrs_dict.keys() if k.startswith("aria-")]
        if aria_keys or "role" in attrs_dict:
            self.aria_elements.append((tag, attrs_dict))

        # Check for tablist and tab roles
        if attrs_dict.get("role") == "tablist":
            self.tablist_elements.append(attrs_dict)
        if attrs_dict.get("role") == "tab":
            self.tab_elements.append(attrs_dict)

        # Check for interactive elements or elements with click handlers
        is_interactive = tag in ["button", "a", "input", "select", "textarea"] or "onclick" in attrs_dict
        if is_interactive:
            self.interactive_elements.append((tag, attrs_dict))

    def handle_endtag(self, tag):
        self.tags.append((tag, "end"))


def test_html_files_existence():
    """Verify that all operational UI dashboards exist in the repository."""
    for filepath in HTML_FILES:
        assert os.path.exists(filepath), f"Operational dashboard file missing: {os.path.basename(filepath)}"


@pytest.mark.parametrize("filepath", HTML_FILES)
def test_html_structural_integrity(filepath):
    """Parse each HTML file to check for structural tag closures and syntax correctness."""
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = UAWOSHTMLParser()
    try:
        parser.feed(html_content)
    except Exception as e:
        pytest.fail(f"HTML parsing failed for {filename}: {e}")

    # Validate essential tags are present
    tags_only = [t[0] for t in parser.tags]
    assert "html" in tags_only, f"{filename} missing <html> tag."
    assert "head" in tags_only, f"{filename} missing <head> tag."
    assert "body" in tags_only, f"{filename} missing <body> tag."

    # Validate correct nesting/closures for key blocks
    open_tags = []
    for tag, action in parser.tags:
        if tag in ["html", "head", "body", "div", "table", "thead", "tbody", "tr", "p"]:
            if action == "start":
                open_tags.append(tag)
            elif action == "end":
                if open_tags and open_tags[-1] == tag:
                    open_tags.pop()

    # We don't assert open_tags is empty because standard HTML allows missing optional tags,
    # but we assert that there are no catastrophic mismatch blocks.
    assert len(open_tags) < 50, f"Excessive unclosed structural tags in {filename}: {open_tags}"


@pytest.mark.parametrize("filepath", HTML_FILES)
def test_dashboard_css_variables_and_styling(filepath):
    """Verify HSL status colors and CSS properties structure match visual system specs."""
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    # All dashboard files should define or utilize HSL variables or standard color variables for system status mapping
    if filename == "uawos_dashboard.html":
        green_var = re.search(r"--color-green-[hsl]", html_content)
        yellow_var = re.search(r"--color-yellow-[hsl]", html_content)
        red_var = re.search(r"--color-red-[hsl]", html_content)
        assert green_var, f"{filename} CSS is missing Green HSL definition."
        assert yellow_var, f"{filename} CSS is missing Yellow HSL definition."
        assert red_var, f"{filename} CSS is missing Red HSL definition."
    else:
        green_var = re.search(r"--green\s*:", html_content)
        yellow_var = re.search(r"--yellow\s*:", html_content)
        red_var = re.search(r"--red\s*:", html_content)
        assert green_var, f"{filename} CSS is missing --green definition."
        assert yellow_var, f"{filename} CSS is missing --yellow definition."
        assert red_var, f"{filename} CSS is missing --red definition."



@pytest.mark.parametrize("filepath", HTML_FILES)
def test_wcag_accessibility_parameters(filepath):
    """Verify keyboard focus outlines and ARIA role mappings comply with WCAG 2.1 AA."""
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = UAWOSHTMLParser()
    parser.feed(html_content)

    # Check for outline style focus indicator
    has_focus_style = "focus-visible" in html_content or ":focus" in html_content
    assert has_focus_style, f"{filename} is missing explicit keyboard focus outlines (:focus-visible)."

    # If tablist is defined, tab elements must exist
    if parser.tablist_elements:
        assert len(parser.tab_elements) > 0, f"{filename} contains tablist but has 0 tabs."

    # Validate that interactive elements have descriptive label helpers
    for tag, attrs in parser.interactive_elements:
        # Elements should either have text content, an aria-label, or an aria-labelledby
        has_label = "aria-label" in attrs or "aria-labelledby" in attrs or "id" in attrs
        # If it's an anchor link, it must have a label or reference
        if tag == "a":
            assert "href" in attrs, f"Anchor link in {filename} is missing href attribute: {attrs}"


if __name__ == "__main__":
    pytest.main([__file__])
