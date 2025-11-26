#!/usr/bin/env python
"""Generate badge system for a GitHub repository.

Usage:
    python generate_badges.py owner/repo [--output badges/]
    
Example:
    python generate_badges.py MODSetter/SurfSense --output badges/
"""

import asyncio
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from scripts.generate_contributing import ContributingGenerator
from utils.hero_badge_generator import HeroBadgeGenerator
from utils.analysis_panel_generator import HealthPanelGenerator, TrendsPanelGenerator, SkillsDistributionGenerator

# Load environment variables from .env file
load_dotenv()

async def generate_all_badges(owner: str, repo: str, output_dir: Path):
    """Generate complete badge system.
    
    Args:
        owner: Repository owner
        repo: Repository name
        output_dir: Output directory for badges
    """
    output_dir = Path(output_dir)
    assets_dir = output_dir / 'assets'
    
    # Create directories
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"  🎨 Generating Badge System for {owner}/{repo}")
    print(f"{'='*70}\n")
    
    # Step 1: Generate CONTRIBUTING.md with task badges
    print("📝 Step 1/5: Generating CONTRIBUTING.md...")
    try:
        content = await ContributingGenerator.generate(owner, repo, output_dir)
        contributing_path = output_dir / 'CONTRIBUTING.md'
        contributing_path.write_text(content, encoding='utf-8')
        print(f"   ✅ {contributing_path}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 2: Generate README.md (simplified)
    print("\n📝 Step 2/5: Generating README.md...")
    try:
        # Import analysis data from CONTRIBUTING generation
        from analyzer.smart_analyzer import smart_analyzer
        analysis = await smart_analyzer.analyze(owner, repo, 'all')
        
        recommended = analysis.get('recommended_task', {})
        health_score = analysis.get('health_score', 50)
        open_count = analysis.get('open_count', 0)
        beginner_count = analysis.get('beginner_task_count', 0)
        
        readme_content = f"""# {repo}

<div align="center">

### 🚀 AI-Powered Contributor Experience

[![TideScope Analysis](./assets/hero_badge.svg)](./CONTRIBUTING.md)

**Health: {health_score}/100** • **{open_count} Open Issues** • **{beginner_count} Beginner Tasks**

[Getting Started](#getting-started) • [Contributing](./CONTRIBUTING.md) • [Documentation](#documentation)

</div>

---

## 🎯 Perfect Task For You

> **AI Recommendation**: Based on current project needs

**[#{recommended.get('number', '')} {recommended.get('title', 'Check CONTRIBUTING.md')}]({recommended.get('url', './CONTRIBUTING.md')})**

- ⚡ **Difficulty**: {recommended.get('difficulty', 'Entry')}
- ⏱️ **Time**: {recommended.get('time_estimate', 'Varies')}
- 🎯 **Impact**: {recommended.get('impact', 'Medium')}
- 💼 **Skills**: {', '.join(recommended.get('skills', ['Various']))}

👉 **[See all tasks in CONTRIBUTING.md](./CONTRIBUTING.md)**

---

## 📖 About This Project

[Add your project description here]

---

## 🤝 Contributing

We love contributions! Check our [**AI-powered contribution guide**](./CONTRIBUTING.md) to find the perfect task.

---

## 📄 License

[Add license information here]

---

<div align="center">

**Powered by [TideScope](https://github.com/unitagain/TideScope)** - AI-driven project health analyzer

</div>
"""
        
        readme_path = output_dir / 'README.md'
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"   ✅ {readme_path}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 3: Generate SVG panels
    print("\n🎨 Step 3/5: Generating analysis panels...")
    try:
        from analyzer.smart_analyzer import smart_analyzer
        analysis = await smart_analyzer.analyze(owner, repo, 'all')
        
        # Health panel
        health_svg = HealthPanelGenerator.generate(
            health_score=analysis.get('health_score', 50),
            trend=analysis.get('trend', 0),
            active_count=analysis.get('active_count', 0),
            stale_count=analysis.get('stale_count', 0),
            urgent_count=analysis.get('urgent_count', 0)
        )
        (assets_dir / 'health_panel.svg').write_text(health_svg, encoding='utf-8')
        print("   ✅ health_panel.svg")
        
        # Trends panel
        trends_svg = TrendsPanelGenerator.generate(
            issues_opened=analysis.get('issues_opened_trend', [0]*6),
            issues_closed=analysis.get('issues_closed_trend', [0]*6),
            months=None  # Will use default
        )
        (assets_dir / 'trends_panel.svg').write_text(trends_svg, encoding='utf-8')
        print("   ✅ trends_panel.svg")
        
        # Skills panel
        skills_data = analysis.get('skills_distribution', {})
        if skills_data:
            skills_svg = SkillsDistributionGenerator.generate(skills_data)
            (assets_dir / 'skills_panel.svg').write_text(skills_svg, encoding='utf-8')
            print("   ✅ skills_panel.svg")
        else:
            print("   ⚠️  skills_panel.svg (no data)")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 4: Generate hero badge
    print("\n🎨 Step 4/5: Generating hero badge...")
    try:
        from analyzer.smart_analyzer import smart_analyzer
        analysis = await smart_analyzer.analyze(owner, repo, 'all')
        
        recommended = analysis.get('recommended_task', {})
        hero_svg = HeroBadgeGenerator.generate(
            task_title=recommended.get('title', 'No tasks available'),
            difficulty=recommended.get('difficulty', 'Entry'),
            time_estimate=recommended.get('time_estimate', 'Unknown'),
            impact=recommended.get('impact', 'Medium'),
            skills=recommended.get('skills', ['General']),
            lang='en'
        )
        (assets_dir / 'hero_badge.svg').write_text(hero_svg, encoding='utf-8')
        print("   ✅ hero_badge.svg")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 5: Create preview HTML
    print("\n📝 Step 5/5: Creating preview...")
    try:
        preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{owner}/{repo} - TideScope Badge Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{ color: #2d3748; }}
        .preview {{ margin: 20px 0; text-align: center; }}
        img {{ max-width: 100%; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 {owner}/{repo} - Badge Preview</h1>
        
        <h2>Hero Badge</h2>
        <div class="preview">
            <img src="./assets/hero_badge.svg" alt="Hero Badge">
        </div>
        
        <h2>📊 Health Panel</h2>
        <div class="preview">
            <img src="./assets/health_panel.svg" alt="Health Panel">
        </div>
        
        <h2>📈 Trends Panel</h2>
        <div class="preview">
            <img src="./assets/trends_panel.svg" alt="Trends Panel">
        </div>
        
        <h2>💼 Skills Panel</h2>
        <div class="preview">
            <img src="./assets/skills_panel.svg" alt="Skills Panel">
        </div>
        
        <h2>🎯 Recommended Task</h2>
        <div class="preview">
            <img src="./assets/recommended_task.svg" alt="Recommended Task">
        </div>
        
        <h2>🌱 Beginner Tasks</h2>
        <div class="preview">
            <img src="./assets/beginner_task_1.svg" alt="Beginner Task 1">
        </div>
        <div class="preview">
            <img src="./assets/beginner_task_2.svg" alt="Beginner Task 2">
        </div>
        
        <p style="text-align: center; margin-top: 40px; color: #718096;">
            Generated by <strong>TideScope</strong>
        </p>
    </div>
</body>
</html>"""
        
        preview_path = output_dir / 'PREVIEW.html'
        preview_path.write_text(preview_html, encoding='utf-8')
        print(f"   ✅ {preview_path}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  ✅ Badge System Generated Successfully!")
    print(f"{'='*70}\n")
    print(f"📁 Output directory: {output_dir.absolute()}\n")
    print("📂 Generated files:")
    print(f"   ├── README.md")
    print(f"   ├── CONTRIBUTING.md")
    print(f"   ├── PREVIEW.html")
    print(f"   └── assets/")
    print(f"       ├── hero_badge.svg")
    print(f"       ├── health_panel.svg")
    print(f"       ├── trends_panel.svg")
    print(f"       ├── skills_panel.svg")
    print(f"       ├── recommended_task.svg")
    print(f"       ├── beginner_task_1.svg")
    print(f"       └── beginner_task_2.svg")
    print(f"\n👉 Open PREVIEW.html in your browser to view the badges!")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate TideScope badge system")
    parser.add_argument('repo', help='Repository in format owner/repo (e.g., MODSetter/SurfSense)')
    parser.add_argument('--output', default='badges', help='Output directory (default: badges/)')
    
    args = parser.parse_args()
    
    # Parse owner/repo
    if '/' not in args.repo:
        print("❌ Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    owner, repo = args.repo.split('/', 1)
    
    # Run generation
    success = asyncio.run(generate_all_badges(owner, repo, Path(args.output)))
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
