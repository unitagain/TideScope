"""Data models for TideScope analyzer outputs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DebtSourceType(str, Enum):
    TODO = "todo"
    ISSUE = "issue"
    PULL_REQUEST = "pr"


class DebtCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    CI = "ci"
    FEATURE = "feature"
    UNKNOWN = "unknown"


class ImpactScope(str, Enum):
    LOCAL = "local"
    MODULE = "module"
    SYSTEM = "system"


class DifficultyLevel(str, Enum):
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ScoreBreakdown(BaseModel):
    risk: float
    impact: float
    interest: float
    cost: float
    total: float


class DebtItem(BaseModel):
    id: str
    source_type: DebtSourceType
    reference_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    module: Optional[str] = None
    category: DebtCategory = DebtCategory.UNKNOWN
    skills: List[str] = Field(default_factory=list)
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    risk_level: int = 1
    impact_scope: ImpactScope = ImpactScope.LOCAL
    cost_level: int = 1
    interest: float = 0.0
    priority: ScoreBreakdown
    status: str = "open"
    assignees: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    html_url: Optional[str] = None
    recommendation: Optional[str] = None  # LLM-generated suggestion for required capabilities


class StarMapNode(BaseModel):
    id: str
    label: str
    module: Optional[str]
    category: DebtCategory
    source_type: DebtSourceType = DebtSourceType.TODO
    reference_id: Optional[str] = None
    priority: float
    radius: float
    angle: float
    size: float
    status: str
    assignees: List[str]
    skills: List[str]
    difficulty: DifficultyLevel
    html_url: Optional[str] = None
    recommendation: Optional[str] = None  # LLM-generated suggestion


class StarMapData(BaseModel):
    nodes: List[StarMapNode]
    metadata: Dict[str, str] = Field(default_factory=dict)


class AggregateMetrics(BaseModel):
    total_debts: int
    by_category: Dict[str, int]
    by_module: Dict[str, int]


class AnalysisReport(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    repository: str
    debts: List[DebtItem]
    aggregates: AggregateMetrics
    star_map: StarMapData

