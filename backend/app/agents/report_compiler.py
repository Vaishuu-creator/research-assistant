from app.agents.state import ResearchState
from app.dependencies import get_chroma_service
from app.config import settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)

REPORT_PROMPT = """You are a research report writer. Based on the following 
summarized sources, write a comprehensive, well-structured research report.

Research query: {query}

Sources:
{sources_text}

Write a markdown report with:
1. An executive summary (2-3 sentences)
2. Key findings (bullet points with inline citations like [1], [2])
3. Detailed analysis (2-3 paragraphs)
4. Conclusion (1 paragraph)
5. References section listing all sources

Use [1], [2], etc. to cite sources inline. Be factual and objective."""


def report_compiler_agent(state: ResearchState) -> dict:
    """
    Reads:  state["summaries"], state["query"]
    Writes: state["report"], state["status"]

    Compiles all summaries into a structured markdown report.
    Also stores final summaries into ChromaDB for future queries.
    """
    logger.info("Report compiler agent running")

    if not state["summaries"]:
        return {
            "report": "No sources found to compile a report.",
            "status": "report_failed",
            "error": "No summaries available",
        }

    # Build numbered source list for the prompt
    sources_text = ""
    for i, s in enumerate(state["summaries"], 1):
        sources_text += f"[{i}] {s['title']}\nURL: {s['url']}\nSummary: {s['summary']}\n\n"

    try:
        prompt = REPORT_PROMPT.format(
            query=state["query"],
            sources_text=sources_text,
        )

        response = client.chat.completions.create(
            model="gpt-4o",            # full model for final report — quality matters here
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1500,
        )

        report = response.choices[0].message.content.strip()

        # Store summaries in ChromaDB for future semantic queries
        chroma = get_chroma_service()
        documents = [
            {
                "content": s["summary"],
                "metadata": {
                    "title": s["title"],
                    "url": s["url"],
                    "query": state["query"],
                },
            }
            for s in state["summaries"]
        ]
        chroma.add_documents(documents)
        logger.info(f"Stored {len(documents)} summaries in ChromaDB")

        return {
            "report": report,
            "status": "complete",
            "error": None,
        }

    except Exception as e:
        logger.error(f"Report compiler failed: {e}")
        return {
            "report": "",
            "status": "report_failed",
            "error": str(e),
        }