from app.agents.state import ResearchState
from app.config import settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)

SUMMARIZE_PROMPT = """You are a research analyst. Given a web search result, 
extract the key information relevant to the research query.

Research query: {query}

Source title: {title}
Source URL: {url}
Source content: {content}

Write a concise summary (3-5 sentences) of what this source says about the query.
Focus only on information directly relevant to the query.
End with one sentence on why this source is credible or not."""


def summarizer_agent(state: ResearchState) -> dict:
    """
    Reads:  state["search_results"], state["query"]
    Writes: state["summaries"], state["status"]

    Calls GPT-4o once per search result to produce clean summaries.
    """
    logger.info(f"Summarizer agent processing {len(state['search_results'])} sources")

    summaries = []

    for result in state["search_results"]:
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        if not content.strip():
            logger.warning(f"Skipping empty content from {url}")
            continue

        try:
            prompt = SUMMARIZE_PROMPT.format(
                query=state["query"],
                title=title,
                url=url,
                content=content[:2000],   # cap at 2000 chars to control tokens
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",       # cheaper than gpt-4o, plenty smart enough
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,           # low temp = consistent, factual summaries
                max_tokens=300,
            )

            summary_text = response.choices[0].message.content.strip()

            summaries.append({
                "title": title,
                "url": url,
                "summary": summary_text,
                "original_score": result.get("score", 0.0),
            })

            logger.info(f"Summarized: {title[:50]}...")

        except Exception as e:
            logger.error(f"Failed to summarize {url}: {e}")
            # Don't crash — skip this source and continue
            continue

    logger.info(f"Summarizer produced {len(summaries)} summaries")
    return {
        "summaries": summaries,
        "status": "summarization_complete",
        "error": None if summaries else "All summarizations failed",
    }