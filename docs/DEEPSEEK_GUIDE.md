# DeepSeek LLM 集成指南

## 为什么选择 DeepSeek？

### 对比 OpenAI

| 特性 | OpenAI (gpt-4o-mini) | DeepSeek (deepseek-chat) |
|------|---------------------|-------------------------|
| **速率限制** | 3 RPM (免费层) | 60 RPM (免费层) |
| **价格** | $0.15/1M tokens | $0.14/1M tokens |
| **质量** | 优秀 | 优秀 (接近 GPT-4) |
| **延迟** | 中等 | 低 |
| **中文支持** | 良好 | 优秀 |

**对于本项目**：
- 分析 46 个 open issues
- OpenAI: 需要 15+ 分钟（速率限制）
- **DeepSeek: 只需 2-3 分钟** ✅

---

## 快速开始

### 1. 获取 DeepSeek API Key

访问 [DeepSeek 平台](https://platform.deepseek.com/)：
1. 注册账号
2. 进入 API Keys 页面
3. 创建新的 API Key
4. 复制密钥

### 2. 设置环境变量

**Windows PowerShell:**
```powershell
$env:DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

**永久设置 (推荐)**：
- Windows: 系统属性 → 环境变量
- Linux/Mac: 添加到 `~/.bashrc` 或 `~/.zshrc`

### 3. 运行分析

```bash
# 使用 DeepSeek (推荐)
python -m cli.main analyze \
  --raw surfsense-raw.json \
  --output surfsense-report.json \
  --use-llm \
  --llm-provider deepseek

# 或使用 OpenAI (如果你有更高的速率限制)
python -m cli.main analyze \
  --raw surfsense-raw.json \
  --output surfsense-report.json \
  --use-llm \
  --llm-provider openai
```

---

## 完整工作流程

### Step 1: 扫描项目

```bash
cd F:\Github-TideScope\TideScope-main

python -m cli.main scan \
  --config config/surfsense.quick.yaml \
  --output surfsense-raw.json \
  --mode quick
```

**输出示例**：
```
✓ Scan completed
  - 155 Issues
  - 308 Pull Requests
```

### Step 2: 使用 DeepSeek 分析

```bash
# 设置 API Key
$env:DEEPSEEK_API_KEY="sk-xxx"

# 运行分析
python -m cli.main analyze \
  --raw surfsense-raw.json \
  --output surfsense-report.json \
  --use-llm \
  --llm-provider deepseek
```

**实时进度显示**：
```
INFO Processing 0 code TODOs...
INFO Processing 46 open issues with LLM (skipping 109 closed)...
INFO [1/46] Analyzing issue #288: [FEATURE] Add a metabase connector...
INFO [2/46] Analyzing issue #474: [BUG] Cannot Register or Log In...
...
INFO [46/46] Analyzing issue #41: Encrypt stored API tokens...
INFO Completed processing 46 issues
INFO Processing 308 pull requests...
✓ Analysis completed
```

### Step 3: 启动可视化

```bash
# 启动后端
cd F:\Github-TideScope\TideScope-main
uvicorn api.main:app --reload

# 另开终端启动前端
cd F:\Github-TideScope\TideScope-main\web
npm run dev
```

访问 http://localhost:4173 查看 StarMap！

---

## 优化策略

### 智能分析范围

系统**自动优化**以节省成本和时间：

1. ✅ **只分析开放的 Issues**
   - 关闭的 issues 使用关键词匹配（秒级）
   - 开放的 issues 使用 LLM 分析（更准确）

2. ✅ **跳过 Pull Requests**
   - PR 通常不需要复杂分类
   - 使用简单规则推断即可

3. ✅ **并发控制**
   - 2 个并发请求避免速率限制
   - 自动重试失败的请求

### 预期效果

**46 个开放 issues**：
```
├─ LLM 成功: ~40-45 个 (87-98%)
├─ LLM 失败: ~1-6 个 (回退到关键词匹配)
└─ 总耗时: 2-3 分钟
```

**成本估算**：
```
46 issues × 平均 300 tokens = 13,800 tokens
13,800 tokens ÷ 1,000,000 × $0.14 = $0.002 (约 0.2 分钱)
```

---

## 验证结果

运行验证脚本：

```bash
python check_llm.py
```

**预期输出**（DeepSeek 成功）：
```
=== LLM Analysis Stats ===
With skills (LLM success): 40-45
Without skills (LLM failed/skipped): 1-6
Success rate: 87-98%

=== LLM Success Examples ===
1. [BUG] Cannot Register or Log In...
   Category: maintainability | Difficulty: intermediate
   Skills: ['Docker', 'Web Development', 'Database Management']
   Risk: 3 | Priority: 1.25

=== Category Distribution ===
  feature: 30-35
  maintainability: 8-12
  security: 3-5
  performance: 2-4
  unknown: 1-5  ← 显著减少！
```

---

## 故障排查

### 问题 1: `DEEPSEEK_API_KEY not found`

**解决方案**：
```powershell
# 确认环境变量设置
echo $env:DEEPSEEK_API_KEY

# 如果为空，重新设置
$env:DEEPSEEK_API_KEY="sk-xxx"
```

### 问题 2: 速率限制（429 错误）

DeepSeek 免费层：60 RPM
- 当前并发：2
- 理论最大：120 次/分钟（足够）

如果仍然遇到：
1. 检查是否有其他程序在调用 DeepSeek API
2. 等待 1 分钟后重试

### 问题 3: 连接超时

```bash
# 检查网络连接
curl https://api.deepseek.com

# 如果失败，可能需要代理
```

---

## 高级配置

### 使用自定义模型

```bash
python -m cli.main analyze \
  --raw surfsense-raw.json \
  --output surfsense-report.json \
  --use-llm \
  --llm-provider deepseek \
  --llm-model deepseek-coder  # 专门优化代码理解
```

### 批量分析多个项目

```bash
# 创建批处理脚本
for project in project1 project2 project3; do
  python -m cli.main analyze \
    --raw ${project}-raw.json \
    --output ${project}-report.json \
    --use-llm \
    --llm-provider deepseek
done
```

---

## 最佳实践

1. **首次分析使用 DeepSeek**
   - 建立准确的基线数据
   - 成本低且速度快

2. **定期更新分析**
   - 每周/每月重新扫描
   - 只分析新增的开放 issues

3. **关键项目使用 LLM**
   - 安全性项目
   - 高优先级 bugs
   - 复杂的技术债务

4. **组合使用**
   - 日常：关键词匹配（快速）
   - 重要决策：DeepSeek 分析（准确）

---

## 技术细节

### API 兼容性

DeepSeek 使用 OpenAI SDK，完全兼容：

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    response_format={"type": "json_schema", "json_schema": schema}
)
```

### 并发处理

```python
# 使用线程池并发处理
max_workers = 2  # 避免速率限制
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(analyze_issue, issue) for issue in issues]
    for future in as_completed(futures):
        result = future.result(timeout=30)
```

---

## 总结

✅ **推荐配置**：
- Provider: **DeepSeek**
- Model: `deepseek-chat`（自动选择）
- 成本: ~$0.002 per 50 issues
- 速度: 2-3 分钟 per 50 issues

🚀 **立即开始**：
```bash
$env:DEEPSEEK_API_KEY="your-key"
python -m cli.main analyze --raw surfsense-raw.json --output surfsense-report.json --use-llm --llm-provider deepseek
```
