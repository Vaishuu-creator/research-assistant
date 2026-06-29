from typing import TypedDict


class ResearchState(TypedDict):
    query: str
    search_results: list[dict]
    summaries: list[dict]
    report: str
    status: str
    error: str | None