# LLM 增强模式使用指南

## 概述

TideScope 支持使用 OpenAI GPT 模型来增强任务分析的准确性。LLM 会自动分析每个 Issue 的标题和描述，准确识别：

- **Category**：security, performance, maintainability, testing, ci, feature, documentation
- **Difficulty**：entry, intermediate, advanced
- **Skills**：所需技能列表（最多3个）
- **is_blocker**：是否阻塞项目运行或导致数据丢失

## 启用 LLM 模式

### 1. 设置 API Key

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 2. 运行分析

```bash
# 首先扫描项目（如已完成可跳过）
tidescope scan --config config/tidescope.config.yaml --output tidescope-raw.json

# 使用 LLM 模式分析
tidescope analyze --raw tidescope-raw.json --output tidescope-report.json --use-llm

# 可选：指定模型（默认 gpt-4o-mini）
tidescope analyze --raw tidescope-raw.json --output tidescope-report.json --use-llm --llm-model gpt-4o
```

## LLM 如何改进优先级

### 后端增强

LLM 分析会影响优先级计算的核心参数：

1. **risk_level**（权重 40%）
   - 基础风险值由 category 决定（security=5, performance=4...）
   - **is_blocker=true 时风险值 +1**
   - 阻塞性 bug 自动获得最高风险等级

2. **准确的 category 识别**
   - 不再依赖关键词匹配，避免误判
   - 复杂描述也能准确分类

3. **智能 difficulty 评估**
   - 基于任务复杂度而非简单的字数统计
   - 考虑技术栈和实现难度

### 前端优化

StarMap 前端使用后端计算好的 priority 值：

```typescript
// node.priority 已包含：
// - risk_level (40%) - 受 is_blocker 影响
// - impact (30%)
// - interest (20%)
// - cost (10%)

importance = priority × difficultyModifier
```

**Difficulty Modifier**：
- 简单任务（entry）：×1.2 - 快速见效，优先处理
- 中等任务（intermediate）：×1.0
- 复杂任务（advanced）：×0.75 - 需长期投入，相对延后

## 效果对比

### 不使用 LLM

- Category 基于关键词匹配，可能不准确
- 例如："优化数据库查询速度" 可能被误判为 `feature` 而非 `performance`
- Difficulty 仅基于描述长度

### 使用 LLM

- 准确识别："优化数据库查询速度" → `performance`
- 阻塞性问题自动标记：is_blocker=true → risk_level +1
- 智能评估复杂度：考虑技术栈、依赖关系

## StarMap 可视化改进

启用 LLM 后，StarMap 将更加合理：

- **安全漏洞 + 阻塞性**：紧贴圆心（最高优先级）
- **性能问题（简单修复）**：中心区域
- **新功能（复杂实现）**：外围区域
- **文档更新**：最外围

## 成本控制

- 默认使用 `gpt-4o-mini`，每个 Issue 约 $0.0001-0.0005
- 100 个 Issue 分析成本约 $0.01-0.05
- 仅在 `analyze` 阶段调用，不影响 `scan` 性能

## 最佳实践

1. **首次分析使用 LLM**：建立准确的基线
2. **增量更新可选用 LLM**：新 Issue 较少时性价比高
3. **关键项目强烈推荐**：安全性、金融、医疗等领域

## 隐私说明

- 仅发送 Issue 标题和描述到 OpenAI API
- 不包含代码内容、敏感信息
- 符合 OpenAI 隐私政策
