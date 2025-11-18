"""Utilities to transform raw scan data into analysis reports."""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from scanner.models import CodeTodo, IssueRaw, PullRequestRaw, RawScanResult

from .llm_client import IssueLLMInsights, LLMClient
from .models import (
    AnalysisReport,
    AggregateMetrics,
    DebtCategory,
    DebtItem,
    DebtSourceType,
    ImpactScope,
)
from .rules import (
    compute_interest,
    compute_priority_score,
    derive_module,
    estimate_cost,
    estimate_risk,
    infer_category,
    infer_difficulty,
    infer_impact_scope,
    infer_skills_from_path,
)
from .star_map import build_star_map

logger = logging.getLogger(__name__)


def _load_raw_scan(path: Path | str) -> RawScanResult:
    raw_path = Path(path).expanduser().resolve()
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw scan file not found: {raw_path}")
    return RawScanResult.model_validate_json(raw_path.read_text(encoding="utf-8"))


class AnalysisBuilder:
    """Build AnalysisReport objects from raw scan data."""

    def __init__(
        self, 
        use_llm: bool = False, 
        llm_model: str = "gpt-4o-mini",
        llm_provider: str = "openai",
        project_context: Optional[str] = None
    ) -> None:
        self.llm_client = LLMClient(
            model=llm_model, 
            enabled=use_llm, 
            provider=llm_provider,
            project_context=project_context
        )
        self.use_llm = use_llm

    def build_from_raw_file(self, raw_path: Path | str) -> AnalysisReport:
        raw = _load_raw_scan(raw_path)
        return self.build_from_raw(raw)

    def build_from_raw(self, raw: RawScanResult) -> AnalysisReport:
        debts: List[DebtItem] = []
        reference_time = raw.generated_at or datetime.utcnow()
        
        # Auto-use README as project context if available and not already set
        if raw.readme and not self.llm_client.project_context:
            logger.info("Using README as project context for LLM analysis")
            self.llm_client.project_context = raw.readme

        # Process TODOs (no LLM needed)
        logger.info(f"Processing {len(raw.code_todos)} code TODOs...")
        for todo in raw.code_todos:
            debts.append(self._debt_from_todo(todo, reference_time))

        # Process Issues with LLM optimization
        # Smart strategy: only use LLM for open issues to save time and cost
        if self.use_llm and len(raw.issues) > 0:
            open_issues = [i for i in raw.issues if i.state.lower() == 'open']
            closed_issues = [i for i in raw.issues if i.state.lower() != 'open']
            
            logger.info(f"Processing {len(open_issues)} open issues with LLM (skipping {len(closed_issues)} closed)...")
            debts.extend(self._process_issues_concurrent(open_issues, reference_time))
            
            # Process closed issues without LLM
            for issue in closed_issues:
                debts.append(self._debt_from_issue(issue, reference_time, use_llm=False))
        else:
            logger.info(f"Processing {len(raw.issues)} issues...")
            for issue in raw.issues:
                debts.append(self._debt_from_issue(issue, reference_time, use_llm=False))

        # Process PRs (no LLM for PRs currently)
        logger.info(f"Processing {len(raw.pull_requests)} pull requests...")
        pr_count_before = len(debts)
        for pull_request in raw.pull_requests:
            debt = self._debt_from_pr(pull_request, reference_time)
            debts.append(debt)
        pr_count_after = len(debts)
        logger.info(f"Added {pr_count_after - pr_count_before} PRs to debts list")

        aggregates = self._build_aggregates(debts)
        star_map = build_star_map(debts)

        return AnalysisReport(
            repository=raw.repository,
            debts=debts,
            aggregates=aggregates,
            star_map=star_map,
        )

    def _debt_from_todo(self, todo: CodeTodo, reference_time: datetime) -> DebtItem:
        file_path = todo.file_path
        module = derive_module(file_path)
        skills = infer_skills_from_path(file_path)
        category = infer_category(todo.content)
        risk_level = estimate_risk(category)
        impact_scope = infer_impact_scope()
        cost_level = estimate_cost(skills, todo.content)
        difficulty = infer_difficulty(cost_level)
        interest = compute_interest(None, reference_time)
        priority = compute_priority_score(risk_level, impact_scope, interest, cost_level)

        return DebtItem(
            id=f"todo:{file_path}:{todo.line_number}",
            source_type=DebtSourceType.TODO,
            title=todo.content[:120] or todo.tag,
            description=todo.context,
            file_path=file_path,
            module=module,
            category=category,
            skills=skills,
            difficulty=difficulty,
            risk_level=risk_level,
            impact_scope=impact_scope,
            cost_level=cost_level,
            interest=interest,
            priority=priority,
        )

    def _debt_from_issue(self, issue: IssueRaw, reference_time: datetime, use_llm: bool = True) -> DebtItem:
        """Process issue with optional LLM."""
        insights = self._maybe_query_llm(issue.title, issue.body) if use_llm and self.use_llm else None
        return self._debt_from_issue_with_insights(issue, reference_time, insights)
    
    def _debt_from_issue_with_insights(
        self, issue: IssueRaw, reference_time: datetime, insights: Optional[IssueLLMInsights]
    ) -> DebtItem:
        """Build DebtItem from issue and optional LLM insights."""
        category = insights.category if insights and insights.category else infer_category(
            issue.title, issue.labels
        )
        skills = insights.skills if insights and insights.skills else []
        impact_scope = infer_impact_scope(issue.labels)
        risk_level = estimate_risk(category, is_blocker=bool(insights and insights.is_blocker))
        cost_level = estimate_cost(skills or ["General"], issue.body)
        difficulty = insights.difficulty if insights and insights.difficulty else infer_difficulty(
            cost_level
        )
        interest = compute_interest(issue.created_at, reference_time)
        priority = compute_priority_score(risk_level, impact_scope, interest, cost_level)
        module = (issue.labels[0].lower() if issue.labels else "issues").replace(" ", "-")

        recommendation = insights.recommendation if insights else None
        
        return DebtItem(
            id=f"issue:{issue.number}",
            source_type=DebtSourceType.ISSUE,
            reference_id=str(issue.number),
            title=issue.title,
            description=issue.body,
            module=module,
            category=category,
            skills=skills,
            difficulty=difficulty,
            risk_level=risk_level,
            impact_scope=impact_scope,
            cost_level=cost_level,
            interest=interest,
            priority=priority,
            status=issue.state,
            assignees=issue.assignees,
            created_at=issue.created_at,
            html_url=issue.html_url,
            recommendation=recommendation,
        )

    def _debt_from_pr(self, pr: PullRequestRaw, reference_time: datetime, use_llm: bool = True) -> DebtItem:
        """Process PR with optional LLM analysis."""
        summary = f"PR #{pr.number}: {pr.title}"
        
        # Use LLM for open PRs if enabled
        insights = None
        if use_llm and self.use_llm and pr.state.lower() == 'open':
            insights = self._maybe_query_pr_llm(pr.title, pr.body)
        
        # Use LLM insights if available, otherwise infer
        category = insights.category if insights and insights.category else infer_category(pr.title)
        skills = insights.skills if insights and insights.skills else []
        difficulty = insights.difficulty if insights and insights.difficulty else infer_difficulty(2)
        
        impact_scope = ImpactScope.MODULE if not pr.draft else ImpactScope.LOCAL
        risk_level = estimate_risk(category)
        cost_level = estimate_cost(skills or ["Code Review"], pr.body)
        interest = compute_interest(pr.created_at, reference_time)
        priority = compute_priority_score(risk_level, impact_scope, interest, cost_level)
        
        # Extract issue reference from PR title and body
        # Priority 1: Look for "Fixes/Closes/Resolves #123" patterns (GitHub linking keywords)
        text = f"{pr.title} {pr.body or ''}"
        fixes_pattern = r'(?:fix(?:es|ed)?|close(?:s|d)?|resolve(?:s|d)?)\s*#(\d+)'
        fixing_refs = re.findall(fixes_pattern, text, re.IGNORECASE)
        
        if fixing_refs:
            # Use the last "fixes" reference (most specific, after template examples)
            reference_id = fixing_refs[-1]
        else:
            # Priority 2: Use first issue reference if no explicit "fixes" found
            all_refs = re.findall(r'#(\d+)', text)
            reference_id = all_refs[0] if all_refs else None

        recommendation = insights.recommendation if insights else None
        
        return DebtItem(
            id=f"pr:{pr.number}",
            source_type=DebtSourceType.PULL_REQUEST,
            reference_id=reference_id,
            title=summary,
            description=pr.body,
            module="pull-requests",
            category=category,
            skills=skills,
            difficulty=difficulty,
            risk_level=risk_level,
            impact_scope=impact_scope,
            cost_level=cost_level,
            interest=interest,
            priority=priority,
            status=pr.state,
            created_at=pr.created_at,
            html_url=pr.html_url,
            recommendation=recommendation,
        )

    def _process_issues_concurrent(self, issues: List[IssueRaw], reference_time: datetime) -> List[DebtItem]:
        """Process issues concurrently with LLM and progress tracking."""
        results = []
        total = len(issues)
        
        # Use thread pool for concurrent API calls
        max_workers = 2  # Reduced to 2 to avoid OpenAI rate limits
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_issue = {
                executor.submit(self._process_single_issue_with_llm, issue, reference_time, idx, total): issue
                for idx, issue in enumerate(issues, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_issue):
                try:
                    debt_item = future.result(timeout=30)  # 30s timeout per issue
                    if debt_item:
                        results.append(debt_item)
                except Exception as exc:
                    issue = future_to_issue[future]
                    logger.error(f"Failed to process issue #{issue.number}: {exc}")
                    # Fallback to non-LLM processing
                    results.append(self._debt_from_issue(issue, reference_time, use_llm=False))
        
        logger.info(f"Completed processing {len(results)} issues")
        return results
    
    def _process_single_issue_with_llm(
        self, issue: IssueRaw, reference_time: datetime, idx: int, total: int
    ) -> DebtItem:
        """Process single issue with LLM and progress logging."""
        logger.info(f"[{idx}/{total}] Analyzing issue #{issue.number}: {issue.title[:50]}...")
        insights = self._maybe_query_llm(issue.title, issue.body)
        return self._debt_from_issue_with_insights(issue, reference_time, insights)
    
    def _maybe_query_llm(self, title: str, body: Optional[str]) -> IssueLLMInsights | None:
        """Query LLM for issue analysis with retry logic."""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return self.llm_client.analyze_issue(title, body)
            except Exception as exc:
                if attempt < max_retries - 1:
                    logger.warning(f"LLM request failed (attempt {attempt + 1}/{max_retries}): {exc}")
                    time.sleep(1)  # Brief delay before retry
                else:
                    logger.error(f"LLM request failed after {max_retries} attempts: {exc}")
                    return None
        return None
    
    def _maybe_query_pr_llm(self, title: str, body: Optional[str]) -> IssueLLMInsights | None:
        """Query LLM for PR analysis with retry logic."""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return self.llm_client.analyze_pr(title, body)
            except Exception as exc:
                if attempt < max_retries - 1:
                    logger.warning(f"PR LLM request failed (attempt {attempt + 1}/{max_retries}): {exc}")
                    time.sleep(1)
                else:
                    logger.error(f"PR LLM request failed after {max_retries} attempts: {exc}")
                    return None
        return None

    @staticmethod
    def _build_aggregates(debts: List[DebtItem]) -> AggregateMetrics:
        by_category_counter = Counter(debt.category.value for debt in debts)
        by_module_counter = Counter((debt.module or "unknown") for debt in debts)
        return AggregateMetrics(
            total_debts=len(debts),
            by_category=dict(by_category_counter),
            by_module=dict(by_module_counter),
        )


def build_analysis_report(
    raw_path: Path | str, 
    use_llm: bool = False, 
    llm_model: str = "gpt-4o-mini",
    llm_provider: str = "openai",
    project_context: Optional[str] = None
) -> AnalysisReport:
    builder = AnalysisBuilder(
        use_llm=use_llm, 
        llm_model=llm_model, 
        llm_provider=llm_provider,
        project_context=project_context
    )
    return builder.build_from_raw_file(raw_path)
