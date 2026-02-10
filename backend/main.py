"""
WebShepherd - WCAG 2.1 AA Accessibility Checker
Main FastAPI application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from config import settings
from database import init_db
from models import ScanRequest, ScanResponse, ScanStatus
from scanner import ScanEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🐑 WebShepherd starting up...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    # Shutdown
    logger.info("🐑 WebShepherd shutting down...")

# Create FastAPI app
app = FastAPI(
    title="WebShepherd",
    description="WCAG 2.1 AA Accessibility Checker - Guiding your website to compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scan engine
scan_engine = ScanEngine()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "WebShepherd",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/scan/", response_model=ScanResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_HOUR}/hour")
async def create_scan(request: Request, scan_request: ScanRequest):
    """
    Submit a URL for WCAG 2.1 AA accessibility scanning

    - **url**: Public HTTP/HTTPS URL to scan (max 2048 chars)

    Returns scan_id to check results with GET /api/scan/{scan_id}
    """
    try:
        logger.info(f"Starting scan for URL: {scan_request.url}")

        # Create and execute scan
        scan_result = await scan_engine.scan_url(str(scan_request.url))

        logger.info(f"Scan complete: {scan_result.scan_id}")
        return scan_result

    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/api/scan/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    """
    Retrieve scan results by scan_id

    - **scan_id**: Unique identifier returned from POST /api/scan/
    """
    try:
        scan_result = await scan_engine.get_scan(scan_id)

        if not scan_result:
            raise HTTPException(status_code=404, detail="Scan not found")

        return scan_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve scan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scan")


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    try:
        stats = await scan_engine.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
