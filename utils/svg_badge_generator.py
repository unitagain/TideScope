"""SVG badge generator for TideScope.

Generates 5 types of intelligent badges:
1. Recommended Task Badge - Shows best starting task for contributors
2. Health Score Badge - Overall project health indicator
3. Beginner Friendly Badge - Number of easy tasks available
4. Distribution Badge - Tech debt distribution by category
5. Activity Badge - Recent activity trends

All badges are designed to be:
- Visually appealing and GitHub-compatible
- Informative without being cluttered
- Responsive to dark/light themes
"""

from __future__ import annotations

from typing import Dict, List, Optional
from xml.sax.saxutils import escape


class BadgeStyle:
    """Color schemes for badges."""
    
    # Health score colors
    EXCELLENT = "#2ea44f"  # Green (80-100)
    GOOD = "#dbab09"       # Yellow (60-79)
    WARNING = "#fb8500"    # Orange (40-59)
    CRITICAL = "#cf222e"   # Red (0-39)
    
    # Category colors
    PERFORMANCE = "#0969da"
    SECURITY = "#cf222e"
    DOCS = "#8250df"
    TESTING = "#1f883d"
    REFACTOR = "#bf3989"
    FEATURE = "#fb8500"
    
    # UI colors
    BACKGROUND = "#24292f"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8b949e"
    BORDER = "#30363d"


def _escape_text(text: str) -> str:
    """Escape text for SVG."""
    return escape(text, {'"': '&quot;', "'": '&apos;'})


def _get_health_color(score: int) -> str:
    """Get color based on health score."""
    if score >= 80:
        return BadgeStyle.EXCELLENT
    elif score >= 60:
        return BadgeStyle.GOOD
    elif score >= 40:
        return BadgeStyle.WARNING
    else:
        return BadgeStyle.CRITICAL


def _get_category_color(category: str) -> str:
    """Get color for debt category."""
    category_map = {
        "performance": BadgeStyle.PERFORMANCE,
        "security": BadgeStyle.SECURITY,
        "documentation": BadgeStyle.DOCS,
        "testing": BadgeStyle.TESTING,
        "refactor": BadgeStyle.REFACTOR,
        "feature": BadgeStyle.FEATURE,
    }
    return category_map.get(category.lower(), BadgeStyle.TEXT_SECONDARY)


def generate_recommended_badge(
    title: str,
    difficulty: str,
    impact: str,
    time_estimate: str
) -> str:
    """Generate smart recommendation badge.
    
    Args:
        title: Task title (will be truncated if too long)
        difficulty: Difficulty level (e.g., "Easy", "Medium")
        impact: Impact level (e.g., "High Impact")
        time_estimate: Estimated time (e.g., "2h")
        
    Returns:
        SVG string
    """
    # Truncate title if too long
    max_title_length = 35
    display_title = title[:max_title_length] + "..." if len(title) > max_title_length else title
    display_title = _escape_text(display_title)
    
    svg = f'''<svg width="450" height="70" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{BadgeStyle.EXCELLENT};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f883d;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect width="450" height="70" fill="url(#grad1)" rx="6"/>
  
  <!-- Title -->
  <text x="15" y="28" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="15" font-weight="600" font-family="Arial, sans-serif">
    🎯 Best Start: {display_title}
  </text>
  
  <!-- Metadata -->
  <text x="15" y="52" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="13" font-family="Arial, sans-serif" opacity="0.9">
    {_escape_text(difficulty)} • {_escape_text(impact)} • {_escape_text(time_estimate)}
  </text>
</svg>'''
    
    return svg


def generate_health_badge(
    score: int,
    urgent_count: int,
    open_count: int,
    stale_count: int
) -> str:
    """Generate project health badge.
    
    Args:
        score: Health score (0-100)
        urgent_count: Number of urgent tasks
        open_count: Number of open tasks
        stale_count: Number of stale tasks
        
    Returns:
        SVG string
    """
    color = _get_health_color(score)
    
    # Determine icon based on score
    if score >= 80:
        icon = "⚡"
    elif score >= 60:
        icon = "✓"
    elif score >= 40:
        icon = "⚠"
    else:
        icon = "⚠"
    
    svg = f'''<svg width="350" height="70" xmlns="http://www.w3.org/2000/svg">
  <rect width="350" height="70" fill="{color}" rx="6"/>
  
  <!-- Health Score -->
  <text x="15" y="30" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="16" font-weight="700" font-family="Arial, sans-serif">
    Project Health: {score}/100 {icon}
  </text>
  
  <!-- Details -->
  <text x="15" y="52" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="13" font-family="Arial, sans-serif" opacity="0.9">
    {urgent_count} urgent • {open_count} open • {stale_count} stale
  </text>
</svg>'''
    
    return svg


