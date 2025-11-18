"""GitHub REST API helpers for TideScope scanner."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Tuple

import httpx

from ..models import GitHubConfig, IssueRaw, PullRequestRaw

_DATETIME_FORMATS = ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

class GitHubFetcher:
    """Thin wrapper around the GitHub REST API."""

    def __init__(self, config: GitHubConfig, timeout: float = 30.0) -> None:
        self.config = config
        self.timeout = timeout
        self.base_url = config.api_base.rstrip("/")
        token_env = config.token_env
        self.token = os.environ.get(token_env) if token_env else None

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _client(self) -> httpx.Client:
        return httpx.Client(headers=self._headers(), timeout=self.timeout)

    def fetch_issues(self) -> List[IssueRaw]:
        url = f"{self.base_url}/repos/{self.config.owner}/{self.config.repo}/issues"
        collected: List[IssueRaw] = []

        with self._client() as client:
            page = 1
            while True:
                response = client.get(
                    url,
                    params={"state": "all", "per_page": 100, "page": page},
                )
                response.raise_for_status()
                payload = response.json()
                if not payload:
                    break

                for item in payload:
                    if "pull_request" in item:
                        continue
                    collected.append(
                        IssueRaw(
                            id=item["id"],
                            number=item["number"],
                            title=item["title"],
                            state=item["state"],
                            labels=[label["name"] for label in item.get("labels", [])],
                            assignees=[assignee["login"] for assignee in item.get("assignees", [])],
                            created_at=_parse_dt(item["created_at"]),
                            updated_at=_parse_dt(item.get("updated_at")),
                            html_url=item["html_url"],
                            body=item.get("body"),
                        )
                    )

                page += 1

        return collected

    def fetch_pull_requests(self) -> List[PullRequestRaw]:
        url = f"{self.base_url}/repos/{self.config.owner}/{self.config.repo}/pulls"
        collected: List[PullRequestRaw] = []

        with self._client() as client:
            page = 1
            while True:
                response = client.get(
                    url,
                    params={"state": "all", "per_page": 100, "page": page},
                )
                response.raise_for_status()
                payload = response.json()
                if not payload:
                    break

                for item in payload:
                    collected.append(
                        PullRequestRaw(
                            id=item["id"],
                            number=item["number"],
                            title=item["title"],
                            state=item["state"],
                            draft=item.get("draft", False),
                            created_at=_parse_dt(item["created_at"]),
                            updated_at=_parse_dt(item.get("updated_at")),
                            merged_at=_parse_dt(item.get("merged_at")),
                            html_url=item["html_url"],
                            body=item.get("body"),
                        )
                    )

                page += 1

        return collected
    
    def fetch_readme(self) -> str | None:
        """Fetch repository README for project context.
        
        Returns:
            README content as markdown text, or None if not found.
        """
        url = f"{self.base_url}/repos/{self.config.owner}/{self.config.repo}/readme"
        
        with self._client() as client:
            try:
                response = client.get(url, headers={**self._headers(), "Accept": "application/vnd.github.raw"})
                response.raise_for_status()
                readme_content = response.text
                
                # Truncate to first 2000 chars to avoid excessive token usage
                if len(readme_content) > 2000:
                    readme_content = readme_content[:2000] + "\n\n[README truncated for brevity...]"
                
                return readme_content
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # No README found
                    return None
                raise


def fetch_github_data(config: GitHubConfig) -> Tuple[List[IssueRaw], List[PullRequestRaw]]:
    fetcher = GitHubFetcher(config)
    return fetcher.fetch_issues(), fetcher.fetch_pull_requests()
