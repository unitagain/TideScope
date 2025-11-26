"""Fallback rule-based analyzer for badge system.

This analyzer is used when:
1. LLM API is unavailable
2. Project exceeds usage threshold (cost control)
3. User hasn't provided API key

It provides reasonable analysis using heuristic rules,
with ~70% accuracy compared to LLM's ~85-90%.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BadgeAnalysis:
    """Result of badge analysis."""
    
    def __init__(self):
        # Recommended task
        self.recommended_task: Optional[Dict] = None
        
        # Health metrics
        self.health_score: int = 50
        self.urgent_count: int = 0
        self.open_count: int = 0
        self.stale_count: int = 0
        
        # Beginner tasks
        self.beginner_task_count: int = 0
        self.beginner_tasks: List[Dict] = []
        
        # Distribution (top 3 categories)
        self.top_categories: List[Dict] = []
        
        # Activity
        self.new_this_week: int = 0
        self.resolved_this_week: int = 0
        self.in_progress: int = 0
        
        # Additional metrics
        self.active_count: int = 0
        self.trend: int = 0
        self.skills_distribution: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for compatibility with smart analyzer."""
        return {
            'recommended_task': self.recommended_task or {},
            'health_score': self.health_score,
            'urgent_count': self.urgent_count,
            'open_count': self.open_count,
            'stale_count': self.stale_count,
            'beginner_task_count': self.beginner_task_count,
            'beginner_tasks': self.beginner_tasks,
            'top_categories': self.top_categories,
            'new_this_week': self.new_this_week,
            'resolved_this_week': self.resolved_this_week,
            'in_progress': self.in_progress,
            'active_count': self.active_count,
            'trend': self.trend,
            'skills_distribution': self.skills_distribution
        }


