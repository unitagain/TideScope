"""Entry point for running TideScope scans."""

from __future__ import annotations

from pathlib import Path

from .code import scan_code_todos
from .config_loader import load_scan_config
from .github import fetch_github_data, GitHubFetcher
from .models import RawScanResult, ScanConfig, ScanMode


def run_scan(config_path: Path | str, mode_override: ScanMode | None = None) -> RawScanResult:
    """Run code + GitHub scanning using a configuration file."""

    scan_config: ScanConfig = load_scan_config(config_path)
    if mode_override:
        scan_config.mode = mode_override

    code_todos = []
    issues = []
    pull_requests = []
    readme = None

    if scan_config.mode == ScanMode.DEEP:
        code_todos = scan_code_todos(scan_config)

    if scan_config.github:
        issues, pull_requests = fetch_github_data(scan_config.github)
        
        # Fetch README for project context
        fetcher = GitHubFetcher(scan_config.github)
        readme = fetcher.fetch_readme()

    repository_name = (
        f"{scan_config.github.owner}/{scan_config.github.repo}"
        if scan_config.github
        else str(scan_config.repository_path)
    )

    return RawScanResult(
        repository=repository_name,
        code_todos=code_todos,
        issues=issues,
        pull_requests=pull_requests,
        mode=scan_config.mode,
        readme=readme,
    )
