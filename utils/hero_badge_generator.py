"""
Hero Badge Generator for TideScope v2

Generates large, visually appealing card-style badges that serve as
the main entry point in README files. Hero badges display AI-recommended
tasks with rich visual design and clear call-to-action.

Design Specifications:
- Size: 550px × 180px (prominent but not overwhelming)
- Style: Card-like with gradients, shadows, and rounded corners
- Colors: Dynamic based on task difficulty/urgency
- Interaction: Clickable, links to CONTRIBUTING.md
"""

from typing import Dict, Optional
from datetime import datetime


class HeroBadgeGenerator:
    """Generator for Hero Badge - the flagship badge of TideScope v2"""
    
    # Color schemes for different difficulty levels
    DIFFICULTY_COLORS = {
        'Entry': {
            'gradient_start': '#10b981',  # Green
            'gradient_end': '#34d399',
            'accent': '#059669'
        },
        'Intermediate': {
            'gradient_start': '#f59e0b',  # Orange
            'gradient_end': '#fbbf24',
            'accent': '#d97706'
        },
        'Advanced': {
            'gradient_start': '#ef4444',  # Red
            'gradient_end': '#f87171',
            'accent': '#dc2626'
        }
    }
    
    # Translations for different languages
    TRANSLATIONS = {
        'en': {
            'ai_analysis': 'TideScope AI Analysis',
            'best_task': 'BEST TASK FOR YOU',
            'level': 'Level',
            'impact': 'Impact',
            'skills': 'Skills',
            'trending': 'trending this week',
            'similar': 'similar tasks',
            'view_full': 'View Full Analysis',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        },
        'zh': {
            'ai_analysis': 'TideScope AI 分析',
            'best_task': '最适合你的任务',
            'level': '难度',
            'impact': '影响力',
            'skills': '技能要求',
            'trending': '本周热度',
            'similar': '相似任务',
            'view_full': '查看完整分析',
            'high': '高',
            'medium': '中',
            'low': '低'
        }
    }
    
    @staticmethod
    def generate(
        task_title: str,
        difficulty: str = 'Entry',
        time_estimate: str = '2-3h',
        impact: str = 'High',
        skills: list = None,
        trending_stars: int = 0,
        similar_count: int = 0,
        theme: str = 'light',
        lang: str = 'en'
    ) -> str:
        """
        Generate Hero Badge SVG
        
        Args:
            task_title: Title of the recommended task
            difficulty: Entry | Intermediate | Advanced
            time_estimate: Estimated time (e.g., "2-3h")
            impact: High | Medium | Low
            skills: List of required skills (max 3 shown)
            trending_stars: Number of stars gained this week
            similar_count: Number of similar available tasks
            theme: light | dark
            lang: en | zh | ja | es
            
        Returns:
            SVG string for the Hero Badge
        """
        
        # Get color scheme
        colors = HeroBadgeGenerator.DIFFICULTY_COLORS.get(
            difficulty,
            HeroBadgeGenerator.DIFFICULTY_COLORS['Entry']
        )
        
        # Get translations
        t = HeroBadgeGenerator.TRANSLATIONS.get(
            lang,
            HeroBadgeGenerator.TRANSLATIONS['en']
        )
        
        # Process skills (max 3)
        skills_text = ', '.join(skills[:3]) if skills else 'Various'
        
        # Truncate task title if too long
        max_title_length = 45
        display_title = (
            task_title[:max_title_length] + '...'
            if len(task_title) > max_title_length
            else task_title
        )
        
        # Translate impact
        impact_translated = t.get(impact.lower(), impact)
        
        # Theme-specific adjustments
        if theme == 'dark':
            bg_overlay = '<rect width="550" height="180" rx="12" fill="#000" opacity="0.2"/>'
        else:
            bg_overlay = ''
        
        svg = f'''<svg width="550" height="180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradient background -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['gradient_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{colors['gradient_end']};stop-opacity:1" />
    </linearGradient>
    
    <!-- Shadow filter -->
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.25"/>
    </filter>
    
    <!-- Button hover effect (optional, for interactive SVG) -->
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Main card background -->
  <rect width="550" height="180" rx="12" fill="url(#bgGradient)" filter="url(#shadow)"/>
  {bg_overlay}
  
  <!-- Brand header -->
  <g opacity="0.95">
    <text x="20" y="28" fill="#ffffff" font-size="13" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
      🤖 {t['ai_analysis']}
    </text>
  </g>
  
  <!-- Separator line -->
  <line x1="20" y1="42" x2="530" y2="42" stroke="#ffffff" stroke-width="1" opacity="0.25"/>
  
  <!-- Section: Best Task Label -->
  <g>
    <text x="20" y="68" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui, -apple-system, sans-serif" letter-spacing="0.5" opacity="0.9">
      🎯 {t['best_task'].upper()}
    </text>
  </g>
  
  <!-- Task title (main content) -->
  <g>
    <text x="20" y="96" fill="#ffffff" font-size="18" font-weight="bold" font-family="system-ui, -apple-system, sans-serif">
      {display_title}
    </text>
  </g>
  
  <!-- Metadata row -->
  <g opacity="0.95">
    <!-- Difficulty -->
    <text x="20" y="122" fill="#ffffff" font-size="13" font-family="system-ui, -apple-system, sans-serif">
      ⚡ {difficulty}
    </text>
    
    <!-- Time estimate -->
    <text x="130" y="122" fill="#ffffff" font-size="13" font-family="system-ui, -apple-system, sans-serif">
      ⏱ {time_estimate}
    </text>
    
    <!-- Impact -->
    <text x="220" y="122" fill="#ffffff" font-size="13" font-family="system-ui, -apple-system, sans-serif">
      🎯 {impact_translated} {t['impact']}
    </text>
  </g>
  
  <!-- Skills row -->
  <g opacity="0.9">
    <text x="20" y="145" fill="#ffffff" font-size="12" font-family="system-ui, -apple-system, sans-serif">
      💼 {t['skills']}: {skills_text}
    </text>
  </g>
  
  <!-- Bottom section: Stats and CTA -->
  <g opacity="0.85">
    <!-- Trending info (if available) -->
    {f'<text x="400" y="122" fill="#ffd700" font-size="12" font-weight="600" font-family="system-ui, -apple-system, sans-serif">🔥 +{trending_stars}★ {t["trending"]}</text>' if trending_stars > 0 else ''}
    
    <!-- Similar tasks count (if available) -->
    {f'<text x="400" y="142" fill="#ffffff" font-size="11" font-family="system-ui, -apple-system, sans-serif">👥 {similar_count} {t["similar"]}</text>' if similar_count > 0 else ''}
  </g>
  
  <!-- Call-to-action button area -->
  <g>
    <!-- Button background (semi-transparent) -->
    <rect x="20" y="158" width="180" height="16" rx="4" fill="#ffffff" opacity="0.2"/>
    
    <!-- Button text -->
    <text x="28" y="170" fill="#ffffff" font-size="11" font-weight="600" font-family="system-ui, -apple-system, sans-serif">
      📊 {t['view_full']} →
    </text>
  </g>
  
  <!-- Branding (bottom right) -->
  <g opacity="0.6">
    <text x="430" y="172" fill="#ffffff" font-size="9" font-family="system-ui, -apple-system, sans-serif">
      Powered by TideScope
    </text>
  </g>
</svg>'''
        
        return svg
    
    @staticmethod
    def generate_loading() -> str:
        """Generate a loading state badge"""
        return '''<svg width="550" height="180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="loadingGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#8b5cf6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#6366f1;stop-opacity:1" />
      <animate attributeName="x1" values="0%;100%" dur="2s" repeatCount="indefinite" />
      <animate attributeName="x2" values="100%;200%" dur="2s" repeatCount="indefinite" />
    </linearGradient>
  </defs>
  
  <rect width="550" height="180" rx="12" fill="url(#loadingGradient)"/>
  
  <text x="275" y="90" fill="#ffffff" font-size="16" font-weight="600" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif">
    🤖 AI Analysis in Progress...
  </text>
  
  <text x="275" y="115" fill="#ffffff" opacity="0.8" font-size="12" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif">
    This may take 10-15 seconds
  </text>
</svg>'''
    
    @staticmethod
    def generate_error(error_message: str = "Analysis failed") -> str:
        """Generate an error state badge"""
        return f'''<svg width="550" height="180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="errorGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#dc2626;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect width="550" height="180" rx="12" fill="url(#errorGradient)"/>
  
  <text x="275" y="80" fill="#ffffff" font-size="16" font-weight="600" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif">
    ⚠️ {error_message}
  </text>
  
  <text x="275" y="105" fill="#ffffff" opacity="0.9" font-size="12" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif">
    Please try again later or check repository visibility
  </text>
  
  <text x="275" y="135" fill="#ffffff" opacity="0.7" font-size="10" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif">
    Having issues? Visit tidescope.dev/support
  </text>
</svg>'''


# Quick test function
if __name__ == "__main__":
    # Test Hero Badge generation
    svg = HeroBadgeGenerator.generate(
        task_title="Fix Slow Frontend - Add Caching Layer",
        difficulty="Entry",
        time_estimate="2-3h",
        impact="High",
        skills=["React", "Redis", "TypeScript"],
        trending_stars=15,
        similar_count=3,
        theme="light",
        lang="en"
    )
    
    print("✅ Hero Badge generated successfully!")
    print(f"Length: {len(svg)} characters")
    
    # Save test output
    with open("test_hero_badge.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("📁 Saved to: test_hero_badge.svg")
