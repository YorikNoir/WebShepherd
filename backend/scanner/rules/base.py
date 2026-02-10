"""
WCAG 2.1 Rules - Base classes and rule registry
"""
from abc import ABC, abstractmethod
from typing import List
from models import Finding, SeverityLevel, WCAGLevel


class WCAGRule(ABC):
    """Base class for all WCAG rules"""

    # Rule metadata (override in subclasses)
    rule_code: str = ""
    wcag_reference: str = ""
    wcag_level: WCAGLevel = WCAGLevel.AA
    principle: str = ""

    @abstractmethod
    def check(self, parsed_html) -> List[Finding]:
        """
        Execute the rule check

        Args:
            parsed_html: ParsedHTML object

        Returns:
            List of Finding objects
        """
        pass

    def create_finding(
        self,
        severity: SeverityLevel,
        message: str,
        remediation: str,
        element: str = None,
        count: int = 1
    ) -> Finding:
        """Helper to create Finding object"""
        return Finding(
            rule_code=self.rule_code,
            severity=severity,
            message=message,
            element=element,
            wcag_reference=self.wcag_reference,
            wcag_level=self.wcag_level,
            principle=self.principle,
            remediation=remediation,
            count=count
        )
