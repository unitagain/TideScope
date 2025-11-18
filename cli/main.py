"""Command-line interface for TideScope."""

from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from analyzer import AnalysisReport, build_analysis_report
from scanner import RawScanResult, ScanMode, run_scan

app = typer.Typer(help="Run TideScope scanners.")
console = Console()

# Configure logging with Rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=False, show_path=False)]
)


def _write_raw_output(result: RawScanResult, output_path: Path) -> Path:
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        result.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )
    return output_path


@app.command()
def scan(
    config: Path = typer.Option(
        Path("config/tidescope.config.yaml"),
        "--config",
        "-c",
        help="Path to the TideScope scan configuration file.",
    ),
    output: Path = typer.Option(
        Path("tidescope-raw.json"),
        "--output",
        "-o",
        help="Path to save the raw scan results JSON.",
    ),
    mode: ScanMode = typer.Option(
        ScanMode.DEEP,
        "--mode",
        "-m",
        case_sensitive=False,
        help="Scan mode: quick (GitHub metadata only) or deep (code + GitHub).",
    ),
) -> None:
    """Scan repository code + GitHub metadata and write raw JSON output."""

    try:
        console.print(f"[cyan]Loading config:[/] {config}")
        result = run_scan(config, mode_override=mode)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Scan failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    final_path = _write_raw_output(result, output)
    console.print(f"[green]Scan completed.[/] Raw data saved to {final_path}")

    summary_table = Table(title="Scan Summary")
    summary_table.add_column("Category", justify="left")
    summary_table.add_column("Count", justify="right")
    summary_table.add_row("Mode", result.mode.value if hasattr(result.mode, "value") else str(result.mode))
    summary_table.add_row("Code TODOs", str(len(result.code_todos)))
    summary_table.add_row("Issues", str(len(result.issues)))
    summary_table.add_row("Pull Requests", str(len(result.pull_requests)))
    console.print(summary_table)


def _write_analysis_report(report: AnalysisReport, output_path: Path) -> Path:
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        report.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )
    return output_path


@app.command()
def analyze(
    raw: Path = typer.Option(
        Path("tidescope-raw.json"),
        "--raw",
        "-r",
        help="Path to the raw scan JSON produced by tidescope scan.",
    ),
    output: Path = typer.Option(
        Path("tidescope-report.json"),
        "--output",
        "-o",
        help="Path to save the analysis report JSON.",
    ),
    use_llm: bool = typer.Option(
        False,
        "--use-llm/--no-llm",
        help="Enable OpenAI GPT assistance when analyzing Issues.",
    ),
    llm_model: str = typer.Option(
        "gpt-4o-mini",
        "--llm-model",
        help="Model name to use when --use-llm is enabled (auto-adjusted for provider).",
    ),
    llm_provider: str = typer.Option(
        "openai",
        "--llm-provider",
        help="LLM provider: 'openai' or 'deepseek' (DeepSeek is faster and cheaper).",
    ),
) -> None:
    """Generate an analysis report and Project Task StarMap from raw data."""

    try:
        console.print(f"[cyan]Loading raw scan:[/] {raw}")
        if use_llm:
            console.print(f"[yellow]Using LLM provider:[/] {llm_provider} (model: {llm_model})")
        report = build_analysis_report(raw, use_llm=use_llm, llm_model=llm_model, llm_provider=llm_provider)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Analysis failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    final_path = _write_analysis_report(report, output)
    console.print(f"[green]Analysis completed.[/] Report saved to {final_path}")

    table = Table(title="Analysis Summary")
    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")
    table.add_row("Total Debts", str(report.aggregates.total_debts))
    table.add_row("Modules", str(len(report.aggregates.by_module)))
    table.add_row("Categories", str(len(report.aggregates.by_category)))
    console.print(table)


def main() -> None:
    """CLI entry point."""

    app()


if __name__ == "__main__":
    main()

