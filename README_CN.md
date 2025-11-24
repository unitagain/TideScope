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

### 后端
- **Python 3.8+** - 核心编程语言
- **FastAPI** - 高性能 REST API 框架
- **Typer** - 优雅的 CLI 工具构建
- **OpenAI / Deepseek API** - LLM 智能分析（支持多种模型）
- **PyGithub** - GitHub API 交互

### 前端
- **React 18** - 现代化 UI 框架
- **TypeScript** - 类型安全的开发体验
- **Apache ECharts** - 强大的可视化库（极坐标图表）
- **Ant Design** - 企业级 UI 组件
- **Vite** - 快速的构建工具

### 核心算法
- **黄金角螺旋布局** (137.5°) - 自然界最优分布算法
- **平方根半径映射** - 解决外圈稀疏、内圈拥挤问题
- **力导向防重叠** - 实时碰撞检测与排斥力
- **反共线力** - 避免节点排列过于规律

---

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- Node.js 16 或更高版本
- GitHub Personal Access Token（用于扫描仓库）

### 1. 克隆项目
```bash
git clone https://github.com/unitagain/TideScope.git
cd TideScope/TideScope-main
```

### 2. 安装后端依赖
```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd web
npm install
cd ..
```

### 4. 配置环境变量

#### GitHub Token
获取 Token：访问 [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="ghp_your_github_token_here"

# Linux / macOS
export GITHUB_TOKEN="ghp_your_github_token_here"
```

#### LLM API 配置（可选但推荐）
如果需要智能分析功能：

```bash
# 使用 Deepseek（推荐，性价比高）
$env:OPENAI_API_KEY="sk-your-deepseek-key"
$env:OPENAI_BASE_URL="https://api.deepseek.com/v1"

# 或使用 OpenAI
$env:OPENAI_API_KEY="sk-your-openai-key"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

⚠️ **重要提示：关于 LLM API**
- **免费 OpenAI API 的限制**：免费额度通常有严格的速率限制（每分钟 3 次请求），扫描大型项目时会触发限制导致分析不完整
- **推荐使用 Deepseek**：API 格式完全兼容 OpenAI，价格非常便宜（约为 OpenAI 的 1/10），速率限制更宽松
- **或升级 OpenAI 付费版**：获得更高的速率限制和更好的体验
- **也可以不使用 LLM**：跳过智能分析步骤，仍可生成基于规则的星图

### 5. 配置扫描目标

编辑 `config/tidescope.config.yaml`：

```yaml
repository_path: ..  # 本地代码路径
include_extensions:
  - .py
  - .ts
  - .tsx
  - .js
  - .jsx
mode: deep  # deep: 扫描代码; quick: 仅 GitHub

github:
  owner: OWNER_NAME     # 仓库所有者
  repo: REPO_NAME       # 仓库名称
  token_env: GITHUB_TOKEN
```

### 6. 运行扫描

```bash
# 扫描并生成原始数据
python -m cli.main scan --config config/tidescope.config.yaml

# 会生成 tidescope-raw.json
```

### 7. 分析数据（使用 LLM）

```bash
# 使用 LLM 进行智能分析
python -m cli.main analyze \
  --scan-result tidescope-raw.json \
  --output tidescope-report.json \
  --use-llm

# 会生成 tidescope-report.json
```

### 8. 启动 Web UI

```bash
# 终端 1：启动后端 API
python -m api.main

# 终端 2：启动前端
cd web
npm run dev
```

访问 `http://localhost:5173` 即可看到星图！🌟

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
├── analyzer/              # 分析引擎
│   ├── builder.py         # 构建分析报告
│   ├── llm_client.py      # LLM API 客户端
│   ├── models.py          # 数据模型
│   ├── rules.py           # 评分规则
│   └── star_map.py        # 星图坐标计算
├── scanner/               # 扫描器
│   ├── github/            # GitHub API 客户端
│   ├── code/              # 代码 TODO 扫描器
│   ├── models.py          # 扫描数据模型
│   └── runner.py          # 扫描流程编排
├── api/                   # REST API
│   └── main.py            # FastAPI 应用
├── cli/                   # 命令行工具
│   └── main.py            # Typer CLI
├── web/                   # 前端应用
│   ├── src/
│   │   ├── components/    # React 组件
│   │   │   ├── Logo.tsx   # Logo 组件
│   │   │   └── AppLayout.tsx
│   │   └── pages/
│   │       └── StarMapPage.tsx  # 星图页面
│   └── public/            # 静态资源
│       ├── logo-option-1.svg
│       └── favicon.svg
├── config/                # 配置模板
│   ├── tidescope.config.yaml
│   └── surfsense.config.yaml
└── docs/                  # 文档
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
