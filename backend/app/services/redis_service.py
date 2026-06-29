import redis
from app.config import settings
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 60 * 60 * 6  # 6 hours — Tavily results don't change that fast


class RedisService:
    """
    Two responsibilities:
    1. Cache Tavily search results (saves API credits on repeated queries)
    2. Task queue for agent jobs (Phase 2)
    """

    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True,   # return str, not bytes
            socket_connect_timeout=5,
        )
        # Verify connection at startup
        self.client.ping()
        logger.info("Redis connection established")

    def _make_cache_key(self, query: str) -> str:
        """Stable hash key for a search query."""
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
        return f"search_cache:{query_hash}"

    def get_cached_search(self, query: str) -> list[dict] | None:
        """Return cached results for this query, or None if cache miss."""
        key = self._make_cache_key(query)
        cached = self.client.get(key)
        if cached:
            logger.info(f"Cache HIT for query: '{query[:50]}...'")
            return json.loads(cached)
        logger.info(f"Cache MISS for query: '{query[:50]}...'")
        return None

    def cache_search_results(self, query: str, results: list[dict]) -> None:
        """Store search results with TTL."""
        key = self._make_cache_key(query)
        self.client.setex(
            name=key,
            time=CACHE_TTL_SECONDS,
            value=json.dumps(results),
        )
        logger.info(f"Cached {len(results)} results for '{query[:50]}...'")

    def is_healthy(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False