import type { ResearchStep } from '../hooks/useResearch'

type Props = {
  steps: ResearchStep[]
}

const AGENT_META: Record<number, { label: string; icon: string; description: string }> = {
  0: { label: 'Initializing', icon: '⚡', description: 'Setting up research pipeline' },
  1: { label: 'Web Search Agent', icon: '🔍', description: 'Searching the web via Tavily' },
  2: { label: 'Summarizer Agent', icon: '📄', description: 'Extracting key insights with GPT-4o-mini' },
  3: { label: 'Report Compiler', icon: '✍️', description: 'Synthesizing report with GPT-4o' },
  4: { label: 'Complete', icon: '✓', description: 'Research finished' },
}

export function AgentProgress({ steps }: Props) {
  if (steps.length === 0) return null

  return (
    <div className="py-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
        <span className="text-xs font-medium text-slate-500 uppercase tracking-widest">
          Agent pipeline running
        </span>
      </div>

      {/* Agent cards */}
      <div className="space-y-2">
        {steps.map((step, i) => {
          const meta = AGENT_META[step.step] ?? AGENT_META[0]
          const isLast = i === steps.length - 1
          const isDone = step.done || !isLast

          return (
            <div
              key={i}
              className={`flex items-start gap-4 p-4 rounded-xl border transition-all
                ${isDone
                  ? 'bg-[#13131f] border-[#1e1e2e] opacity-70'
                  : 'bg-[#13131f] border-indigo-500/30 shadow-lg shadow-indigo-500/5'
                }`}
            >
              {/* Icon */}
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-base flex-shrink-0
                ${isDone ? 'bg-[#1e1e2e]' : 'bg-indigo-500/20'}`}
              >
                {!isDone && isLast
                  ? <span className="animate-spin text-sm inline-block">⟳</span>
                  : <span>{isDone ? '✓' : meta.icon}</span>
                }
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className={`text-sm font-medium ${isDone ? 'text-slate-500' : 'text-slate-200'}`}>
                    {meta.label}
                  </p>
                  {isDone && (
                    <span className="text-xs text-emerald-600 flex-shrink-0">done</span>
                  )}
                  {!isDone && isLast && (
                    <span className="text-xs text-indigo-400 flex-shrink-0 animate-pulse">running</span>
                  )}
                </div>
                <p className="text-xs text-slate-600 mt-0.5">{meta.description}</p>
                {step.message && (
                  <p className="text-xs text-slate-500 mt-1.5 font-mono">{step.message}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Bottom note */}
      <p className="text-xs text-slate-700 text-center mt-6">
        This typically takes 30–45 seconds
      </p>
    </div>
  )
}