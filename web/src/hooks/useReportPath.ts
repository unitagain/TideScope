import { useSearchParams } from 'react-router-dom'

const DEFAULT_REPORT = 'surfsense-report.json'

export const useReportPath = (): string => {
  const [params] = useSearchParams()
  return params.get('report')?.trim() || DEFAULT_REPORT
}
