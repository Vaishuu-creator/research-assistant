import { useState, useCallback, useRef } from 'react'

export type ResearchStep = {
  message: string
  step: number
  done: boolean
}

export type ResearchState = {
  status: 'idle' | 'loading' | 'complete' | 'error'
  steps: ResearchStep[]
  report: string
  sourcesUsed: number
  error: string | null
  currentStep: number
}

export function useResearch() {
  const [state, setState] = useState<ResearchState>({
    status: 'idle',
    steps: [],
    report: '',
    sourcesUsed: 0,
    error: null,
    currentStep: 0,
  })

  const eventSourceRef = useRef<EventSource | null>(null)

  const research = useCallback((query: string) => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    // Reset state
    setState({
      status: 'loading',
      steps: [],
      report: '',
      sourcesUsed: 0,
      error: null,
      currentStep: 0,
    })

    // Connect to SSE stream
    const url = `/api/research/stream?query=${encodeURIComponent(query)}`
    const es = new EventSource(url)
    eventSourceRef.current = es

    es.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'status') {
        setState(prev => ({
          ...prev,
          currentStep: data.step,
          steps: [
            ...prev.steps,
            { message: data.message, step: data.step, done: false },
          ],
        }))
      }

      if (data.type === 'complete') {
        setState(prev => ({
          ...prev,
          status: 'complete',
          report: data.report,
          sourcesUsed: data.sources_used,
          steps: prev.steps.map(s => ({ ...s, done: true })),
        }))
        es.close()
      }

      if (data.type === 'error') {
        setState(prev => ({
          ...prev,
          status: 'error',
          error: data.message,
        }))
        es.close()
      }
    }

    es.onerror = () => {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: 'Connection to server lost. Please try again.',
      }))
      es.close()
    }
  }, [])

  const reset = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }
    setState({
      status: 'idle',
      steps: [],
      report: '',
      sourcesUsed: 0,
      error: null,
      currentStep: 0,
    })
  }, [])

  return { state, research, reset }
}