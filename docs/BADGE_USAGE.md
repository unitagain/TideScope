# 🎨 TideScope Badge System

Intelligent badges powered by LLM to showcase your project's technical debt status.

## 📋 Available Badges

### 1. Recommended Task Badge ⭐ Most Attractive

Shows the best starting task for new contributors.

```markdown
[![Recommended Task](https://tidescope.vercel.app/api/badge/unitagain/TideScope/recommended.svg)](https://github.com/unitagain/TideScope)
```

**Features:**
- LLM-powered task recommendation
- Displays difficulty, impact, and time estimate
- Perfect for attracting new contributors

---

### 2. Project Health Badge

Overall health score with key metrics.

```markdown
[![Project Health](https://tidescope.vercel.app/api/badge/unitagain/TideScope/health.svg)](https://github.com/unitagain/TideScope)
```

**Metrics:**
- Health score (0-100)
- Urgent task count
- Open task count
- Stale task count (>90 days)

---

### 3. Beginner Friendly Badge

Number of tasks suitable for beginners.

```markdown
[![Beginner Friendly](https://tidescope.vercel.app/api/badge/unitagain/TideScope/beginner.svg)](https://github.com/unitagain/TideScope)
```

**Features:**
- LLM identifies truly beginner-friendly tasks
- Not just based on "good-first-issue" labels
- Encourages community participation

---

### 4. Tech Debt Distribution Badge

Visual breakdown of technical debt by category.

```markdown
[![Tech Debt Distribution](https://tidescope.vercel.app/api/badge/unitagain/TideScope/distribution.svg)](https://github.com/unitagain/TideScope)
```

**Categories:**
- Performance
- Security
- Documentation
- Testing
- Refactor
- Feature

---

### 5. Activity Badge

Recent activity trends (last 7 days).

```markdown
[![Activity](https://tidescope.vercel.app/api/badge/unitagain/TideScope/activity.svg)](https://github.com/unitagain/TideScope)
```

**Metrics:**
- New tasks this week
- Resolved tasks
- Tasks in progress

---

## 🚀 Quick Start

### For Users

Simply copy the markdown code and paste it into your README:

```markdown
<!-- Add to your README.md -->
[![Recommended Task](https://tidescope.vercel.app/api/badge/YOUR_GITHUB_USERNAME/YOUR_REPO/recommended.svg)](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO)
```

Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO` with your actual repository details.

### For Developers

#### Local Testing

1. **Setup environment:**

```bash
# Copy environment template
cp .env.example .env

# Add your API keys
# GITHUB_TOKEN=your_token
# DEEPSEEK_API_KEY=your_key  # or OPENAI_API_KEY
```

2. **Run test script:**

```bash
python test_badges.py
```

This will generate sample badges in `./test_output/` and create an HTML preview.

3. **Start local server:**

```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m api

# or with uvicorn
uvicorn api.main:app --reload
```

4. **Test badge endpoints:**

```bash
# Get recommended badge
curl http://localhost:8000/api/badge/unitagain/TideScope/recommended.svg

# Get all badge URLs
curl http://localhost:8000/api/badge/unitagain/TideScope/all
```

---

## 🎯 How It Works

### Architecture

```
User Request → CDN Cache (95% hit rate)
                    ↓ (miss)
              API Server
                    ↓
              Check Cache (24h)
                    ↓ (miss)
              Fetch GitHub Data
                    ↓
              Analyze (LLM or Rules)
                    ↓
              Generate SVG Badge
                    ↓
              Cache & Return
