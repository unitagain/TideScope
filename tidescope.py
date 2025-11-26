#!/usr/bin/env python3
"""
TideScope - AI-Powered Technical Debt Analyzer

Main CLI entry point for all TideScope functionality.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TideScopeConfig:
    """Configuration manager for TideScope"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file"""
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    @property
    def owner(self) -> str:
        return self.config['repository']['owner']
    
    @property
    def repo(self) -> str:
        return self.config['repository']['name']
    
    @property
    def output_dir(self) -> Path:
        return Path(self.config['output']['report_dir'])
    
    @property
    def badge_dir(self) -> Path:
        return Path(self.config['output']['badge_dir'])
    
    @property
    def use_llm(self) -> bool:
        return self.config['analysis'].get('use_llm', False)
    
    @property
    def badge_language(self) -> str:
        return self.config['analysis'].get('badge_language', 'en')
    
    @property
    def badge_theme(self) -> str:
        return self.config['analysis'].get('badge_theme', 'light')
    
    @property
    def target_level(self) -> str:
        return self.config['badge'].get('target_level', 'all')


class TideScopeCLI:
    """Main CLI interface for TideScope"""
    
    def __init__(self):
        """Initialize TideScope CLI"""
        self.config: Optional[TideScopeConfig] = None
    
    def print_banner(self):
        """Print TideScope banner"""
        banner = """
████████╗██╗██████╗ ███████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
╚══██╔══╝██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ██║   ██║██║  ██║█████╗  ███████╗██║     ██║   ██║██████╔╝█████╗  
   ██║   ██║██║  ██║██╔══╝  ╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝  
   ██║   ██║██████╔╝███████╗███████║╚██████╗╚██████╔╝██║     ███████╗
   ╚═╝   ╚═╝╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝

        🌊 AI-Powered Technical Debt Analyzer v2.0 🌊
"""
        print(banner)
    
    def print_menu(self):
        """Print main menu"""
        print("\n📋 What would you like to generate?\n")
        print("  1️⃣  Star Map (Technical Debt Visualization)")
        print("  2️⃣  Badge System (AI-Powered Contributor Guide)")
        print("  3️⃣  Both (Complete Analysis)")
        print("  0️⃣  Exit")
        print()
    
    def load_config(self):
        """Load configuration file"""
        print("📄 Loading configuration from config.yaml...")
        
        try:
            self.config = TideScopeConfig()
            print(f"✅ Configuration loaded successfully")
            print(f"   Repository: {self.config.owner}/{self.config.repo}")
            return True
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print("\n💡 Tip: Make sure config.yaml exists in the current directory")
            return False
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    
    def check_environment(self):
        """Check environment variables"""
        print("\n🔍 Checking environment...")
        
        # Check GitHub token
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            print("  ✅ GITHUB_TOKEN is set")
        else:
            print("  ⚠️  GITHUB_TOKEN not set (analysis will use cached/mock data)")
        
        # Check LLM API keys if needed
        if self.config.use_llm:
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if deepseek_key or openai_key:
                print("  ✅ LLM API key is set")
            else:
                print("  ⚠️  LLM API key not set (will use rule-based analysis)")
        
        print()
    
    async def generate_starmap(self):
        """Generate Star Map (Technical Debt Visualization)"""
        print("\n" + "="*70)
        print(" "*20 + "⭐ Generating Star Map")
        print("="*70)
        
        try:
            from scanner.models import ScanConfig, GitHubConfig, ScanMode
            from scanner.github import fetch_github_data
            from analyzer import build_analysis_report
            from scanner.models import RawScanResult
            
            # Create output directory
            self.config.output_dir.mkdir(exist_ok=True, parents=True)
            
            # Step 1: Fetch GitHub data (Star Map focuses on GitHub issues/PRs, not code TODOs)
            print(f"\n🔍 Step 1/2: Fetching GitHub data for {self.config.owner}/{self.config.repo}...")
            
            github_config = GitHubConfig(
                owner=self.config.owner,
                repo=self.config.repo,
                token_env="GITHUB_TOKEN"
            )
            
            issues, pull_requests = fetch_github_data(github_config)
            
            print(f"✅ GitHub data fetched")
            print(f"   Issues: {len(issues)}")
            print(f"   Pull Requests: {len(pull_requests)}")
            
            # Create raw result (without code scanning for now)
            raw_result = RawScanResult(
                repository=f"{self.config.owner}/{self.config.repo}",
                code_todos=[],  # Star Map focuses on GitHub data
                issues=issues,
                pull_requests=pull_requests,
                mode=ScanMode.QUICK,
                readme=None
            )
            
            # Step 2: Generate analysis report
            print(f"\n📊 Step 2/2: Generating analysis report...")
            
            # Save raw data first
            raw_output = self.config.output_dir / "tidescope-raw.json"
            raw_output.write_text(
                raw_result.model_dump_json(indent=2, by_alias=True),
                encoding="utf-8"
            )
            
            # Build report from the saved file
            report = build_analysis_report(raw_output)
            
            report_output = self.config.output_dir / self.config.config['output']['starmap_file']
            report_output.write_text(
                report.model_dump_json(indent=2, by_alias=True),
                encoding="utf-8"
            )
            
            print("\n" + "="*70)
            print(" "*25 + "✅ Star Map Complete!")
            print("="*70)
            print(f"\n📁 Files generated:")
            print(f"   Raw data: {raw_output}")
            print(f"   Report: {report_output}")
            print(f"\n📊 Summary:")
            print(f"   Repository: {report.repository}")
            print(f"   Total Debt Items: {len(report.debts)}")
            print(f"   Issues: {len([d for d in report.debts if d.source_type == 'issue'])}")
            print(f"   Pull Requests: {len([d for d in report.debts if d.source_type == 'pr'])}")
            print(f"   Code TODOs: {len([d for d in report.debts if d.source_type == 'todo'])}")
            if hasattr(report, 'star_map') and report.star_map:
                print(f"   Star Map: ✅ Generated")
            
        except ImportError as e:
            print("⚠️  Star Map generation requires full scanner installation")
            print(f"   Missing: {e}")
            print("   Run: pip install -r requirements.txt")
        except Exception as e:
            logger.error(f"Star Map generation failed: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
    
    async def generate_badges(self):
        """Generate Badge System (Complete set)"""
        print("\n" + "="*70)
        print(" "*18 + "🎨 Generating Badge System")
        print("="*70)
        
        try:
            from analyzer.smart_analyzer import smart_analyzer
            from utils.hero_badge_generator import HeroBadgeGenerator
            from utils.analysis_panel_generator import (
                HealthPanelGenerator,
                TrendsPanelGenerator,
                SkillsDistributionGenerator
            )
            
            # Create output directories
            badge_dir = self.config.badge_dir
            badge_dir.mkdir(exist_ok=True, parents=True)
            
            assets_dir = badge_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Step 1: Analyze repository
            print(f"\n🔍 Step 1/4: Analyzing {self.config.owner}/{self.config.repo}...")
            analysis = await smart_analyzer.analyze(
                self.config.owner,
                self.config.repo,
                self.config.target_level
            )
            
            if analysis.get('error'):
                print(f"⚠️  Analysis had issues, using fallback data")
            else:
                print(f"✅ Analysis complete (Method: {analysis.get('analysis_method', 'unknown')})")
                print(f"   Health Score: {analysis.get('health_score', 0)}/100")
                print(f"   Open Issues: {analysis.get('open_count', 0)}")
                print(f"   Beginner Tasks: {len(analysis.get('beginner_tasks', []))}")
            
            # Step 2: Generate SVG badges
            print(f"\n🎨 Step 2/4: Generating SVG badges...")
            
            recommended = analysis.get('recommended_task', {})
            
            # Hero Badge
            hero_svg = HeroBadgeGenerator.generate(
                task_title=recommended.get('title', 'Check CONTRIBUTING.md for tasks'),
                difficulty=recommended.get('difficulty', 'Entry'),
                time_estimate=recommended.get('time_estimate', 'Various'),
                impact=recommended.get('impact', 'Medium'),
                skills=recommended.get('skills', []),
                theme=self.config.badge_theme,
                lang=self.config.badge_language
            )
            (assets_dir / "hero_badge.svg").write_text(hero_svg, encoding='utf-8')
            print("  ✅ hero_badge.svg")
            
            # Health Panel
            if self.config.config['badge'].get('generate_health_panel', True):
                health_svg = HealthPanelGenerator.generate(
                    health_score=analysis.get('health_score', 50),
                    trend=analysis.get('trend', 0),
                    active_count=analysis.get('active_count', 0),
                    stale_count=analysis.get('stale_count', 0),
                    urgent_count=analysis.get('urgent_count', 0),
                    in_progress=analysis.get('in_progress', 0)
                )
                (assets_dir / "health_panel.svg").write_text(health_svg, encoding='utf-8')
                print("  ✅ health_panel.svg")
            
            # Trends Panel
            if self.config.config['badge'].get('generate_trends_panel', True):
                trends_svg = TrendsPanelGenerator.generate(
                    issues_opened=[10, 15, 12, 18, 14, 20],
                    issues_closed=[8, 12, 15, 16, 13, 19]
                )
                (assets_dir / "trends_panel.svg").write_text(trends_svg, encoding='utf-8')
                print("  ✅ trends_panel.svg")
            
            # Skills Panel
            if self.config.config['badge'].get('generate_skills_panel', True):
                skills_data = analysis.get('skills_distribution', {})
                if not skills_data:
                    skills_data = {'Various': 1}
                
                skills_svg = SkillsDistributionGenerator.generate(skills_data)
                (assets_dir / "skills_panel.svg").write_text(skills_svg, encoding='utf-8')
                print("  ✅ skills_panel.svg")
            
            # Step 3: Generate README.md
            print(f"\n📝 Step 3/4: Generating README.md...")
            readme_content = self._generate_readme(analysis)
            (badge_dir / "README.md").write_text(readme_content, encoding='utf-8')
            print("  ✅ README.md")
            
            # Step 4: Generate CONTRIBUTING.md
            print(f"\n📝 Step 4/4: Generating CONTRIBUTING.md...")
            from scripts.generate_contributing import ContributingGenerator
            contributing_content = await ContributingGenerator.generate(
                self.config.owner,
                self.config.repo,
                badge_dir
            )
            (badge_dir / "CONTRIBUTING.md").write_text(contributing_content, encoding='utf-8')
            print("  ✅ CONTRIBUTING.md")
            
            # Generate summary
            print("\n" + "="*70)
            print(" "*23 + "✅ Badge System Complete!")
            print("="*70)
            print(f"\n📁 Files generated in: {badge_dir.absolute()}")
            print("\n📂 Structure:")
            print("  ├── README.md")
            print("  ├── CONTRIBUTING.md")
            print("  └── assets/")
            print("      ├── hero_badge.svg")
            print("      ├── health_panel.svg")
            print("      ├── trends_panel.svg")
            print("      └── skills_panel.svg")
            
            print("\n📖 Next Steps:")
            print(f"  1. Review the generated files in {badge_dir}/")
            print(f"  2. Copy README.md and CONTRIBUTING.md to your repository root")
            print(f"  3. Copy assets/ folder to your repository (e.g., .github/assets/)")
            print(f"  4. Update image paths in the markdown files if needed")
            print(f"  5. Commit and push to GitHub!")
            
        except Exception as e:
            logger.error(f"Badge generation failed: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
    
    def _generate_readme(self, analysis: dict) -> str:
        """Generate README.md content"""
        recommended = analysis.get('recommended_task', {})
        
        return f"""# {self.config.repo}

<div align="center">

### 🚀 AI-Powered Contributor Experience

[![TideScope Analysis](./assets/hero_badge.svg)](./CONTRIBUTING.md)

**Health: {analysis.get('health_score', 50)}/100** • **{analysis.get('open_count', 0)} Open Issues** • **{len(analysis.get('beginner_tasks', []))} Beginner Tasks**

[Getting Started](#getting-started) • [Contributing](./CONTRIBUTING.md) • [Documentation](#documentation)

</div>

---

## 🎯 Perfect Task For You

> **AI Recommendation**: Based on current project needs

**[#{recommended.get('number', '')} {recommended.get('title', 'Check CONTRIBUTING.md for available tasks')}]({recommended.get('url', './CONTRIBUTING.md')})**

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
    
    # Note: _generate_contributing() removed - now using ContributingGenerator from scripts/
    
    async def run(self):
        """Run TideScope CLI"""
        self.print_banner()
        
        # Load configuration
        if not self.load_config():
            return 1
        
        # Check environment
        self.check_environment()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("👉 Select an option (0-3): ").strip()
                
                if choice == '0':
                    print("\n👋 Goodbye!")
                    return 0
                
                elif choice == '1':
                    await self.generate_starmap()
                    input("\n✅ Press Enter to continue...")
                
                elif choice == '2':
                    await self.generate_badges()
                    input("\n✅ Press Enter to continue...")
                
                elif choice == '3':
                    await self.generate_starmap()
                    await self.generate_badges()
                    input("\n✅ Press Enter to continue...")
                
                else:
                    print("\n❌ Invalid option. Please choose 0-3.")
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                return 1
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point"""
    cli = TideScopeCLI()
    return asyncio.run(cli.run())


if __name__ == '__main__':
    sys.exit(main())
