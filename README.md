![IMG_20251120_191504](https://github.com/user-attachments/assets/10241819-cc96-4b41-b080-419ead551b31)


<div align="center">
  <img src="web/public/logo-option-1.svg" alt="TideScope Logo" width="560"/>
  
  <p><strong>Make Technical Debt Visible, Make Open Source Collaboration Easier</strong></p>
  
  <p>
    <a href="README_CN.md">中文文档</a>
    &nbsp;|&nbsp;
    <a href="#quick-start">Quick Start</a>
    &nbsp;|&nbsp;
    <a href="#tech-stack">Tech Stack</a>
    &nbsp;|&nbsp;
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## 💫 Our Mission

As a **beginner**, have you ever found an open source project that interests you, but struggled to figure out what you could contribute? Where to start?

As an **open source project maintainer**, have you ever felt overwhelmed by the flood of PRs and Issues, unsure how to prioritize tasks and manage technical debt?

**TideScope** is inspired by star maps. By **scanning GitHub repositories for Issues, PRs, and TODO comments in code**, combined with **LLM-powered intelligent analysis** to extract required skills and difficulty assessments, it generates an intuitive **Technical Debt StarMap**. Each task appears as a star, distributed in a polar coordinate system by importance from center to edge, with related PR-Issue pairs forming constellation-like visual clusters.

Through this **innovative visualization approach**, we aim to help:
- 🌱 **New contributors** quickly find tasks matching their skill level
- 🎯 **Project maintainers** gain a clear overview of technical debt at a glance
- 🤝 **Team collaboration** become more efficient, transparent, and organized

---

## ✨ Core Features

### 🌌 StarMap Visualization
- **Ranking-Based Golden Angle Spiral Layout** - Mathematically optimized distribution algorithm ensures uniform node placement
- **Force-Directed Anti-Overlap Mechanism** - Intelligent repulsion algorithm prevents node collisions, keeping the chart clear
- **Constellation-Style Clustering** - PRs and Issues automatically form tight constellation groups, intuitively showing relationships
- **Gradient Glow Effects** - Modern visual design optimized for dark themes

### 🧠 Intelligent Analysis
- **LLM Skill Extraction** - Automatically analyzes required tech stacks and skill points for each task
- **Multi-Dimensional Scoring** - Comprehensive assessment of priority, difficulty, impact scope, and risk level
- **Smart Recommendations** - Generates targeted implementation suggestions for each task
- **Automatic Context** - Automatically fetches project README as analysis background

### 🎯 Developer Friendly
- **One-Click Scanning** - Supports both local code and remote GitHub repositories
- **Flexible Configuration** - YAML config files for easy customization of scan rules
- **Dual Interface** - Web UI + CLI command line to meet different use cases

---

## 🖼️ Demo

### StarMap View
*Example using [SurfSense](https://github.com/MODSetter/SurfSense) project*
<img width="1332" height="1164" alt="QQ_1763474452961" src="https://github.com/user-attachments/assets/1e99fb0f-2c35-41d6-b1c9-c9d70fbfc4f2" />
<img width="2416" height="807" alt="image" src="https://github.com/user-attachments/assets/a66a87f0-c8bc-42b5-b798-d84be218369d" />

**StarMap Features:**
- 🎯 Important tasks in the center circle, priority decreases outward
- 🌟 Golden lines connect related PRs and Issues, forming "constellations"
- 🔍 Hover for details: title, skills, difficulty, recommendations
- 🎨 Glow effects and animations enhance visual experience
- 🌀 Golden angle spiral distribution, nodes evenly fill the entire space

### Task Detail Assessment
*Intelligent analysis example*

**Assessment Content:**
- 📊 **Priority**: Auto-calculated (based on labels, update time, relevance)
- 🎓 **Required Skills**: LLM auto-extraction (e.g., Docker, Authentication, Database, Backend)
- 📈 **Difficulty**: Smart assessment (1-5 scale)
- 💡 **Recommendations**: Specific implementation steps and considerations
- 🔗 **Related**: Auto-identify related PRs and discussions

---

## 🎨 Dual System Architecture

TideScope provides **two core systems** to meet different needs:

### 1️⃣ Badge System - Best Entry Point for New Contributors

**Core Value:** Lower the barrier to open source contribution, help beginners quickly find suitable tasks

#### 🎯 System Features

- **📊 Project Health Dashboard**
  - Real-time health score (0-100)
  - Project activity trend analysis
  - Open Issues and PR statistics

- **🎖️ AI-Powered Task Badges**
  - Auto-generate beautiful SVG badges
  - Display task title, difficulty, required skills
  - One-click jump to GitHub Issue

- **🌱 Beginner-Friendly Task List**
  - Filter Issues suitable for beginners
  - Categorized by difficulty and skills
  - Includes detailed implementation suggestions

- **📝 Auto-Generate CONTRIBUTING.md**
  - AI analyzes project to generate contribution guide
  - Includes health metrics, recommended tasks, skill distribution
  - Beautiful Markdown format, GitHub-ready

#### 🔧 Technical Implementation

**Workflow:**
```
GitHub API → Data Fetch → LLM/Rule Analysis → SVG Generation → Markdown Rendering
```

**Core Components:**
1. **`analyzer/smart_analyzer.py`** - Smart Analyzer
   - Automatically choose LLM or rule-based analysis
   - Extract required skills from Issues
   - Assess task difficulty and priority

2. **`utils/hero_badge_generator.py`** - Hero Badge Generator
   - Generate project health panel
   - Create recommended task badges
   - Support multiple themes and sizes

3. **`scripts/generate_contributing.py`** - Documentation Generator
   - Auto-generate CONTRIBUTING.md
   - Integrate health, tasks, and skill information
   - Support custom templates

**Output Files:**
```
badges/
├── CONTRIBUTING.md          # AI-generated contribution guide
├── README.md                # Project README snippet
├── PREVIEW.html             # Local preview page
└── assets/
    ├── hero_badge.svg       # Project hero badge
    ├── health_panel.svg     # Health panel
    ├── recommended_task.svg # Recommended task badge
    └── beginner_task_*.svg  # Beginner task badges
```

#### 💡 Use Cases

- ✅ **Open Source Maintainers**: One-click professional contribution guide
- ✅ **New Contributors**: Quickly understand project health and recommended tasks
- ✅ **Team Collaboration**: Unified task priority and skill requirements

---

### 2️⃣ Star Map System - Universe View of Technical Debt

**Core Value:** Visualize technical debt as a starry sky, making management intuitive and engaging

#### 🌌 System Features

- **Polar Coordinate Layout**
  - Based on Golden Angle Spiral (137.5°)
  - Important tasks in center, priority decreases outward
  - Node size reflects impact scope

- **Constellation-Style Clustering**
  - PRs and Issues connected by golden lines forming "constellations"
  - Auto-identify relationships between related tasks
  - Visualize project module division

- **Interactive Exploration**
  - Hover to view task details (title, skills, difficulty, recommendations)
  - Click to jump to GitHub
  - Support zoom and pan

- **Multi-Dimensional Analysis**
  - Color-coded by difficulty (green-orange-red)
  - Categorized by status (Open/Closed/Merged)
  - Skill tag visualization

#### 🔧 Technical Implementation

**Workflow:**
```
GitHub API → Scan Issues/PRs → LLM Analysis → Coordinate Calculation → ECharts Rendering
```

**Core Components:**
1. **`scanner/github/client.py`** - GitHub Data Fetcher
   - Batch fetch Issues and PRs
   - Handle pagination and rate limits
   - Caching mechanism to reduce API calls

2. **`analyzer/builder.py`** - Analysis Engine
   - Multi-dimensional scoring (priority, difficulty, impact)
   - LLM skill extraction and recommendation generation
   - Relationship identification

3. **`analyzer/star_map.py`** - StarMap Coordinate Algorithm
   - Golden angle spiral layout
   - Square root radius mapping
   - Force-directed anti-overlap optimization

4. **`web/src/pages/StarMapPage.tsx`** - Frontend Visualization
   - ECharts polar coordinate chart
   - Interactive nodes and connections
   - Responsive design

**Output Files:**
```
reports/
├── tidescope-raw.json       # Raw scan data
└── tidescope-report.json    # Analysis report (with coordinates)
```

#### 💡 Use Cases

- ✅ **Project Maintainers**: Global view of technical debt management
- ✅ **Team Leads**: Identify critical paths and bottlenecks
- ✅ **Product Managers**: Understand dev resource allocation
- ✅ **Developers**: Find interesting modules and tasks

---

## 🛠️ Tech Stack

### 🐍 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|----------|
| **Python** | 3.8+ | Core programming language |
| **Pydantic** | 2.x | Data validation and modeling |
| **HTTPX** | Latest | Async HTTP client (GitHub API) |
| **PyYAML** | Latest | Configuration file parsing |
| **python-dotenv** | Latest | Environment variable management |
| **FastAPI** | Latest | REST API framework (Optional, for Web UI) |
| **Typer** | Latest | Advanced CLI tool (Optional) |

### 🎨 Frontend Technologies (Web UI)

| Technology | Version | Purpose |
|------------|---------|----------|
| **React** | 18 | Modern UI framework |
| **TypeScript** | Latest | Type-safe development |
| **Apache ECharts** | 5.x | Data visualization (polar charts) |
| **Ant Design** | 5.x | UI component library |
| **Vite** | 5.x | Fast build tool |

### 🤖 LLM Integration

| Provider | Model | Notes |
|----------|-------|-------|
| **Deepseek** | deepseek-chat | Recommended: Cost-effective, relaxed rate limits |
| **OpenAI** | gpt-4o-mini | Alternative: Powerful, higher cost |

**LLM Analysis Content:**
- Extract required skills (e.g., React, TypeScript, Docker)
- Assess difficulty (1-5 scale)
- Generate implementation recommendations

**Fallback Strategy:**
- Automatically uses rule-based analysis when no API key
- System works in any configuration

### 🧠 Core Algorithms

#### StarMap Layout Algorithm
```python
# Golden Angle Spiral Layout
GOLDEN_ANGLE = 137.5  # degrees
angle = i * GOLDEN_ANGLE
radius = sqrt(i / total_count) * max_radius

# Polar to Cartesian conversion
x = radius * cos(angle)
y = radius * sin(angle)
```

**Features:**
- 📐 **Golden Angle Spiral** (137.5°) - Nature's optimal distribution
- 📏 **Square Root Radius** - Solves sparse outer ring problem
- 🔄 **Force-Directed Optimization** - Prevents node overlap
- 🌟 **Constellation Linking** - PR-Issue auto-connection

#### Smart Scoring System
```python
# Multi-dimensional scoring
priority_score = (
    label_weight * 0.4 +      # Label importance
    activity_score * 0.3 +     # Activity level
    age_factor * 0.2 +         # Creation time
    relation_count * 0.1       # Relationship count
)
```

**Scoring Dimensions:**
- 🏷️ Label weight (bug > feature > enhancement)
- 📈 Activity (recent updates, comments)
- ⏰ Age factor (freshness decay)
- 🔗 Relationships (PR count, references)

---

## 🚀 Quick Start

### Requirements
- **Python 3.8+**
- **GitHub Personal Access Token** (for fetching repository data)
- **LLM API Key** (Optional, for AI-powered analysis)

### 📦 Installation

#### 1. Clone the Project
```bash
git clone https://github.com/unitagain/TideScope.git
cd TideScope/TideScope-main
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required: GitHub Token
GITHUB_TOKEN=ghp_your_github_token_here

# Optional: LLM API (for AI analysis)
DEEPSEEK_API_KEY=sk-your-deepseek-key
# Or
OPENAI_API_KEY=sk-your-openai-key
```

**Get GitHub Token:**
Visit [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

**About LLM API:**
- 🟢 **Recommended: Deepseek** - Cost-effective, fully compatible with OpenAI API
- 🔵 **OpenAI** - Powerful features, higher cost
- ⚪ **Skip LLM** - Still works with rule-based analysis

#### 4. Edit Configuration File

Edit `config.yaml` to set the repository to analyze:

```yaml
repository:
  owner: "MODSetter"      # GitHub username or organization
  name: "SurfSense"       # Repository name

analysis:
  use_llm: false          # Whether to use LLM (requires API Key)
  max_issues: 100         # Maximum issues to analyze
```

### 🎯 Using Interactive CLI

TideScope provides an **interactive CLI interface** for easy usage:

```bash
python tidescope.py
```

You'll see:

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

#### Option Description

**1️⃣ Star Map**
- Generates technical debt visualization JSON report
- Output: `reports/tidescope-raw.json` and `tidescope-report.json`
- Purpose: Analyze technical debt distribution

**2️⃣ Badge System**
- Generates AI-powered contributor guide
- Output: `badges/CONTRIBUTING.md` and SVG badge files
- Purpose: Help new contributors get started quickly

**3️⃣ Both**
- Run both Star Map and Badge System
- Complete project analysis

### 🌐 Using Web UI to View StarMap

**Prerequisites:**
- Node.js 16+ installed
- StarMap report generated (Option 1 or 3)

**Steps:**

```bash
# 1. Install frontend dependencies (first time only)
cd web
npm install

# 2. Start backend API (new terminal)
cd ..
python -m api.main

# 3. Start frontend dev server (new terminal)
cd web
npm run dev
```

**Visit:** `http://localhost:5173`

You'll see:
- 🌌 **StarMap Visualization**: Polar coordinate distribution of technical debt
- 🎯 **Task Details**: Click nodes for detailed information
- 🔗 **Relationship Analysis**: Lines connecting PRs and Issues
- 📊 **Statistics Panel**: Project health and trends

---

## 🤝 Contributing

We warmly welcome all forms of contributions! Whether you:
- 🐛 Found a bug
- 💡 Have a new feature idea
- 📝 Want to improve documentation
- 🎨 Optimize UI/UX
- 🧪 Add test cases

You can participate in TideScope's development!

### Contribution Process

1. **💬 Discuss Your Idea First**
   - Before submitting code, please create an [Issue](https://github.com/unitagain/TideScope/issues)
   - Describe your idea, problem encountered, or improvement suggestions
   - Wait for project maintainers to respond and discuss feasibility

2. **✅ Start Development After Being Assigned**
   - After the Issue discussion is approved, maintainers will assign the Issue to you
   - This indicates you can start implementing the feature or fix
   - Avoids duplicate work and ensures work has a clear direction

3. **🔧 Fork and Create Branch**
   ```bash
   # Fork this repository to your account
   # Then clone your fork
   git clone https://github.com/unitagain/TideScope.git
   cd TideScope/TideScope-main
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   # Or fix branch
   git checkout -b fix/bug-description
   ```

4. **💻 Develop**
   - Follow existing code style
   - Add necessary comments and documentation
   - Ensure code runs correctly

5. **✅ Test Your Changes**
   ```bash
   # Backend tests
   python -m pytest  # (Test cases to be added)
   
   # Frontend tests
   cd web
   npm run build  # Ensure successful build
   ```

6. **📤 Submit Pull Request**
   ```bash
   git add .
   git commit -m "feat: added xxx feature"
   # or
   git commit -m "fix: fixed xxx issue"
   
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub:
   - Clearly describe what you did
   - Link related Issue (use `Fixes #123`)
   - If there are UI changes, attach screenshots

7. **🔄 Code Review and Merge**
   - Maintainers will review your code
   - May suggest some modifications
   - Once approved, your PR will be merged! 🎉

### Commit Message Convention

Please use semantic commit messages:

- `feat: new feature`
- `fix: bug fix`
- `docs: documentation update`
- `style: code format (no functional impact)`
- `refactor: refactoring (no functional change)`
- `perf: performance optimization`
- `test: add tests`
- `chore: build/tool related`

Examples:
```bash
feat: add task filtering by difficulty
fix: fix StarMap node overlap issue
docs: update Chinese README installation instructions
```

### Development Suggestions

- 💡 **Small Commits**: Break features into small, testable parts
- 📖 **Sync Docs**: Keep code and documentation in sync
- 🎯 **Stay Focused**: One PR should do one thing
- 🤝 **Active Communication**: Feel free to discuss in Issues

---

## 🎯 Future Development Goals

TideScope is currently in early stages, and we have many exciting plans:

### Near-term Goals (v0.2 - v0.3)

#### 📱 One-Click Generation Website
- 🌐 **Online Service**: Provide a website where users simply input a GitHub repository URL to generate StarMaps online
- ⚡ **Real-time Analysis**: No local installation needed, view results directly in browser
- 🔗 **Shareable Links**: Generate shareable StarMap links for easy team collaboration
- 📊 **Historical Records**: Track changes in project technical debt over time

Technical Approach:
- Backend: Cloud functions + message queue to process scan tasks
- Frontend: Static deployment, dynamic data loading
- Storage: GitHub repository data caching to avoid repeated requests

#### 🎨 More Visualization Views
In addition to the StarMap, we plan to add:

1. **Timeline View**
   - X-axis for time, Y-axis for priority
   - Show creation, update, close times of Issues/PRs
   - Identify long-standing unaddressed technical debt

2. **Relationship Network Graph**
   - Show connections between Issues, PRs, and contributors
   - Identify core contributors and key nodes
   - Discover potential collaboration opportunities

3. **Skill Radar Chart**
   - Visualize distribution of required skills in the project
   - Help new contributors understand what to learn
   - Identify team skill gaps

4. **Health Dashboard**
   - Technical debt volume trends
   - Issue response time
   - PR merge speed
   - Contributor activity

### Mid-term Goals (v0.4 - v0.6)

#### 🤖 AI Assistant Features
- **Smart Recommendations**: Recommend suitable tasks based on user skills and experience
- **Auto-Assignment**: AI-assisted Issue assignment to appropriate developers
- **Risk Alerts**: Identify high-risk, long-standing technical debt

#### 🔗 Integrations and Extensions
- **GitHub App**: One-click installation, automatic repository data sync
- **Slack/Discord Bot**: Team notifications and quick queries
- **VS Code Extension**: View project StarMap within IDE
- **CI/CD Integration**: Auto-assess technical debt impact in PRs

### Long-term Vision

🌍 **Become the Standard Tool for Open Source Collaboration**
- Help developers worldwide participate in open source projects more efficiently
- Lower the barrier to open source contributions
- Make technical debt management intuitive and fun

💡 **We Need Your Participation!**

Achieving these goals requires community strength. Whether you're skilled in:
- Frontend development (React, ECharts)
- Backend development (Python, FastAPI)
- Algorithm optimization (visualization layouts)
- UI/UX design
- Documentation writing
- Test case development

You're welcome to join us!

**Let's create better open source collaboration tools together!** 🚀

---

## 📚 Project Structure

```
TideScope-main/
├── tidescope.py           # 🎯 Interactive CLI main entry
├── generate_badges.py     # 🎨 Badge generation CLI tool
├── config.yaml            # ⚙️ Project configuration file
│
├── analyzer/              # 🧠 Analysis Engine
│   ├── smart_analyzer.py  # Smart analyzer (LLM/Rule switching)
│   ├── builder.py         # Report builder
│   ├── llm_client.py      # LLM API client (Deepseek/OpenAI support)
│   ├── models.py          # Data models (DebtItem, AnalysisReport)
│   ├── rules.py           # Rule-based scoring engine
│   └── star_map.py        # StarMap coordinate calculation (Golden Angle Spiral)
│
├── scanner/               # 🔍 Data Scanner
│   ├── github/
│   │   ├── client.py      # GitHub API client
│   │   └── __init__.py    # Data fetch interface
│   ├── code/              # Code TODO scanner
│   │   └── todo_scanner.py
│   ├── models.py          # Scan data models
│   ├── runner.py          # Scan orchestration
│   └── config_loader.py   # Configuration loader
│
├── utils/                 # 🛠️ Utilities
│   ├── github_helper.py   # GitHub data fetching
│   ├── hero_badge_generator.py     # Hero badge generation
│   ├── analysis_panel_generator.py # Analysis panel generation
│   ├── svg_badge_generator.py      # SVG badge utilities
│   ├── task_badge_generator.py     # Task badge generation
│   └── cache_manager.py   # Cache management
│
├── scripts/               # 📝 Script Tools
│   └── generate_contributing.py # CONTRIBUTING.md generator
│
├── api/                   # 🌐 REST API
│   └── main.py            # FastAPI application (for Web UI)
│
├── cli/                   # 💻 Traditional CLI Tool
│   └── main.py            # Typer CLI (advanced usage)
│
├── web/                   # 🎨 Frontend Application
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Logo.tsx   # Logo component
│   │   │   └── AppLayout.tsx
│   │   ├── pages/
│   │   │   └── StarMapPage.tsx  # StarMap visualization page
│   │   └── main.tsx       # Entry file
│   └── public/            # Static assets
│       ├── logo-option-1.svg
│       └── favicon.svg
│
└── config/                # 📋 Configuration Templates (legacy)
    └── tidescope.config.yaml
```

### 🔑 Key Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `tidescope.py` | CLI main entry | Interactive menu, generate StarMap/Badges |
| `generate_badges.py` | Badge generation tool | Direct CLI badge generation |
| `config.yaml` | Configuration file | Repository info, analysis settings, LLM config |
| `analyzer/smart_analyzer.py` | Smart analysis | Auto-select LLM or rule-based analysis |
| `analyzer/builder.py` | Report building | Integrate scan data, generate analysis report |
| `scanner/github/client.py` | GitHub fetching | Get Issues/PRs, handle rate limits |
| `utils/hero_badge_generator.py` | Badge generation | Generate health, recommended task SVGs |
| `scripts/generate_contributing.py` | Doc generation | Auto-generate CONTRIBUTING.md |

---

## � License

[To be added - Suggest MIT or Apache 2.0]

---

## 🙏 Acknowledgments

- Thanks to all developers who contributed to TideScope
- Logo design inspired by Vercel, Next.js, Tailwind CSS
- StarMap layout algorithm references nature's golden angle spiral distribution
- Thanks to the ECharts team for their powerful visualization library

---

## 📞 Contact Us

- 📧 Email: [1467673018@qq.com]
- 💬 Discussions: [GitHub Discussions](https://github.com/unitagain/TideScope/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/unitagain/TideScope/issues)

---

<div align="center">
  <p>If TideScope helps you, please give us a ⭐ Star!</p>
  <p>Let's make open source collaboration better together!</p>
  
  <br/>
  
  Made with ❤️ and ☕ by TideScope Team
</div>

