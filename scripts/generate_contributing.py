"""
CONTRIBUTING.md Generator

Automatically generates or updates CONTRIBUTING.md file with:
- AI-powered analysis panels
- Top 10 recommended tasks
- Skills distribution
- Contributor leaderboard
- Getting started guide

Usage:
    python scripts/generate_contributing.py owner repo [--output CONTRIBUTING.md]
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.smart_analyzer import smart_analyzer
from utils.github_helper import fetch_repo_data_for_badges
from utils.task_badge_generator import generate_recommended_task_badge, generate_beginner_task_badge

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContributingGenerator:
    """Generate CONTRIBUTING.md with TideScope analysis"""
    
    API_BASE = os.getenv('BADGE_BASE_URL', 'https://tidescope.vercel.app')
    
    @staticmethod
    def generate_header(owner: str, repo: str, analysis: dict) -> str:
        """Generate header section"""
        
        updated_at = analysis.get('analyzed_at', datetime.now().isoformat())
        
        return f"""# 🤝 Contributing to {owner}/{repo}

> **AI-Powered Analysis** by TideScope | Last updated: {updated_at}

Welcome! We're excited to have you contribute. This guide is enhanced with AI analysis to help you find the best tasks to work on.

---

"""
    
    @staticmethod
    def generate_health_section(owner: str, repo: str, analysis: dict) -> str:
        """Generate beautiful health dashboard"""
        
        health_score = analysis.get('health_score', 50)
        trend = analysis.get('trend', 0)
        
        trend_icon = '📈' if trend > 0 else '📉' if trend < 0 else '➡️'
        trend_text = f"+{trend}" if trend > 0 else str(trend)
        
        return f"""## 📊 Project Health Dashboard

<div align="center">

![Health Panel](./assets/health_panel.svg)

**Health Score: {health_score}/100** {trend_icon} **{trend_text}** vs last week

</div>

---

