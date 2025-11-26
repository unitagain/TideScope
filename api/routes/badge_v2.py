"""
Badge API v2 - Enhanced Badge System

New features in v2:
- Hero Badge: Large card-style badge for README
- Analysis Panels: Rich SVG panels for CONTRIBUTING.md
- Smart Analysis: Automatic LLM/rules selection
- Better Caching: Multi-layer cache with CDN support
- Cost Control: Automatic budget management

Endpoints:
- GET /api/v2/badge/{owner}/{repo}/hero.svg - Hero badge
- GET /api/v2/panel/{owner}/{repo}/health.svg - Health panel
- GET /api/v2/panel/{owner}/{repo}/trends.svg - Trends panel
- GET /api/v2/panel/{owner}/{repo}/skills.svg - Skills panel
"""

import logging
from fastapi import APIRouter, Request, Response, Query, HTTPException
from fastapi.responses import Response as FastAPIResponse
from typing import Optional

from utils.hero_badge_generator import HeroBadgeGenerator
from utils.analysis_panel_generator import (
    HealthPanelGenerator,
    TrendsPanelGenerator,
    SkillsDistributionGenerator
)
from analyzer.smart_analyzer import smart_analyzer, check_budget_alert
from utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2", tags=["badges-v2"])

# Initialize cache manager
cache_manager = CacheManager(
    memory_ttl=3600,  # 1 hour memory cache
    disk_ttl=86400    # 24 hour disk cache
)

# CDN cache headers
CDN_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=86400",  # 24 hours
    "CDN-Cache-Control": "max-age=86400",
    "Surrogate-Control": "max-age=86400",
    "Vary": "Accept-Encoding"
}


@router.get("/badge/{owner}/{repo}/hero.svg")
async def get_hero_badge(
    owner: str,
    repo: str,
    theme: str = Query("light", regex="^(light|dark)$"),
    lang: str = Query("en", regex="^(en|zh|ja|es)$"),
    for_level: str = Query("all", regex="^(beginners|all|experts)$", alias="for"),
    cache: int = Query(1, ge=0, le=1),
    request: Request = None
):
    """
    Get Hero Badge for repository
    
    Args:
        owner: Repository owner (username or org)
        repo: Repository name
        theme: Visual theme (light or dark)
        lang: Language (en, zh, ja, es)
        for_level: Target user level (beginners, all, experts)
        cache: Use cache (1) or force refresh (0)
        
    Returns:
        SVG image response with Hero Badge
    """
    
    repo_key = f"{owner}/{repo}"
    cache_key = f"hero:v2:{owner}:{repo}:{theme}:{lang}:{for_level}"
    
    logger.info(f"Hero badge request: {repo_key} (theme={theme}, lang={lang}, for={for_level})")
    
    # Check budget alert
    budget_alert = check_budget_alert()
    if budget_alert:
        logger.warning(budget_alert)
    
    # Check cache if enabled
    if cache == 1:
        cached_svg = cache_manager.get(cache_key)
        if cached_svg:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(
                content=cached_svg,
                media_type="image/svg+xml",
                headers={
                    **CDN_CACHE_HEADERS,
                    "X-TideScope-Cache": "HIT",
                    "X-TideScope-Version": "2.0.0"
                }
            )
    
    logger.info(f"Cache MISS for {cache_key}, generating badge...")
    
    try:
        # Perform smart analysis
        analysis_result = await smart_analyzer.analyze(owner, repo, for_level)
        
        # Check for errors
        if analysis_result.get('error'):
            error_msg = analysis_result.get('error_message', 'Analysis failed')
            logger.error(f"Analysis error for {repo_key}: {error_msg}")
            svg_content = HeroBadgeGenerator.generate_error(error_msg)
        else:
            # Extract recommended task
            recommended = analysis_result.get('recommended_task', {})
            
            # Generate Hero Badge
            svg_content = HeroBadgeGenerator.generate(
                task_title=recommended.get('title', 'No task available'),
                difficulty=recommended.get('difficulty', 'Entry'),
                time_estimate=recommended.get('time_estimate', 'Unknown'),
                impact=recommended.get('impact', 'Medium'),
                skills=recommended.get('skills', []),
                trending_stars=recommended.get('trending_stars', 0),
                similar_count=len(analysis_result.get('beginner_tasks', [])),
                theme=theme,
                lang=lang
            )
            
            logger.info(f"Hero badge generated for {repo_key} using {analysis_result.get('analysis_method', 'unknown')}")
        
        # Cache the result
        cache_manager.set(cache_key, svg_content, ttl=3600)
        
        # Return SVG response
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                **CDN_CACHE_HEADERS,
                "X-TideScope-Cache": "MISS",
                "X-TideScope-Version": "2.0.0",
                "X-TideScope-Analysis-Method": analysis_result.get('analysis_method', 'unknown'),
                "X-TideScope-Quality": analysis_result.get('quality', 'unknown'),
                "X-TideScope-Analysis-Time": analysis_result.get('analyzed_at', '')
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate hero badge for {repo_key}: {e}", exc_info=True)
        
        # Return error badge
        error_svg = HeroBadgeGenerator.generate_error(str(e))
        return Response(
            content=error_svg,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "public, max-age=300",  # 5 min cache for errors
                "X-TideScope-Error": "true"
            }
        )


