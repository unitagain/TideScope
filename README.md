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

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - High-performance REST API framework
- **Typer** - Elegant CLI tool builder
- **OpenAI / Deepseek API** - LLM intelligent analysis (supports multiple models)
- **PyGithub** - GitHub API interaction

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development experience
- **Apache ECharts** - Powerful visualization library (polar coordinate charts)
- **Ant Design** - Enterprise-level UI components
- **Vite** - Fast build tool

### Core Algorithms
- **Golden Angle Spiral Layout** (137.5°) - Nature's optimal distribution algorithm
- **Square Root Radius Mapping** - Solves sparse outer ring and crowded inner ring issues
- **Force-Directed Anti-Overlap** - Real-time collision detection and repulsion
- **Anti-Collinearity Force** - Prevents nodes from being too regularly arranged

---

## 🚀 Quick Start

### Requirements
- Python 3.8 or higher
- Node.js 16 or higher
- GitHub Personal Access Token (for repository scanning)

### 1. Clone the Project
```bash
git clone https://github.com/unitagain/TideScope.git
cd TideScope/TideScope-main
```

### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd web
npm install
cd ..
```

### 4. Configure Environment Variables

#### GitHub Token
Get Token: Visit [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="ghp_your_github_token_here"

# Linux / macOS
export GITHUB_TOKEN="ghp_your_github_token_here"
```

#### LLM API Configuration (Optional but Recommended)
If you need intelligent analysis features:

```bash
# Use Deepseek (Recommended, cost-effective)
$env:OPENAI_API_KEY="sk-your-deepseek-key"
$env:OPENAI_BASE_URL="https://api.deepseek.com/v1"

# Or use OpenAI
$env:OPENAI_API_KEY="sk-your-openai-key"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

⚠️ **Important Note: About LLM API**
- **Free OpenAI API Limitations**: Free tier usually has strict rate limits (3 requests per minute), which can cause incomplete analysis when scanning large projects
- **Recommended: Use Deepseek**: API format fully compatible with OpenAI, very affordable pricing (about 1/10 of OpenAI), more relaxed rate limits
- **Or Upgrade to OpenAI Paid**: Get higher rate limits and better experience
- **Can Also Skip LLM**: Skip intelligent analysis step, still can generate rule-based StarMap

### 5. Configure Scan Target

Edit `config/tidescope.config.yaml`:

```yaml
repository_path: ..  # Local code path
include_extensions:
  - .py
  - .ts
  - .tsx
  - .js
  - .jsx
mode: deep  # deep: scan code; quick: GitHub only

github:
  owner: OWNER_NAME     # Repository owner
  repo: REPO_NAME       # Repository name
  token_env: GITHUB_TOKEN
```

### 6. Run Scan

```bash
# Scan and generate raw data
python -m cli.main scan --config config/tidescope.config.yaml

# Generates tidescope-raw.json
```

### 7. Analyze Data (Using LLM)

```bash
# Use LLM for intelligent analysis
python -m cli.main analyze \
  --scan-result tidescope-raw.json \
  --output tidescope-report.json \
  --use-llm

# Generates tidescope-report.json
```

### 8. Launch Web UI

```bash
# Terminal 1: Start backend API
python -m api.main

# Terminal 2: Start frontend
cd web
npm run dev
```

Visit `http://localhost:5173` to see the StarMap! 🌟

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
├── analyzer/              # Analysis engine
│   ├── builder.py         # Build analysis reports
│   ├── llm_client.py      # LLM API client
│   ├── models.py          # Data models
│   ├── rules.py           # Scoring rules
│   └── star_map.py        # StarMap coordinate calculation
├── scanner/               # Scanners
│   ├── github/            # GitHub API client
│   ├── code/              # Code TODO scanner
│   ├── models.py          # Scan data models
│   └── runner.py          # Scan orchestration
├── api/                   # REST API
│   └── main.py            # FastAPI application
├── cli/                   # Command-line tool
│   └── main.py            # Typer CLI
├── web/                   # Frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Logo.tsx   # Logo component
│   │   │   └── AppLayout.tsx
│   │   └── pages/
│   │       └── StarMapPage.tsx  # StarMap page
│   └── public/            # Static assets
│       ├── logo-option-1.svg
│       └── favicon.svg
├── config/                # Configuration templates
│   ├── tidescope.config.yaml
│   └── surfsense.config.yaml
└── docs/                  # Documentation
```

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

