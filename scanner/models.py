"""Data models shared across scanner modules."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, validator


TODO_PATTERNS = ("TODO", "FIXME", "HACK", "NOTE", "@tech-debt")


class GitHubConfig(BaseModel):
    owner: str
    repo: str
    token_env: Optional[str] = Field(
        default=None,
        description="Name of the environment variable storing the PAT.",
    )
    api_base: str = Field(default="https://api.github.com")


class ScanMode(str, Enum):
    QUICK = "quick"
    DEEP = "deep"


class ScanConfig(BaseModel):
    repository_path: Path = Field(default=Path("."))
    include_extensions: List[str] = Field(
        default_factory=lambda: [
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".java",
            ".kt",
            ".swift",
        ]
    )
    github: Optional[GitHubConfig] = None
    mode: ScanMode = Field(default=ScanMode.DEEP, description="quick skips code scan")

    @validator("repository_path", pre=True)
    def _resolve_repo_path(cls, value: str | Path) -> Path:
        """Ensure repository_path is always a Path object."""

        return Path(value).expanduser().resolve()


class CodeTodo(BaseModel):
    file_path: str
    line_number: int
    tag: str
    content: str
    context: Optional[str] = None


class IssueRaw(BaseModel):
    id: int
    number: int
    title: str
    state: str
    labels: List[str]
    assignees: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    html_url: str
    body: Optional[str] = None


class PullRequestRaw(BaseModel):
    id: int
    number: int
    title: str
    state: str
    draft: bool
    created_at: datetime
    updated_at: Optional[datetime]
    merged_at: Optional[datetime]
    html_url: str
    body: Optional[str] = None


class RawScanResult(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    repository: str
    code_todos: List[CodeTodo] = Field(default_factory=list)
    issues: List[IssueRaw] = Field(default_factory=list)
    pull_requests: List[PullRequestRaw] = Field(default_factory=list)
    mode: ScanMode = Field(default=ScanMode.DEEP)
    readme: Optional[str] = Field(default=None, description="Repository README for project context")
