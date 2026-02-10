"""
WCAG 2.1 AA Rules Registry
All rules are imported and registered here
"""
from .perceivable import ImageAltTextRule, HTMLLangAttributeRule, PageTitleRule
from .operable import FormLabelRule, ButtonAccessibleNameRule, LinkTextRule
from .understandable import HeadingHierarchyRule, H1ExistsRule
from .robust import DuplicateIDRule, ARIARoleValidRule

# Registry of all rules to execute
ALL_RULES = [
    # Perceivable
    ImageAltTextRule,
    HTMLLangAttributeRule,
    PageTitleRule,

    # Operable
    FormLabelRule,
    ButtonAccessibleNameRule,
    LinkTextRule,

    # Understandable
    HeadingHierarchyRule,
    H1ExistsRule,

    # Robust
    DuplicateIDRule,
    ARIARoleValidRule,
]

__all__ = ["ALL_RULES"]
