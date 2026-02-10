"""
WCAG Rules for Operable principle
Success criteria related to making interface components operable
"""
from typing import List
from models import Finding, SeverityLevel, WCAGLevel
from .base import WCAGRule


class FormLabelRule(WCAGRule):
    """1.3.1 & 3.3.2 - Form inputs must have labels"""

    rule_code = "FORM_LABEL_MISSING"
    wcag_reference = "3.3.2"
    wcag_level = WCAGLevel.AA
    principle = "Operable"

    def check(self, parsed_html) -> List[Finding]:
        inputs = parsed_html.inputs
        unlabeled = []

        for input_elem in inputs:
            # Skip hidden inputs and buttons
            input_type = input_elem.get('type', 'text').lower()
            if input_type in ['hidden', 'submit', 'button', 'reset']:
                continue

            # Check for associated label
            input_id = input_elem.get('id')
            has_label = False

            # Check for label with for attribute
            if input_id:
                label = parsed_html.find('label', attrs={'for': input_id})
                if label:
                    has_label = True

            # Check if input is wrapped in label
            if not has_label:
                parent = input_elem.parent
                if parent and parent.name == 'label':
                    has_label = True

            # Check for aria-label or aria-labelledby
            if not has_label:
                if input_elem.get('aria-label') or input_elem.get('aria-labelledby'):
                    has_label = True

            # Check for title attribute (not ideal but acceptable)
            if not has_label:
                if input_elem.get('title'):
                    has_label = True

            if not has_label:
                unlabeled.append(str(input_elem)[:100])

        if unlabeled:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(unlabeled)} form inputs missing labels",
                remediation="Add <label> elements with 'for' attribute, or use aria-label",
                element=unlabeled[0] if unlabeled else None,
                count=len(unlabeled)
            )]
        elif len(inputs) > 0:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"All {len(inputs)} form inputs have labels",
                remediation="N/A - Check passed"
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message="No form inputs found on page",
                remediation="N/A - No inputs to check"
            )]


class ButtonAccessibleNameRule(WCAGRule):
    """4.1.2 - Buttons must have accessible names"""

    rule_code = "BUTTON_NAME_MISSING"
    wcag_reference = "4.1.2"
    wcag_level = WCAGLevel.AA
    principle = "Operable"

    def check(self, parsed_html) -> List[Finding]:
        buttons = parsed_html.buttons
        unnamed = []

        for btn in buttons:
            has_name = False

            # Check text content
            text = btn.get_text().strip()
            if text:
                has_name = True

            # Check value attribute (for input buttons)
            if not has_name and btn.get('value'):
                has_name = True

            # Check aria-label
            if not has_name and btn.get('aria-label'):
                has_name = True

            # Check aria-labelledby
            if not has_name and btn.get('aria-labelledby'):
                has_name = True

            # Check title
            if not has_name and btn.get('title'):
                has_name = True

            if not has_name:
                unnamed.append(str(btn)[:100])

        if unnamed:
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(unnamed)} buttons missing accessible names",
                remediation="Add text content, value, aria-label, or title to buttons",
                element=unnamed[0] if unnamed else None,
                count=len(unnamed)
            )]
        elif len(buttons) > 0:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"All {len(buttons)} buttons have accessible names",
                remediation="N/A - Check passed"
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message="No buttons found on page",
                remediation="N/A - No buttons to check"
            )]


class LinkTextRule(WCAGRule):
    """2.4.4 - Links must have descriptive text"""

    rule_code = "LINK_TEXT_EMPTY"
    wcag_reference = "2.4.4"
    wcag_level = WCAGLevel.AA
    principle = "Operable"

    def check(self, parsed_html) -> List[Finding]:
        links = parsed_html.links
        empty_links = []
        vague_links = []
        vague_texts = ['click here', 'read more', 'more', 'here', 'link']

        for link in links:
            # Get link text
            text = link.get_text().strip().lower()

            # Check for aria-label
            aria_label = link.get('aria-label', '').strip()

            # Check for images inside link
            img = link.find('img')
            img_alt = ''
            if img:
                img_alt = img.get('alt', '').strip()

            # Determine if link has meaningful text
            effective_text = text or aria_label or img_alt

            if not effective_text:
                empty_links.append(str(link)[:100])
            elif effective_text in vague_texts:
                vague_links.append(str(link)[:100])

        findings = []

        if empty_links:
            findings.append(self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(empty_links)} links have no text or accessible name",
                remediation="Add descriptive text or aria-label to links",
                element=empty_links[0] if empty_links else None,
                count=len(empty_links)
            ))

        if vague_links:
            findings.append(self.create_finding(
                severity=SeverityLevel.WARNING,
                message=f"{len(vague_links)} links have vague text (e.g., 'click here')",
                remediation="Use descriptive link text that makes sense out of context",
                element=vague_links[0] if vague_links else None,
                count=len(vague_links)
            ))

        if not findings and len(links) > 0:
            findings.append(self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"All {len(links)} links have meaningful text",
                remediation="N/A - Check passed"
            ))
        elif not findings:
            findings.append(self.create_finding(
                severity=SeverityLevel.PASS,
                message="No links found on page",
                remediation="N/A - No links to check"
            ))

        return findings
