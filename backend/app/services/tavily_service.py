from tavily import TavilyClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TavilyService:
    """Wraps Tavily search API. Returns clean, structured results."""

    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
    ) -> list[dict]:
        """
        Search the web and return structured results.

        Returns list of dicts with keys:
          - title: str
          - url: str
          - content: str   (clean extracted text, no HTML)
          - score: float   (relevance score 0-1)
        """
        try:
            logger.info(f"Tavily search: '{query}' (max={max_results})")
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=False,   # we build our own answer
                include_raw_content=False,
            )
            results = response.get("results", [])
            logger.info(f"Tavily returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise