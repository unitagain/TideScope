"""LLM-powered badge analyzer for TideScope.

Uses LLM to provide intelligent, context-aware analysis for badges:
- Smart task recommendation for new contributors
- Accurate difficulty and impact assessment
- Natural language task descriptions
- Context-aware categorization

Optimized for cost:
- Batch analysis (one LLM call for all badges)
- Only analyzes top N open issues (default: 10)
- 24-hour caching to minimize repeated calls
- Automatic fallback to rule-based analyzer
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

from .llm_client import LLMClient
from .fallback_analyzer import BadgeAnalysis, FallbackAnalyzer

logger = logging.getLogger(__name__)


class LLMBadgeAnalyzer:
    """LLM-powered analyzer for generating intelligent badge data."""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        use_llm: bool = True,
        max_issues_to_analyze: int = 10
    ):
        """Initialize LLM badge analyzer.
        
        Args:
            llm_client: LLM client instance (creates new if None)
            use_llm: Whether to use LLM (falls back to rules if False)
            max_issues_to_analyze: Maximum number of issues to send to LLM
        """
        self.llm_client = llm_client
        self.use_llm = use_llm and (llm_client is not None) and llm_client.enabled
        self.max_issues = max_issues_to_analyze
        self.fallback_analyzer = FallbackAnalyzer()
        
        logger.info(
            f"LLMBadgeAnalyzer initialized: use_llm={self.use_llm}, "
            f"max_issues={self.max_issues}"
        )
    
    def analyze(self, issues: List[Dict], prs: List[Dict] = None) -> BadgeAnalysis:
        """Analyze issues and generate badge data.
        
        Args:
            issues: List of GitHub issues (dict format)
            prs: List of GitHub pull requests (optional)
            
        Returns:
            BadgeAnalysis object with all badge data
        """
        prs = prs or []
        
        # Always have fallback ready
        if not self.use_llm:
            logger.info("Using fallback analyzer (LLM disabled)")
            return self.fallback_analyzer.analyze(issues, prs)
        
        try:
            return self._analyze_with_llm(issues, prs)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}, falling back to rules")
            return self.fallback_analyzer.analyze(issues, prs)
    
    def _analyze_with_llm(self, issues: List[Dict], prs: List[Dict]) -> BadgeAnalysis:
        """Perform LLM-powered analysis.
        
        Args:
            issues: List of GitHub issues
            prs: List of GitHub pull requests
            
        Returns:
            BadgeAnalysis object
        """
        # Filter open issues
        open_issues = [i for i in issues if i.get("state", "").lower() == "open"]
        
        # Take only top N issues (cost optimization)
        # Sort by: label priority > creation date (newest first)
        open_issues.sort(
            key=lambda x: (
                self._has_priority_label(x),
                x.get("created_at", "")
            ),
            reverse=True
        )
        issues_to_analyze = open_issues[:self.max_issues]
        
        logger.info(f"Analyzing {len(issues_to_analyze)} issues with LLM")
        
        # Prepare batch prompt
        issues_text = self._format_issues_for_prompt(issues_to_analyze)
        
        # Call LLM once for comprehensive analysis
        llm_response = self._call_llm_batch(issues_text)
        
        # Parse response
        result = self._parse_llm_response(llm_response, open_issues, issues_to_analyze)
        
        # Override with accurate counts calculated from all issues
        from datetime import datetime, timedelta
        
        # Calculate accurate activity metrics
        result.new_this_week = self.fallback_analyzer._count_recent_issues(issues, days=7, state="all")
        result.resolved_this_week = self.fallback_analyzer._count_recent_closed(issues, days=7)
        result.active_count = result.new_this_week
        
        # Count assigned issues (in progress) - check assignees field
        result.in_progress = sum(1 for i in open_issues 
                                if i.get("assignees") and len(i.get("assignees", [])) > 0)
        
        # Calculate accurate stale count from all open issues
        ninety_days_ago = datetime.now() - timedelta(days=90)
        result.stale_count = 0
        for issue in open_issues:
            created_at_str = issue.get("created_at", "")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if created_at < ninety_days_ago:
                        result.stale_count += 1
                except:
                    pass
        
        # Calculate accurate urgent count
        result.urgent_count = sum(1 for i in open_issues
                                 if any(keyword in str(i.get("labels_text", "")).lower()
                                       for keyword in ["urgent", "critical", "blocker", "p0", "high priority"]))
        
        # Calculate trend
        last_week_count = self.fallback_analyzer._count_recent_issues(issues, days=14, state="all") - result.new_this_week
        result.trend = result.new_this_week - last_week_count if last_week_count > 0 else 0
        
        # Calculate skills distribution from beginner tasks
        skills_count = {}
        for task in result.beginner_tasks:
            for skill in task.get('skills', []):
                skills_count[skill] = skills_count.get(skill, 0) + 1
        # Add skills from recommended task
        if result.recommended_task:
            for skill in result.recommended_task.get('skills', []):
                skills_count[skill] = skills_count.get(skill, 0) + 1
        
        result.skills_distribution = skills_count
        
        logger.info(
            f"LLM analysis complete: health={result.health_score}, "
            f"beginner={result.beginner_task_count}, open={result.open_count}, "
            f"skills={len(skills_count)}"
        )
        
        return result
    
    def _has_priority_label(self, issue: Dict) -> bool:
        """Check if issue has priority/urgent labels."""
        labels_text = str(issue.get("labels", [])).lower()
        priority_keywords = ["urgent", "critical", "priority", "blocker", "p0", "p1"]
        return any(keyword in labels_text for keyword in priority_keywords)
    
    def _format_issues_for_prompt(self, issues: List[Dict]) -> str:
        """Format issues for LLM prompt.
        
        Args:
            issues: List of issues to format
            
        Returns:
            Formatted string for prompt
        """
        formatted = []
        for i, issue in enumerate(issues, 1):
            title = issue.get("title", "Untitled")
            body = issue.get("body", "")[:300]  # Truncate body to save tokens
            labels = issue.get("labels_text", "")
            created = issue.get("created_at", "")
            
            formatted.append(
                f"Issue #{i}:\n"
                f"Title: {title}\n"
                f"Body: {body}\n"
                f"Labels: {labels}\n"
                f"Created: {created}\n"
            )
        
        return "\n---\n".join(formatted)
    
    def _call_llm_batch(self, issues_text: str) -> Dict:
        """Call LLM for batch analysis of issues.
        
        Args:
            issues_text: Formatted issues string
            
        Returns:
            Parsed JSON response from LLM
        """
        prompt = f"""You are analyzing GitHub issues for a badge system. Analyze these issues and provide:

{issues_text}

Provide analysis in JSON format:
{{
  "recommended_task": {{
    "issue_number": <which issue # is best for new contributors (1-{self.max_issues})>,
    "title": "<shortened to 35 chars max>",
    "difficulty": "<entry|intermediate|advanced>",
    "impact": "<Low Impact|Medium Impact|High Impact>",
    "time_estimate": "<e.g., 1h, 2-3h, 1 day>",
    "skills": ["<skill1>", "<skill2>", "<skill3>"]
  }},
  "health_score": <0-100, considering urgency, age, staleness>,
  "urgent_count": <number of urgent/critical issues>,
  "stale_count": <number of issues older than 90 days>,
  "beginner_tasks": [
    {{
      "issue_number": <issue #>,
      "skills": ["<skill1>", "<skill2>"]
    }}
  ],
  "categories": [
    {{"name": "<category>", "count": <number>}},
    {{"name": "<category>", "count": <number>}},
    {{"name": "<category>", "count": <number>}}
  ]
}}

Categories: performance, security, documentation, testing, refactor, feature, bug

Guidelines:
- recommended_task: Choose task that is both important and accessible to new contributors
- skills: Extract specific technical skills needed (e.g., Python, React, Docker, API, Testing, Documentation)
- health_score: 80-100=excellent, 60-79=good, 40-59=warning, 0-39=critical
- beginner_tasks: Only include issues that are truly beginner-friendly (clear scope, minimal dependencies)
- For each task, identify 1-3 key skills required based on issue description
- Prioritize issues with clear descriptions and reasonable scope"""

        try:
            if self.llm_client.provider == "deepseek":
                response = self.llm_client._client.chat.completions.create(
                    model=self.llm_client.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an engineering assistant analyzing GitHub issues. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
            else:  # OpenAI
                response = self.llm_client._client.chat.completions.create(
                    model=self.llm_client.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an engineering assistant analyzing GitHub issues. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
            
            content = response.choices[0].message.content
            logger.debug(f"LLM raw response: {content[:200]}...")
            
            return json.loads(content)
        
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _parse_llm_response(
        self,
        llm_response: Dict,
        all_open_issues: List[Dict],
        analyzed_issues: List[Dict]
    ) -> BadgeAnalysis:
        """Parse LLM response into BadgeAnalysis object.
        
        Args:
            llm_response: Parsed JSON from LLM
            all_open_issues: All open issues
            analyzed_issues: Issues that were sent to LLM
            
        Returns:
            BadgeAnalysis object
        """
        result = BadgeAnalysis()
        
        # Basic counts
        result.open_count = len(all_open_issues)
        result.urgent_count = llm_response.get("urgent_count", 0)
        result.stale_count = llm_response.get("stale_count", 0)
        result.health_score = llm_response.get("health_score", 50)
        
        # Recommended task
        rec_data = llm_response.get("recommended_task", {})
        if rec_data:
            # Get actual issue
            issue_num = rec_data.get("issue_number", 1)
            if 1 <= issue_num <= len(analyzed_issues):
                issue = analyzed_issues[issue_num - 1]
                result.recommended_task = {
                    "title": rec_data.get("title", issue.get("title", "")[:35]),
                    "difficulty": rec_data.get("difficulty", "intermediate").capitalize(),
                    "impact": rec_data.get("impact", "Medium Impact"),
                    "time_estimate": rec_data.get("time_estimate", "2-3h"),
                    "url": issue.get("html_url", ""),
                    "number": issue.get("number", 0),
                    "skills": rec_data.get("skills", ["Various"]),
                }
        
        # Beginner tasks
        beginner_tasks_data = llm_response.get("beginner_tasks", [])
        result.beginner_task_count = len(beginner_tasks_data)
        
        # Build beginner tasks list with full details
        result.beginner_tasks = []
        for task_data in beginner_tasks_data[:10]:
            if isinstance(task_data, dict):
                issue_num = task_data.get("issue_number", 0)
                if 1 <= issue_num <= len(analyzed_issues):
                    issue = analyzed_issues[issue_num - 1]
                    result.beginner_tasks.append({
                        "title": issue.get("title", "")[:60],
                        "url": issue.get("html_url", ""),
                        "number": issue.get("number", 0),
                        "difficulty": "entry",
                        "time_estimate": "1-2h",
                        "impact": "Medium",
                        "skills": task_data.get("skills", ["Various"])
                    })
        
        # Distribution
        categories = llm_response.get("categories", [])
        if len(categories) >= 3:
            result.top_categories = categories[:3]
        else:
            # Pad with empty categories
            result.top_categories = categories + [
                {"name": "Other", "count": 0}
                for _ in range(3 - len(categories))
            ]
        
        return result


def create_badge_analyzer(
    use_llm: bool = True,
    llm_provider: str = "deepseek",
    llm_model: Optional[str] = None
) -> LLMBadgeAnalyzer:
    """Factory function to create badge analyzer.
    
    Args:
        use_llm: Whether to use LLM
        llm_provider: LLM provider ("openai" or "deepseek")
        llm_model: LLM model name (auto-selects if None)
        
    Returns:
        LLMBadgeAnalyzer instance
    """
    if not use_llm:
        return LLMBadgeAnalyzer(llm_client=None, use_llm=False)
    
    # Determine model
    if llm_model is None:
        llm_model = "deepseek-chat" if llm_provider == "deepseek" else "gpt-4o-mini"
    
    # Create LLM client
    try:
        llm_client = LLMClient(
            model=llm_model,
            enabled=True,
            provider=llm_provider
        )
        
        if not llm_client.enabled:
            logger.warning("LLM client not enabled, falling back to rules")
            return LLMBadgeAnalyzer(llm_client=None, use_llm=False)
        
        return LLMBadgeAnalyzer(llm_client=llm_client, use_llm=True)
    
    except Exception as e:
        logger.error(f"Failed to create LLM client: {e}")
        return LLMBadgeAnalyzer(llm_client=None, use_llm=False)
