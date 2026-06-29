from functools import lru_cache
from app.services.tavily_service import TavilyService
from app.services.chroma_service import ChromaService
from app.services.redis_service import RedisService


@lru_cache(maxsize=1)
def get_tavily_service() -> TavilyService:
    """Singleton — one Tavily client for the app lifetime."""
    return TavilyService()


@lru_cache(maxsize=1)
def get_chroma_service() -> ChromaService:
    """Singleton — one ChromaDB connection for the app lifetime."""
    return ChromaService()


@lru_cache(maxsize=1)
def get_redis_service() -> RedisService:
    """Singleton — one Redis connection pool for the app lifetime."""
    return RedisService()