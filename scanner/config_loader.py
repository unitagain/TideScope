"""Utilities for loading scanner configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .models import ScanConfig


def load_scan_config(config_path: Path | str) -> ScanConfig:
    """Load a ScanConfig object from a YAML file."""

    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw_data: Dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    if "repository_path" in raw_data:
        repo_path = Path(raw_data["repository_path"])
        if not repo_path.is_absolute():
            raw_data["repository_path"] = (path.parent / repo_path).resolve()
    else:
        raw_data["repository_path"] = path.parent

    return ScanConfig(**raw_data)
