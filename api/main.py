"""FastAPI server exposing TideScope analysis data."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException

from analyzer import AnalysisReport
from api.routes import badge, badge_v2

app = FastAPI(
    title="TideScope API",
    version="2.0.0",
    description="Technical Debt Analysis and Smart Badge System"
)

# Register badge routes
app.include_router(badge.router)  # v1 badges (legacy)
app.include_router(badge_v2.router)  # v2 badges (new Hero Badge system)

_REPORT_CACHE: Dict[Path, AnalysisReport] = {}


def _load_report(path: Path | str) -> AnalysisReport:
    report_path = Path(path).expanduser().resolve()
    cached = _REPORT_CACHE.get(report_path)
    if cached:
        return cached

    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Report file not found: {report_path}")

    try:
        report = AnalysisReport.model_validate_json(report_path.read_text(encoding="utf-8"))
    except ValueError as exc:  # noqa: PERF203
        raise HTTPException(status_code=400, detail=f"Invalid report file: {exc}") from exc

    _REPORT_CACHE[report_path] = report
    return report


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/debt/list")
def list_debts(
    report_path: str = "tidescope-report.json",
    source_type: str | None = None,
    module: str | None = None,
    difficulty: str | None = None,
) -> list[dict]:
    report = _load_report(report_path)
    debts = report.debts

    if source_type:
        debts = [debt for debt in debts if debt.source_type.value == source_type]
    if module:
        debts = [debt for debt in debts if (debt.module or "").lower() == module.lower()]
    if difficulty:
        debts = [debt for debt in debts if debt.difficulty.value == difficulty]

    return [debt.model_dump() for debt in debts]


@app.get("/api/debt/star-map")
def star_map(report_path: str = "tidescope-report.json") -> dict:
    report = _load_report(report_path)
    return report.star_map.model_dump()


@app.get("/api/debt/aggregates")
def aggregates(report_path: str = "tidescope-report.json") -> dict:
    report = _load_report(report_path)
    return report.aggregates.model_dump()

