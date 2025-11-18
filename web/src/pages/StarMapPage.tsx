import { Badge, Button, Empty, Space, Spin, Tag, Typography } from 'antd'
import * as echarts from 'echarts'
import { useEffect, useMemo, useRef, useState } from 'react'
import ReactECharts from 'echarts-for-react'

import { fetchDebtList, fetchStarMap } from '../services/api'
import { useReportPath } from '../hooks/useReportPath'
import type { DebtItem, StarMapData, StarMapNode } from '../types/analyzer'
import {
  CATEGORY_COLORS,
  DIFFICULTY_TAG_COLORS,
  SOURCE_TYPE_COLORS,
  SOURCE_TYPE_LABELS,
  STATUS_BADGE_STATUS,
} from '../constants/debt'

const humanize = (value?: string | null): string => {
  if (!value) {
    return 'N/A'
  }
  return value
    .replace(/[_\-]+/g, ' ')
    .split(' ')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ')
}

const pseudoRandom = (seed: string): number => {
  let hash = 0
  for (let i = 0; i < seed.length; i += 1) {
    hash = Math.imul(31, hash) + seed.charCodeAt(i)
    hash |= 0
  }
  const x = Math.sin(hash) * 10000
  return x - Math.floor(x)
}

const clamp = (value: number, min: number, max: number): number => Math.min(Math.max(value, min), max)

