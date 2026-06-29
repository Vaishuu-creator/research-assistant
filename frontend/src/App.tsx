// import { useState, useRef, KeyboardEvent } from 'react'
import { useState, useRef } from 'react'
import type { KeyboardEvent } from 'react'
import { useResearch } from './hooks/useResearch'
import { ProgressTimeline } from './components/ProgressTimeline'
import { ReportView } from './components/ReportView'

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

  const handleReset = () => {
    reset()
    setQuery('')
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  return (
    <div className="min-h-screen bg-[#0f1117]">
      <div className="max-w-3xl mx-auto px-4 py-16">

        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Research Assistant
          </h1>
          <p className="mt-2 text-slate-500 text-sm">
            Multi-agent AI · Web search · Structured reports
          </p>
        </div>

        {/* Search bar — hide when report is shown */}
        {state.status !== 'complete' && (
          <div className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What do you want to research?"
              disabled={state.status === 'loading'}
              className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl
                text-slate-200 placeholder-slate-500 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all"
            />
            <button
              onClick={handleSubmit}
              disabled={!query.trim() || state.status === 'loading'}
              className="px-5 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40
                disabled:cursor-not-allowed text-white text-sm font-medium
                rounded-xl transition-colors"
            >
              {state.status === 'loading' ? 'Researching...' : 'Research'}
            </button>
          </div>
        )}

        {/* Progress timeline */}
        {state.status === 'loading' && (
          <ProgressTimeline
            steps={state.steps}
            isLoading={state.status === 'loading'}
          />
        )}

        {/* Error state */}
        {state.status === 'error' && (
          <div className="mt-8 p-4 bg-red-900/30 border border-red-800 rounded-xl">
            <p className="text-red-400 text-sm font-medium">Research failed</p>
            <p className="text-red-300 text-sm mt-1">{state.error}</p>
            <button
              onClick={handleReset}
              className="mt-3 px-3 py-1.5 text-xs bg-red-800 hover:bg-red-700
                text-white rounded-lg transition-colors"
            >
              Try again
            </button>
          </div>
        )}

        {/* Report */}
        {state.status === 'complete' && (
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