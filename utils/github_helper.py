"""Simplified GitHub data fetcher for badge system.

Lightweight wrapper around existing GitHub client,
optimized for badge generation (only fetches necessary data).
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def fetch_repo_data_for_badges(owner: str, repo: str) -> Dict[str, List[Dict]]:
    """Fetch GitHub issues and PRs for badge generation.
    
    This is a simplified interface specifically for badges.
    Only fetches open issues and recent PRs to minimize API calls.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        Dict with 'issues' and 'prs' lists
        Each issue/PR is a dict with simplified fields
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning(
            "GITHUB_TOKEN not set - proceeding with unauthenticated GitHub API calls (rate limits may be low)"
        )
    
    try:
        # Import here to avoid circular dependency
        from scanner.github.client import GitHubFetcher
        from scanner.models import GitHubConfig
        
        # Create config
        config = GitHubConfig(
            owner=owner,
            repo=repo,
            token_env="GITHUB_TOKEN"
        )
        
        # Create client (works with or without token)
        client = GitHubFetcher(config=config)
        
        # Fetch ALL issues (GitHub API fetches all pages automatically)
        logger.info(f"Fetching all issues for {owner}/{repo}...")
        all_issues = client.fetch_issues()
        logger.info(f"  Fetched {len(all_issues)} total issues from GitHub")
        
        # Filter to open issues only
        open_issues = [i for i in all_issues if i.state.lower() == "open"]
        logger.info(f"  Found {len(open_issues)} open issues")
        
        # Limit to recent 50 for badge analysis (most recent first)
        from datetime import datetime
        raw_issues = sorted(open_issues, key=lambda x: x.created_at if x.created_at else datetime.min, reverse=True)[:50]
        logger.info(f"  Using top {len(raw_issues)} issues for badge analysis")
        
        # Fetch ALL PRs
        logger.info(f"Fetching all PRs for {owner}/{repo}...")
        all_prs = client.fetch_pull_requests()
        logger.info(f"  Fetched {len(all_prs)} total PRs from GitHub")
        
        # Filter to open PRs only
        open_prs = [p for p in all_prs if p.state.lower() == "open"]
        logger.info(f"  Found {len(open_prs)} open PRs")
        
        # Limit to recent 20 for badge analysis
        raw_prs = sorted(open_prs, key=lambda x: x.created_at if x.created_at else datetime.min, reverse=True)[:20]
        logger.info(f"  Using top {len(raw_prs)} PRs for badge analysis")
        
        # Simplify data structure for badges
        issues = [
            {
                "title": issue.title,
                "number": issue.number,
                "body": issue.body or "",
                "state": issue.state,
                "created_at": issue.created_at.isoformat() if issue.created_at else "",
                "closed_at": getattr(issue, 'closed_at', None).isoformat() if getattr(issue, 'closed_at', None) else "",
                "html_url": issue.html_url,
                "labels": issue.labels if issue.labels else [],
                "labels_text": " ".join(issue.labels) if issue.labels else "",
                "assignees": getattr(issue, 'assignees', []),
            }
            for issue in raw_issues
        ]
        
        prs = [
            {
                "title": pr.title,
                "body": pr.body or "",
                "state": pr.state,
                "created_at": pr.created_at.isoformat() if pr.created_at else "",
                "html_url": pr.html_url,
            }
            for pr in raw_prs
        ]
        
        logger.info(f"Fetched {len(issues)} issues and {len(prs)} PRs for {owner}/{repo}")
        
        return {"issues": issues, "prs": prs}
    
    except Exception as e:
        logger.error(f"Failed to fetch GitHub data for {owner}/{repo}: {e}")
        # Return empty data rather than crashing
        return {"issues": [], "prs": []}
