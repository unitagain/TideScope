export type DebtSourceType = 'todo' | 'issue' | 'pr'

export type DebtCategory =
  | 'security'
  | 'performance'
  | 'maintainability'
  | 'documentation'
  | 'testing'
  | 'ci'
  | 'feature'
  | 'unknown'

export type ImpactScope = 'local' | 'module' | 'system'

export type DifficultyLevel = 'entry' | 'intermediate' | 'advanced'

export interface ScoreBreakdown {
  risk: number
  impact: number
  interest: number
  cost: number
  total: number
}

export interface DebtItem {
  id: string
  source_type: DebtSourceType
  reference_id?: string
  title: string
  description?: string
  file_path?: string
  module?: string
  category: DebtCategory
  skills: string[]
  difficulty: DifficultyLevel
  risk_level: number
  impact_scope: ImpactScope
  cost_level: number
  interest: number
  priority: ScoreBreakdown
  status: string
  assignees: string[]
  created_at?: string
  html_url?: string
  recommendation?: string
}

export interface StarMapNode {
  id: string
  label: string
  module?: string
  category: DebtCategory
  source_type: DebtSourceType
  reference_id?: string
  priority: number
  radius: number
  angle: number
  size: number
  status: string
  assignees: string[]
  skills: string[]
  difficulty: DifficultyLevel
  html_url?: string
  recommendation?: string
}

export interface StarMapData {
  nodes: StarMapNode[]
  metadata: Record<string, string>
}
