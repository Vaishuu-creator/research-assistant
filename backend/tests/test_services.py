import pytest
from unittest.mock import MagicMock, patch
from app.services.redis_service import RedisService
from app.services.chroma_service import ChromaService


class TestRedisService:
    """Test Redis caching logic without a real Redis connection."""

    def test_cache_key_is_stable(self):
        """Same query → same cache key, always."""
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            svc = RedisService()
            key1 = svc._make_cache_key("LLM reasoning advances")
            key2 = svc._make_cache_key("LLM reasoning advances")
            assert key1 == key2

    def test_cache_key_is_query_insensitive(self):
        """Case and whitespace shouldn't create different cache entries."""
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            svc = RedisService()
            key1 = svc._make_cache_key("LLM Reasoning")
            key2 = svc._make_cache_key("llm reasoning")
            assert key1 == key2

    def test_cache_miss_returns_none(self):
        with patch("redis.from_url") as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_redis.return_value = mock_client

            svc = RedisService()
            result = svc.get_cached_search("some query")
            assert result is None


class TestChromaService:
    """Test ChromaDB document operations."""

    def test_add_and_count(self, tmp_path):
        """Documents added should increase count."""
        with patch("app.services.chroma_service.settings") as mock_settings:
            mock_settings.chroma_persist_dir = str(tmp_path)
            mock_settings.chroma_collection_name = "test_collection"

            svc = ChromaService()
            assert svc.get_count() == 0

            svc.add_documents([
                {"content": "LLMs are transformer-based models.", "metadata": {"url": "https://example.com"}},
                {"content": "RAG combines retrieval with generation.", "metadata": {"url": "https://example2.com"}},
            ])
            assert svc.get_count() == 2

    def test_empty_documents_returns_empty_list(self, tmp_path):
        with patch("app.services.chroma_service.settings") as mock_settings:
            mock_settings.chroma_persist_dir = str(tmp_path)
            mock_settings.chroma_collection_name = "test_collection2"

            svc = ChromaService()
            ids = svc.add_documents([])
            assert ids == []