import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useState } from 'react'

type Props = {
  report: string
  sourcesUsed: number
  query: string
  onReset: () => void
}

export function ReportView({ report, sourcesUsed, query, onReset }: Props) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(report)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleExport = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="mt-8">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-700">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wide">Research complete</p>
          <p className="text-sm text-slate-300 mt-1">
            {sourcesUsed} sources analysed for "{query}"
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-colors"
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>
          <button
            onClick={handleExport}
            className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-colors"
          >
            Export .md
          </button>
          <button
            onClick={onReset}
            className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
          >
            New research
          </button>
        </div>
      </div>

      {/* Markdown report */}
      <div className="prose prose-invert prose-sm max-w-none
        prose-headings:text-slate-100 prose-headings:font-semibold
        prose-p:text-slate-300 prose-p:leading-relaxed
        prose-li:text-slate-300
        prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
        prose-strong:text-slate-200
        prose-code:text-emerald-400 prose-code:bg-slate-800 prose-code:px-1 prose-code:rounded
        prose-hr:border-slate-700">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {report}
        </ReactMarkdown>
      </div>
    </div>
  )
}