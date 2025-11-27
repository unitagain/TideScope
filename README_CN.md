<div align="center">
  <img src="web/public/logo-option-1.svg" alt="TideScope Logo" width="560"/>
  
  <p><strong>让技术债务可视化，让开源协作更简单</strong></p>
  
  <p>
    <a href="README.md">English</a>
    &nbsp;|&nbsp;
    <a href="#快速开始">快速开始</a>
    &nbsp;|&nbsp;
    <a href="#技术栈">技术栈</a>
    &nbsp;|&nbsp;
    <a href="#贡献指南">贡献</a>
  </p>
</div>

---

## 💫 项目初衷

作为**初学者**，看到一个你很感兴趣的开源项目，你是否纠结于不知道能为它做些什么？从哪里开始贡献？

作为**开源项目维护者**，面对大量的 PR 和 Issue，你是否会对任务的优先级排序和技术债务管理感到困扰？

**TideScope** 受到星系图的启发，通过**扫描 GitHub 仓库中的 Issue、PR 和代码 TODO 注释**，结合 **LLM 智能分析**提取所需技能和难度评估，最终生成一张直观的**技术债务星图**。让每个任务如同星辰一般，在极坐标系中按重要性由内向外分布，相关联的 PR-Issue 形成星座般的视觉聚类。

我希望通过这个**新颖的可视化方式**，帮助：
- 🌱 **新贡献者** 快速找到适合自己技能水平的任务
- 🎯 **项目维护者** 一目了然地掌握技术债务全局
- 🤝 **团队协作** 更加高效、透明、有序

---

## ✨ 核心特性

### 🌌 星图可视化
- **基于排名的黄金角螺旋布局** - 使用数学优化的分布算法，确保节点均匀分布
- **力导向防重叠机制** - 智能排斥算法防止节点碰撞，保持图表清晰
- **星座式聚类** - PR 与 Issue 自动形成紧密的星座群，直观展示关联关系
- **渐变发光效果** - 现代化的视觉设计，深色主题优化

### 🧠 智能分析
- **LLM 技能提取** - 自动分析任务所需的技术栈和技能点
- **多维度评分** - 优先级、难度、影响范围、风险等级综合评估
- **智能推荐** - 为每个任务生成针对性的实施建议
- **自动上下文** - 自动获取项目 README 作为分析背景

### 🎯 开发者友好
- **一键扫描** - 支持本地代码和 GitHub 远程仓库
- **灵活配置** - YAML 配置文件，轻松定制扫描规则
- **双界面** - Web UI + CLI 命令行，满足不同使用场景

---

## 🎨 双系统架构

TideScope 提供**两大核心系统**，满足不同场景的需求：

### 1️⃣ Badge System（徽章系统）- 新贡献者的最佳入口

