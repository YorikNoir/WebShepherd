"""
Pydantic models for WebShepherd
Data validation and schema definitions
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, validator


class SeverityLevel(str, Enum):
    """WCAG finding severity levels"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class ScanStatus(str, Enum):
    """Scan processing status"""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETE = "complete"
    FAILED = "failed"


class WCAGLevel(str, Enum):
    """WCAG conformance levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class ScanRequest(BaseModel):
    """Request model for URL scanning"""
    url: HttpUrl = Field(
        ...,
        description="Public HTTP/HTTPS URL to scan",
        examples=["https://example.com"]
    )

    @validator('url')
    def validate_public_url(cls, v):
        """Ensure URL is public (not localhost, private IPs, etc.)"""
        url_str = str(v)

        # Block localhost
        if 'localhost' in url_str or '127.0.0.1' in url_str:
            raise ValueError("Cannot scan localhost URLs")

        # Block private IP ranges (basic check)
        private_patterns = ['192.168.', '10.', '172.16.', '172.31.']
        if any(pattern in url_str for pattern in private_patterns):
            raise ValueError("Cannot scan private IP addresses")

        # Ensure HTTP/HTTPS only
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError("Only HTTP/HTTPS URLs are supported")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }


class Finding(BaseModel):
    """Individual WCAG finding/issue"""
    rule_code: str = Field(..., description="Unique rule identifier (e.g., IMG_ALT_MISSING)")
    severity: SeverityLevel = Field(..., description="Issue severity level")
    message: str = Field(..., description="Human-readable issue description")
    element: Optional[str] = Field(None, description="HTML element snippet causing the issue")
    wcag_reference: str = Field(..., description="WCAG 2.1 success criterion (e.g., 1.1.1)")
    wcag_level: WCAGLevel = Field(..., description="WCAG conformance level")
    principle: str = Field(..., description="WCAG principle (Perceivable, Operable, etc.)")
    remediation: str = Field(..., description="How to fix this issue")
    count: int = Field(default=1, description="Number of occurrences")

    class Config:
        json_schema_extra = {
            "example": {
                "rule_code": "IMG_ALT_MISSING",
                "severity": "fail",
                "message": "Image missing alt text",
                "element": '<img src="logo.png">',
                "wcag_reference": "1.1.1",
                "wcag_level": "AA",
                "principle": "Perceivable",
                "remediation": "Add descriptive alt text to all images",
                "count": 3
            }
        }


class ScanResponse(BaseModel):
    """Response model with scan results"""
    scan_id: str = Field(..., description="Unique scan identifier")
    url: str = Field(..., description="Scanned URL")
    status: ScanStatus = Field(..., description="Current scan status")
    score: Optional[float] = Field(None, description="Accessibility score (0-100)")
    findings: List[Finding] = Field(default_factory=list, description="List of WCAG findings")

    # Counters
    total_checks: int = Field(default=0, description="Total number of checks performed")
    passed_checks: int = Field(default=0, description="Number of passed checks")
    warnings: int = Field(default=0, description="Number of warnings")
    failures: int = Field(default=0, description="Number of failures")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    scan_duration_ms: Optional[int] = Field(None, description="Scan duration in milliseconds")

    # Summary by principle
    perceivable_issues: int = Field(default=0)
    operable_issues: int = Field(default=0)
    understandable_issues: int = Field(default=0)
    robust_issues: int = Field(default=0)

    class Config:
        json_schema_extra = {
            "example": {
                "scan_id": "abc123xyz",
                "url": "https://example.com",
                "status": "complete",
                "score": 78.5,
                "findings": [
                    {
                        "rule_code": "IMG_ALT_MISSING",
                        "severity": "fail",
                        "message": "3 images missing alt text",
                        "element": '<img src="logo.png">',
                        "wcag_reference": "1.1.1",
                        "wcag_level": "AA",
                        "principle": "Perceivable",
                        "remediation": "Add descriptive alt text to all images",
                        "count": 3
                    }
                ],
                "total_checks": 12,
                "passed_checks": 9,
                "warnings": 1,
                "failures": 2,
                "created_at": "2026-02-10T14:30:00Z",
                "completed_at": "2026-02-10T14:30:05Z",
                "scan_duration_ms": 5234
            }
        }


class StatsResponse(BaseModel):
    """Overall statistics response"""
    total_scans: int
    scans_today: int
    average_score: float
    common_issues: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "total_scans": 1247,
                "scans_today": 34,
                "average_score": 72.3,
                "common_issues": [
                    {"rule": "IMG_ALT_MISSING", "count": 523},
                    {"rule": "FORM_LABEL_MISSING", "count": 412}
                ]
            }
        }
