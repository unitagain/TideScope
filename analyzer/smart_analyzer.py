"""
Smart Badge Analyzer with Automatic Fallback Strategy

This analyzer intelligently decides whether to use LLM or rule-based
analysis based on:
- Repository visit count (new vs popular)
- Daily LLM cost budget
- Analysis quality requirements
- Cache availability

Cost Control Strategy:
- New repos (< 10 visits): Use LLM for high quality
- Medium repos (10-100 visits): Use rule-based analysis
- Popular repos (> 100 visits): Use pregenerated/cached results
- Cost limit reached: Force fallback to rules
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime

from analyzer.llm_badge_analyzer import LLMBadgeAnalyzer
from analyzer.llm_client import LLMClient
from analyzer.fallback_analyzer import FallbackAnalyzer
from utils.github_helper import fetch_repo_data_for_badges

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Track API usage and costs
    
    In production, this should use Redis or a database.
    For now, using in-memory cache with file backup.
    """
    
    def __init__(self):
        self._visit_counts = {}  # repo_key -> count
        self._llm_costs = {}  # date -> cost
        self._daily_limit = float(os.getenv('DAILY_LLM_LIMIT', '1.0'))  # ¥1 per day
    
    def get_visit_count(self, repo_key: str) -> int:
        """Get visit count for a repository (last 30 days)"""
        return self._visit_counts.get(repo_key, 0)
    
    def increment_visit(self, repo_key: str):
        """Increment visit count for a repository"""
        self._visit_counts[repo_key] = self._visit_counts.get(repo_key, 0) + 1
        logger.debug(f"Visit count for {repo_key}: {self._visit_counts[repo_key]}")
    
    def record_llm_usage(self, repo_key: str, cost: float):
        """Record LLM API usage cost"""
        today = datetime.now().strftime('%Y-%m-%d')
        self._llm_costs[today] = self._llm_costs.get(today, 0.0) + cost
        logger.info(f"LLM cost for {repo_key}: ¥{cost:.4f}, Today total: ¥{self._llm_costs[today]:.4f}")
    
    def get_daily_cost(self) -> float:
        """Get today's total LLM cost"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self._llm_costs.get(today, 0.0)
    
    def has_budget_remaining(self) -> bool:
        """Check if daily budget has remaining capacity"""
        return self.get_daily_cost() < self._daily_limit
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            'daily_cost': self.get_daily_cost(),
            'daily_limit': self._daily_limit,
            'budget_used_percent': (self.get_daily_cost() / self._daily_limit) * 100,
            'total_repos_tracked': len(self._visit_counts),
            'total_visits_today': sum(1 for k, v in self._visit_counts.items() if v > 0)
        }


# Global usage tracker instance
usage_tracker = UsageTracker()


class SmartBadgeAnalyzer:
    """
    Smart analyzer that automatically chooses between LLM and rule-based analysis
    
    Decision Logic:
    1. Check if LLM is enabled and budget available
    2. Check repository visit count
    3. New repos (<10 visits) -> LLM (high quality)
    4. Medium repos (10-100) -> Rules (medium quality)
    5. Popular repos (>100) -> Cached (basic quality)
    """
    
    # Cost per LLM analysis (DeepSeek estimate)
    COST_PER_LLM_CALL = 0.003  # ¥0.003 per analysis
    
    # Visit thresholds for decision making
    THRESHOLD_NEW = 10  # Below this: use LLM
    THRESHOLD_MEDIUM = 100  # Below this: use rules, above: use cache
    
    def __init__(self):
        """Initialize smart analyzer with both LLM and fallback engines"""
        # Initialize LLM client
        provider = os.getenv('LLM_PROVIDER', 'deepseek')  # Default to DeepSeek
        llm_client = LLMClient(
            provider=provider,
            enabled=True  # Will auto-disable if no API key
        )
        
        # Initialize analyzers
        self.llm_analyzer = LLMBadgeAnalyzer(
            llm_client=llm_client,
            use_llm=True,
            max_issues_to_analyze=10
        )
        self.fallback_analyzer = FallbackAnalyzer()
        self.usage_tracker = usage_tracker
        
        # Check if LLM should be force-disabled
        self.force_fallback = os.getenv('FORCE_FALLBACK', '0') == '1'
        
        if self.force_fallback:
            logger.warning("FORCE_FALLBACK enabled - LLM analysis disabled")
        
        # Log LLM status
        if self.llm_analyzer.use_llm:
            logger.info(f"LLM analysis enabled with provider: {provider}")
        else:
            logger.info("LLM analysis disabled (no API key found)")
    
    def set_force_fallback(self, force: bool):
        """Enable or disable forced fallback mode at runtime."""
        self.force_fallback = bool(force)
        if self.force_fallback:
            logger.warning("FORCE_FALLBACK enabled - LLM analysis disabled")
        else:
            logger.info("FORCE_FALLBACK disabled - LLM analysis allowed")

    async def analyze(
        self,
        owner: str,
        repo: str,
        for_level: str = 'all'
    ) -> Dict:
        """
        Analyze repository with smart strategy selection
        
        Args:
            owner: Repository owner
            repo: Repository name
            for_level: Target user level (beginners|all|experts)
            
        Returns:
            Analysis result dict with badge data
        """
        
        repo_key = f"{owner}/{repo}"
        
        # Increment visit counter
        self.usage_tracker.increment_visit(repo_key)
        
        # Get visit count
        visit_count = self.usage_tracker.get_visit_count(repo_key)
        
        # Decide which analyzer to use
        use_llm = self._should_use_llm(repo_key, visit_count)
        
        logger.info(f"Analyzing {repo_key} - visits: {visit_count}, use_llm: {use_llm}")
        
        # Fetch GitHub data
        try:
            github_data = fetch_repo_data_for_badges(owner, repo)
        except Exception as e:
            logger.error(f"Failed to fetch GitHub data for {repo_key}: {e}")
            return self._generate_error_result(str(e))
        
        # Perform analysis
        if use_llm:
            return await self._analyze_with_llm(
                github_data,
                repo_key,
                for_level
            )
        else:
            return self._analyze_with_rules(
                github_data,
                repo_key,
                for_level
            )
    
    def _should_use_llm(self, repo_key: str, visit_count: int) -> bool:
        """
        Determine if LLM should be used for this analysis
        
        Returns True if:
        - Not force-disabled
        - Budget available
        - Visit count below threshold
        """
        
        # Force fallback check
        if self.force_fallback:
            logger.debug(f"{repo_key}: LLM disabled by FORCE_FALLBACK")
            return False
        
        # Budget check
        if not self.usage_tracker.has_budget_remaining():
            daily_cost = self.usage_tracker.get_daily_cost()
            logger.warning(f"{repo_key}: Daily budget limit reached (¥{daily_cost:.2f})")
            return False
        
        # Visit count check
        if visit_count >= self.THRESHOLD_NEW:
            logger.info(f"{repo_key}: Visit count {visit_count} >= {self.THRESHOLD_NEW}, using fallback")
            return False
        
        # LLM analyzer availability check
        if not self.llm_analyzer.use_llm:
            logger.warning(f"{repo_key}: LLM analyzer not available")
            return False
        
        return True
    
    async def _analyze_with_llm(
        self,
        github_data: Dict,
        repo_key: str,
        for_level: str
    ) -> Dict:
        """Perform LLM-powered analysis"""
        
        logger.info(f"Using LLM analysis for {repo_key}")
        
        try:
            # Call LLM analyzer
            result_obj = self.llm_analyzer.analyze(
                github_data['issues'],
                github_data['prs']
            )
            
            # Convert to dict (handle Pydantic models)
            if hasattr(result_obj, 'to_dict'):
                result = result_obj.to_dict()
            elif hasattr(result_obj, 'model_dump'):
                result = result_obj.model_dump()
            elif hasattr(result_obj, 'dict'):
                result = result_obj.dict()
            else:
                result = dict(result_obj)
            
            # Record cost
            self.usage_tracker.record_llm_usage(
                repo_key,
                self.COST_PER_LLM_CALL
            )
            
            # Add metadata
            result['analysis_method'] = 'llm'
            result['quality'] = 'high'
            result['analyzed_at'] = datetime.now().isoformat()
            
            logger.info(f"LLM analysis completed for {repo_key}")
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed for {repo_key}: {e}")
            logger.info(f"Falling back to rule-based analysis for {repo_key}")
            
            # Fallback to rules on error
            return self._analyze_with_rules(github_data, repo_key, for_level)
    
    def _analyze_with_rules(
        self,
        github_data: Dict,
        repo_key: str,
        for_level: str
    ) -> Dict:
        """Perform rule-based analysis"""
        
        logger.info(f"Using rule-based analysis for {repo_key}")
        
        try:
            # Call fallback analyzer
            result_obj = self.fallback_analyzer.analyze(
                github_data['issues'],
                github_data['prs']
            )
            
            # Convert result object to dict
            if hasattr(result_obj, 'to_dict'):
                result = result_obj.to_dict()
            elif hasattr(result_obj, 'model_dump'):
                result = result_obj.model_dump()
            elif hasattr(result_obj, 'dict'):
                result = result_obj.dict()
            else:
                result = dict(result_obj)
            
            result['analysis_method'] = 'rules'
            result['quality'] = 'medium'
            result['analyzed_at'] = datetime.now().isoformat()
            
            logger.info(f"Rule-based analysis completed for {repo_key}")
            return result
            
        except Exception as e:
            logger.error(f"Rule-based analysis failed for {repo_key}: {e}")
            return self._generate_error_result(str(e))
    
    def _generate_error_result(self, error_message: str) -> Dict:
        """Generate error result when analysis fails"""
        
        return {
            'error': True,
            'error_message': error_message,
            'health_score': 50,
            'recommended_task': {
                'title': 'Unable to analyze repository',
                'difficulty': 'Unknown',
                'time_estimate': 'N/A',
                'impact': 'Unknown',
                'skills': [],
                'url': ''
            },
            'beginner_tasks': [],
            'open_count': 0,
            'urgent_count': 0,
            'stale_count': 0,
            'analysis_method': 'error',
            'quality': 'none',
            'analyzed_at': datetime.now().isoformat()
        }
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return self.usage_tracker.get_stats()


# Singleton instance for easy import
smart_analyzer = SmartBadgeAnalyzer()


# Cost monitoring utility functions
def check_budget_alert() -> Optional[str]:
    """
    Check if budget is approaching limit and return alert message
    
    Returns:
        Alert message if budget > 80%, None otherwise
    """
    stats = usage_tracker.get_stats()
    percent = stats['budget_used_percent']
    
    if percent >= 100:
        return f"🚨 CRITICAL: Daily budget exceeded ({percent:.1f}%)"
    elif percent >= 80:
        return f"⚠️ WARNING: Daily budget at {percent:.1f}%"
    
    return None


def enable_strict_mode():
    """
    Enable strict cost control mode
    
    This disables all LLM calls and increases cache TTL
    """
    os.environ['FORCE_FALLBACK'] = '1'
    os.environ['CACHE_TTL'] = '172800'  # 48 hours
    logger.warning("🛑 Strict mode enabled - All LLM calls suspended")


def disable_strict_mode():
    """Disable strict mode and restore normal operation"""
    os.environ['FORCE_FALLBACK'] = '0'
    os.environ['CACHE_TTL'] = '86400'  # 24 hours
    logger.info("✅ Strict mode disabled - Normal operation restored")


# Quick test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        analyzer = SmartBadgeAnalyzer()
        
        # Simulate analysis for a new repo
        print("\n=== Test 1: New Repository ===")
        result1 = await analyzer.analyze("test", "repo1", "all")
        print(f"Method: {result1.get('analysis_method')}")
        print(f"Quality: {result1.get('quality')}")
        
        # Simulate multiple visits (should trigger fallback)
        print("\n=== Test 2: Popular Repository ===")
        for i in range(15):
            usage_tracker.increment_visit("test/repo2")
        
        result2 = await analyzer.analyze("test", "repo2", "all")
        print(f"Method: {result2.get('analysis_method')}")
        print(f"Quality: {result2.get('quality')}")
        
        # Check stats
        print("\n=== Usage Statistics ===")
        stats = analyzer.get_usage_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Check budget alert
        alert = check_budget_alert()
        if alert:
            print(f"\n{alert}")
    
    asyncio.run(test())
