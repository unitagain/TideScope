"""Utilities to scan source files for TODO-style annotations."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Sequence

from ..models import CodeTodo, ScanConfig, TODO_PATTERNS

COMMENT_PATTERN = re.compile(r"(?P<tag>TODO|FIXME|HACK|NOTE|@tech-debt)(?::|\b)(?P<content>.*)")


def _should_scan_file(path: Path, allowed_exts: Sequence[str]) -> bool:
    if not path.is_file():
        return False
    if not allowed_exts:
        return True
    return path.suffix.lower() in {ext.lower() for ext in allowed_exts}


def _iter_source_files(root: Path, allowed_exts: Sequence[str]) -> Iterable[Path]:
    for file_path in root.rglob("*"):
        if _should_scan_file(file_path, allowed_exts):
            yield file_path


def scan_code_todos(config: ScanConfig) -> List[CodeTodo]:
    """Scan repository files for TODO-like comments."""

    repo_root = config.repository_path
    todos: List[CodeTodo] = []

    for file_path in _iter_source_files(repo_root, config.include_extensions):
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for idx, line in enumerate(lines, start=1):
            match = COMMENT_PATTERN.search(line)
            if not match:
                continue

            tag = match.group("tag")
            if tag not in TODO_PATTERNS:
                continue

            content = match.group("content").strip()
            context = line.strip()
            todos.append(
                CodeTodo(
                    file_path=str(file_path.relative_to(repo_root)),
                    line_number=idx,
                    tag=tag,
                    content=content,
                    context=context,
                )
            )

    return todos
