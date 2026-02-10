"""
WCAG Rules for Understandable principle
Success criteria related to making content understandable
"""
from typing import List
from models import Finding, SeverityLevel, WCAGLevel
from .base import WCAGRule


class HeadingHierarchyRule(WCAGRule):
    """1.3.1 - Headings should not skip levels"""

    rule_code = "HEADING_SKIP_LEVEL"
    wcag_reference = "1.3.1"
    wcag_level = WCAGLevel.AA
    principle = "Understandable"

    def check(self, parsed_html) -> List[Finding]:
        headings = parsed_html.headings

        if not headings:
            return [self.create_finding(
                severity=SeverityLevel.WARNING,
                message="No heading elements found on page",
                remediation="Add heading structure (h1-h6) to organize content"
            )]

        # Extract heading levels
        levels = []
        for h in headings:
            level = int(h.name[1])  # h1 -> 1, h2 -> 2, etc.
            levels.append(level)

        # Check for skipped levels
        skipped = []
        prev_level = 0

        for i, level in enumerate(levels):
            if i == 0:
                if level != 1:
                    skipped.append(f"First heading is {headings[i].name}, should start with h1")
            else:
                if level > prev_level + 1:
                    skipped.append(
                        f"Skipped from {prev_level} to {level} "
                        f"at heading: '{headings[i].get_text().strip()[:30]}'"
                    )
            prev_level = level

        if skipped:
            return [self.create_finding(
                severity=SeverityLevel.WARNING,
                message=f"Heading hierarchy has {len(skipped)} issues",
                remediation="Use sequential heading levels (h1 -> h2 -> h3) without skipping",
                element=skipped[0] if skipped else None,
                count=len(skipped)
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"Heading hierarchy is correct ({len(headings)} headings)",
                remediation="N/A - Check passed"
            )]


class H1ExistsRule(WCAGRule):
    """2.4.6 - Page should have exactly one h1"""

    rule_code = "H1_MISSING_OR_MULTIPLE"
    wcag_reference = "2.4.6"
    wcag_level = WCAGLevel.AA
    principle = "Understandable"

    def check(self, parsed_html) -> List[Finding]:
        h1_elements = parsed_html.find_all('h1')
        h1_count = len(h1_elements)

        if h1_count == 0:
            return [self.create_finding(
                severity=SeverityLevel.WARNING,
                message="No <h1> element found on page",
                remediation="Add a single <h1> element to serve as the main page heading"
            )]
        elif h1_count > 1:
            h1_texts = [h.get_text().strip()[:30] for h in h1_elements[:3]]
            return [self.create_finding(
                severity=SeverityLevel.WARNING,
                message=f"Multiple <h1> elements found ({h1_count}): {', '.join(h1_texts)}",
                remediation="Use only one <h1> per page for the main heading",
                count=h1_count
            )]
        else:
            h1_text = h1_elements[0].get_text().strip()
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"Page has one <h1>: '{h1_text[:50]}'",
                remediation="N/A - Check passed"
            )]
