"""
WCAG Rules for Perceivable principle
Success criteria related to making content perceivable to all users
"""
from typing import List
from models import Finding, SeverityLevel, WCAGLevel
from .base import WCAGRule


class ImageAltTextRule(WCAGRule):
    """1.1.1 Non-text Content - Images must have alt text"""

    rule_code = "IMG_ALT_MISSING"
    wcag_reference = "1.1.1"
    wcag_level = WCAGLevel.AA
    principle = "Perceivable"

    def check(self, parsed_html) -> List[Finding]:
        images = parsed_html.images
        missing_alt = []

        for img in images:
            alt = img.get('alt')
            # Check if alt is missing or empty (but allow alt="")
            if alt is None:
                missing_alt.append(str(img)[:100])

        if missing_alt:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(missing_alt)} images missing alt attribute",
                remediation="Add descriptive alt text to all images. Use alt='' for decorative images.",
                element=missing_alt[0] if missing_alt else None,
                count=len(missing_alt)
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message="All images have alt attributes",
                remediation="N/A - Check passed"
            )]


class HTMLLangAttributeRule(WCAGRule):
    """3.1.1 Language of Page - HTML must have lang attribute"""

    rule_code = "HTML_LANG_MISSING"
    wcag_reference = "3.1.1"
    wcag_level = WCAGLevel.AA
    principle = "Understandable"

    def check(self, parsed_html) -> List[Finding]:
        html_tag = parsed_html.html_tag

        if not html_tag:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message="No <html> tag found",
                remediation="Ensure document has a valid <html> tag with lang attribute"
            )]

        lang = html_tag.get('lang')

        if not lang:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message="<html> tag missing lang attribute",
                remediation="Add lang attribute to <html> tag (e.g., <html lang='en'>)",
                element=str(html_tag)[:100]
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"Page language is set to '{lang}'",
                remediation="N/A - Check passed"
            )]


class PageTitleRule(WCAGRule):
    """2.4.2 Page Titled - Pages must have descriptive titles"""

    rule_code = "PAGE_TITLE_MISSING"
    wcag_reference = "2.4.2"
    wcag_level = WCAGLevel.AA
    principle = "Operable"

    def check(self, parsed_html) -> List[Finding]:
        title = parsed_html.title

        if not title:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message="Page has no <title> element",
                remediation="Add a descriptive <title> element in the <head> section"
            )]
        elif len(title.strip()) == 0:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message="Page title is empty",
                remediation="Provide a descriptive, meaningful page title",
                element=f"<title>{title}</title>"
            )]
        elif len(title) < 3:
            return [self.create_finding(
                severity=SeverityLevel.WARNING,
                message=f"Page title is very short: '{title}'",
                remediation="Provide a more descriptive page title (at least a few words)",
                element=f"<title>{title}</title>"
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"Page has title: '{title}'",
                remediation="N/A - Check passed"
            )]
