"""OpenAI GPT helper for TideScope analyzer."""

from __future__ import annotations

import json
import logging
import os
from typing import List, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from .models import DebtCategory, DifficultyLevel

logger = logging.getLogger(__name__)


class IssueLLMInsights(BaseModel):
    category: Optional[DebtCategory] = None
    skills: List[str] = Field(default_factory=list)
    difficulty: Optional[DifficultyLevel] = None
    is_blocker: bool = False
    recommendation: Optional[str] = None  # Brief suggestion for required capabilities


class LLMClient:
    """Lightweight wrapper around OpenAI-compatible APIs (OpenAI, DeepSeek)."""

    def __init__(
        self, 
        model: str = "gpt-4o-mini", 
        enabled: bool = False,
        provider: str = "openai",
        project_context: Optional[str] = None
    ) -> None:
        self.provider = provider.lower()
        self.model = model
        self.project_context = project_context or ""
        
        # Get API key and base URL based on provider
        if self.provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = "https://api.deepseek.com"
            # Use deepseek-chat if no model specified or default is used
            if model in ["gpt-4o-mini", "gpt-4o"]:
                self.model = "deepseek-chat"
        else:  # openai
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = None  # Use default OpenAI base URL
        
        self.enabled = enabled and bool(api_key)
        self._client: Optional[OpenAI] = None
        
        if self.enabled:
            if base_url:
                self._client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                self._client = OpenAI(api_key=api_key)
        
        logger.info(f"LLM Client initialized: provider={self.provider}, model={self.model}, enabled={self.enabled}")
        if not api_key:
            env_var = "DEEPSEEK_API_KEY" if self.provider == "deepseek" else "OPENAI_API_KEY"
            logger.warning(f"{env_var} not found in environment")
        if not enabled:
            logger.info("LLM analysis is disabled (use --use-llm to enable)")

    def analyze_issue(self, title: str, body: Optional[str]) -> Optional[IssueLLMInsights]:
        """Use GPT to infer metadata for an issue."""

        if not self.enabled or not self._client:
            logger.debug(f"LLM analysis skipped for: {title[:50]}...")
            return None
        
        logger.info(f"Analyzing issue with LLM: {title[:50]}...")

        schema = {
            "name": "issue_insight",
            "schema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                    },
                    "difficulty": {"type": "string"},
                    "is_blocker": {"type": "boolean", "default": False},
                    "recommendation": {"type": "string"},
                },
                "required": ["category", "skills", "difficulty", "is_blocker", "recommendation"],
                "additionalProperties": False,
            },
        }

        context_section = f"\n\nProject Context:\n{self.project_context}\n" if self.project_context else ""
        
        prompt = (
            f"You are analyzing a GitHub issue for a software project.{context_section}\n"
            f"Title: {title}\n"
            f"Body: {body or 'N/A'}\n\n"
            f"Provide analysis:\n"
            f"1. category: Choose from security, performance, maintainability, documentation, testing, ci, or feature\n"
            f"2. skills: List 2-4 specific technical skills/technologies needed (e.g., React, Python, PostgreSQL, Docker, REST API)\n"
            f"3. difficulty: entry (good-first-issue), intermediate (requires some experience), or advanced (complex/architectural)\n"
            f"4. is_blocker: true ONLY if prevents project from running or causes data loss\n"
            f"5. recommendation: A brief 1-sentence summary of what capabilities/knowledge are needed to complete this task\n\n"
            f"Example recommendation: 'Requires frontend experience with React hooks and state management'\n"
            f"Be specific and actionable in the recommendation."
        )

        try:
            # DeepSeek doesn't support json_schema, use simple json mode
            if self.provider == "deepseek":
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an engineering assistant that classifies GitHub issues. Always respond with valid JSON.",
                        },
                        {"role": "user", "content": prompt + "\n\nRespond with valid JSON only."},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
            else:  # OpenAI with structured outputs
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an engineering assistant that classifies GitHub issues.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_schema", "json_schema": schema},
                    temperature=0.1,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM request failed: %s", exc)
            return None

        try:
            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty LLM response")
                return None
            payload = json.loads(content)
        except (IndexError, KeyError, json.JSONDecodeError) as exc:
            logger.warning("Failed to parse LLM response: %s", exc)
            return None

        insights = IssueLLMInsights()

        category_value = (payload.get("category") or "").lower()
        for category in DebtCategory:
            if category.value == category_value:
                insights.category = category
                break

        skills_value = payload.get("skills") or []
        insights.skills = [skill.strip() for skill in skills_value if isinstance(skill, str)]

        difficulty_value = (payload.get("difficulty") or "").lower()
        for difficulty in DifficultyLevel:
            if difficulty.value == difficulty_value:
                insights.difficulty = difficulty
                break

        insights.is_blocker = bool(payload.get("is_blocker", False))
        
        recommendation_value = payload.get("recommendation")
        if recommendation_value and isinstance(recommendation_value, str):
            insights.recommendation = recommendation_value.strip()

        return insights
    
    def analyze_pr(self, title: str, body: Optional[str]) -> Optional[IssueLLMInsights]:
        """Use GPT to infer metadata for a pull request."""
        
        if not self.enabled or not self._client:
            logger.debug(f"LLM analysis skipped for PR: {title[:50]}...")
            return None
        
        logger.info(f"Analyzing PR with LLM: {title[:50]}...")

        schema = {
            "name": "pr_insight",
            "schema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                    },
                    "difficulty": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": ["category", "skills", "difficulty", "recommendation"],
                "additionalProperties": False,
            },
        }

        context_section = f"\n\nProject Context:\n{self.project_context}\n" if self.project_context else ""
        
        prompt = (
            f"You are reviewing a Pull Request for a software project.{context_section}\n"
            f"Title: {title}\n"
            f"Description: {body or 'N/A'}\n\n"
            f"Provide analysis:\n"
            f"1. category: Choose from security, performance, maintainability, documentation, testing, ci, or feature\n"
            f"2. skills: List 2-4 specific technical skills needed to review/understand this PR (e.g., React, Python, Git, Testing)\n"
            f"3. difficulty: entry, intermediate, or advanced (based on code review complexity)\n"
            f"4. recommendation: A brief 1-sentence summary of what expertise is needed to review/approve this PR\n\n"
            f"Example recommendation: 'Requires understanding of state management patterns and code review best practices'\n"
            f"Be specific and actionable."
        )

        try:
            if self.provider == "deepseek":
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code review assistant that analyzes Pull Requests. Always respond with valid JSON.",
                        },
                        {"role": "user", "content": prompt + "\n\nRespond with valid JSON only."},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
            else:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code review assistant that analyzes Pull Requests.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_schema", "json_schema": schema},
                    temperature=0.1,
                )
        except Exception as exc:
            logger.warning("LLM request failed for PR: %s", exc)
            return None

        try:
            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty LLM response for PR")
                return None
            payload = json.loads(content)
        except (IndexError, KeyError, json.JSONDecodeError) as exc:
            logger.warning("Failed to parse LLM response for PR: %s", exc)
            return None

        insights = IssueLLMInsights()

        category_value = (payload.get("category") or "").lower()
        for category in DebtCategory:
            if category.value == category_value:
                insights.category = category
                break

        skills_value = payload.get("skills") or []
        insights.skills = [skill.strip() for skill in skills_value if isinstance(skill, str)]

        difficulty_value = (payload.get("difficulty") or "").lower()
        for difficulty in DifficultyLevel:
            if difficulty.value == difficulty_value:
                insights.difficulty = difficulty
                break
        
        recommendation_value = payload.get("recommendation")
        if recommendation_value and isinstance(recommendation_value, str):
            insights.recommendation = recommendation_value.strip()

        return insights
