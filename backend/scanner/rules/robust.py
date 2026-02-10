"""
WCAG Rules for Robust principle
Success criteria related to maximizing compatibility with assistive technologies
"""
from typing import List
from models import Finding, SeverityLevel, WCAGLevel
from .base import WCAGRule


class DuplicateIDRule(WCAGRule):
    """4.1.1 - IDs must be unique"""

    rule_code = "DUPLICATE_ID"
    wcag_reference = "4.1.1"
    wcag_level = WCAGLevel.AA
    principle = "Robust"

    def check(self, parsed_html) -> List[Finding]:
        all_ids = parsed_html.get_all_ids()

        # Find duplicates
        seen = set()
        duplicates = set()

        for id_val in all_ids:
            if id_val in seen:
                duplicates.add(id_val)
            seen.add(id_val)

        if duplicates:
            dup_list = ', '.join(f"'{d}'" for d in list(duplicates)[:5])
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(duplicates)} duplicate IDs found: {dup_list}",
                remediation="Ensure all ID attributes are unique within the document",
                count=len(duplicates)
            )]
        elif len(all_ids) > 0:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"All {len(all_ids)} IDs are unique",
                remediation="N/A - Check passed"
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message="No ID attributes found",
                remediation="N/A - No IDs to check"
            )]


class ARIARoleValidRule(WCAGRule):
    """4.1.2 - ARIA roles must be valid"""

    rule_code = "ARIA_ROLE_INVALID"
    wcag_reference = "4.1.2"
    wcag_level = WCAGLevel.AA
    principle = "Robust"

    # Valid ARIA 1.2 roles (subset of most common ones)
    VALID_ROLES = {
        'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
        'checkbox', 'columnheader', 'combobox', 'complementary', 'contentinfo',
        'definition', 'dialog', 'directory', 'document', 'feed', 'figure',
        'form', 'grid', 'gridcell', 'group', 'heading', 'img', 'link', 'list',
        'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'menu',
        'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation',
        'none', 'note', 'option', 'presentation', 'progressbar', 'radio',
        'radiogroup', 'region', 'row', 'rowgroup', 'rowheader', 'scrollbar',
        'search', 'searchbox', 'separator', 'slider', 'spinbutton', 'status',
        'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox',
        'timer', 'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem'
    }

    def check(self, parsed_html) -> List[Finding]:
        elements_with_role = parsed_html.soup.find_all(attrs={"role": True})
        invalid_roles = []

        for elem in elements_with_role:
            role = elem.get('role', '').strip().lower()
            if role and role not in self.VALID_ROLES:
                invalid_roles.append((role, str(elem)[:100]))

        if invalid_roles:
            role_names = ', '.join(f"'{r[0]}'" for r in invalid_roles[:5])
            return [self.create_finding(
                severity=SeverityLevel.FAIL,
                message=f"{len(invalid_roles)} invalid ARIA roles found: {role_names}",
                remediation="Use only valid ARIA 1.2 role values",
                element=invalid_roles[0][1] if invalid_roles else None,
                count=len(invalid_roles)
            )]
        elif len(elements_with_role) > 0:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message=f"All {len(elements_with_role)} ARIA roles are valid",
                remediation="N/A - Check passed"
            )]
        else:
            return [self.create_finding(
                severity=SeverityLevel.PASS,
                message="No ARIA roles found",
                remediation="N/A - No roles to check"
            )]