**核心价值：** 降低开源贡献门槛，让新手快速找到适合的任务
![IMG_20251127_150637](https://github.com/user-attachments/assets/372d0475-1068-4ba4-95ac-405e678f2ff0)


#### 🎯 系统特点

- **📊 项目健康仪表盘**
  - 实时健康度评分（0-100）
  - 项目活跃度趋势分析
  - Open Issues 和 PR 统计

- **🎖️ AI 推荐任务徽章**
  - 自动生成精美的 SVG 徽章
  - 显示推荐任务的标题、难度、技能
  - 一键跳转到 GitHub Issue

- **🌱 新手友好任务列表**
  - 筛选适合初学者的 Issues
  - 按难度和技能分类
  - 包含详细的实施建议

- **📝 自动生成 CONTRIBUTING.md**
  - AI 分析项目生成贡献指南
  - 包含项目健康度、推荐任务、技能分布
  - 美观的 Markdown 格式，支持 GitHub 展示

#### 🔧 技术实现

**工作流程：**
```
GitHub API → 数据获取 → LLM/规则分析 → SVG 生成 → Markdown 渲染
```

**核心组件：**
1. **`analyzer/smart_analyzer.py`** - 智能分析器
   - 自动选择 LLM 或规则分析
   - 提取 Issue 所需技能
   - 评估任务难度和优先级

2. **`utils/hero_badge_generator.py`** - 英雄徽章生成器
   - 生成项目健康度面板
   - 创建推荐任务徽章
   - 支持多种主题和尺寸

3. **`scripts/generate_contributing.py`** - 文档生成器
   - 自动生成 CONTRIBUTING.md
   - 整合健康度、任务、技能信息
   - 支持自定义模板

**输出文件：**
```
badges/
├── CONTRIBUTING.md          # AI 生成的贡献指南
├── README.md                # 项目 README 片段
├── PREVIEW.html             # 本地预览页面
└── assets/
    ├── hero_badge.svg       # 项目英雄徽章
    ├── health_panel.svg     # 健康度面板
    ├── recommended_task.svg # 推荐任务徽章
    └── beginner_task_*.svg  # 新手任务徽章
```

#### 💡 使用场景

- ✅ **开源项目维护者**：一键生成专业的贡献指南
- ✅ **新贡献者**：快速了解项目健康度和推荐任务
- ✅ **团队协作**：统一的任务优先级和技能需求

---

### 2️⃣ Star Map（星图系统）- 技术债务的宇宙视图

**核心价值：** 将技术债务可视化为星空，让管理变得直观有趣

#### 🌌 系统特点

- **极坐标布局**
  - 基于黄金角螺旋（137.5°）分布
  - 重要任务位于中心，优先级由内向外递减
  - 节点大小反映影响范围

- **星座式聚类**
  - PR 与 Issue 通过金色连线形成"星座"
  - 自动识别相关任务的关联关系
  - 视觉化展示项目的模块划分

- **交互式探索**
  - 悬停查看任务详情（标题、技能、难度、推荐）
  - 点击跳转到 GitHub
  - 支持缩放和平移

- **多维度分析**
  - 按难度颜色编码（绿色-橙色-红色）
  - 按状态分类（Open/Closed/Merged）
  - 技能标签可视化

#### 🔧 技术实现

**工作流程：**
```
GitHub API → 扫描 Issues/PRs → LLM 分析 → 坐标计算 → ECharts 渲染
```

**核心组件：**
1. **`scanner/github/client.py`** - GitHub 数据抓取
   - 批量获取 Issues 和 PRs
   - 支持分页和速率限制处理
   - 缓存机制减少 API 调用

2. **`analyzer/builder.py`** - 分析引擎
   - 多维度评分（优先级、难度、影响范围）
   - LLM 技能提取和推荐生成
   - 关联关系识别

3. **`analyzer/star_map.py`** - 星图坐标算法
   - 黄金角螺旋布局
   - 平方根半径映射
   - 力导向防重叠优化

4. **`web/src/pages/StarMapPage.tsx`** - 前端可视化
   - ECharts 极坐标图表
   - 交互式节点和连线
   - 响应式设计

**输出文件：**
```
reports/
├── tidescope-raw.json       # 原始扫描数据
└── tidescope-report.json    # 分析报告（含坐标）
```

#### 💡 使用场景

- ✅ **项目维护者**：全局视角管理技术债务
- ✅ **团队 Lead**：识别关键路径和瓶颈
- ✅ **产品经理**：了解开发资源分配
- ✅ **开发者**：找到感兴趣的模块和任务

---

## 🖼️ 效果展示

### StarMap 星图视图
*以 [SurfSense](https://github.com/MODSetter/SurfSense) 项目为例*
<img width="1332" height="1164" alt="QQ_1763474452961" src="https://github.com/user-attachments/assets/3f7ce0f1-8923-4688-a412-fde1a6a9a338" />
<img width="2416" height="807" alt="QQ_1763474637137" src="https://github.com/user-attachments/assets/ec5de69a-19c2-4cc1-8c73-de766dbf9050" />

**星图特点：**
- 🎯 重要任务位于中心圈，越向外优先级越低
- 🌟 金色连线连接相关的 PR 和 Issue，形成"星座"
- 🔍 悬停查看详细信息：标题、技能、难度、推荐等
- 🎨 发光效果和动画增强视觉体验
- 🌀 黄金角螺旋分布，节点均匀铺满整个空间

### 任务详情评估
*智能分析示例*

**评估内容：**
- 📊 **优先级**: 自动计算（基于标签、更新时间、关联度）
- 🎓 **所需技能**: LLM 自动提取（如：Docker, Authentication, Database, Backend）
- 📈 **难度**: 智能评估（1-5 级）
- 💡 **推荐**: 具体的实施步骤和注意事项
- 🔗 **关联**: 自动识别相关 PR 和讨论

---

## 🛠️ 技术栈

### 🐍 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 核心编程语言 |
| **Pydantic** | 2.x | 数据验证和模型定义 |
| **HTTPX** | 最新 | 异步 HTTP 客户端（GitHub API） |
| **PyYAML** | 最新 | 配置文件解析 |
| **python-dotenv** | 最新 | 环境变量管理 |
| **FastAPI** | 最新 | REST API 框架（可选，用于 Web UI） |
| **Typer** | 最新 | 高级 CLI 工具（可选） |

### 🎨 前端技术（Web UI）

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 18 | 现代化 UI 框架 |
| **TypeScript** | 最新 | 类型安全开发 |
| **Apache ECharts** | 5.x | 数据可视化（极坐标图表） |
| **Ant Design** | 5.x | UI 组件库 |
| **Vite** | 5.x | 快速构建工具 |

### 🤖 LLM 集成

| 提供商 | 模型 | 用途 |
|--------|------|------|
| **Deepseek** | deepseek-chat | 推荐：性价比高，速率限制宽松 |
| **OpenAI** | gpt-4o-mini | 备选：功能强大，价格较高 |

**LLM 分析内容：**
- 任务所需技能提取（如：React, TypeScript, Docker）
- 难度评估（1-5 级）
- 实施建议生成

**降级策略：**
- 无 API Key 时自动使用规则分析
- 确保系统在任何情况下都能运行

### 🧮 核心算法

#### 星图布局算法
```python
# 黄金角螺旋布局
GOLDEN_ANGLE = 137.5  # 度
angle = i * GOLDEN_ANGLE
radius = sqrt(i / total_count) * max_radius

# 极坐标转换
x = radius * cos(angle)
y = radius * sin(angle)
```

**特点：**
- 📐 **黄金角螺旋** (137.5°) - 自然界最优分布，确保节点均匀
- 📏 **平方根半径** - 解决外圈稀疏问题，保持密度一致
- 🔄 **力导向优化** - 防止节点重叠，智能排斥力
- 🌟 **星座连线** - PR-Issue 自动关联，形成视觉聚类

#### 智能评分系统
```python
# 多维度评分
priority_score = (
    label_weight * 0.4 +      # 标签重要性
    activity_score * 0.3 +     # 活跃度
    age_factor * 0.2 +         # 创建时间
    relation_count * 0.1       # 关联数量
)
```

**评分维度：**
- 🏷️ 标签权重（bug > feature > enhancement）
- 📈 活跃度（最近更新、评论数）
- ⏰ 年龄因子（新鲜度衰减）
- 🔗 关联关系（PR 数量、引用次数）

---

## 🚀 快速开始

### 环境要求
- **Python 3.8+**
- **GitHub Personal Access Token**（用于获取仓库数据）
- **LLM API Key**（可选，用于AI智能分析）

### 📦 安装

#### 1. 克隆项目
```bash
git clone https://github.com/unitagain/TideScope.git
cd TideScope/TideScope-main
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# 必需：GitHub Token
GITHUB_TOKEN=ghp_your_github_token_here

# 可选：LLM API（用于AI分析）
DEEPSEEK_API_KEY=sk-your-deepseek-key
# 或者
OPENAI_API_KEY=sk-your-openai-key
```

**获取 GitHub Token：**
访问 [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

**关于 LLM API：**
- 🟢 **推荐 Deepseek**：性价比高，API 完全兼容 OpenAI
- 🔵 **OpenAI**：功能强大，价格较高
- ⚪ **不使用 LLM**：仍可生成基于规则的分析

#### 4. 编辑配置文件

编辑 `config.yaml` 设置要分析的仓库：

```yaml
repository:
  owner: "MODSetter"      # GitHub 用户名或组织
  name: "SurfSense"       # 仓库名称

analysis:
  use_llm: false          # 是否使用 LLM（需要 API Key）
  max_issues: 100         # 最多分析的 issue 数量
```

### 🎯 使用 CLI 快速开始

TideScope 提供了**交互式 CLI 界面**，让使用更加简单：

```bash
python tidescope.py
```

你会看到：

```
████████╗██╗██████╗ ███████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
╚══██╔══╝██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ██║   ██║██║  ██║█████╗  ███████╗██║     ██║   ██║██████╔╝█████╗  
   ██║   ██║██║  ██║██╔══╝  ╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝  
   ██║   ██║██████╔╝███████╗███████║╚██████╗╚██████╔╝██║     ███████╗
   ╚═╝   ╚═╝╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝

        🌊 AI-Powered Technical Debt Analyzer v2.0 🌊

📋 What would you like to generate?

  1️⃣  Star Map (Technical Debt Visualization)
  2️⃣  Badge System (AI-Powered Contributor Guide)
  3️⃣  Both (Complete Analysis)
  0️⃣  Exit

👉 Select an option (0-3):
```

#### 选项说明

**1️⃣ Star Map（星图）**
- 生成技术债务可视化的 JSON 报告
- 输出：`reports/tidescope-raw.json` 和 `tidescope-report.json`
- 用途：分析项目的技术债务分布

**2️⃣ Badge System（徽章系统）**
- 生成 AI 驱动的贡献者指南
- 输出：`badges/CONTRIBUTING.md` 和 SVG 徽章文件
- 用途：帮助新贡献者快速上手

**3️⃣ Both（两者都生成）**
- 同时运行星图和徽章系统
- 完整的项目分析

### 🌐 使用 Web UI 查看星图

**前提条件：**
- 已安装 Node.js 16+
- 已生成星图报告（选项 1 或 3）

**步骤：**

```bash
# 1. 安装前端依赖（仅首次）
cd web
npm install

# 2. 启动后端 API（新终端）
cd ..
python -m api.main

# 3. 启动前端开发服务器（新终端）
cd web
npm run dev
```

**访问：** `http://localhost:5173`

你将看到：
- 🌌 **星图可视化**：技术债务的极坐标分布
- 🎯 **任务详情**：点击节点查看详细信息
- 🔗 **关联分析**：PR 与 Issue 的连线关系
- 📊 **统计面板**：项目健康度和趋势

---

## 🤝 贡献指南

我们非常欢迎各种形式的贡献！无论您是：
- 🐛 发现了 bug
- 💡 有新的功能想法
- 📝 改进文档
- 🎨 优化 UI/UX
- 🧪 添加测试用例

都可以参与到 TideScope 的发展中来！

### 贡献流程

1. **💬 先讨论想法**
   - 在提交代码前，请先创建一个 [Issue](https://github.com/unitagain/TideScope/issues)
   - 描述您的想法、遇到的问题或改进建议
   - 等待项目维护者回复并讨论可行性

2. **✅ 被 Assign 后开始开发**
   - Issue 讨论通过后，维护者会将 Issue assign 给您
   - 这表示您可以开始实现这个功能或修复了
   - 避免重复劳动，确保工作有明确的方向

3. **🔧 Fork 并创建分支**
   ```bash
   # Fork 本仓库到您的账号
   # 然后克隆您的 Fork
   git clone https://github.com/unitagain/TideScope.git
   cd TideScope/TideScope-main
   
   # 创建功能分支
   git checkout -b feature/your-feature-name
   # 或修复分支
   git checkout -b fix/bug-description
   ```

4. **💻 进行开发**
   - 遵循现有的代码风格
   - 添加必要的注释和文档
   - 确保代码可以正常运行

5. **✅ 测试您的更改**
   ```bash
   # 后端测试
   python -m pytest  # （待添加测试用例）
   
   # 前端测试
   cd web
   npm run build  # 确保能够成功构建
   ```

6. **📤 提交 Pull Request**
   ```bash
   git add .
   git commit -m "feat: 添加了 xxx 功能"
   # 或
   git commit -m "fix: 修复了 xxx 问题"
   
   git push origin feature/your-feature-name
   ```
   
   然后在 GitHub 上创建 Pull Request：
   - 清晰地描述您做了什么
   - 关联相关的 Issue（使用 `Fixes #123`）
   - 如果有 UI 变化，请附上截图

7. **🔄 代码审查与合并**
   - 维护者会审查您的代码
   - 可能会提出一些修改建议
   - 修改通过后，您的 PR 就会被合并！🎉

### 提交信息规范

请使用语义化的提交信息：

- `feat: 新功能`
- `fix: 修复 bug`
- `docs: 文档更新`
- `style: 代码格式（不影响功能）`
- `refactor: 重构（不改变功能）`
- `perf: 性能优化`
- `test: 添加测试`
- `chore: 构建/工具相关`

示例：
```bash
feat: 添加按难度筛选任务的功能
fix: 修复 StarMap 节点重叠问题
docs: 更新中文 README 的安装说明
```

### 开发建议

- 💡 **小步提交**：功能拆分成小的、可测试的部分
- 📖 **文档同步**：代码和文档要同步更新
- 🎯 **专注重点**：一个 PR 只做一件事
- 🤝 **积极沟通**：有疑问随时在 Issue 中讨论

---

## 🎯 后续发展目标

TideScope 目前还处于早期阶段，我们有很多激动人心的计划：

### 近期目标（v0.2 - v0.3）

#### 📱 一键生成网站
- 🌐 **在线服务**：提供一个网站，用户只需输入 GitHub 仓库地址，即可在线生成星图
- ⚡ **实时分析**：无需本地安装，浏览器直接查看结果
- 🔗 **分享链接**：生成可分享的星图链接，方便团队协作
- 📊 **历史记录**：跟踪项目技术债务的变化趋势

技术方案：
- 后端：云函数 + 消息队列处理扫描任务
- 前端：静态部署，动态加载数据
- 存储：GitHub 仓库数据缓存，避免重复请求

#### 🎨 更多可视化视图
除了星图，我们计划添加：

1. **时间轴视图**
   - 横轴为时间，纵轴为优先级
   - 显示 Issue/PR 的创建、更新、关闭时间
   - 识别长期未处理的技术债务

2. **关系网络图**
   - 展示 Issue、PR、贡献者之间的关联
   - 识别核心贡献者和关键节点
   - 发现潜在的协作机会

3. **技能雷达图**
   - 统计项目所需的技能分布
   - 帮助新贡献者了解需要学习什么
   - 识别团队技能缺口

4. **健康度仪表盘**
   - 技术债务总量趋势
   - Issue 响应时间
   - PR 合并速度
   - 贡献者活跃度

### 中期目标（v0.4 - v0.6）

#### 🤖 AI 助手功能
- **智能推荐**：根据用户技能和经验，推荐合适的任务
- **自动分配**：AI 辅助 Issue 分配给合适的开发者
- **风险预警**：识别高风险、长期未处理的技术债务

#### 🔗 集成与扩展
- **GitHub App**：一键安装，自动同步仓库数据
- **Slack/Discord 机器人**：团队通知和快速查询
- **VS Code 插件**：IDE 内查看项目星图
- **CI/CD 集成**：在 PR 中自动评估技术债务影响

### 长期愿景

🌍 **成为开源协作的标准工具**
- 帮助全球开发者更高效地参与开源项目
- 降低开源贡献的门槛
- 让技术债务管理变得直观、有趣

💡 **我们需要您的参与！**

这些目标的实现需要社区的力量。无论您擅长：
- 前端开发（React, ECharts）
- 后端开发（Python, FastAPI）
- 算法优化（可视化布局）
- UI/UX 设计
- 文档撰写
- 测试用例编写

都欢迎加入我们！

**一起创造更好的开源协作工具！** 🚀

---

## 📚 项目结构

```
TideScope-main/
├── tidescope.py           # 🎯 交互式 CLI 主入口
├── generate_badges.py     # 🎨 徽章生成命令行工具
├── config.yaml            # ⚙️ 项目配置文件
│
├── analyzer/              # 🧠 分析引擎
│   ├── smart_analyzer.py  # 智能分析器（LLM/规则切换）
│   ├── builder.py         # 报告构建器
│   ├── llm_client.py      # LLM API 客户端（支持 Deepseek/OpenAI）
│   ├── models.py          # 数据模型（DebtItem, AnalysisReport）
│   ├── rules.py           # 规则评分引擎
│   └── star_map.py        # 星图坐标计算（黄金角螺旋）
│
├── scanner/               # 🔍 数据扫描器
│   ├── github/
│   │   ├── client.py      # GitHub API 客户端
│   │   └── __init__.py    # 数据获取接口
│   ├── code/              # 代码 TODO 扫描
│   │   └── todo_scanner.py
│   ├── models.py          # 扫描数据模型
│   ├── runner.py          # 扫描流程编排
│   └── config_loader.py   # 配置加载
│
├── utils/                 # 🛠️ 工具库
│   ├── github_helper.py   # GitHub 数据获取
│   ├── hero_badge_generator.py     # 英雄徽章生成
│   ├── analysis_panel_generator.py # 分析面板生成
│   ├── svg_badge_generator.py      # SVG 徽章工具
│   ├── task_badge_generator.py     # 任务徽章生成
│   └── cache_manager.py   # 缓存管理
│
├── scripts/               # 📝 脚本工具
│   └── generate_contributing.py # CONTRIBUTING.md 生成
│
├── api/                   # 🌐 REST API
│   └── main.py            # FastAPI 应用（用于 Web UI）
│
├── cli/                   # 💻 传统命令行工具
│   └── main.py            # Typer CLI（高级用法）
│
├── web/                   # 🎨 前端应用
│   ├── src/
│   │   ├── components/    # React 组件
│   │   │   ├── Logo.tsx   # Logo 组件
│   │   │   └── AppLayout.tsx
│   │   ├── pages/
│   │   │   └── StarMapPage.tsx  # 星图可视化页面
│   │   └── main.tsx       # 入口文件
│   └── public/            # 静态资源
│       ├── logo-option-1.svg
│       └── favicon.svg
│
└── config/                # 📋 配置模板（历史遗留）
    └── tidescope.config.yaml
```

### 🔑 关键文件说明

| 文件 | 用途 | 关键功能 |
|------|------|----------|
| `tidescope.py` | CLI 主入口 | 交互式菜单，生成星图/徽章 |
| `generate_badges.py` | 徽章生成工具 | 命令行直接生成徽章系统 |
| `config.yaml` | 配置文件 | 仓库信息、分析设置、LLM 配置 |
| `analyzer/smart_analyzer.py` | 智能分析 | 自动选择 LLM 或规则分析 |
| `analyzer/builder.py` | 报告构建 | 整合扫描数据，生成分析报告 |
| `scanner/github/client.py` | GitHub 抓取 | 获取 Issues/PRs，处理速率限制 |
| `utils/hero_badge_generator.py` | 徽章生成 | 生成健康度、推荐任务 SVG |
| `scripts/generate_contributing.py` | 文档生成 | 自动生成 CONTRIBUTING.md |

---

## 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

## 🙏 致谢

- 感谢所有为 TideScope 做出贡献的开发者
- Logo 设计灵感来自 Vercel、Next.js、Tailwind CSS
- 星图布局算法参考了自然界的黄金角螺旋分布
- 感谢 ECharts 团队提供强大的可视化库

---

## 📞 联系我们

- 📧 Email: [1467673018@qq.com]
- 💬 Discussions: [GitHub Discussions](https://github.com/unitagain/TideScope/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/unitagain/TideScope/issues)

---

<div align="center">
  <p>如果 TideScope 对您有帮助，请给我们一个 ⭐ Star！</p>
  <p>让我们一起让开源协作变得更美好！</p>
  
  <br/>
  
  Made with ❤️ and ☕ by TideScope Team
</div>
