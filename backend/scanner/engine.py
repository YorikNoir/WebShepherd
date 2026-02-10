"""
Main scan engine - orchestrates URL fetching, parsing, and WCAG checks
"""
import logging
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import ScanResponse, ScanStatus, Finding
from database import async_session_maker, ScanRecord
from .fetcher import URLFetcher
from .parser import HTMLParser
from .rules import ALL_RULES

logger = logging.getLogger(__name__)


class ScanEngine:
    """Main engine for coordinating accessibility scans"""

    def __init__(self):
        self.fetcher = URLFetcher()
        self.parser = HTMLParser()
        self.rules = ALL_RULES

    async def scan_url(self, url: str) -> ScanResponse:
        """
        Perform complete accessibility scan of a URL

        Args:
            url: URL to scan

        Returns:
            ScanResponse with results
        """
        scan_id = str(uuid.uuid4())[:12]
        start_time = datetime.utcnow()

        try:
            # Create database record
            async with async_session_maker() as session:
                scan_record = ScanRecord(
                    scan_id=scan_id,
                    url=url,
                    status=ScanStatus.SCANNING.value
                )
                session.add(scan_record)
                await session.commit()

            # Fetch HTML
            logger.info(f"Fetching URL: {url}")
            html_content = await self.fetcher.fetch(url)

            # Parse HTML
            logger.info(f"Parsing HTML for scan {scan_id}")
            parsed_html = self.parser.parse(html_content)

            # Run all WCAG rules
            logger.info(f"Running {len(self.rules)} WCAG checks")
            findings = []

            for rule_class in self.rules:
                rule = rule_class()
                rule_findings = rule.check(parsed_html)
                findings.extend(rule_findings)

            # Calculate metrics
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            passed = sum(1 for f in findings if f.severity.value == "pass")
            warnings = sum(1 for f in findings if f.severity.value == "warning")
            failures = sum(1 for f in findings if f.severity.value == "fail")
            total = len(findings)

            # Calculate score (100 = perfect, 0 = many failures)
            if total > 0:
                score = ((passed + (warnings * 0.5)) / total) * 100
            else:
                score = 100.0

            # Count issues by principle
            principle_counts = {
                "Perceivable": 0,
                "Operable": 0,
                "Understandable": 0,
                "Robust": 0
            }

            for finding in findings:
                if finding.severity.value in ("warning", "fail"):
                    principle_counts[finding.principle] = principle_counts.get(finding.principle, 0) + 1

            # Update database record
            async with async_session_maker() as session:
                result = await session.execute(
                    select(ScanRecord).where(ScanRecord.scan_id == scan_id)
                )
                scan_record = result.scalar_one()

                scan_record.status = ScanStatus.COMPLETE.value
                scan_record.score = round(score, 1)
                scan_record.findings = [f.model_dump() for f in findings]
                scan_record.total_checks = total
                scan_record.passed_checks = passed
                scan_record.warnings = warnings
                scan_record.failures = failures
                scan_record.perceivable_issues = principle_counts["Perceivable"]
                scan_record.operable_issues = principle_counts["Operable"]
                scan_record.understandable_issues = principle_counts["Understandable"]
                scan_record.robust_issues = principle_counts["Robust"]
                scan_record.completed_at = end_time
                scan_record.scan_duration_ms = duration_ms

                await session.commit()

            # Build response
            response = ScanResponse(
                scan_id=scan_id,
                url=url,
                status=ScanStatus.COMPLETE,
                score=round(score, 1),
                findings=findings,
                total_checks=total,
                passed_checks=passed,
                warnings=warnings,
                failures=failures,
                perceivable_issues=principle_counts["Perceivable"],
                operable_issues=principle_counts["Operable"],
                understandable_issues=principle_counts["Understandable"],
                robust_issues=principle_counts["Robust"],
                created_at=start_time,
                completed_at=end_time,
                scan_duration_ms=duration_ms
            )

            logger.info(f"Scan {scan_id} complete - Score: {score:.1f}")
            return response

        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {str(e)}")

            # Update database with error
            async with async_session_maker() as session:
                result = await session.execute(
                    select(ScanRecord).where(ScanRecord.scan_id == scan_id)
                )
                scan_record = result.scalar_one_or_none()

                if scan_record:
                    scan_record.status = ScanStatus.FAILED.value
                    scan_record.error_message = str(e)
                    scan_record.completed_at = datetime.utcnow()
                    await session.commit()

            raise

    async def get_scan(self, scan_id: str) -> Optional[ScanResponse]:
        """
        Retrieve scan results by ID

        Args:
            scan_id: Scan identifier

        Returns:
            ScanResponse or None if not found
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(ScanRecord).where(ScanRecord.scan_id == scan_id)
            )
            scan_record = result.scalar_one_or_none()

            if not scan_record:
                return None

            # Convert findings from JSON to Finding objects
            findings = []
            if scan_record.findings:
                findings = [Finding(**f) for f in scan_record.findings]

            return ScanResponse(
                scan_id=scan_record.scan_id,
                url=scan_record.url,
                status=ScanStatus(scan_record.status),
                score=scan_record.score,
                findings=findings,
                total_checks=scan_record.total_checks,
                passed_checks=scan_record.passed_checks,
                warnings=scan_record.warnings,
                failures=scan_record.failures,
                perceivable_issues=scan_record.perceivable_issues,
                operable_issues=scan_record.operable_issues,
                understandable_issues=scan_record.understandable_issues,
                robust_issues=scan_record.robust_issues,
                created_at=scan_record.created_at,
                completed_at=scan_record.completed_at,
                scan_duration_ms=scan_record.scan_duration_ms
            )

    async def get_stats(self) -> dict:
        """Get overall statistics"""
        async with async_session_maker() as session:
            # Total scans
            total_result = await session.execute(
                select(func.count(ScanRecord.id))
            )
            total_scans = total_result.scalar()

            # Today's scans
            today = datetime.utcnow().date()
            today_result = await session.execute(
                select(func.count(ScanRecord.id)).where(
                    func.date(ScanRecord.created_at) == today
                )
            )
            scans_today = today_result.scalar()

            # Average score
            avg_result = await session.execute(
                select(func.avg(ScanRecord.score)).where(
                    ScanRecord.score.isnot(None)
                )
            )
            average_score = avg_result.scalar() or 0.0

            return {
                "total_scans": total_scans or 0,
                "scans_today": scans_today or 0,
                "average_score": round(average_score, 1),
                "common_issues": []  # TODO: Implement
            }
