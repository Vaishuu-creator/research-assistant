from app.agents.state import ResearchState
from app.dependencies import get_tavily_service
import logging

logger = logging.getLogger(__name__)


def search_agent(state: ResearchState) -> dict:
    """
    Reads:  state["query"]
    Writes: state["search_results"], state["status"]

    Calls Tavily and returns raw search results.
    Single responsibility — search only, nothing else.
    """
    logger.info(f"Search agent running for: '{state['query']}'")

    try:
        tavily = get_tavily_service()
        results = tavily.search(
            query=state["query"],
            max_results=6,
        )

        if not results:
            logger.warning("Search agent got 0 results")
            return {
                "search_results": [],
                "status": "search_empty",
                "error": "No results found for query",
            }

        logger.info(f"Search agent found {len(results)} results")
        return {
            "search_results": results,
            "status": "search_complete",
            "error": None,
        }

    except Exception as e:
        logger.error(f"Search agent failed: {e}")
        return {
            "search_results": [],
            "status": "search_failed",
            "error": str(e),
        }