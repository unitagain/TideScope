"""Badge API routes for TideScope.

Provides 5 types of intelligent badges:
1. /recommended - Smart task recommendation for new contributors
2. /health - Project health score with metrics
3. /beginner - Count of beginner-friendly tasks
4. /distribution - Tech debt distribution by category
5. /activity - Recent activity trends

All badges use:
- Multi-layer caching (memory + disk + CDN)
- Automatic fallback to rule-based analysis
- Cost-optimized LLM usage
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, Response, HTTPException, BackgroundTasks
from pydantic import BaseModel

from analyzer.llm_badge_analyzer import create_badge_analyzer
from utils.cache_manager import get_cache
from utils.svg_badge_generator import (
    generate_recommended_badge,
    generate_health_badge,
    generate_beginner_badge,
    generate_distribution_badge,
    generate_activity_badge,
    generate_error_badge,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/badge", tags=["badges"])

# Cache control headers for CDN
CACHE_HEADERS = {
    "Cache-Control": "public, max-age=86400",  # 24 hours
    "CDN-Cache-Control": "max-age=86400",
    "Surrogate-Control": "max-age=86400",
    "Vary": "Accept-Encoding",
}

# Usage tracking for automatic fallback
_usage_counter: Dict[str, int] = {}
USAGE_THRESHOLD_LLM = 10  # After 10 requests, switch to rules
USAGE_THRESHOLD_PREGENERATE = 100  # After 100 requests, consider pre-generation


class RepoIdentifier(BaseModel):
    """Repository identifier."""
    owner: str
    repo: str


def _get_cache_key(owner: str, repo: str, badge_type: str) -> str:
    """Generate cache key for badge."""
    return f"badge:{owner}:{repo}:{badge_type}"


def _track_usage(owner: str, repo: str) -> int:
    """Track badge usage for automatic fallback.
    
    Returns:
        Current usage count
    """
    key = f"{owner}/{repo}"
    _usage_counter[key] = _usage_counter.get(key, 0) + 1
    return _usage_counter[key]


def _should_use_llm(owner: str, repo: str) -> bool:
    """Determine if should use LLM based on usage."""
    usage = _usage_counter.get(f"{owner}/{repo}", 0)
    
    # If usage is high, switch to rule-based to save costs
    if usage >= USAGE_THRESHOLD_LLM:
        logger.info(f"High usage ({usage}), using rule-based analyzer for {owner}/{repo}")
        return False
    
    return True


async def _fetch_github_data(owner: str, repo: str) -> Dict[str, List[Dict]]:
    """Fetch GitHub issues and PRs.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        Dict with 'issues' and 'prs' lists
    """
    from utils.github_helper import fetch_repo_data_for_badges
    
    # Fetch data (sync operation, but fast enough for badges)
    return fetch_repo_data_for_badges(owner, repo)


async def _analyze_and_generate_all_badges(
    owner: str,
    repo: str,
    use_llm: bool = True
) -> Dict[str, str]:
    """Analyze repo and generate all 5 badges in one go.
    
    This is cost-efficient: one LLM call generates data for all badges.
    
    Args:
        owner: Repository owner
        repo: Repository name
        use_llm: Whether to use LLM (falls back to rules if False)
        
    Returns:
        Dict mapping badge_type to SVG string
    """
    # Check cache first (all badges together)
    cache = get_cache()
    cache_key_base = f"badges_all:{owner}:{repo}"
    
    cached_badges = cache.get(cache_key_base)
    if cached_badges:
        logger.info(f"All badges cache hit for {owner}/{repo}")
        return cached_badges
    
    # Fetch GitHub data
    try:
        data = await _fetch_github_data(owner, repo)
        issues = data.get("issues", [])
        prs = data.get("prs", [])
        
        # If no data, return placeholder badges
        if not issues and not prs:
            logger.warning(f"No issues/PRs found for {owner}/{repo}")
            badges = _generate_placeholder_badges()
            cache.set(cache_key_base, badges, ttl=3600)  # Cache for 1 hour only
            return badges
        
        # Analyze with LLM or fallback
        analyzer = create_badge_analyzer(
            use_llm=use_llm,
            llm_provider=os.getenv("LLM_PROVIDER", "deepseek").lower()
        )
        
        logger.info(f"Analyzing {owner}/{repo} with {'LLM' if use_llm else 'rules'}")
        analysis = analyzer.analyze(issues, prs)
        
        # Generate all badges from analysis
        badges = {
            "recommended": _generate_recommended_from_analysis(analysis),
            "health": _generate_health_from_analysis(analysis),
            "beginner": _generate_beginner_from_analysis(analysis),
            "distribution": _generate_distribution_from_analysis(analysis),
            "activity": _generate_activity_from_analysis(analysis),
        }
        
        # Cache all badges (24 hours)
        cache.set(cache_key_base, badges, ttl=86400)
        logger.info(f"Generated and cached all badges for {owner}/{repo}")
        
        return badges
    
    except Exception as e:
        logger.error(f"Failed to analyze {owner}/{repo}: {e}")
        # Return error badges
        return _generate_error_badges(str(e))


def _generate_recommended_from_analysis(analysis) -> str:
    """Generate recommended badge from analysis."""
    if analysis.recommended_task:
        task = analysis.recommended_task
        return generate_recommended_badge(
            title=task.get("title", "Check issues"),
            difficulty=task.get("difficulty", "Intermediate"),
            impact=task.get("impact", "Medium Impact"),
            time_estimate=task.get("time_estimate", "2-3h")
        )
    else:
        return generate_error_badge("No recommended tasks available")


def _generate_health_from_analysis(analysis) -> str:
    """Generate health badge from analysis."""
    return generate_health_badge(
        score=analysis.health_score,
        urgent_count=analysis.urgent_count,
        open_count=analysis.open_count,
        stale_count=analysis.stale_count
    )


def _generate_beginner_from_analysis(analysis) -> str:
    """Generate beginner badge from analysis."""
    return generate_beginner_badge(
        task_count=analysis.beginner_task_count
    )


def _generate_distribution_from_analysis(analysis) -> str:
    """Generate distribution badge from analysis."""
    return generate_distribution_badge(
        top_categories=analysis.top_categories
    )


def _generate_activity_from_analysis(analysis) -> str:
    """Generate activity badge from analysis."""
    return generate_activity_badge(
        new_count=analysis.new_this_week,
        resolved_count=analysis.resolved_this_week,
        in_progress_count=analysis.in_progress
    )


def _generate_placeholder_badges() -> Dict[str, str]:
    """Generate placeholder badges when no data available."""
    return {
        "recommended": generate_error_badge("No issues found"),
        "health": generate_health_badge(80, 0, 0, 0),  # Perfect health if no issues
        "beginner": generate_beginner_badge(0),
        "distribution": generate_distribution_badge([
            {"name": "No data", "count": 0},
            {"name": "N/A", "count": 0},
            {"name": "N/A", "count": 0},
        ]),
        "activity": generate_activity_badge(0, 0, 0),
    }


def _generate_error_badges(error_msg: str) -> Dict[str, str]:
    """Generate error badges when analysis fails."""
    error_svg = generate_error_badge(f"Error: {error_msg[:30]}")
    return {
        "recommended": error_svg,
        "health": error_svg,
        "beginner": error_svg,
        "distribution": error_svg,
        "activity": error_svg,
    }


@router.get("/{owner}/{repo}/{badge_type}.svg")
async def get_badge(
    owner: str,
    repo: str,
    badge_type: str,
    background_tasks: BackgroundTasks,
    refresh: bool = False
):
    """Get a specific badge type for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        badge_type: One of: recommended, health, beginner, distribution, activity
        refresh: Force refresh (bypass cache)
        
    Returns:
        SVG badge image
    """
    # Validate badge type
    valid_types = ["recommended", "health", "beginner", "distribution", "activity"]
    if badge_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid badge type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Track usage
    usage = _track_usage(owner, repo)
    logger.info(f"Badge request: {owner}/{repo}/{badge_type} (usage: {usage})")
    
    # Check individual badge cache first (if not forcing refresh)
    cache = get_cache()
    cache_key = _get_cache_key(owner, repo, badge_type)
    
    if not refresh:
        cached_svg = cache.get(cache_key)
        if cached_svg:
            logger.info(f"Individual badge cache hit: {cache_key}")
            return Response(
                content=cached_svg,
                media_type="image/svg+xml",
                headers=CACHE_HEADERS
            )
    
    # Generate all badges (cost-efficient)
    try:
        use_llm = _should_use_llm(owner, repo) and not refresh
        all_badges = await _analyze_and_generate_all_badges(owner, repo, use_llm=use_llm)
        
        # Get requested badge
        svg = all_badges.get(badge_type)
        
        if not svg:
            raise HTTPException(status_code=500, detail="Failed to generate badge")
        
        # Cache individual badge
        cache.set(cache_key, svg, ttl=86400)
        
        # Schedule cache cleanup in background
        background_tasks.add_task(cache.clear_expired)
        
        return Response(
            content=svg,
            media_type="image/svg+xml",
            headers=CACHE_HEADERS
        )
    
    except Exception as e:
        logger.error(f"Badge generation failed for {owner}/{repo}/{badge_type}: {e}")
        
        # Return error badge
        error_svg = generate_error_badge("Analysis failed")
        return Response(
            content=error_svg,
            media_type="image/svg+xml",
            headers={"Cache-Control": "no-cache"}  # Don't cache errors
        )


@router.get("/{owner}/{repo}/all")
async def get_all_badges(owner: str, repo: str):
    """Get URLs for all badge types.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        JSON with badge URLs and markdown
    """
    base_url = os.getenv("BADGE_BASE_URL", "https://tidescope.vercel.app")
    
    badge_types = ["recommended", "health", "beginner", "distribution", "activity"]
    
    badges = {}
    for badge_type in badge_types:
        url = f"{base_url}/api/badge/{owner}/{repo}/{badge_type}.svg"
        markdown = f"[![{badge_type.capitalize()} Badge]({url})](https://github.com/{owner}/{repo})"
        
        badges[badge_type] = {
            "url": url,
            "markdown": markdown,
        }
    
    return {
        "owner": owner,
        "repo": repo,
        "badges": badges,
        "usage_count": _usage_counter.get(f"{owner}/{repo}", 0),
    }


@router.post("/clear-cache/{owner}/{repo}")
async def clear_badge_cache(owner: str, repo: str):
    """Clear badge cache for a repository.
    
    Useful for forcing a refresh after major changes.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        Success message
    """
    cache = get_cache()
    
    # Clear all badge types
    cleared = []
    badge_types = ["recommended", "health", "beginner", "distribution", "activity"]
    for badge_type in badge_types:
        cache_key = _get_cache_key(owner, repo, badge_type)
        cache.delete(cache_key)
        cleared.append(badge_type)
    
    # Clear combined cache
    cache.delete(f"badges_all:{owner}:{repo}")
    
    # Reset usage counter
    key = f"{owner}/{repo}"
    if key in _usage_counter:
        del _usage_counter[key]
    
    logger.info(f"Cleared badge cache for {owner}/{repo}")
    
    return {
        "success": True,
        "owner": owner,
        "repo": repo,
        "cleared_badges": cleared,
    }
