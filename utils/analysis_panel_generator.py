"""
Analysis Panel Generators for CONTRIBUTING.md

These generators create rich, data-dense SVG panels that display
project health, trends, and statistics for the CONTRIBUTING.md page.

Panels include:
- Health Dashboard: Overall project health score with breakdown
- Trends Chart: Historical issue/PR activity over time
- Skills Distribution: Most needed skills visualization
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta


class HealthPanelGenerator:
    """Generate health dashboard panel for project overview"""
    
    @staticmethod
    def generate(
        health_score: int,
        trend: int,
        active_count: int,
        stale_count: int,
        urgent_count: int,
        in_progress: int = 0,
        updated_at: str = None
    ) -> str:
        """
        Generate health dashboard panel
        
        Args:
            health_score: Overall health score (0-100)
            trend: Change vs last week (+5, -3, etc)
            active_count: Issues active this week
            stale_count: Issues stale (>90 days)
            urgent_count: Critical/urgent issues
            in_progress: Tasks currently being worked on
            updated_at: ISO timestamp of last update
            
        Returns:
            SVG string for health panel
        """
        
        # Determine color based on score
        if health_score >= 80:
            score_color = '#10b981'  # Green
            status_text = 'Excellent'
        elif health_score >= 60:
            score_color = '#f59e0b'  # Orange
            status_text = 'Good'
        else:
            score_color = '#ef4444'  # Red
            status_text = 'Needs Attention'
        
        # Calculate progress circle
        # SVG circle: circumference = 2πr, for r=60: ~377
        circumference = 377
        progress_length = (health_score / 100) * circumference
        gap_length = circumference - progress_length
        
        # Trend arrow
        if trend > 0:
            trend_arrow = '↗'
            trend_color = '#10b981'
        elif trend < 0:
            trend_arrow = '↘'
            trend_color = '#ef4444'
        else:
            trend_arrow = '→'
            trend_color = '#6b7280'
        
        # Format updated time
        if not updated_at:
            updated_at = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        
        svg = f'''<svg width="700" height="280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .panel-bg {{ fill: #f9fafb; }}
      .title {{ font-family: system-ui, -apple-system, sans-serif; font-size: 20px; font-weight: bold; fill: #1f2937; }}
      .subtitle {{ font-family: system-ui, -apple-system, sans-serif; font-size: 14px; fill: #6b7280; }}
      .metric-label {{ font-family: system-ui, -apple-system, sans-serif; font-size: 14px; fill: #374151; }}
      .metric-value {{ font-family: system-ui, -apple-system, sans-serif; font-size: 13px; font-weight: 600; }}
      .footer {{ font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #9ca3af; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="700" height="280" rx="8" class="panel-bg"/>
  
  <!-- Title -->
  <text x="20" y="35" class="title">📊 Project Health Dashboard</text>
  <text x="20" y="55" class="subtitle">{status_text} - Keep up the momentum!</text>
  
  <!-- Main circular progress indicator -->
  <g transform="translate(120, 160)">
    <!-- Background circle -->
    <circle cx="0" cy="0" r="60" fill="none" stroke="#e5e7eb" stroke-width="12"/>
    
    <!-- Progress circle -->
    <circle cx="0" cy="0" r="60" fill="none" 
            stroke="{score_color}" 
            stroke-width="12"
            stroke-dasharray="{progress_length} {gap_length}" 
            stroke-linecap="round" 
            transform="rotate(-90)"
            style="transition: stroke-dasharray 0.5s ease;"/>
    
    <!-- Score text -->
    <text x="0" y="10" text-anchor="middle" font-size="40" font-weight="bold" fill="{score_color}" font-family="system-ui, -apple-system, sans-serif">
      {health_score}
    </text>
    <text x="0" y="28" text-anchor="middle" font-size="14" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">
      /100
    </text>
    
    <!-- Trend indicator -->
    <text x="0" y="75" text-anchor="middle" font-size="16" fill="{trend_color}" font-family="system-ui, -apple-system, sans-serif">
      {trend_arrow} {abs(trend)} this week
    </text>
  </g>
  
  <!-- Metrics section -->
  <g transform="translate(250, 90)">
    <!-- Active Issues -->
    <g>
      <circle cx="10" cy="0" r="6" fill="#10b981"/>
      <text x="25" y="5" class="metric-label">
        Active: <tspan class="metric-value" fill="#10b981">{active_count}</tspan> issues this week
      </text>
    </g>
    
    <!-- Stale Issues -->
    <g transform="translate(0, 40)">
      <circle cx="10" cy="0" r="6" fill="#f59e0b"/>
      <text x="25" y="5" class="metric-label">
        Stale: <tspan class="metric-value" fill="#f59e0b">{stale_count}</tspan> issues &gt; 90 days
      </text>
    </g>
    
    <!-- Urgent Issues -->
    <g transform="translate(0, 80)">
      <circle cx="10" cy="0" r="6" fill="#ef4444"/>
      <text x="25" y="5" class="metric-label">
        Urgent: <tspan class="metric-value" fill="#ef4444">{urgent_count}</tspan> critical bugs
      </text>
    </g>
    
    <!-- In Progress -->
    <g transform="translate(0, 120)">
      <circle cx="10" cy="0" r="6" fill="#3b82f6"/>
      <text x="25" y="5" class="metric-label">
        In Progress: <tspan class="metric-value" fill="#3b82f6">{in_progress}</tspan> tasks
      </text>
    </g>
  </g>
  
  <!-- Footer -->
  <text x="20" y="265" class="footer">
    🤖 AI-Powered Analysis • Last updated: {updated_at}
  </text>
</svg>'''
        
        return svg


class TrendsPanelGenerator:
    """Generate historical trends chart panel"""
    
    @staticmethod
    def generate(
        issues_opened: List[int],
        issues_closed: List[int],
        months: List[str] = None,
        resolution_rate: float = None
    ) -> str:
        """
        Generate trends chart panel
        
        Args:
            issues_opened: List of issues opened per period (max 6 points)
            issues_closed: List of issues closed per period (max 6 points)
            months: List of month labels (e.g., ['Jan', 'Feb', ...])
            resolution_rate: Overall resolution rate percentage
            
        Returns:
            SVG string for trends panel
        """
        
        # Ensure we have 6 data points
        issues_opened = issues_opened[-6:] if len(issues_opened) > 6 else issues_opened
        issues_closed = issues_closed[-6:] if len(issues_closed) > 6 else issues_closed
        
        # Pad with zeros if needed
        while len(issues_opened) < 6:
            issues_opened.insert(0, 0)
        while len(issues_closed) < 6:
            issues_closed.insert(0, 0)
        
        # Generate month labels if not provided
        if not months:
            now = datetime.now()
            months = []
            for i in range(5, -1, -1):
                month = (now - timedelta(days=30*i)).strftime('%b')
                months.append(month)
        
        # Calculate resolution rate if not provided
        if resolution_rate is None:
            total_opened = sum(issues_opened)
            total_closed = sum(issues_closed)
            resolution_rate = (total_closed / total_opened * 100) if total_opened > 0 else 0
        
        # Find max value for scaling
        max_value = max(max(issues_opened), max(issues_closed), 1)
        scale_factor = 150 / max_value  # Scale to fit 150px height
        
        # Generate polyline points for opened issues
        points_opened = []
        for i, value in enumerate(issues_opened):
            x = 50 + i * 100
            y = 180 - (value * scale_factor)
            points_opened.append(f"{x},{y}")
        polyline_opened = " ".join(points_opened)
        
        # Generate polyline points for closed issues
        points_closed = []
        for i, value in enumerate(issues_closed):
            x = 50 + i * 100
            y = 180 - (value * scale_factor)
            points_closed.append(f"{x},{y}")
        polyline_closed = " ".join(points_closed)
        
        # Generate month labels SVG
        month_labels = []
        for i, month in enumerate(months):
            x = 50 + i * 100
            month_labels.append(f'<text x="{x}" y="200" text-anchor="middle" font-size="11" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">{month}</text>')
        month_labels_svg = "\n    ".join(month_labels)
        
        # Generate data point circles for opened
        circles_opened = []
        for i, value in enumerate(issues_opened):
            x = 50 + i * 100
            y = 180 - (value * scale_factor)
            circles_opened.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#10b981"/>')
        circles_opened_svg = "\n    ".join(circles_opened)
        
        # Generate data point circles for closed
        circles_closed = []
        for i, value in enumerate(issues_closed):
            x = 50 + i * 100
            y = 180 - (value * scale_factor)
            circles_closed.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#3b82f6"/>')
        circles_closed_svg = "\n    ".join(circles_closed)
        
        svg = f'''<svg width="700" height="320" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .panel-bg {{ fill: #f9fafb; }}
      .title {{ font-family: system-ui, -apple-system, sans-serif; font-size: 20px; font-weight: bold; fill: #1f2937; }}
      .axis {{ stroke: #d1d5db; stroke-width: 2; }}
      .grid {{ stroke: #e5e7eb; stroke-width: 1; stroke-dasharray: 3,3; opacity: 0.5; }}
      .legend-text {{ font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #374151; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="700" height="320" rx="8" class="panel-bg"/>
  
  <!-- Title -->
  <text x="20" y="35" class="title">📈 Activity Trends (Last 6 Months)</text>
  
  <!-- Chart area -->
  <g transform="translate(30, 60)">
    <!-- Y-axis -->
    <line x1="20" y1="0" x2="20" y2="180" class="axis"/>
    <text x="10" y="5" text-anchor="end" font-size="11" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">{int(max_value)}</text>
    <text x="10" y="95" text-anchor="end" font-size="11" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">{int(max_value/2)}</text>
    <text x="10" y="185" text-anchor="end" font-size="11" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">0</text>
    
    <!-- Grid lines -->
    <line x1="20" y1="90" x2="620" y2="90" class="grid"/>
    <line x1="20" y1="180" x2="620" y2="180" class="grid"/>
    
    <!-- X-axis -->
    <line x1="20" y1="180" x2="620" y2="180" class="axis"/>
    
    <!-- Month labels -->
    {month_labels_svg}
    
    <!-- Line for opened issues (green) -->
    <polyline points="{polyline_opened}" 
              fill="none" 
              stroke="#10b981" 
              stroke-width="3" 
              stroke-linecap="round"
              stroke-linejoin="round"/>
    
    <!-- Line for closed issues (blue) -->
    <polyline points="{polyline_closed}" 
              fill="none" 
              stroke="#3b82f6" 
              stroke-width="3" 
              stroke-linecap="round"
              stroke-linejoin="round"/>
    
    <!-- Data points for opened -->
    {circles_opened_svg}
    
    <!-- Data points for closed -->
    {circles_closed_svg}
  </g>
  
  <!-- Legend -->
  <g transform="translate(50, 270)">
    <!-- Opened legend -->
    <rect x="0" y="-4" width="24" height="4" fill="#10b981" rx="2"/>
    <text x="30" y="2" class="legend-text">Opened: {sum(issues_opened)}</text>
    
    <!-- Closed legend -->
    <rect x="150" y="-4" width="24" height="4" fill="#3b82f6" rx="2"/>
    <text x="180" y="2" class="legend-text">Closed: {sum(issues_closed)}</text>
    
    <!-- Resolution rate -->
    <text x="300" y="2" class="legend-text" fill="#6b7280">
      Resolution Rate: <tspan font-weight="600" fill="#10b981">{resolution_rate:.1f}%</tspan>
    </text>
  </g>
  
  <!-- Footer -->
  <text x="20" y="310" font-size="10" fill="#9ca3af" font-family="system-ui, -apple-system, sans-serif">
    Data represents monthly aggregates • Hover for details
  </text>
</svg>'''
        
        return svg


class SkillsDistributionGenerator:
    """Generate skills distribution visualization"""
    
    @staticmethod
    def generate(skills_data: Dict[str, int], max_display: int = 8) -> str:
        """
        Generate skills distribution bar chart
        
        Args:
            skills_data: Dict of skill -> count (e.g., {'React': 15, 'Python': 10})
            max_display: Maximum number of skills to display
            
        Returns:
            SVG string for skills distribution
        """
        
        # Sort by count and take top N
        sorted_skills = sorted(skills_data.items(), key=lambda x: x[1], reverse=True)[:max_display]
        
        if not sorted_skills:
            return '<svg width="700" height="200" xmlns="http://www.w3.org/2000/svg"><text x="350" y="100" text-anchor="middle" fill="#6b7280">No skills data available</text></svg>'
        
        max_count = sorted_skills[0][1]
        total_count = sum(count for _, count in sorted_skills)
        
        # Generate bars
        bars_svg = []
        y_offset = 80
        for skill, count in sorted_skills:
            percentage = (count / total_count) * 100
            bar_width = (count / max_count) * 450
            
            bars_svg.append(f'''
    <g transform="translate(0, {y_offset})">
      <text x="20" y="0" font-size="13" fill="#374151" font-family="system-ui, -apple-system, sans-serif">{skill}</text>
      <rect x="150" y="-12" width="{bar_width}" height="20" fill="#3b82f6" rx="4"/>
      <text x="{160 + bar_width}" y="0" font-size="12" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">
        {count} ({percentage:.1f}%)
      </text>
    </g>''')
            y_offset += 35
        
        height = y_offset + 30
        bars_content = "\n".join(bars_svg)
        
        svg = f'''<svg width="700" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .panel-bg {{ fill: #f9fafb; }}
      .title {{ font-family: system-ui, -apple-system, sans-serif; font-size: 20px; font-weight: bold; fill: #1f2937; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="700" height="{height}" rx="8" class="panel-bg"/>
  
  <!-- Title -->
  <text x="20" y="35" class="title">💼 Most Needed Skills</text>
  <text x="20" y="55" font-size="13" fill="#6b7280" font-family="system-ui, -apple-system, sans-serif">
    Based on open issues and PRs
  </text>
  
  <!-- Bars -->
  {bars_content}
</svg>'''
        
        return svg


# Quick test
if __name__ == "__main__":
    # Test Health Panel
    health_svg = HealthPanelGenerator.generate(
        health_score=75,
        trend=5,
        active_count=12,
        stale_count=5,
        urgent_count=2,
        in_progress=3
    )
    
    with open("test_health_panel.svg", "w", encoding="utf-8") as f:
        f.write(health_svg)
    print("✅ Health panel saved to: test_health_panel.svg")
    
    # Test Trends Panel
    trends_svg = TrendsPanelGenerator.generate(
        issues_opened=[10, 15, 12, 18, 14, 20],
        issues_closed=[8, 12, 15, 16, 13, 19]
    )
    
    with open("test_trends_panel.svg", "w", encoding="utf-8") as f:
        f.write(trends_svg)
    print("✅ Trends panel saved to: test_trends_panel.svg")
    
    # Test Skills Distribution
    skills_svg = SkillsDistributionGenerator.generate({
        'React': 25,
        'Python': 18,
        'TypeScript': 15,
        'Docker': 12,
        'SQL': 8,
        'Redis': 6
    })
    
    with open("test_skills_panel.svg", "w", encoding="utf-8") as f:
        f.write(skills_svg)
    print("✅ Skills panel saved to: test_skills_panel.svg")
