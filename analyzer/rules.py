"""Heuristics for classifying and scoring DebtItems."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from .models import (
    DebtCategory,
    DifficultyLevel,
    ImpactScope,
    ScoreBreakdown,
)


CATEGORY_KEYWORDS = {
    DebtCategory.SECURITY: {"security", "vulnerability", "xss", "csrf", "encryption"},
    DebtCategory.PERFORMANCE: {"perf", "latency", "slow", "optimize", "throughput"},
    DebtCategory.MAINTAINABILITY: {"refactor", "cleanup", "tech debt", "restructure"},
    DebtCategory.DOCUMENTATION: {"docs", "documentation", "readme", "guide"},
    DebtCategory.TESTING: {"test", "coverage", "unit test", "integration"},
    DebtCategory.CI: {"ci", "pipeline", "workflow", "actions", "build"},
    DebtCategory.FEATURE: {"feature", "enhancement", "improve", "epic"},
}

SKILL_BY_EXTENSION = {
    ".py": ["Python"],
    ".ts": ["TypeScript"],
    ".tsx": ["TypeScript", "React"],
    ".js": ["JavaScript"],
    ".jsx": ["JavaScript", "React"],
    ".go": ["Go"],
    ".rs": ["Rust"],
    ".java": ["Java"],
    ".kt": ["Kotlin"],
    ".swift": ["Swift"],
}

_IMPACT_VALUE = {
    ImpactScope.LOCAL: 1.0,
    ImpactScope.MODULE: 2.0,
    ImpactScope.SYSTEM: 3.0,
}


def _normalize_tokens(*sources: Optional[str]) -> List[str]:
    tokens: List[str] = []
    for source in sources:
        if not source:
            continue
        tokens.append(source.lower())
    return tokens


def _matches_keywords(tokens: Iterable[str], keywords: Iterable[str]) -> bool:
    joined = " ".join(tokens)
    return any(keyword in joined for keyword in keywords)


def infer_category(text: Optional[str], labels: Optional[List[str]] = None) -> DebtCategory:
    """Infer category from text and labels, with support for PR/Issue title tags."""
    if not text:
        return DebtCategory.UNKNOWN
    
    # First, check for common PR/Issue title prefixes like [Feat], [Fix], [Bug], etc.
    import re
    title_prefix_pattern = r'^\[?(feat|feature|bug|fix|docs?|documentation|test|refactor|perf|performance|ci|chore|style)\]?'
    match = re.search(title_prefix_pattern, text, re.IGNORECASE)
    
    if match:
        prefix = match.group(1).lower()
        if prefix in ('feat', 'feature'):
            return DebtCategory.FEATURE
        elif prefix in ('bug', 'fix'):
            return DebtCategory.MAINTAINABILITY
        elif prefix in ('docs', 'doc', 'documentation'):
            return DebtCategory.DOCUMENTATION
        elif prefix in ('test'):
            return DebtCategory.TESTING
        elif prefix in ('perf', 'performance'):
            return DebtCategory.PERFORMANCE
        elif prefix == 'ci':
            return DebtCategory.CI
        elif prefix in ('refactor', 'chore'):
            return DebtCategory.MAINTAINABILITY
    
    # Fallback to keyword matching
    tokens = _normalize_tokens(text, " ".join(labels or []))
    for category, keywords in CATEGORY_KEYWORDS.items():
        if _matches_keywords(tokens, keywords):
            return category
    return DebtCategory.UNKNOWN


def derive_module(file_path: Optional[str]) -> str:
    if not file_path:
        return "root"
    parts = Path(file_path).as_posix().split("/")
    return parts[0] or "root"


def infer_skills_from_path(file_path: Optional[str]) -> List[str]:
    if not file_path:
        return []
    extension = Path(file_path).suffix.lower()
    return SKILL_BY_EXTENSION.get(extension, [])


def infer_impact_scope(labels: Optional[List[str]] = None) -> ImpactScope:
    labels = [label.lower() for label in (labels or [])]
    if any(label in {"critical", "high"} for label in labels):
        return ImpactScope.SYSTEM
    if any(label in {"backend", "frontend", "api"} for label in labels):
        return ImpactScope.MODULE
    return ImpactScope.LOCAL


def estimate_risk(category: DebtCategory, is_blocker: bool = False) -> int:
    base = {
        DebtCategory.SECURITY: 5,
        DebtCategory.PERFORMANCE: 4,
        DebtCategory.MAINTAINABILITY: 3,
        DebtCategory.DOCUMENTATION: 2,
        DebtCategory.TESTING: 3,
        DebtCategory.CI: 3,
        DebtCategory.FEATURE: 2,
        DebtCategory.UNKNOWN: 2,
    }.get(category, 2)
    if is_blocker:
        base += 1
    return min(base, 5)


def estimate_cost(skills: List[str], body: Optional[str]) -> int:
    complexity_hint = 1
    if body:
        length = len(body)
        if length > 1500:
            complexity_hint = 4
        elif length > 800:
            complexity_hint = 3
        elif length > 300:
            complexity_hint = 2
    return min(max(complexity_hint + max(len(skills) - 1, 0), 1), 5)


def infer_difficulty(cost_level: int) -> DifficultyLevel:
    if cost_level >= 4:
        return DifficultyLevel.ADVANCED
    if cost_level >= 2:
        return DifficultyLevel.INTERMEDIATE
    return DifficultyLevel.ENTRY


def compute_interest(created_at: Optional[datetime], reference: datetime) -> float:
    if not created_at:
        return 1.0
    age_days = max((reference - created_at).days, 0)
    return 1.0 + age_days / 30.0


def compute_priority_score(
    risk_level: int,
    impact_scope: ImpactScope,
    interest: float,
    cost_level: int,
) -> ScoreBreakdown:
    impact_value = _IMPACT_VALUE.get(impact_scope, 1.0)
    weights = {
        "risk": 0.4,
        "impact": 0.3,
        "interest": 0.2,
        "cost": 0.1,
    }
    total = (
        weights["risk"] * risk_level
        + weights["impact"] * impact_value
        + weights["interest"] * interest
        - weights["cost"] * cost_level
    )
    return ScoreBreakdown(
        risk=risk_level,
        impact=impact_value,
        interest=interest,
        cost=cost_level,
        total=round(total, 2),
    )

