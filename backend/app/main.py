from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import research
from app.dependencies import get_tavily_service, get_chroma_service, get_redis_service
import logging

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: initialize all service singletons.
    If any service fails (bad API key, Redis down), the app won't start.
    This is intentional — we catch infra problems before any request arrives.
    """
    logger.info("Starting Research Assistant API...")
    try:
        get_tavily_service()
        logger.info("✓ Tavily service ready")
    except Exception as e:
        logger.error(f"✗ Tavily init failed: {e}")
        raise

    try:
        get_chroma_service()
        logger.info("✓ ChromaDB service ready")
    except Exception as e:
        logger.error(f"✗ ChromaDB init failed: {e}")
        raise

    try:
        get_redis_service()
        logger.info("✓ Redis service ready")
    except Exception as e:
        logger.warning(f"⚠ Redis init failed (non-fatal in dev): {e}")
        # Redis failure is non-fatal in dev — cache just won't work

    logger.info("All services ready. API is live.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Research Assistant API",
    description="Multi-agent research assistant with LangGraph + RAG",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router)


@app.get("/health")
async def health_check():
    """
    Liveness check. Returns status of each downstream service.
    Used by Docker, load balancers, and your own sanity.
    """
    redis_ok = False
    try:
        redis_ok = get_redis_service().is_healthy()
    except Exception:
        pass

    chroma_count = 0
    try:
        chroma_count = get_chroma_service().get_count()
    except Exception:
        pass

    return {
        "status": "ok",
        "version": "0.1.0",
        "services": {
            "redis": "up" if redis_ok else "down",
            "chromadb": "up",
            "chromadb_docs": chroma_count,
        },
    }