def generate_beginner_badge(task_count: int) -> str:
    """Generate beginner-friendly badge.
    
    Args:
        task_count: Number of beginner-friendly tasks
        
    Returns:
        SVG string
    """
    # Color based on availability
    if task_count >= 5:
        color = BadgeStyle.EXCELLENT
    elif task_count >= 3:
        color = BadgeStyle.GOOD
    elif task_count >= 1:
        color = BadgeStyle.WARNING
    else:
        color = BadgeStyle.TEXT_SECONDARY
    
    message = "Start today!" if task_count > 0 else "No tasks yet"
    
    svg = f'''<svg width="320" height="70" xmlns="http://www.w3.org/2000/svg">
  <rect width="320" height="70" fill="{color}" rx="6"/>
  
  <!-- Title -->
  <text x="15" y="30" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="16" font-weight="700" font-family="Arial, sans-serif">
    🌱 Beginner Friendly
  </text>
  
  <!-- Count -->
  <text x="15" y="52" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="14" font-family="Arial, sans-serif" opacity="0.9">
    {task_count} easy tasks • {message}
  </text>
</svg>'''
    
    return svg


def generate_distribution_badge(
    top_categories: List[Dict[str, any]]
) -> str:
    """Generate tech debt distribution badge.
    
    Args:
        top_categories: List of {name, count} for top 3 categories
        
    Returns:
        SVG string
    """
    # Calculate total for percentage
    total = sum(cat["count"] for cat in top_categories) or 1
    
    # Ensure we have exactly 3 categories (pad if needed)
    while len(top_categories) < 3:
        top_categories.append({"name": "Other", "count": 0})
    
    # Take only top 3
    top_categories = top_categories[:3]
    
    # Generate bars
    bar_y_start = 35
    bar_height = 8
    bar_spacing = 15
    max_bar_width = 120
    
    bars_svg = ""
    for i, cat in enumerate(top_categories):
        percentage = (cat["count"] / total) * 100
        bar_width = int((cat["count"] / max(c["count"] for c in top_categories)) * max_bar_width)
        color = _get_category_color(cat["name"])
        y_pos = bar_y_start + i * bar_spacing
        
        cat_name = cat["name"].capitalize()[:12]  # Truncate if needed
        
        bars_svg += f'''
  <text x="15" y="{y_pos}" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="12" font-family="monospace">
    {_escape_text(cat_name)}
  </text>
  <rect x="120" y="{y_pos - 8}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="2"/>
  <text x="{125 + bar_width}" y="{y_pos}" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="11" font-family="Arial, sans-serif">
    {cat["count"]}
  </text>'''
    
    svg = f'''<svg width="280" height="90" xmlns="http://www.w3.org/2000/svg">
  <rect width="280" height="90" fill="{BadgeStyle.BACKGROUND}" rx="6"/>
  
  <!-- Title -->
  <text x="15" y="22" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="14" font-weight="600" font-family="Arial, sans-serif">
    Tech Debt Distribution
  </text>
  
  <!-- Bars -->
  {bars_svg}
</svg>'''
    
    return svg


def generate_activity_badge(
    new_count: int,
    resolved_count: int,
    in_progress_count: int
) -> str:
    """Generate activity badge showing recent changes.
    
    Args:
        new_count: New tasks this week
        resolved_count: Resolved tasks this week
        in_progress_count: Tasks in progress
        
    Returns:
        SVG string
    """
    # Determine color based on activity
    total_activity = new_count + resolved_count
    if total_activity >= 10:
        color = BadgeStyle.EXCELLENT
    elif total_activity >= 5:
        color = BadgeStyle.GOOD
    elif total_activity >= 1:
        color = BadgeStyle.WARNING
    else:
        color = BadgeStyle.TEXT_SECONDARY
    
    svg = f'''<svg width="340" height="70" xmlns="http://www.w3.org/2000/svg">
  <rect width="340" height="70" fill="{color}" rx="6"/>
  
  <!-- Title -->
  <text x="15" y="28" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="15" font-weight="600" font-family="Arial, sans-serif">
    📈 Activity: {new_count} new this week
  </text>
  
  <!-- Details -->
  <text x="15" y="52" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="13" font-family="Arial, sans-serif" opacity="0.9">
    {resolved_count} resolved • {in_progress_count} in progress
  </text>
</svg>'''
    
    return svg


def generate_error_badge(error_message: str = "Analysis in progress") -> str:
    """Generate error/loading badge.
    
    Args:
        error_message: Error message to display
        
    Returns:
        SVG string
    """
    svg = f'''<svg width="300" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="50" fill="{BadgeStyle.TEXT_SECONDARY}" rx="6"/>
  
  <text x="15" y="30" fill="{BadgeStyle.TEXT_PRIMARY}" font-size="13" font-family="Arial, sans-serif">
    ⏳ {_escape_text(error_message)}
  </text>
</svg>'''
    
    return svg
