from langgraph.graph import StateGraph, END
from app.agents.state import ResearchState
from app.agents.search_agent import search_agent
from app.agents.summarizer import summarizer_agent
from app.agents.report_compiler import report_compiler_agent
import logging

logger = logging.getLogger(__name__)


def should_continue_after_search(state: ResearchState) -> str:
    """
    Conditional edge — decides what happens after search agent runs.
    Returns the name of the next node to run.
    """
    if state["status"] == "search_failed":
        logger.warning("Search failed — ending graph early")
        return END

    if state["status"] == "search_empty":
        logger.warning("Search returned empty — ending graph early")
        return END

    return "summarizer"


def build_research_graph() -> StateGraph:
    """
    Assembles the LangGraph StateGraph.

    Nodes = agents (each does one job)
    Edges = flow between agents
    Conditional edges = decision points
    """
    graph = StateGraph(ResearchState)

    # Register nodes
    graph.add_node("search", search_agent)
    graph.add_node("summarizer", summarizer_agent)
    graph.add_node("compiler", report_compiler_agent)

    # Entry point
    graph.set_entry_point("search")

    # Conditional edge after search
    graph.add_conditional_edges(
        "search",
        should_continue_after_search,
        {
            "summarizer": "summarizer",
            END: END,
        }
    )

    # Fixed edges after summarizer and compiler
    graph.add_edge("summarizer", "compiler")
    graph.add_edge("compiler", END)

    return graph.compile()


# Compiled graph — imported by the router
research_graph = build_research_graph()