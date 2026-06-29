import type { ResearchStep } from '../hooks/useResearch'

const STEP_ICONS = ['🔍', '📄', '✍️', '✅']

type Props = {
  steps: ResearchStep[]
  isLoading: boolean
}

export function ProgressTimeline({ steps, isLoading }: Props) {
  if (steps.length === 0) return null

  return (
    <div className="mt-8 space-y-3">
      {steps.map((step, i) => (
        <div key={i} className="flex items-start gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-sm">
            {step.done
              ? '✓'
              : isLoading && i === steps.length - 1
              ? <span className="animate-spin inline-block">⟳</span>
              : STEP_ICONS[step.step - 1] ?? '•'}
          </div>
          <div className="pt-1">
            <p className={`text-sm ${step.done ? 'text-emerald-400' : 'text-slate-300'}`}>
              {step.message}
            </p>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex items-center gap-2 pl-11 pt-1">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150" />
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-300" />
        </div>
      )}
    </div>
  )
}