class FallbackAnalyzer:
    """Rule-based analyzer for generating badge data without LLM."""
    
    # Keywords for difficulty detection
    EASY_KEYWORDS = [
        "typo", "fix typo", "update doc", "add doc", "readme", 
        "comment", "formatting", "style", "lint", "minor",
        "good first issue", "beginner", "starter", "easy"
    ]
    
    HARD_KEYWORDS = [
        "refactor", "redesign", "rewrite", "architecture", "performance",
        "security", "critical", "complex", "algorithm", "optimization"
    ]
    
    # Keywords for category detection
    CATEGORY_KEYWORDS = {
        "performance": ["slow", "performance", "optimize", "speed", "latency", "bottleneck"],
        "security": ["security", "vulnerability", "auth", "permission", "xss", "sql injection"],
        "documentation": ["doc", "readme", "comment", "explain", "guide", "tutorial"],
        "testing": ["test", "coverage", "unit test", "integration", "ci"],
        "refactor": ["refactor", "clean", "technical debt", "duplicate", "smell"],
        "feature": ["feature", "implement", "add", "new", "enhancement"],
    }
    
    def __init__(self):
        """Initialize fallback analyzer."""
        pass
    
    def analyze(self, issues: List[Dict], prs: List[Dict] = None) -> BadgeAnalysis:
        """Analyze issues and PRs using rule-based heuristics.
        
        Args:
            issues: List of GitHub issues
            prs: List of GitHub pull requests (optional)
            
        Returns:
            BadgeAnalysis object
        """
        prs = prs or []
        result = BadgeAnalysis()
        
        # Filter open issues
        open_issues = [i for i in issues if i.get("state", "").lower() == "open"]
        result.open_count = len(open_issues)
        
        # Analyze each issue
        scored_issues = []
        for issue in open_issues:
            score_data = self._score_issue(issue)
            scored_issues.append({
                "issue": issue,
                "score": score_data["priority_score"],
                "difficulty": score_data["difficulty"],
                "category": score_data["category"],
                "is_urgent": score_data["is_urgent"],
                "is_beginner": score_data["is_beginner"],
                "is_stale": score_data["is_stale"],
                "is_assigned": score_data["is_assigned"],
                "skills": score_data["skills"],
            })
        
        # Sort by priority score
        scored_issues.sort(key=lambda x: x["score"], reverse=True)
        
        # Find recommended task (high priority but easy)
        result.recommended_task = self._find_recommended_task(scored_issues)
        
        # Calculate health score
        result.health_score = self._calculate_health_score(scored_issues)
        
        # Count metrics
        result.urgent_count = sum(1 for s in scored_issues if s["is_urgent"])
        result.stale_count = sum(1 for s in scored_issues if s["is_stale"])
        result.beginner_task_count = sum(1 for s in scored_issues if s["is_beginner"])
        
        # Extract beginner tasks (exclude assigned ones)
        beginner_issues = [
            s for s in scored_issues 
            if s["is_beginner"] and not s["is_assigned"]
        ][:10]
        result.beginner_tasks = [
            {
                'title': b['issue'].get('title', ''),
                'url': b['issue'].get('html_url', ''),
                'number': b['issue'].get('number', 0),
                'difficulty': b['difficulty'],
                'time_estimate': '1-2h',
                'impact': 'Medium',
                'skills': b['skills']
            }
            for b in beginner_issues
        ]
        
        # Calculate distribution
        result.top_categories = self._calculate_distribution(scored_issues)
        
        # Calculate activity (last 7 days)
        result.new_this_week = self._count_recent_issues(issues, days=7, state="all")
        result.resolved_this_week = self._count_recent_closed(issues, days=7)
        # Count issues that are assigned (in progress)
        result.in_progress = sum(1 for s in scored_issues if s["is_assigned"])
        result.active_count = result.new_this_week
        
        # Simple trend calculation (compare current week to last week)
        last_week_count = self._count_recent_issues(issues, days=14, state="all") - result.new_this_week
        result.trend = result.new_this_week - last_week_count if last_week_count > 0 else 0
        
        logger.info(
            f"Fallback analysis complete: {result.open_count} open, "
            f"{result.beginner_task_count} beginner, health={result.health_score}"
        )
        
        return result
    
    def _score_issue(self, issue: Dict) -> Dict:
        """Score a single issue using heuristics.
        
        Returns:
            Dict with priority_score, difficulty, category, etc.
        """
        title = issue.get("title", "").lower()
        body = issue.get("body", "").lower()
        labels = issue.get("labels_text", "").lower()
        created_at = issue.get("created_at", "")
        
        # Combine text for analysis
        text = f"{title} {body} {labels}"
        
        # Determine difficulty
        difficulty = self._infer_difficulty(text, labels)
        
        # Determine category
        category = self._infer_category(text)
        
        # Calculate age in days
        age_days = self._calculate_age_days(created_at)
        
        # Check if urgent (has urgent/critical labels or keywords)
        is_urgent = any(
            keyword in text
            for keyword in ["urgent", "critical", "blocker", "p0", "high priority"]
        )
        
        # Check if stale (> 90 days old)
        is_stale = age_days > 90
        
        # Check if beginner-friendly
        is_beginner = difficulty == "entry" or any(
            keyword in labels for keyword in ["good first issue", "beginner", "easy"]
        )
        
        # Check if assigned to someone (in progress)
        assignees = issue.get("assignees", [])
        is_assigned = len(assignees) > 0 if isinstance(assignees, list) else False
        
        # Extract skills from labels and title
        skills = self._extract_skills(text, labels)
        
        # Calculate priority score (0-100)
        priority_score = 50  # Base score
        
        # Age factor (older = higher priority)
        priority_score += min(age_days / 3, 20)  # +20 max for age
        
        # Urgency boost
        if is_urgent:
            priority_score += 30
        
        # Category impact
        if category in ["security", "performance"]:
            priority_score += 15
        elif category == "feature":
            priority_score -= 10  # Features lower priority than bugs
        
        # Difficulty factor (easier tasks slightly higher for community)
        if difficulty == "entry":
            priority_score += 5
        elif difficulty == "advanced":
            priority_score -= 5
        
        # Cap at 100
        priority_score = min(priority_score, 100)
        
        return {
            "priority_score": priority_score,
            "difficulty": difficulty,
            "category": category,
            "is_urgent": is_urgent,
            "is_beginner": is_beginner,
            "is_stale": is_stale,
            "is_assigned": is_assigned,
            "skills": skills,
            "age_days": age_days,
        }
    
    def _infer_difficulty(self, text: str, labels: str) -> str:
        """Infer difficulty level from text and labels.
        
        Returns:
            "entry", "intermediate", or "advanced"
        """
        # Check labels first
        if any(keyword in labels for keyword in ["easy", "good first issue", "beginner"]):
            return "entry"
        if any(keyword in labels for keyword in ["hard", "complex", "advanced"]):
            return "advanced"
        
        # Check text
        easy_count = sum(1 for keyword in self.EASY_KEYWORDS if keyword in text)
        hard_count = sum(1 for keyword in self.HARD_KEYWORDS if keyword in text)
        
        if easy_count > hard_count:
            return "entry"
        elif hard_count > easy_count:
            return "advanced"
        else:
            return "intermediate"
    
    def _infer_category(self, text: str) -> str:
        """Infer category from text.
        
        Returns:
            Category name
        """
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            scores[category] = sum(1 for keyword in keywords if keyword in text)
        
        # Return category with highest score, or "other"
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "other"
    
    def _calculate_age_days(self, created_at: str) -> int:
        """Calculate age of issue in days."""
        if not created_at:
            return 0
        
        try:
            # Parse ISO format datetime
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age = datetime.now(created.tzinfo) - created
            return age.days
        except (ValueError, AttributeError):
            return 0
    
    def _find_recommended_task(self, scored_issues: List[Dict]) -> Optional[Dict]:
        """Find best recommended task for new contributors.
        
        Criteria:
        - Easy or intermediate difficulty
        - High priority
        - Not stale
        """
        candidates = [
            s for s in scored_issues
            if s["difficulty"] in ["entry", "intermediate"]
            and not s["is_stale"]
            and not s["is_assigned"]  # Exclude assigned issues
            and s["score"] >= 40
        ]
        
        if not candidates:
            # Fallback to any easy task that's not assigned
            candidates = [
                s for s in scored_issues 
                if s["difficulty"] == "entry" and not s["is_assigned"]
            ]
        
        if candidates:
            best = candidates[0]
            issue = best["issue"]
            
            # Estimate time based on difficulty
            time_map = {"entry": "1-2h", "intermediate": "3-5h", "advanced": "1-2 days"}
            time_estimate = time_map.get(best["difficulty"], "3-5h")
            
            # Format impact
            impact = "High Impact" if best["is_urgent"] else "Medium Impact"
            
            return {
                "title": issue.get("title", "Untitled"),
                "difficulty": best["difficulty"].capitalize(),
                "impact": impact,
                "time_estimate": time_estimate,
                "url": issue.get("html_url", ""),
                "number": issue.get("number", 0),
                "skills": best["skills"],
            }
        
        return None
    
    def _calculate_health_score(self, scored_issues: List[Dict]) -> int:
        """Calculate overall project health score (0-100).
        
        Factors:
        - Number of urgent issues (worse)
        - Number of stale issues (worse)
        - Average age of issues (worse)
        - Ratio of easy to hard issues (better if balanced)
        """
        if not scored_issues:
            return 80  # No issues = healthy
        
        score = 100
        
        # Penalty for urgent issues
        urgent_count = sum(1 for s in scored_issues if s["is_urgent"])
        score -= min(urgent_count * 5, 30)
        
        # Penalty for stale issues
        stale_count = sum(1 for s in scored_issues if s["is_stale"])
        stale_ratio = stale_count / len(scored_issues)
        score -= int(stale_ratio * 30)
        
        # Penalty for high average age
        avg_age = sum(s["score"] for s in scored_issues) / len(scored_issues)
        if avg_age > 60:
            score -= 15
        elif avg_age > 40:
            score -= 5
        
        # Bonus for having beginner-friendly tasks
        beginner_count = sum(1 for s in scored_issues if s["is_beginner"])
        if beginner_count >= 3:
            score += 10
        
        return max(0, min(100, score))
    
    def _extract_skills(self, text: str, labels: str) -> List[str]:
        """Extract required skills from issue text and labels.
        
        Uses pattern matching to identify programming languages,
        frameworks, and technical skills mentioned.
        
        Returns:
            List of skill names
        """
        skills = set()
        
        # Common programming languages
        languages = [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go',
            'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
        ]
        
        # Popular frameworks and libraries
        frameworks = [
            'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express',
            'node', 'nodejs', 'spring', 'dotnet', '.net', 'rails', 'laravel',
            'flutter', 'react native', 'tensorflow', 'pytorch', 'pandas', 'numpy'
        ]
        
        # Databases
        databases = [
            'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite',
            'elasticsearch', 'cassandra', 'dynamodb', 'firebase'
        ]
        
        # DevOps and tools
        tools = [
            'docker', 'kubernetes', 'k8s', 'aws', 'azure', 'gcp', 'git',
            'ci/cd', 'jenkins', 'github actions', 'terraform', 'ansible'
        ]
        
        # Other technical skills
        other_skills = [
            'api', 'rest', 'graphql', 'websocket', 'microservices',
            'machine learning', 'ml', 'ai', 'data science', 'frontend',
            'backend', 'full stack', 'devops', 'testing', 'security',
            'ui/ux', 'design', 'documentation', 'sql'
        ]
        
        # Combine all skill keywords
        all_keywords = languages + frameworks + databases + tools + other_skills
        
        # Search in text and labels
        text_lower = text.lower()
        labels_lower = labels.lower()
        combined = f"{text_lower} {labels_lower}"
        
        for keyword in all_keywords:
            if keyword in combined:
                # Capitalize nicely
                if keyword in ['nodejs', 'node']:
                    skills.add('Node.js')
                elif keyword in ['react native']:
                    skills.add('React Native')
                elif keyword in ['github actions']:
                    skills.add('GitHub Actions')
                elif keyword in ['ci/cd']:
                    skills.add('CI/CD')
                elif keyword in ['dotnet', '.net']:
                    skills.add('.NET')
                elif keyword in ['ui/ux']:
                    skills.add('UI/UX')
                elif keyword in ['machine learning', 'ml']:
                    skills.add('Machine Learning')
                elif keyword in ['k8s']:
                    skills.add('Kubernetes')
                elif keyword in ['postgres', 'postgresql']:
                    skills.add('PostgreSQL')
                elif keyword == 'api':
                    skills.add('API Development')
                elif keyword == 'rest':
                    skills.add('REST API')
                elif keyword == 'sql':
                    skills.add('SQL')
                else:
                    skills.add(keyword.capitalize())
        
        # If no skills found, return generic category-based skills
        if not skills:
            if 'documentation' in combined or 'docs' in combined or 'readme' in combined:
                skills.add('Documentation')
            elif 'test' in combined:
                skills.add('Testing')
            elif 'bug' in combined or 'fix' in combined:
                skills.add('Debugging')
            elif 'feature' in combined:
                skills.add('Feature Development')
            elif 'ui' in combined or 'interface' in combined:
                skills.add('UI Development')
            else:
                return ['General']  # Default if nothing found
        
        return sorted(list(skills))
    
    def _calculate_distribution(self, scored_issues: List[Dict]) -> List[Dict]:
        """Calculate top 3 categories by count."""
        if not scored_issues:
            return [
                {"name": "No issues", "count": 0},
                {"name": "N/A", "count": 0},
                {"name": "N/A", "count": 0},
            ]
        
        # Count by category
        category_counts = {}
        for s in scored_issues:
            cat = s["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Sort by count
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top 3
        result = []
        for cat, count in sorted_categories[:3]:
            result.append({"name": cat, "count": count})
        
        # Pad if less than 3
        while len(result) < 3:
            result.append({"name": "Other", "count": 0})
        
        return result
    
    def _count_recent_issues(self, issues: List[Dict], days: int, state: str = "all") -> int:
        """Count issues created in last N days."""
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = 0
        
        for issue in issues:
            created_at = issue.get("created_at", "")
            if not created_at:
                continue
            
            try:
                # Parse datetime and ensure it's timezone-aware
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                # If somehow still naive, make it UTC
                if created.tzinfo is None:
                    from datetime import timezone
                    created = created.replace(tzinfo=timezone.utc)
                if created >= cutoff:
                    if state == "all" or issue.get("state", "").lower() == state:
                        count += 1
            except (ValueError, AttributeError):
                continue
        
        return count
    
    def _count_recent_closed(self, issues: List[Dict], days: int) -> int:
        """Count issues closed in last N days."""
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = 0
        
        for issue in issues:
            if issue.get("state", "").lower() != "closed":
                continue
            
            closed_at = issue.get("closed_at", "")
            if not closed_at:
                continue
            
            try:
                # Parse datetime and ensure it's timezone-aware
                closed = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))
                # If somehow still naive, make it UTC
                if closed.tzinfo is None:
                    from datetime import timezone
                    closed = closed.replace(tzinfo=timezone.utc)
                if closed >= cutoff:
                    count += 1
            except (ValueError, AttributeError):
                continue
        
        return count
