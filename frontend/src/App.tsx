import { useState, useRef } from 'react'
import type { KeyboardEvent } from 'react'
import { useResearch } from './hooks/useResearch'
import { AgentProgress } from './components/AgentProgress'
import { ReportView } from './components/ReportView'

const EXAMPLE_QUERIES = [
  'How does chain of thought prompting work?',
  'What are the latest advances in AI agents?',
  'Explain retrieval augmented generation',
  'What is the transformer architecture?',
]

export default function App() {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const { state, research, reset } = useResearch()

  const handleSubmit = () => {
    if (!query.trim() || state.status === 'loading') return
    research(query.trim())
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSubmit()
  }

  const handleExample = (q: string) => {
    setQuery(q)
    research(q)
  }

  const handleReset = () => {
    reset()
    setQuery('')
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  const isIdle = state.status === 'idle'
  const isLoading = state.status === 'loading'
  const isComplete = state.status === 'complete'
  const isError = state.status === 'error'

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Top nav */}
      <nav className="border-b border-[#1e1e2e] px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center text-xs font-bold text-white">R</div>
          <span className="text-sm font-semibold text-slate-200">ResearchMind</span>
          <span className="text-xs text-slate-600 ml-1">/ multi-agent</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-600">
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>
            LangGraph
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>
            GPT-4o
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>
            Tavily
          </span>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4">

        {/* Hero — only shown when idle */}
        {isIdle && (
          <div className="pt-20 pb-10 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-medium mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
              Powered by 4 AI agents
            </div>
            <h1 className="text-4xl font-bold text-white tracking-tight mb-3">
              Research anything,<br />
              <span className="text-indigo-400">instantly.</span>
            </h1>
            <p className="text-slate-500 text-sm max-w-md mx-auto">
              Multi-agent AI that searches the web, summarizes sources,
              and compiles structured reports with citations.
            </p>
          </div>
        )}

        {/* Search bar */}
        {!isComplete && (
          <div className={`${isIdle ? 'pb-6' : 'pt-8 pb-6'}`}>
            <div className="relative flex gap-2">
              <div className="relative flex-1">
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a research question..."
                  disabled={isLoading}
                  autoFocus
                  className="w-full px-4 py-3.5 bg-[#13131f] border border-[#2d2d3d] rounded-xl
                    text-slate-200 placeholder-slate-600 text-sm
                    focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30
                    disabled:opacity-40 disabled:cursor-not-allowed transition-all pr-16"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-700 hidden sm:block">
                  ↵ Enter
                </span>
              </div>
              <button
                onClick={handleSubmit}
                disabled={!query.trim() || isLoading}
                className="px-5 py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30
                  disabled:cursor-not-allowed text-white text-sm font-medium
                  rounded-xl transition-all active:scale-95 whitespace-nowrap"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    Working...
                  </span>
                ) : 'Research →'}
              </button>
            </div>

            {/* Example queries */}
            {isIdle && (
              <div className="flex flex-wrap gap-2 mt-4">
                {EXAMPLE_QUERIES.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleExample(q)}
                    className="px-3 py-1.5 text-xs text-slate-500 border border-[#2d2d3d]
                      hover:border-indigo-500/40 hover:text-slate-300 rounded-lg
                      bg-[#13131f] transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Agent progress */}
        {isLoading && (
          <AgentProgress steps={state.steps} />
        )}

        {/* Error */}
        {isError && (
          <div className="mt-6 p-4 bg-red-950/40 border border-red-900/50 rounded-xl">
            <p className="text-red-400 text-sm font-medium mb-1">Research failed</p>
            <p className="text-red-300/70 text-xs">{state.error}</p>
            <button
              onClick={handleReset}
              className="mt-3 px-3 py-1.5 text-xs bg-red-900/50 hover:bg-red-800/50
                text-red-300 rounded-lg transition-colors border border-red-800/50"
            >
              Try again
            </button>
          </div>
        )}

        {/* Report */}
        {isComplete && (
          <ReportView
            report={state.report}
            sourcesUsed={state.sourcesUsed}
            query={query}
            onReset={handleReset}
          />
        )}

      </div>
    </div>
  )
}