@router.get("/panel/{owner}/{repo}/health.svg")
async def get_health_panel(
    owner: str,
    repo: str,
    cache: int = Query(1, ge=0, le=1)
):
    """
    Get health dashboard panel
    
    Returns:
        SVG panel with project health metrics
    """
    
    repo_key = f"{owner}/{repo}"
    cache_key = f"panel:health:v2:{owner}:{repo}"
    
    logger.info(f"Health panel request: {repo_key}")
    
    # Check cache
    if cache == 1:
        cached_svg = cache_manager.get(cache_key)
        if cached_svg:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(
                content=cached_svg,
                media_type="image/svg+xml",
                headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "HIT"}
            )
    
    try:
        # Perform analysis
        analysis_result = await smart_analyzer.analyze(owner, repo, 'all')
        
        if analysis_result.get('error'):
            raise HTTPException(status_code=500, detail=analysis_result.get('error_message'))
        
        # Generate health panel
        svg_content = HealthPanelGenerator.generate(
            health_score=analysis_result.get('health_score', 50),
            trend=analysis_result.get('trend', 0),
            active_count=analysis_result.get('active_count', 0),
            stale_count=analysis_result.get('stale_count', 0),
            urgent_count=analysis_result.get('urgent_count', 0),
            in_progress=analysis_result.get('in_progress', 0),
            updated_at=analysis_result.get('analyzed_at', '')
        )
        
        # Cache the result
        cache_manager.set(cache_key, svg_content, ttl=3600)
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "MISS"}
        )
        
    except Exception as e:
        logger.error(f"Failed to generate health panel for {repo_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/panel/{owner}/{repo}/trends.svg")
async def get_trends_panel(
    owner: str,
    repo: str,
    cache: int = Query(1, ge=0, le=1)
):
    """
    Get trends chart panel
    
    Returns:
        SVG panel with historical trends
    """
    
    repo_key = f"{owner}/{repo}"
    cache_key = f"panel:trends:v2:{owner}:{repo}"
    
    logger.info(f"Trends panel request: {repo_key}")
    
    # Check cache
    if cache == 1:
        cached_svg = cache_manager.get(cache_key)
        if cached_svg:
            return Response(
                content=cached_svg,
                media_type="image/svg+xml",
                headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "HIT"}
            )
    
    try:
        # Perform analysis
        analysis_result = await smart_analyzer.analyze(owner, repo, 'all')
        
        if analysis_result.get('error'):
            raise HTTPException(status_code=500, detail=analysis_result.get('error_message'))
        
        # Get historical data (mock for now, should come from database)
        # TODO: Implement actual historical data collection
        issues_opened = analysis_result.get('issues_opened_history', [10, 15, 12, 18, 14, 20])
        issues_closed = analysis_result.get('issues_closed_history', [8, 12, 15, 16, 13, 19])
        
        # Generate trends panel
        svg_content = TrendsPanelGenerator.generate(
            issues_opened=issues_opened,
            issues_closed=issues_closed
        )
        
        # Cache the result
        cache_manager.set(cache_key, svg_content, ttl=3600)
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "MISS"}
        )
        
    except Exception as e:
        logger.error(f"Failed to generate trends panel for {repo_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/panel/{owner}/{repo}/skills.svg")
async def get_skills_panel(
    owner: str,
    repo: str,
    cache: int = Query(1, ge=0, le=1)
):
    """
    Get skills distribution panel
    
    Returns:
        SVG panel with skills breakdown
    """
    
    repo_key = f"{owner}/{repo}"
    cache_key = f"panel:skills:v2:{owner}:{repo}"
    
    logger.info(f"Skills panel request: {repo_key}")
    
    # Check cache
    if cache == 1:
        cached_svg = cache_manager.get(cache_key)
        if cached_svg:
            return Response(
                content=cached_svg,
                media_type="image/svg+xml",
                headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "HIT"}
            )
    
    try:
        # Perform analysis
        analysis_result = await smart_analyzer.analyze(owner, repo, 'all')
        
        if analysis_result.get('error'):
            raise HTTPException(status_code=500, detail=analysis_result.get('error_message'))
        
        # Get skills data
        skills_data = analysis_result.get('skills_distribution', {})
        
        if not skills_data:
            # Generate mock data if not available
            skills_data = {'Various': 1}
        
        # Generate skills panel
        svg_content = SkillsDistributionGenerator.generate(skills_data)
        
        # Cache the result
        cache_manager.set(cache_key, svg_content, ttl=3600)
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={**CDN_CACHE_HEADERS, "X-TideScope-Cache": "MISS"}
        )
        
    except Exception as e:
        logger.error(f"Failed to generate skills panel for {repo_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get usage statistics (admin only in production)
    
    Returns:
        JSON with usage and cost statistics
    """
    
    stats = smart_analyzer.get_usage_stats()
    budget_alert = check_budget_alert()
    
    return {
        "status": "ok",
        "version": "2.0.0",
        "usage": stats,
        "alert": budget_alert,
        "timestamp": smart_analyzer.usage_tracker.get_stats()
    }


# Health check endpoint
@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "TideScope Badge API v2"
    }
