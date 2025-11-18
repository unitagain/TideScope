import { useEffect, useMemo, useState } from 'react'
import type { ColumnsType } from 'antd/es/table'
import { Badge, Input, Select, Space, Table, Tag, Typography } from 'antd'

import type { DebtItem } from '../types/analyzer'
import type { DebtListFilters } from '../services/api'
import { fetchDebtList } from '../services/api'
import {
  CATEGORY_COLORS,
  DIFFICULTY_OPTIONS,
  DIFFICULTY_TAG_COLORS,
  SOURCE_TYPE_LABELS,
  SOURCE_TYPE_OPTIONS,
  STATUS_BADGE_STATUS,
} from '../constants/debt'
import { useReportPath } from '../hooks/useReportPath'

const modulePlaceholder = 'Filter by module path (e.g. analyzer, api)'

const ListPage = () => {
  const reportPath = useReportPath()
  const [debts, setDebts] = useState<DebtItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<DebtListFilters>({})
  const [moduleInput, setModuleInput] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        setLoading(true)
        const list = await fetchDebtList(filters, reportPath)
        if (!active) return
        setDebts(list)
        setError(null)
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Failed to load debt list')
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [filters, reportPath])

  const columns: ColumnsType<DebtItem> = useMemo(
    () => [
      {
        title: 'Title',
        dataIndex: 'title',
        key: 'title',
        width: '28%',
        render: (_, record) => (
          <Space direction="vertical" size={0}>
            {record.html_url ? (
              <Typography.Link href={record.html_url} target="_blank" rel="noreferrer">
                {record.title}
              </Typography.Link>
            ) : (
              <Typography.Text strong>{record.title}</Typography.Text>
            )}
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {record.module ?? 'unknown module'}
            </Typography.Text>
          </Space>
        ),
      },
      {
        title: 'Type',
        dataIndex: 'source_type',
        key: 'type',
        width: 110,
        render: (value: DebtItem['source_type']) => (
          <Tag color="geekblue">{SOURCE_TYPE_LABELS[value] ?? value}</Tag>
        ),
      },
      {
        title: 'Category',
        dataIndex: 'category',
        key: 'category',
        width: 150,
        render: (value: DebtItem['category']) => (
          <Tag style={{ border: 'none' }} color={CATEGORY_COLORS[value] ?? '#999'}>
            {value}
          </Tag>
        ),
      },
      {
        title: 'Priority',
        dataIndex: ['priority', 'total'],
        key: 'priority',
        width: 110,
        sorter: (a, b) => a.priority.total - b.priority.total,
        defaultSortOrder: 'descend',
        render: (_, record) => <Typography.Text strong>{record.priority.total.toFixed(1)}</Typography.Text>,
      },
      {
        title: 'Difficulty',
        dataIndex: 'difficulty',
        key: 'difficulty',
        width: 140,
        render: (value: DebtItem['difficulty']) => (
          <Tag color={DIFFICULTY_TAG_COLORS[value] ?? 'default'}>{value}</Tag>
        ),
      },
      {
        title: 'Skills',
        dataIndex: 'skills',
        key: 'skills',
        render: (skills: string[]) =>
          skills.length ? (
            <Space wrap>
              {skills.map((skill) => (
                <Tag key={skill}>{skill}</Tag>
              ))}
            </Space>
          ) : (
            <Typography.Text type="secondary">n/a</Typography.Text>
          ),
      },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        width: 140,
        render: (value: string) => (
          <Badge status={STATUS_BADGE_STATUS[value] ?? 'default'} text={value} />
        ),
      },
    ],
    [],
  )

  const handleFilterChange = (key: keyof DebtListFilters, value?: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }))
  }

  const handleModuleSearch = (value: string) => {
    setModuleInput(value)
    handleFilterChange('module', value.trim())
  }

  const headerSubtitle = useMemo(() => {
    const parts: string[] = []
    if (filters.sourceType) parts.push(SOURCE_TYPE_LABELS[filters.sourceType] ?? filters.sourceType)
    if (filters.difficulty) parts.push(filters.difficulty)
    if (filters.module) parts.push(`module:"${filters.module}"`)
    if (!parts.length) return 'Showing all debt items'
    return `Filtered by ${parts.join(' · ')}`
  }, [filters])

  return (
    <div className="page-card">
      <div className="page-header">
        <div>
          <Typography.Title level={3} style={{ marginBottom: 4 }}>
            Debt List
          </Typography.Title>
          <Typography.Text type="secondary">
            {headerSubtitle} · Source: {reportPath}
          </Typography.Text>
        </div>
        <Typography.Text strong>{debts.length} items</Typography.Text>
      </div>

      <div className="filters-row">
        <Select
          allowClear
          style={{ minWidth: 180 }}
          placeholder="Source type"
          value={filters.sourceType}
          options={SOURCE_TYPE_OPTIONS}
          onChange={(value) => handleFilterChange('sourceType', value)}
        />
        <Select
          allowClear
          style={{ minWidth: 180 }}
          placeholder="Difficulty"
          value={filters.difficulty}
          options={DIFFICULTY_OPTIONS}
          onChange={(value) => handleFilterChange('difficulty', value)}
        />
        <Input.Search
          allowClear
          style={{ minWidth: 220 }}
          placeholder={modulePlaceholder}
          value={moduleInput}
          onChange={(event) => setModuleInput(event.target.value)}
          onSearch={handleModuleSearch}
          enterButton
        />
      </div>

      {error && (
        <Typography.Text type="danger" style={{ marginBottom: 12, display: 'inline-block' }}>
          {error}
        </Typography.Text>
      )}

      <Table<DebtItem>
        rowKey="id"
        columns={columns}
        dataSource={debts}
        loading={loading}
        pagination={{ pageSize: 12, showSizeChanger: false }}
        scroll={{ x: 900 }}
      />
    </div>
  )
}

export default ListPage
