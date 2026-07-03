# Research Assistant

A production grade multi-agent AI research assistant that searches the web, summarizes sources, and compiles structured reports with citations in real time.

**Live demo:** [research-assistant-delta-six.vercel.app](https://research-assistant-delta-six.vercel.app)

![Research Assistant Demo](https://img.shields.io/badge/status-live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![React](https://img.shields.io/badge/React-18-61dafb) ![LangGraph](https://img.shields.io/badge/LangGraph-0.3-orange)

---

## What it does

Type any research question. Four AI agents coordinate to produce a structured report:

1. **Web Search Agent** - queries the live web via Tavily API
2. **Summarizer Agent** - extracts key insights from each source using GPT-4o-mini
3. **Report Compiler Agent** - synthesizes everything into a markdown report with inline citations using GPT-4o
4. Results stream back to the UI in real time via Server-Sent Events

---

## Architecture

```
User Query
    │
    ▼
FastAPI (SSE endpoint)
    │
    ▼
LangGraph StateGraph
    ├── Search Agent      → Tavily API
    ├── Summarizer Agent  → GPT-4o-mini (per source)
    └── Report Compiler   → GPT-4o + ChromaDB
    │
    ▼
Streamed response → React frontend
```

### Agent State

All agents share a typed state object - a whiteboard every agent reads from and writes to:

```python
class ResearchState(TypedDict):
    query: str
    search_results: list[dict]
    summaries: list[dict]
    report: str
    status: str
    error: str | None
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph 0.3 (StateGraph) |
| **LLM** | GPT-4o (reports) + GPT-4o-mini (summaries) |
| **Web Search** | Tavily API |
| **Vector Store** | ChromaDB (persistent embeddings) |
| **Cache** | Redis (search result caching) |
| **Backend** | FastAPI + Server-Sent Events |
| **Frontend** | React 18 + TypeScript + Vite |
| **Styling** | Tailwind CSS v3 |
| **Deployment** | Render (backend) + Vercel (frontend) |

---

## Project Structure

```
research-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── state.py              # Shared ResearchState TypedDict
│   │   │   ├── search_agent.py       # Web Search Agent
│   │   │   ├── summarizer.py         # Summarizer Agent
│   │   │   └── report_compiler.py    # Report Compiler Agent
│   │   ├── graph/
│   │   │   └── research_graph.py     # LangGraph StateGraph assembly
│   │   ├── services/
│   │   │   ├── tavily_service.py     # Tavily API wrapper
│   │   │   ├── chroma_service.py     # ChromaDB wrapper
│   │   │   └── redis_service.py      # Redis cache wrapper
│   │   ├── routers/
│   │   │   └── research.py           # SSE + REST endpoints
│   │   ├── config.py                 # Pydantic settings
│   │   ├── dependencies.py           # Singleton service injection
│   │   └── main.py                   # FastAPI app + lifespan
│   └── requirements.txt
└── frontend/
    └── src/
        ├── hooks/
        │   └── useResearch.ts        # SSE connection + state management
        ├── components/
        │   ├── ProgressTimeline.tsx  # Live agent progress UI
        │   └── ReportView.tsx        # Markdown report renderer
        └── App.tsx
```

---

## Running Locally

### Prerequisites

- Python 3.12
- Node.js 18+
- Redis (Windows: [Redis for Windows](https://github.com/microsoftarchive/redis/releases))
- API keys: [OpenAI](https://platform.openai.com), [Tavily](https://app.tavily.com)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Fill in your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### Environment Variables

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_NAME=research_chunks
APP_ENV=development
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Key Design Decisions

**Why LangGraph over plain LangChain?**
The research pipeline needs conditional routing - if search returns no results, skip summarization entirely. LangGraph's StateGraph enables this with `add_conditional_edges`, making the pipeline resilient rather than brittle.

**Why SSE over WebSockets?**
Research takes 30-45 seconds. SSE streams agent progress events to the frontend so users see real-time feedback instead of a blank screen. SSE is simpler than WebSockets for one-directional server→client streaming.

**Why GPT-4o-mini for summaries and GPT-4o for reports?**
Summarization is high-volume (one call per source) and doesn't require deep reasoning - GPT-4o-mini is 10x cheaper and fast enough. The final report is the user-facing output where quality matters most, so GPT-4o is justified there.

**Why Redis caching?**
Tavily costs money per search. Identical queries within 6 hours return cached results instantly - saving API costs and reducing latency significantly.

---

## Deployment

- **Backend** - Render (Python 3 web service, free tier)
- **Frontend** - Vercel (Vite, auto-deploy on push)
- **Redis** - Render Key Value store (free tier)
- **ChromaDB** - Embedded, persists on Render disk

---

## Built by

**Vaishali Murugesan** 