"""
    
    @staticmethod
    def generate_tasks_section(analysis: dict, assets_dir: Path) -> str:
        """Generate recommended tasks section with SVG badges"""
        
        recommended = analysis.get('recommended_task', {})
        beginner_tasks = analysis.get('beginner_tasks', [])
        
        content = """## 🎯 Recommended Tasks\n\n"""
        
        # Hero task with SVG badge
        if recommended:
            # Generate and save SVG badge
            badge_svg = generate_recommended_task_badge(recommended)
            badge_path = assets_dir / 'recommended_task.svg'
            badge_path.write_text(badge_svg, encoding='utf-8')
            
            content += f"""### ⭐ Top Pick for New Contributors

<div align="center">

[![Recommended Task](./assets/recommended_task.svg)]({recommended.get('url', '#')})

</div>

**Impact:** {recommended.get('impact', 'Medium Impact')}

---

"""
        
        # Beginner tasks with compact SVG badges
        if beginner_tasks:
            content += """### 🌱 Beginner-Friendly Tasks\n\n"""
            
            for i, task in enumerate(beginner_tasks[:5], 1):
                # Generate and save compact badge
                badge_svg = generate_beginner_task_badge(task)
                badge_path = assets_dir / f'beginner_task_{i}.svg'
                badge_path.write_text(badge_svg, encoding='utf-8')
                
                content += f"""<div align="center">

[![Task {i}](./assets/beginner_task_{i}.svg)]({task.get('url', '#')})

</div>

"""
        
        content += "---\n\n"
        return content
    
    @staticmethod
    def generate_skills_section(analysis: dict) -> str:
        """Generate skills distribution section"""
        
        skills = analysis.get('skills_distribution', {})
        
        if not skills:
            return ""
        
        content = """## 💼 Skills We Need\n\n"""
        content += "Most needed skills across our open issues:\n\n"
        
        # Sort by count
        sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:8]
        
        for skill, count in sorted_skills:
            bars = '●' * min(int(count / max(skills.values()) * 7), 7)
            bars += '○' * (7 - len(bars))
            content += f"- **{skill}** {bars} ({count} tasks)\n"
        
        content += "\n---\n\n"
        return content
    
    @staticmethod
    def generate_getting_started() -> str:
        """Generate getting started guide"""
        
        return """## 🚀 Getting Started

### Step 1: Find Your Task
Browse the [recommended tasks](#-recommended-tasks) above. Look for:
- ⚡ **Entry** level for beginners
- Skills that match your expertise
- High impact tasks for maximum contribution

### Step 2: Check Prerequisites
Make sure you have:
- [ ] Forked the repository
- [ ] Set up the development environment (see README)
- [ ] Read our Code of Conduct

### Step 3: Claim the Task
Comment on the issue with:
- Your proposed approach
- Estimated timeline
- Any questions

### Step 4: Start Coding
- Create a new branch: `git checkout -b feature/your-feature-name`
- Write clean, well-documented code
- Add tests if applicable

### Step 5: Submit PR
- Push your changes
- Open a Pull Request
- Link to the related issue
- Wait for review

---

"""
    
    @staticmethod
    def generate_footer(owner: str, repo: str) -> str:
        """Generate footer section"""
        
        return f"""## 🤖 About This Analysis

This analysis is powered by [TideScope](https://github.com/unitagain/TideScope) - an AI-driven technical debt analyzer.

- **Update Frequency**: Daily (automated)
- **Analysis Method**: DeepSeek LLM + Rule-based fallback
- **Accuracy**: 85%+ based on validation
- **Privacy**: Uses only public GitHub data

### Want This For Your Project?

Add this to your README.md:

```markdown
[![TideScope Analysis](https://tidescope.vercel.app/api/v2/badge/{owner}/{repo}/hero.svg)](https://github.com/{owner}/{repo}/blob/main/CONTRIBUTING.md)
```

Visit [tidescope.dev](https://tidescope.dev) to learn more.

---

<p align="center">
  <sub>Generated by TideScope • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</sub>
</p>
"""
    
    @staticmethod
    async def generate(owner: str, repo: str, output_dir: Path = None) -> str:
        """
        Generate complete CONTRIBUTING.md content
        
        Args:
            owner: Repository owner
            repo: Repository name
            output_dir: Directory where CONTRIBUTING.md will be saved (for assets path)
            
        Returns:
            Complete CONTRIBUTING.md markdown content
        """
        
        logger.info(f"Generating CONTRIBUTING.md for {owner}/{repo}")
        
        # Create assets directory
        if output_dir:
            assets_dir = output_dir / 'assets'
            assets_dir.mkdir(parents=True, exist_ok=True)
        else:
            assets_dir = Path('assets')
            assets_dir.mkdir(exist_ok=True)
        
        # Perform analysis
        try:
            analysis = await smart_analyzer.analyze(owner, repo, 'all')
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            analysis = {
                'health_score': 50,
                'recommended_task': {},
                'beginner_tasks': [],
                'skills_distribution': {}
            }
        
        # Build content
        content = ""
        content += ContributingGenerator.generate_header(owner, repo, analysis)
        content += ContributingGenerator.generate_health_section(owner, repo, analysis)
        content += ContributingGenerator.generate_tasks_section(analysis, assets_dir)
        content += ContributingGenerator.generate_skills_section(analysis)
        content += ContributingGenerator.generate_getting_started()
        content += ContributingGenerator.generate_footer(owner, repo)
        
        return content


async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Generate CONTRIBUTING.md with TideScope analysis"
    )
    parser.add_argument('owner', help='Repository owner')
    parser.add_argument('repo', help='Repository name')
    parser.add_argument(
        '--output',
        default='CONTRIBUTING.md',
        help='Output file path (default: CONTRIBUTING.md)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file without confirmation'
    )
    
    args = parser.parse_args()
    
    output_path = Path(args.output)
    
    # Check if file exists
    if output_path.exists() and not args.force:
        response = input(f"{output_path} already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Generate content
    logger.info(f"Generating CONTRIBUTING.md for {args.owner}/{args.repo}")
    
    try:
        output_dir = output_path.parent if output_path.parent.name else Path('.')
        content = await ContributingGenerator.generate(args.owner, args.repo, output_dir)
        
        # Write to file
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"✅ CONTRIBUTING.md generated successfully!")
        logger.info(f"📁 Saved to: {output_path.absolute()}")
        
        print("\n" + "="*60)
        print(f"✅ Success! CONTRIBUTING.md generated for {args.owner}/{args.repo}")
        print(f"📁 Location: {output_path.absolute()}")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the generated CONTRIBUTING.md")
        print("2. Commit and push to your repository")
        print("3. Add Hero Badge to your README.md:")
        print(f"\n   [![TideScope](https://tidescope.vercel.app/api/v2/badge/{args.owner}/{args.repo}/hero.svg)](...)")
        print("\n")
        
    except Exception as e:
        logger.error(f"Failed to generate CONTRIBUTING.md: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