```

### Cost Optimization

The system uses multiple strategies to minimize LLM costs:

1. **Multi-layer caching:**
   - CDN cache (24h): 95% hit rate
   - Memory cache (1h): 4% hit rate
   - LLM analysis: Only 1% of requests

2. **Batch optimization:**
   - One LLM call generates data for all 5 badges
   - Reduces API calls by 80%

3. **Automatic fallback:**
   - Low usage (<10): LLM analysis (high quality)
   - Medium usage (10-100): Rule-based analysis (good quality)
   - High usage (>100): Pre-generated badges (basic quality)

4. **Smart filtering:**
   - Only analyzes top 10 most important issues
   - Skips closed issues
   - Focuses on actionable tasks

### Cost Estimate

Using DeepSeek API (recommended):
- 10 projects: ¥0.9/month
- 50 projects: ¥4.5/month
- 100+ projects: ¥0/month (auto-fallback to rules)

Using OpenAI API:
- 10 projects: ¥9/month
- Cost 10x higher than DeepSeek

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=ghp_xxxxx          # GitHub API token

# LLM Provider (choose one)
LLM_PROVIDER=deepseek            # Options: "openai" or "deepseek"
DEEPSEEK_API_KEY=sk-xxxxx       # DeepSeek API key (recommended)
OPENAI_API_KEY=sk-xxxxx         # OpenAI API key (alternative)

# Optional
BADGE_BASE_URL=https://your-domain.vercel.app  # Base URL for badges
```

### Cache Configuration

Edit `utils/cache_manager.py`:

```python
# Default settings
MEMORY_TTL = 3600    # 1 hour
DISK_TTL = 86400     # 24 hours

# Adjust as needed
cache = CacheManager(
    cache_dir=".cache/badges",
    memory_ttl=1800,   # 30 minutes
    disk_ttl=43200     # 12 hours
)
```

---

## 📊 API Reference

### GET /api/badge/{owner}/{repo}/{badge_type}.svg

Get a specific badge type.

**Parameters:**
- `owner`: Repository owner (string)
- `repo`: Repository name (string)
- `badge_type`: Badge type (recommended | health | beginner | distribution | activity)
- `refresh`: Force refresh (optional, default: false)

**Response:**
- Content-Type: `image/svg+xml`
- Cache-Control: `public, max-age=86400` (24 hours)

**Example:**
```bash
curl https://tidescope.vercel.app/api/badge/unitagain/TideScope/health.svg
```

---

### GET /api/badge/{owner}/{repo}/all

Get URLs for all badge types.

**Response:**
```json
{
  "owner": "unitagain",
  "repo": "TideScope",
  "badges": {
    "recommended": {
      "url": "https://tidescope.vercel.app/api/badge/unitagain/TideScope/recommended.svg",
      "markdown": "[![Recommended Badge](...)](...)"
    },
    ...
  },
  "usage_count": 5
}
```

---

### POST /api/badge/clear-cache/{owner}/{repo}

Clear badge cache for a repository (force refresh).

**Response:**
```json
{
  "success": true,
  "owner": "unitagain",
  "repo": "TideScope",
  "cleared_badges": ["recommended", "health", "beginner", "distribution", "activity"]
}
```

---

## 🐛 Troubleshooting

### Badge shows "Analysis in progress"

**Cause:** First request is being processed (LLM analysis takes 10-15 seconds)

**Solution:** Refresh the page after 15 seconds

---

### Badge shows "No issues found"

**Cause:** Repository has no open issues or GITHUB_TOKEN is not set

**Solution:**
1. Check if repository has open issues
2. Verify GITHUB_TOKEN is set correctly
3. Ensure token has `public_repo` scope

---

### Badge not updating

**Cause:** CDN cache is serving old version

**Solution:**
1. Wait 24 hours for automatic refresh
2. OR use refresh parameter: `?refresh=true`
3. OR call clear-cache API endpoint

---

### LLM analysis fails

**Cause:** API key is invalid or quota exceeded

**Solution:**
1. Check API key is correct
2. Verify you have API credits
3. System will automatically fall back to rule-based analysis

---

## 🤝 Contributing

Want to improve the badge system?

1. **Add new badge types:** Edit `utils/svg_badge_generator.py`
2. **Improve analysis:** Edit `analyzer/llm_badge_analyzer.py`
3. **Optimize caching:** Edit `utils/cache_manager.py`

See `CONTRIBUTING.md` for details.

---

## 📝 License

Same as TideScope project license.

---

## 💬 Feedback

Have questions or suggestions? [Open an issue](https://github.com/unitagain/TideScope/issues) or start a [discussion](https://github.com/unitagain/TideScope/discussions).
