"""
Database setup and models
Using SQLAlchemy with async support
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON
from datetime import datetime
from typing import Optional

from config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class ScanRecord(Base):
    """Database model for scan results"""
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # JSON field for findings
    findings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Counters
    total_checks: Mapped[int] = mapped_column(Integer, default=0)
    passed_checks: Mapped[int] = mapped_column(Integer, default=0)
    warnings: Mapped[int] = mapped_column(Integer, default=0)
    failures: Mapped[int] = mapped_column(Integer, default=0)

    # Issue counts by principle
    perceivable_issues: Mapped[int] = mapped_column(Integer, default=0)
    operable_issues: Mapped[int] = mapped_column(Integer, default=0)
    understandable_issues: Mapped[int] = mapped_column(Integer, default=0)
    robust_issues: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scan_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Error info (if scan failed)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
