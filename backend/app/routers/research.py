from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.graph.research_graph import research_graph
from app.agents.state import ResearchState
import logging
import json
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)


class ResearchResponse(BaseModel):
    query: str
    report: str
    sources_used: int
    status: str
    error: str | None = None


def format_sse(data: dict) -> str:
    """Format a dict as an SSE message."""
    return f"data: {json.dumps(data)}\n\n"


async def run_research_stream(query: str):
    """
    Generator that yields SSE events as each agent completes.
    This is what the frontend EventSource consumes.
    """
    yield format_sse({"type": "status", "message": "Starting research...", "step": 0})

    initial_state: ResearchState = {
        "query": query,
        "search_results": [],
        "summaries": [],
        "report": "",
        "status": "starting",
        "error": None,
    }

    try:
        # Stream progress through each graph step
        yield format_sse({
            "type": "status",
            "message": "Searching the web...",
            "step": 1
        })
        await asyncio.sleep(0)  # yield control to event loop

        # Run the graph — LangGraph 0.3.x supports astream
        final_state = initial_state
        async for chunk in research_graph.astream(initial_state):
            node_name = list(chunk.keys())[0]
            node_output = chunk[node_name]

            if node_name == "search":
                count = len(node_output.get("search_results", []))
                yield format_sse({
                    "type": "status",
                    "message": f"Found {count} sources. Summarizing...",
                    "step": 2,
                    "sources_found": count,
                })

            elif node_name == "summarizer":
                count = len(node_output.get("summaries", []))
                yield format_sse({
                    "type": "status",
                    "message": f"Summarized {count} sources. Compiling report...",
                    "step": 3,
                    "summaries_count": count,
                })

            elif node_name == "compiler":
                yield format_sse({
                    "type": "status",
                    "message": "Report ready.",
                    "step": 4,
                })

            # Merge chunk into final state
            final_state = {**final_state, **node_output}

        # Send the final report
        yield format_sse({
            "type": "complete",
            "query": query,
            "report": final_state.get("report", ""),
            "sources_used": len(final_state.get("summaries", [])),
            "status": final_state.get("status", "complete"),
        })

    except Exception as e:
        logger.error(f"Stream error: {e}")
        yield format_sse({
            "type": "error",
            "message": str(e),
        })


@router.get("/stream")
async def stream_research(query: str):
    """SSE endpoint — frontend connects here with EventSource."""
    if not query or len(query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query too short")

    return StreamingResponse(
        run_research_stream(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",    # disable nginx buffering
        },
    )


@router.post("/", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """Original blocking endpoint — kept for testing via Swagger."""
    initial_state: ResearchState = {
        "query": request.query,
        "search_results": [],
        "summaries": [],
        "report": "",
        "status": "starting",
        "error": None,
    }
    try:
        final_state = research_graph.invoke(initial_state)
        return ResearchResponse(
            query=request.query,
            report=final_state["report"],
            sources_used=len(final_state["summaries"]),
            status=final_state["status"],
            error=final_state.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))