"""Task badge generator for recommended and beginner tasks.

Generates beautiful, compact SVG badges for individual tasks.
"""

from typing import Dict, List


def generate_task_badge(
    title: str,
    number: int,
    difficulty: str,
    time_estimate: str,
    skills: List[str],
    width: int = 800,
    compact: bool = False
) -> str:
    """Generate SVG badge for a single task.
    
    Args:
        title: Task title
        number: Issue number
        difficulty: entry/intermediate/advanced
        time_estimate: Time estimate string
        skills: List of required skills
        width: Badge width
        compact: If True, generate compact version
        
    Returns:
        SVG string
    """
    # Color scheme based on difficulty
    difficulty_colors = {
        "entry": "#10b981",       # Green
        "intermediate": "#f59e0b", # Orange
        "advanced": "#ef4444"      # Red
    }
    
    bg_color = difficulty_colors.get(difficulty.lower(), "#6b7280")
    
    # Truncate title if too long
    display_title = title[:60] + "..." if len(title) > 60 else title
    
    # Format skills
    skills_text = ", ".join(skills[:3]) if skills else "General"
    if len(skills) > 3:
        skills_text += f" +{len(skills)-3}"
    
    if compact:
        height = 40
        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad-{number}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{bg_color};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{bg_color};stop-opacity:0.6" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" rx="6" fill="url(#grad-{number})"/>
  
  <!-- Number badge -->
  <circle cx="25" cy="20" r="14" fill="white" opacity="0.3"/>
  <text x="25" y="25" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="12" font-weight="bold">#{number}</text>
  
  <!-- Title -->
  <text x="50" y="16" fill="white" font-family="Arial, sans-serif" font-size="13" font-weight="600">{display_title}</text>
  
  <!-- Time and skills -->
  <text x="50" y="32" fill="white" font-family="Arial, sans-serif" font-size="11" opacity="0.9">⏱️ {time_estimate} · 💼 {skills_text}</text>
</svg>"""
    else:
        height = 80
        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad-{number}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_color};stop-opacity:0.9" />
      <stop offset="100%" style="stop-color:{bg_color};stop-opacity:0.7" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" rx="8" fill="url(#grad-{number})"/>
  
  <!-- Top section -->
  <rect width="{width}" height="35" rx="8" fill="white" opacity="0.15"/>
  
  <!-- Issue number badge -->
  <circle cx="30" cy="17.5" r="16" fill="white" opacity="0.25"/>
  <text x="30" y="23" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="13" font-weight="bold">#{number}</text>
  
  <!-- Difficulty badge -->
  <rect x="{width-120}" y="7" width="110" height="20" rx="10" fill="white" opacity="0.25"/>
  <text x="{width-65}" y="21" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="11" font-weight="600">{difficulty.upper()}</text>
  
  <!-- Title -->
  <text x="60" y="23" fill="white" font-family="Arial, sans-serif" font-size="15" font-weight="bold">{display_title}</text>
  
  <!-- Time estimate -->
  <text x="15" y="55" fill="white" font-family="Arial, sans-serif" font-size="12" opacity="0.95">⏱️ Time: {time_estimate}</text>
  
  <!-- Skills -->
  <text x="15" y="70" fill="white" font-family="Arial, sans-serif" font-size="12" opacity="0.95">💼 Skills: {skills_text}</text>
</svg>"""
    
    return svg


def generate_recommended_task_badge(task: Dict) -> str:
    """Generate featured badge for recommended task.
    
    Args:
        task: Task dict with title, number, difficulty, etc.
        
    Returns:
        SVG string
    """
    return generate_task_badge(
        title=task.get('title', 'No task available'),
        number=task.get('number', 0),
        difficulty=task.get('difficulty', 'intermediate'),
        time_estimate=task.get('time_estimate', '2-3h'),
        skills=task.get('skills', ['General']),
        width=850,
        compact=False
    )


def generate_beginner_task_badge(task: Dict) -> str:
    """Generate compact badge for beginner task.
    
    Args:
        task: Task dict with title, number, difficulty, etc.
        
    Returns:
        SVG string
    """
    return generate_task_badge(
        title=task.get('title', 'Task'),
        number=task.get('number', 0),
        difficulty='entry',
        time_estimate=task.get('time_estimate', '1-2h'),
        skills=task.get('skills', ['General']),
        width=800,
        compact=True
    )