// Helper function to adjust color brightness
const adjustColorBrightness = (color: string, amount: number): string => {
  const hex = color.replace('#', '')
  const r = Math.max(0, Math.min(255, parseInt(hex.substring(0, 2), 16) + amount))
  const g = Math.max(0, Math.min(255, parseInt(hex.substring(2, 4), 16) + amount))
  const b = Math.max(0, Math.min(255, parseInt(hex.substring(4, 6), 16) + amount))
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

// Get category color (fine-grained)
const getCategoryColor = (category: string): string => {
  return CATEGORY_COLORS[category] ?? '#6366f1'
}

// Get beautiful priority-based color gradient
const getPriorityColor = (priority: number): string => {
  // Priority range: typically 0.5 - 3.0
  // Color gradient: Blue (low) → Cyan → Green → Yellow → Orange → Red (high)
  const normalized = Math.max(0, Math.min(1, (priority - 0.5) / 2.5))
  
  if (normalized < 0.2) {
    // Low priority: Cool blue to cyan
    return interpolateColor('#3b82f6', '#06b6d4', normalized / 0.2)
  } else if (normalized < 0.4) {
    // Medium-low: Cyan to green
    return interpolateColor('#06b6d4', '#10b981', (normalized - 0.2) / 0.2)
  } else if (normalized < 0.6) {
    // Medium: Green to yellow
    return interpolateColor('#10b981', '#fbbf24', (normalized - 0.4) / 0.2)
  } else if (normalized < 0.8) {
    // Medium-high: Yellow to orange
    return interpolateColor('#fbbf24', '#f97316', (normalized - 0.6) / 0.2)
  } else {
    // High priority: Orange to red
    return interpolateColor('#f97316', '#ef4444', (normalized - 0.8) / 0.2)
  }
}

// Interpolate between two hex colors
const interpolateColor = (color1: string, color2: string, factor: number): string => {
  const hex1 = color1.replace('#', '')
  const hex2 = color2.replace('#', '')
  
  const r1 = parseInt(hex1.substring(0, 2), 16)
  const g1 = parseInt(hex1.substring(2, 4), 16)
  const b1 = parseInt(hex1.substring(4, 6), 16)
  
  const r2 = parseInt(hex2.substring(0, 2), 16)
  const g2 = parseInt(hex2.substring(2, 4), 16)
  const b2 = parseInt(hex2.substring(4, 6), 16)
  
  const r = Math.round(r1 + (r2 - r1) * factor)
  const g = Math.round(g1 + (g2 - g1) * factor)
  const b = Math.round(b1 + (b2 - b1) * factor)
  
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

// Get final node color: prefer category; for unknown category, fall back to source_type color
const getNodeColor = (node: StarMapNode): string => {
  if (node.category === 'unknown') {
    return SOURCE_TYPE_COLORS[node.source_type] ?? getCategoryColor(node.category)
  }
  return getCategoryColor(node.category)
}

/**
 * Calculate node comprehensive importance
 * 
 * When using LLM-enhanced mode:
 * - Backend has accurately identified category, difficulty, is_blocker via LLM
 * - priority already considers risk_level(40%), impact(30%), interest(20%), cost(10%)
 * - is_blocker increases risk_level +1, auto-boosting priority
 * 
 * Frontend strategy:
 * 1. Use backend priority as base score
 * 2. Simple tasks +20% (quick wins)
 * 3. Complex tasks -25% (long-term investment)
 * 4. Keep category color differentiation
 */
const getDifficultyModifier = (difficulty: string): number => {
  const modifiers: Record<string, number> = {
    entry: 1.2,        // Simple tasks +20% priority
    intermediate: 1.0,
    advanced: 0.75,    // Complex tasks -25%
  }
  return modifiers[difficulty] ?? 1.0
}

// Calculate comprehensive importance: backend priority × difficulty modifier
const calculateNodeImportance = (node: StarMapNode): number => {
  const difficultyModifier = getDifficultyModifier(node.difficulty)
  // node.priority already includes risk_level (affected by is_blocker), impact, interest, etc.
  return node.priority * difficultyModifier
}

const StarMapPage = () => {
  const reportPath = useReportPath()
  const [data, setData] = useState<StarMapData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [debts, setDebts] = useState<DebtItem[]>([])
  const chartRef = useRef<echarts.ECharts | null>(null)
  const pointerCenterRef = useRef<[number, number]>([50, 50])
  const polarZoomRef = useRef(1)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [starMap, debtList] = await Promise.all([fetchStarMap(reportPath), fetchDebtList({}, reportPath)])
        setData(starMap)
        setDebts(debtList)
        // Don't auto-select any node - let all planets show their original colors
        // setSelectedId((prev) => prev ?? starMap.nodes[0]?.id ?? null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load star map')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [reportPath])

  const nodes = data?.nodes ?? []
  const openNodes = useMemo(() => nodes.filter((node) => node.status?.toLowerCase() === 'open'), [nodes])
  const visibleNodes = openNodes.length ? openNodes : nodes

  const polarPoints = useMemo(() => {
    if (!visibleNodes.length) {
      return { points: [], lookup: new Map<string, { radius: number; angle: number }>() }
    }

    // Calculate comprehensive importance for each node
    const nodesWithImportance = visibleNodes.map((node) => ({
      node,
      importance: calculateNodeImportance(node),
    }))

    // 🎯 新策略：基于相对重要性排名均匀分配半径
    // 按重要性排序（高到低）
    const sortedByImportance = [...nodesWithImportance].sort((a, b) => b.importance - a.importance)

    const innerRadius = 0.3
    const outerRadius = 6.5
    const totalNodes = sortedByImportance.length

    const lookup = new Map<string, { radius: number; angle: number }>()
    const points: Array<{ node: StarMapNode; radius: number; angle: number }> = []
    
    // 为每个节点分配唯一的相对位置（0到1之间）
    sortedByImportance.forEach((item, rankIndex) => {
      const { node } = item
      
      // 基于排名计算归一化位置（0=最重要，1=最不重要）
      const normalizedRank = totalNodes > 1 ? rankIndex / (totalNodes - 1) : 0
      
      // 计算基础半径：重要的在内圈，不重要的在外圈
      // 使用平方根函数让分布更均匀（避免外圈过于拥挤）
      const radiusRatio = Math.sqrt(normalizedRank)
      const baseRadius = innerRadius + radiusRatio * (outerRadius - innerRadius)
      
      // 添加小的随机扰动（避免完全重叠，但保持整体顺序）
      const radiusJitter = (pseudoRandom(`${node.id}-radius`) - 0.5) * 0.15
      const radius = Number(Math.max(innerRadius, Math.min(outerRadius, baseRadius + radiusJitter)).toFixed(3))
      
      // 计算角度：基于排名和类别
      // 使用黄金角（137.5度）分布，这是最均匀的角度分布方式
      const goldenAngle = 137.5
      const baseAngle = (rankIndex * goldenAngle) % 360
      
      // 添加类别聚集偏移
      const categoryOffset = (node.category.charCodeAt(0) % 8) * 5
      
      // 增强随机扰动，避免共线
      const jitter = (pseudoRandom(`${node.id}-angle`) - 0.5) * 20
      const nonlinearJitter = Math.sin(pseudoRandom(`${node.id}-nonlinear`) * Math.PI * 2) * 8
      const angle = (baseAngle + categoryOffset + jitter + nonlinearJitter + 3600) % 360

      lookup.set(node.id, { radius, angle })
      points.push({ node, radius, angle })
    })

    // 🌟 第二步：PR-Issue 星座式关联布局（让有连线的星球靠近，避免平行排列）
    const linkedPRs = new Set<string>()
    const linkedGroups: Array<{ pr: typeof points[0], issue: typeof points[0] }> = []
    
    points.forEach((point) => {
      if (point.node.source_type === 'pr' && point.node.reference_id) {
        const issueId = `issue:${point.node.reference_id}`
        const issuePoint = points.find(p => p.node.id === issueId)
        
        if (issuePoint) {
          linkedGroups.push({ pr: point, issue: issuePoint })
        }
      }
    })
    
    // 检测并避免平行排列（特别是 3 组平行的情况）
    linkedGroups.forEach((group, groupIndex) => {
      const { pr, issue } = group
      const targetAngle = issue.angle
      const targetRadius = issue.radius
      
      // 计算靠近的位置（极度紧密，形成超紧凑星座）
      // 角度范围：±6度（非常紧密）
      const baseOffset = (pseudoRandom(`${pr.node.id}-attract`) - 0.5) * 12
      // 组多样性偏移：减小到 ±5 度
      const groupDiversityOffset = (groupIndex % 3) * 5 - 5  // -5, 0, +5 度
      const attractAngle = targetAngle + baseOffset + groupDiversityOffset
      
      // 半径范围：±0.15（极小范围，几乎贴在一起）
      const radiusOffset = (pseudoRandom(`${pr.node.id}-r-attract`) - 0.5) * 0.3
      // 组半径偏移：减小到 ±0.08
      const groupRadiusOffset = ((groupIndex % 3) - 1) * 0.08  // -0.08, 0, +0.08
      const attractRadius = targetRadius + radiusOffset + groupRadiusOffset
      
      // 限制在合理范围内
      pr.angle = (attractAngle + 360) % 360
      pr.radius = Math.max(innerRadius, Math.min(outerRadius, attractRadius))
      
      // 更新 lookup
      lookup.set(pr.node.id, { radius: pr.radius, angle: pr.angle })
      linkedPRs.add(pr.node.id)
    })
    
    // 🌟 第三步：力导向防重叠优化（在保持优先级环的基础上微调，增加角度多样性）
    const iterations = 50  // 迭代次数
    const minDistance = 0.35  // 最小距离（防止重叠）
    const repulsionStrength = 0.08  // 排斥力强度
    const antiCollinearStrength = 0.15  // 反共线强度（增强）
    
    for (let iter = 0; iter < iterations; iter++) {
      const forces: Array<{ deltaRadius: number; deltaAngle: number }> = points.map(() => ({ 
        deltaRadius: 0, 
        deltaAngle: 0 
      }))
      
      // 计算排斥力和反共线力
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const p1 = points[i]
          const p2 = points[j]
          
          // 计算极坐标距离
          const dr = p1.radius - p2.radius
          const da = Math.min(
            Math.abs(p1.angle - p2.angle),
            360 - Math.abs(p1.angle - p2.angle)
          )
          const distance = Math.sqrt(dr * dr + (da / 60) ** 2)
          
          // 1. 如果太近，施加排斥力（但如果是连线关系则豁免）
          const isLinkedPair = linkedGroups.some(g => 
            (g.pr.node.id === p1.node.id && g.issue.node.id === p2.node.id) ||
            (g.pr.node.id === p2.node.id && g.issue.node.id === p1.node.id)
          )
          
          if (distance < minDistance && distance > 0.001 && !isLinkedPair) {
            const force = ((minDistance - distance) / distance) * repulsionStrength
            
            // 计算力的方向
            const angleForce = (p1.angle - p2.angle + 360) % 360 > 180 ? -1 : 1
            const radiusForce = dr > 0 ? 1 : -1
            
            forces[i].deltaAngle += angleForce * force * 10
            forces[i].deltaRadius += radiusForce * force * 0.3
            forces[j].deltaAngle -= angleForce * force * 10
            forces[j].deltaRadius -= radiusForce * force * 0.3
          }
          
          // 2. 反共线力：如果角度差很小（接近共线），增加角度扰动
          if (Math.abs(da) < 5 || Math.abs(da - 180) < 5) {
            // 接近 0 度或 180 度，可能共线
            const antiCollinearForce = antiCollinearStrength * (1 - Math.abs(da) / 180)
            forces[i].deltaAngle += (pseudoRandom(`${p1.node.id}-${p2.node.id}-anti`) - 0.5) * antiCollinearForce * 20
            forces[j].deltaAngle += (pseudoRandom(`${p2.node.id}-${p1.node.id}-anti`) - 0.5) * antiCollinearForce * 20
          }
        }
      }
      
      // 应用力（对于有连线的节点大幅减小移动幅度，保持紧密星座）
      points.forEach((point, i) => {
        const isLinked = linkedPRs.has(point.node.id)
        const damping = isLinked ? 0.15 : 0.6  // 有连线的节点移动幅度极小（从0.3减至0.15）
        
        point.angle = (point.angle + forces[i].deltaAngle * damping + 360) % 360
        point.radius = Math.max(
          innerRadius, 
          Math.min(outerRadius, point.radius + forces[i].deltaRadius * damping)
        )
        
        lookup.set(point.node.id, { radius: point.radius, angle: point.angle })
      })
    }
    
    return { points, lookup }
  }, [visibleNodes])

  const selectedNode = visibleNodes.find((node) => node.id === selectedId) ?? null
  const selectedDebt = selectedId ? debts.find((debt) => debt.id === selectedId) ?? null : null

  const constellationLinks = useMemo(() => {
    const connections: Array<{ from: string; to: string; distance: number; type: 'reference' | 'proximity' }> = []

    // console.log('Building constellation links...')
    // console.log('Total points:', polarPoints.points.length)

    // Build connections: 1. PR-Issue strong association  2. Same-category proximity
    let prIssueLinks = 0
    for (const point of polarPoints.points) {
      if (point.node.source_type === 'pr' && point.node.reference_id) {
        const issueId = `issue:${point.node.reference_id}`
        if (polarPoints.lookup.has(issueId)) {
          connections.push({
            from: point.node.id,
            to: issueId,
            distance: 0.1,  // Highest priority
            type: 'reference'
          })
          prIssueLinks++
        }
      }
    }
    // console.log('PR-Issue links created:', prIssueLinks)

    // Same-category proximity connections (constellation auxiliary lines)
    for (let i = 0; i < polarPoints.points.length; i++) {
      for (let j = i + 1; j < polarPoints.points.length; j++) {
        const p1 = polarPoints.points[i]
        const p2 = polarPoints.points[j]

        // Calculate polar coordinate distance
        const dr = Math.abs(p1.radius - p2.radius)
        const da = Math.min(
          Math.abs(p1.angle - p2.angle),
          360 - Math.abs(p1.angle - p2.angle)
        )
        const distance = Math.sqrt(dr * dr + (da / 60) ** 2)

        // Build ID-to-index mapping for PR-Issue connections
        const hasReference = connections.some(
          c => (c.from === p1.node.id && c.to === p2.node.id) ||
               (c.from === p2.node.id && c.to === p1.node.id)
        )

        if (!hasReference && p1.node.category === p2.node.category && distance < 0.6) {
          connections.push({
            from: p1.node.id,
            to: p2.node.id,
            distance,
            type: 'proximity'
          })
        }
      }
    }

    // Sort by distance, prioritize closer connections
    const sorted = connections.sort((a, b) => a.distance - b.distance).slice(0, 50)
    return sorted
  }, [polarPoints.points])

  // Performance: Removed auto-select useEffect that caused continuous re-renders
  // User can click to select nodes instead

  const chartOption = useMemo(() => {
    if (!visibleNodes.length) {
      return {}
    }

    // Performance: Chart option memoized
    const neighborIds = new Set<string>()
    if (selectedNode) {
      constellationLinks.forEach((conn) => {
        if (conn.from === selectedNode.id) neighborIds.add(conn.to)
        if (conn.to === selectedNode.id) neighborIds.add(conn.from)
      })
    }

    const scatterData = polarPoints.points.map(({ node, radius, angle }) => {
      // Calculate priority-based color (beautiful gradient from blue to red)
      const priority = node.priority  // Already a number (total value)
      const categoryColor = getPriorityColor(priority)
      
      // Calculate size based on difficulty level (string)
      // entry < intermediate < advanced (smaller sizes to reduce overlap)
      const difficultySizeMap: Record<string, number> = {
        entry: 35,
        intermediate: 52,
        advanced: 70,
      }
      const baseSize = difficultySizeMap[node.difficulty] ?? 50

      // Focus highlighting
      const isSelected = !!selectedNode && node.id === selectedNode.id
      const isNeighbor = !!selectedNode && neighborIds.has(node.id)

      let visualColor = categoryColor
      if (selectedNode) {
        if (isSelected) {
          visualColor = categoryColor
        } else if (isNeighbor) {
          visualColor = adjustColorBrightness(categoryColor, 12)
        } else {
          visualColor = adjustColorBrightness(categoryColor, -48)
        }
      }

      const finalSize = isSelected ? baseSize + 6 : baseSize

      // Check if assignees is a valid array with actual values (force boolean type)
      const hasAssignee =
        Array.isArray(node.assignees) &&
        node.assignees.length > 0 &&
        !!node.assignees[0] &&
        node.assignees[0].trim() !== ''
      
      // Extract PR/Issue number for display
      const referenceId = node.reference_id || ''
      const prefix = node.source_type === 'pr' ? 'PR' : node.source_type === 'issue' ? 'IS' : ''
      const displayText = referenceId ? `${prefix}${referenceId}` : ''
      
      // Calculate adaptive font size based on text length
      let labelFontSize = baseSize * 0.28  // Base size
      if (displayText.length > 5) {
        labelFontSize = baseSize * 0.22  // Smaller for longer IDs
      } else if (displayText.length > 3) {
        labelFontSize = baseSize * 0.25
      }
      
      return {
        value: [radius, angle], // ECharts polar uses [radius, angle]
        symbolSize: finalSize,
        name: node.label,
        itemStyle: {
          color: visualColor,
          // White thick border for nodes with assignees
          borderColor: hasAssignee ? '#f8fafc' : adjustColorBrightness(visualColor, 30),
          borderWidth: hasAssignee ? 6 : 3,
          shadowBlur: 0,  // Disabled for performance
          shadowColor: 'transparent',
        },
        // Show PR/Issue number in planet center
        label: {
          show: !!displayText,
          formatter: displayText,
          fontSize: labelFontSize,
          fontWeight: '600',
          color: '#ffffff',
          textBorderColor: 'rgba(0,0,0,0.5)',
          textBorderWidth: 1.5,
        },
        emphasis: {
          disabled: false,
          scale: false,
          itemStyle: {
            shadowBlur: 0,  // Disabled for performance
            borderWidth: hasAssignee ? 8 : 4,
          },
          label: {
            show: !!displayText,
            fontSize: labelFontSize * 1.1,  // Slight increase
            fontWeight: 'bold',
          },
        },
        node,
        hasAssignee,  // Store for later use
      }
    })
    
    // Debug: Scatter data generation complete (logs disabled for performance)
    
    // No longer need separate ring layer - rings are now part of the planet SVG

    // Set style based on connection type and distance
    const lineData = constellationLinks.map((conn) => {
      const fromPos = polarPoints.lookup.get(conn.from)
      const toPos = polarPoints.lookup.get(conn.to)
      
      if (!fromPos || !toPos) {
        console.warn('Missing position for connection:', conn)
        return null
      }

      const isReference = conn.type === 'reference'
      const isDirectlyConnected =
        !!selectedNode && (conn.from === selectedNode.id || conn.to === selectedNode.id)

      // Improved visibility for dark background
      const baseOpacity = isReference ? 1 : Math.max(0.65, 1 - conn.distance / 0.6)
      const finalOpacity = selectedNode ? (isDirectlyConnected ? baseOpacity : 0.45) : baseOpacity
      const width = isReference ? (isDirectlyConnected ? 4 : 2.5) : 2.5
      const color = isReference
        ? `rgba(251, 191, 36, ${finalOpacity})`  // PR-Issue: golden
        : `rgba(226, 232, 240, ${finalOpacity})`  // Same-category: bright gray

      return {
        coords: [
          [fromPos.radius, fromPos.angle],
          [toPos.radius, toPos.angle],
        ],
        lineStyle: {
          color,
          width,
          shadowBlur: 0,  // Completely disabled
          shadowColor: 'transparent',
        },
      }
    }).filter((item): item is NonNullable<typeof item> => item !== null)
    
    // console.log('Line data generated:', lineData.length)

    const activePoint = selectedNode
      ? [
          {
            value: [
              polarPoints.lookup.get(selectedNode.id)?.radius ?? 2.5,
              polarPoints.lookup.get(selectedNode.id)?.angle ?? 0,
            ],
            symbolSize: Math.max(20, selectedNode.size + 6),
            itemStyle: {
              color: getNodeColor(selectedNode),
              shadowBlur: 0,
              shadowColor: 'transparent',
            },
          },
        ]
      : []

    return {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 200,  // Very fast initial render
      animationEasing: 'linear',  // Linear is faster than cubicOut
      animationDurationUpdate: 300,  // Slightly longer for updates
      dataZoom: [],
      tooltip: {
        show: true,
        confine: true,
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        borderWidth: 0,
        padding: 10,
        textStyle: { fontSize: 12, color: '#f8fafc' },
        extraCssText: 'box-shadow:0 12px 30px rgba(2,6,23,0.45);border-radius:12px;',
        transitionDuration: 0.1,  // Fast tooltip transition
        formatter: (params: { data?: { node?: StarMapNode } }) => {
          const node = params.data?.node
          if (!node) return ''
          return `
            <div style="min-width:160px;display:flex;flex-direction:column;gap:4px;">
              <strong style="font-size:13px;">${node.label}</strong>
              <span style="font-size:11px;color:#cbd5f5;">${humanize(node.module)}</span>
              <span style="font-size:11px;">${humanize(node.source_type)} · Score ${node.priority.toFixed(1)}</span>
            </div>
          `
        },
      },
      // Polar coordinate system for StarMap (maximized for best visibility)
      polar: {
        center: ['50%', '50%'],
        radius: ['2%', '97%'],
      },
      angleAxis: {
        type: 'value',
        startAngle: 90,
        min: 0,
        max: 360,
        splitNumber: 12,  // 分隔数
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: false },
        splitLine: {
          show: false,  // 完全隐藏射线，让背景更简洁
        },
      },
      radiusAxis: {
        min: 0,
        max: 7,
        splitNumber: 7,
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: false },
        splitLine: {
          show: true,
          lineStyle: {
            // 渐变发光同心圆
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: 'rgba(99, 102, 241, 0.3)' },   // 内圈：蓝紫光晕
              { offset: 0.5, color: 'rgba(139, 92, 246, 0.2)' }, // 中圈：紫色
              { offset: 1, color: 'rgba(168, 85, 247, 0.1)' }    // 外圈：淡紫
            ]),
            width: 1.5,
            shadowBlur: 8,
            shadowColor: 'rgba(139, 92, 246, 0.4)',
          },
        },
        splitArea: {
          show: true,
          areaStyle: {
            // 渐变背景环
            color: [
              'rgba(30, 41, 59, 0.15)',   // 深色
              'rgba(51, 65, 85, 0.08)',   // 中色
            ],
          },
        },
      },

      series: [
        // Connection lines between nodes
        {
          type: 'lines',
          coordinateSystem: 'polar',
          data: lineData,
          lineStyle: {
            color: 'rgba(255, 200, 100, 0.6)',
            width: 2,
            shadowBlur: 0,  // Disabled
            shadowColor: 'transparent',
            type: 'solid',
          },
          symbol: 'none',
          silent: true,
          zlevel: 1,
          smooth: true,
        },
        // Main planet nodes on polar coordinate system
        {
          type: 'scatter',
          coordinateSystem: 'polar',
          symbol: 'circle',  // Use native circle symbol for reliable rendering
          zlevel: 2,
          data: scatterData,
          cursor: 'pointer',
          animation: true,
          animationDuration: 300,  // Further reduced
          animationEasing: 'linear',  // Linear for speed
          emphasis: {
            focus: 'none',  // Don't blur other items on hover
            scale: false,   // Disable scale animation completely
          }
        },
        // Selected node ripple effect
        ...(activePoint.length
          ? [
              {
                type: 'effectScatter',
                coordinateSystem: 'polar',
                rippleEffect: { 
                  brushType: 'stroke', 
                  scale: 2.5,  // Slightly smaller
                  period: 2,   // Faster ripple
                },
                data: activePoint,
                zlevel: 3,
                animation: false,  // No animation for ripple
              },
            ]
          : []),
      ],
    }
  }, [visibleNodes, polarPoints, selectedNode, constellationLinks])

  const handleChartReady = (instance: echarts.ECharts) => {
    chartRef.current = instance
    
    // Force GPU acceleration and performance optimization
    const canvas = instance.getDom().querySelector('canvas') as HTMLCanvasElement
    if (canvas) {
      // Force hardware acceleration via CSS
      canvas.style.transform = 'translate3d(0,0,0)'
      canvas.style.willChange = 'transform'
      
      const ctx = canvas.getContext('2d', { 
        alpha: true,
        desynchronized: true,  // Reduce latency
      })
      if (ctx) {
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'low'
      }
      
      console.log('[PERF] Canvas optimized:', {
        width: canvas.width,
        height: canvas.height,
        transform: canvas.style.transform,
        willChange: canvas.style.willChange,
      })
    }
  }

  useEffect(() => {
    const chart = chartRef.current
    if (!chart) return
    const dom = chart.getDom() as HTMLDivElement

    const handlePointerMove = (event: MouseEvent) => {
      const rect = dom.getBoundingClientRect()
      const xPercent = clamp(((event.clientX - rect.left) / rect.width) * 100, 5, 95)
      const yPercent = clamp(((event.clientY - rect.top) / rect.height) * 100, 5, 95)
      pointerCenterRef.current = [xPercent, yPercent]
    }

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault()
      const delta = event.deltaY
      const factor = delta > 0 ? 1.08 : 0.92
      const nextZoom = clamp(polarZoomRef.current * factor, 0.6, 2.4)
      polarZoomRef.current = nextZoom
      const [pointerX, pointerY] = pointerCenterRef.current
      const lerp = 0.4
      const targetCenterX = clamp(50 + (pointerX - 50) * lerp, 25, 75)
      const targetCenterY = clamp(50 + (pointerY - 50) * lerp, 25, 75)
      chart.setOption(
        {
          polar: {
            center: [targetCenterX, targetCenterY],
            radius: ['2%', `${clamp(97 * nextZoom, 65, 160)}%`],
          },
        },
        false,
        true,
      )
    }

    dom.addEventListener('mousemove', handlePointerMove)
    dom.addEventListener('wheel', handleWheel, { passive: false })

    return () => {
      dom.removeEventListener('mousemove', handlePointerMove)
      dom.removeEventListener('wheel', handleWheel)
    }
  }, [visibleNodes.length])

  const chartEvents = useMemo(
    () => ({
      click: (params: { data?: { node?: StarMapNode } }) => {
        const node = params.data?.node
        if (node) {
          setSelectedId(node.id)
        }
      },
      dblclick: (params: { data?: { node?: StarMapNode } }) => {
        const node = params.data?.node
        if (node?.html_url) {
          window.open(node.html_url, '_blank', 'noopener')
        }
      },
      mouseover: (params: { data?: { node?: StarMapNode } }) => {
        const t0 = performance.now()
        // Hover processing
        const t1 = performance.now()
        if (t1 - t0 > 16) {  // >16ms = below 60fps
          console.warn(`[PERF] Slow hover: ${(t1 - t0).toFixed(1)}ms`)
        }
      },
    }),
    [],
  )

  return (
    <div className="page-card">
      <div className="page-header">
        <div>
          <Typography.Title level={3} style={{ marginBottom: 4 }}>
            Project Task StarMap
          </Typography.Title>
          <Typography.Text type="secondary">
            {data?.metadata?.description ?? 'Higher-priority tasks sit closer to the center.'} · Source: {reportPath}
          </Typography.Text>
        </div>
        <Typography.Text strong>
          {visibleNodes.length} open items{openNodes.length === 0 && nodes.length ? ` · total ${nodes.length}` : ''}
        </Typography.Text>
      </div>

      {error && <Typography.Text type="danger">{error}</Typography.Text>}

      {loading ? (
        <div style={{ width: '100%', textAlign: 'center', padding: '64px 0' }}>
          <Spin size="large" tip="Loading star map ...">
            <div style={{ minHeight: 200 }} />
          </Spin>
        </div>
      ) : visibleNodes.length === 0 ? (
        <Empty description="No StarMap nodes available" />
      ) : (
        <div className="star-map-grid">
          <div className="star-map-panel" style={{ position: 'relative' }}>
            {/* 星空背景 */}
            <div 
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `
                  radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 25%),
                  radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.06) 0%, transparent 25%),
                  radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.04) 0%, transparent 50%),
                  radial-gradient(2px 2px at 15% 20%, rgba(255,255,255,0.5) 0%, transparent 100%),
                  radial-gradient(2px 2px at 85% 15%, rgba(255,255,255,0.4) 0%, transparent 100%),
                  radial-gradient(1px 1px at 25% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),
                  radial-gradient(1px 1px at 75% 80%, rgba(255,255,255,0.3) 0%, transparent 100%),
                  radial-gradient(1px 1px at 45% 25%, rgba(255,255,255,0.4) 0%, transparent 100%),
                  radial-gradient(1px 1px at 65% 45%, rgba(255,255,255,0.3) 0%, transparent 100%),
                  radial-gradient(2px 2px at 35% 75%, rgba(255,255,255,0.5) 0%, transparent 100%),
                  radial-gradient(1px 1px at 90% 40%, rgba(255,255,255,0.3) 0%, transparent 100%),
                  radial-gradient(1px 1px at 10% 85%, rgba(255,255,255,0.4) 0%, transparent 100%),
                  radial-gradient(1px 1px at 55% 10%, rgba(255,255,255,0.3) 0%, transparent 100%),
                  linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)
                `,
                pointerEvents: 'none',
                zIndex: 0,
              }}
            />
            <ReactECharts
              echarts={echarts}
              option={chartOption}
              notMerge={false}
              lazyUpdate={true}
              opts={{ 
                renderer: 'canvas',
                devicePixelRatio: 1,  // Force 1:1 ratio for better performance
                width: 'auto',
                height: 'auto',
              }}
              style={{ height: '100%', minHeight: 1400, width: '100%', position: 'relative', zIndex: 1 }}
              onEvents={chartEvents}
              onChartReady={handleChartReady}
            />
          </div>
          <div className="star-map-details">
            {selectedNode ? (
              <div style={{ width: '100%' }}>
                <div className="details-header">
                  <div>
                    <Typography.Title level={4} style={{ marginBottom: 0 }}>
                      {selectedNode.label}
                    </Typography.Title>
                    <Typography.Text type="secondary">
                      {humanize(selectedNode.module)} · {SOURCE_TYPE_LABELS[selectedNode.source_type]}
                    </Typography.Text>
                  </div>
                  {selectedDebt?.html_url && (
                    <Button
                      className="details-link"
                      size="small"
                      ghost
                      href={selectedDebt.html_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View on GitHub
                    </Button>
                  )}
                </div>

                <div className="details-description">
                  <h5>Context</h5>
                  <Typography.Paragraph style={{ marginBottom: 0 }}>
                    {selectedDebt?.description?.trim() || 'No description provided.'}
                  </Typography.Paragraph>
                </div>

                <div className="details-metric-grid">
                  <div className="metric-card accent">
                    <div className="details-label">Priority Score</div>
                    <div className="details-value">{selectedNode.priority.toFixed(1)}</div>
                  </div>
                  <div className="metric-card">
                    <div className="details-label">Status</div>
                    <div className="details-value">
                      <Badge
                        status={STATUS_BADGE_STATUS[selectedNode.status] ?? 'default'}
                        text={<span style={{ color: '#f8fafc' }}>{humanize(selectedNode.status)}</span>}
                      />
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="details-label">Difficulty</div>
                    <Tag color={DIFFICULTY_TAG_COLORS[selectedNode.difficulty] ?? 'default'}>
                      {humanize(selectedNode.difficulty)}
                    </Tag>
                  </div>
                  <div className="metric-card">
                    <div className="details-label">Impact Scope</div>
                    <div className="details-value">{humanize(selectedDebt?.impact_scope)}</div>
                  </div>
                  <div className="metric-card">
                    <div className="details-label">Risk Level</div>
                    <div className="details-value">
                      {selectedDebt?.risk_level ? `Level ${selectedDebt.risk_level}` : 'Unknown'}
                    </div>
                  </div>
                </div>

                <div className="details-section details-assignees">
                  <div className="details-label">Assignees</div>
                  <div className="details-value">
                    {selectedNode.assignees.length ? (
                      <Space wrap>
                        {selectedNode.assignees.map((person) => (
                          <Tag key={person}>{person}</Tag>
                        ))}
                      </Space>
                    ) : (
                      <Typography.Text type="secondary">Unassigned</Typography.Text>
                    )}
                  </div>
                </div>

                {selectedNode.recommendation && (
                  <div className="details-section">
                    <div className="details-label">💡 Recommendation</div>
                    <div 
                      style={{
                        background: 'rgba(99, 102, 241, 0.1)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        borderRadius: '12px',
                        padding: '12px 16px',
                        marginTop: '8px',
                        fontSize: '14px',
                        lineHeight: '1.6',
                        color: '#cbd5e1',
                      }}
                    >
                      {selectedNode.recommendation}
                    </div>
                  </div>
                )}

                <div className="details-section details-skills">
                  <div className="details-label">Skills</div>
                  <Space wrap>
                    {selectedNode.skills.length ? (
                      selectedNode.skills.map((skill) => (
                        <Tag key={skill}>{skill}</Tag>
                      ))
                    ) : (
                      <Typography.Text type="secondary">No skill tags</Typography.Text>
                    )}
                  </Space>
                </div>
              </div>
            ) : (
              <Empty description="Select a node to inspect details" />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default StarMapPage
