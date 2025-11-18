type BadgeStatus = 'success' | 'processing' | 'default' | 'error' | 'warning'

type TagTone = 'default' | 'success' | 'processing' | 'warning' | 'error'

export const CATEGORY_COLORS: Record<string, string> = {
  security: '#f5222d',
  performance: '#fa8c16',
  maintainability: '#13c2c2',
  documentation: '#9254de',
  testing: '#52c41a',
  ci: '#1890ff',
  feature: '#722ed1',
  unknown: '#94a3b8',
}

export const DIFFICULTY_TAG_COLORS: Record<string, TagTone> = {
  entry: 'processing',
  intermediate: 'warning',
  advanced: 'error',
}

export const STATUS_BADGE_STATUS: Record<string, BadgeStatus> = {
  open: 'processing',
  closed: 'success',
  merged: 'success',
  draft: 'warning',
}

export const SOURCE_TYPE_LABELS: Record<string, string> = {
  todo: 'Code TODO',
  issue: 'GitHub Issue',
  pr: 'Pull Request',
}

export const SOURCE_TYPE_OPTIONS = Object.entries(SOURCE_TYPE_LABELS).map(([value, label]) => ({
  label,
  value,
}))

export const SOURCE_TYPE_COLORS: Record<string, string> = {
  todo: '#2dd4bf',
  issue: '#f97316',
  pr: '#a855f7',
}

export const DIFFICULTY_OPTIONS = [
  { label: 'Entry', value: 'entry' },
  { label: 'Intermediate', value: 'intermediate' },
  { label: 'Advanced', value: 'advanced' },
]

export const DEFAULT_AVATAR_PLACEHOLDER =
  'https://api.dicebear.com/7.x/initials/png?backgroundColor=0f172a&seed=tidescope'
