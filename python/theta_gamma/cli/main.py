"""
CLI — Command-line interface for Theta-Gamma pipeline.

Provides commands for:
- run: Execute training runs
- eval: Run evaluation suites
- weekly-loop: Execute weekly control loop
- status: Show pipeline status
- init: Initialize database and config
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click

from theta_gamma import __version__
from theta_gamma.orchestration.pipeline import ThetaGammaPipeline, PipelineConfig
from theta_gamma.persistence.database import init_database, get_database
from theta_gamma.persistence.metrics_store import MetricsStore
from theta_gamma.persistence.checkpoints import CheckpointStore
from theta_gamma.persistence.decision_log import DecisionLog
from theta_gamma.evaluation.harness import EvalHarness, EvalMode


@click.group()
@click.version_option(version=__version__, prog_name="theta-gamma")
@click.option(
    "--db",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to SQLite database",
)
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to config YAML file",
)
@click.pass_context
def cli(ctx: click.Context, db: Path | None, config: Path | None) -> None:
    """
    Theta-Gamma v4.1 — Autonomous ML Training Pipeline

    A production-grade autonomous machine learning pipeline with
    gated milestone progression and budget guardrails.
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db
    ctx.obj["config_path"] = config


@cli.command()
@click.option(
    "--checkpoint",
    type=str,
    default=None,
    help="Checkpoint ID to evaluate",
)
@click.option(
    "--mode",
    type=click.Choice(["full", "quick", "perf", "safety"]),
    default="full",
    help="Evaluation mode",
)
@click.pass_context
def run(ctx: click.Context, checkpoint: str | None, mode: str) -> None:
    """
    Run a training run with evaluation.

    Executes a training run and evaluates the checkpoint against
    milestone gates.
    """
    db_path = ctx.obj.get("db_path")
    config_path = ctx.obj.get("config_path")

    # Initialize database
    db = init_database(db_path or "theta_gamma.db")

    # Create pipeline
    config = PipelineConfig()
    if config_path:
        # Would load from YAML in production
        click.echo(f"Loading config from {config_path}")

    pipeline = ThetaGammaPipeline(config)

    async def _run() -> None:
        # Initialize pipeline
        click.echo("Initializing pipeline...")
        await pipeline.initialize()

        # Run training/evaluation
        checkpoint_id = checkpoint or f"ckpt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        click.echo(f"Running evaluation for checkpoint: {checkpoint_id}")

        eval_mode = {
            "full": EvalMode.FULL,
            "quick": EvalMode.QUICK,
            "perf": EvalMode.PERF_ONLY,
            "safety": EvalMode.SAFETY_ONLY,
        }.get(mode, EvalMode.FULL)

        result = await pipeline.run_training_run(checkpoint_id, eval_mode)

        # Display results
        click.echo("\n=== Results ===")
        click.echo(f"Checkpoint: {checkpoint_id}")
        click.echo(f"Current Gate: {pipeline.get_current_gate()}")

        metrics = result.get("metrics", {})
        for metric_id, value in list(metrics.items())[:10]:
            click.echo(f"  {metric_id}: {value}")

        gate_result = result.get("gate_result", {})
        click.echo(f"\nGate Status: {gate_result.get('status', 'unknown')}")
        click.echo(f"Message: {gate_result.get('message', '')}")

    asyncio.run(_run())


@cli.command()
@click.option(
    "--checkpoint",
    type=str,
    required=True,
    help="Checkpoint ID to evaluate",
)
@click.option(
    "--suite",
    type=click.Choice(["cross-modal", "per-modality", "latency", "safety", "all"]),
    default="all",
    help="Evaluation suite to run",
)
@click.pass_context
def eval(ctx: click.Context, checkpoint: str, suite: str) -> None:
    """
    Run evaluation suites on a checkpoint.

    Executes specific evaluation suites and outputs metrics.
    """
    db_path = ctx.obj.get("db_path")
    db = init_database(db_path or "theta_gamma.db")

    harness = EvalHarness()
    metrics_store = MetricsStore(db)

    eval_mode_map = {
        "cross-modal": EvalMode.QUICK,
        "per-modality": EvalMode.QUICK,
        "latency": EvalMode.PERF_ONLY,
        "safety": EvalMode.SAFETY_ONLY,
        "all": EvalMode.FULL,
    }

    async def _eval() -> None:
        click.echo(f"Running evaluation on checkpoint: {checkpoint}")
        click.echo(f"Suite: {suite}")

        results = await harness.run_eval(
            mode=eval_mode_map[suite],
            checkpoint_id=checkpoint,
        )

        # Store metrics
        for result in results:
            for metric_id, value in result.metrics.items():
                metrics_store.record(metric_id, value, checkpoint_id=checkpoint)

        # Display results
        click.echo("\n=== Evaluation Results ===")
        for result in results:
            click.echo(f"\n{result.suite_type.value}:")
            for metric_id, value in result.metrics.items():
                click.echo(f"  {metric_id}: {value}")

    asyncio.run(_eval())


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force execution even if not Monday",
)
@click.pass_context
def weekly_loop(ctx: click.Context, force: bool) -> None:
    """
    Execute the weekly control loop.

    Runs all 7 steps of the weekly loop:
    1. Collect metrics
    2. Evaluate gates
    3. Prioritize backlog
    4. Decide go/no-go
    5. Plan next 7 days
    6. Generate report
    7. Begin execution
    """
    db_path = ctx.obj.get("db_path")
    db = init_database(db_path or "theta_gamma.db")

    # Check if Monday (unless forced)
    today = datetime.now()
    if today.weekday() != 0 and not force:
        click.echo("Weekly loop should run on Monday. Use --force to override.")
        return

    async def _loop() -> None:
        click.echo("=== Weekly Control Loop ===")
        click.echo(f"Date: {today.strftime('%Y-%m-%d')}")
        click.echo(f"Week: {today.year}-W{today.isocalendar()[1]:02d}")

        # Create and initialize pipeline
        pipeline = ThetaGammaPipeline()
        await pipeline.initialize()

        # Run weekly loop
        click.echo("\nExecuting weekly loop...")
        report = await pipeline.run_weekly_loop()

        # Display results
        click.echo(f"\n=== Go/No-Go Decision: {report.go_no_go_decision.value} ===")

        if report.watch_items:
            click.echo("\nWatch Items:")
            for item in report.watch_items:
                click.echo(f"  - {item}")

        if report.blockers:
            click.echo("\nBlockers:")
            for blocker in report.blockers:
                click.echo(f"  - {blocker}")

        click.echo("\nTop Packets for Next Week:")
        for i, packet in enumerate(report.top_packets[:5], 1):
            click.echo(f"  {i}. {packet.get('packet_id', 'unknown')} (score: {packet.get('score', 0)})")

        click.echo(f"\nNext 7 Days Plan:")
        plan = report.next_7_days_plan
        click.echo(f"  Estimated Cost: ${plan.get('estimated_cost_usd', 0):.2f}")
        click.echo(f"  Packets: {len(plan.get('packets', []))}")

        # Store report in database
        # In production, would use WeeklyReportStore

    asyncio.run(_loop())


@cli.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.pass_context
def status(ctx: click.Context, output_json: bool) -> None:
    """
    Show pipeline status.

    Displays current gate, budget status, incidents, and packet progress.
    """
    db_path = ctx.obj.get("db_path")
    db = init_database(db_path or "theta_gamma.db")

    # Get stores
    metrics_store = MetricsStore(db)
    checkpoint_store = CheckpointStore(db)
    decision_log = DecisionLog(db)

    # Create pipeline (without full initialization for speed)
    pipeline = ThetaGammaPipeline()

    status_data = {
        "version": __version__,
        "timestamp": datetime.now().isoformat(),
        "database": str(db_path or "theta_gamma.db"),
        "current_gate": pipeline.get_current_gate(),
        "state": pipeline._state.value,
        "metrics": {},
        "checkpoints": {
            "total": checkpoint_store.count(),
            "latest": [],
        },
        "decisions": {
            "total": decision_log.count(),
        },
    }

    # Get latest metrics for primary gate metrics
    primary_metrics = ["M-CM-001", "M-CM-002", "M-LAT-002", "M-SAF-001"]
    for metric_id in primary_metrics:
        value = metrics_store.get_latest(metric_id)
        if value is not None:
            status_data["metrics"][metric_id] = value

    # Get latest checkpoints
    latest = checkpoint_store.get_latest(5)
    status_data["checkpoints"]["latest"] = [
        {
            "checkpoint_id": ck.checkpoint_id,
            "gate_id": ck.gate_id,
            "created_at": ck.created_at.isoformat(),
        }
        for ck in latest
    ]

    if output_json:
        click.echo(json.dumps(status_data, indent=2))
    else:
        click.echo("=== Theta-Gamma Pipeline Status ===")
        click.echo(f"Version: {status_data['version']}")
        click.echo(f"Timestamp: {status_data['timestamp']}")
        click.echo(f"Database: {status_data['database']}")
        click.echo(f"\nCurrent Gate: {status_data['current_gate']}")
        click.echo(f"State: {status_data['state']}")

        if status_data["metrics"]:
            click.echo("\nLatest Metrics:")
            for metric_id, value in status_data["metrics"].items():
                click.echo(f"  {metric_id}: {value}")

        click.echo(f"\nCheckpoints: {status_data['checkpoints']['total']} total")
        for ck in status_data["checkpoints"]["latest"]:
            click.echo(f"  - {ck['checkpoint_id']} ({ck['gate_id']}) - {ck['created_at']}")

        click.echo(f"\nDecisions Logged: {status_data['decisions']['total']}")


@cli.command()
@click.option(
    "--db",
    "db_path",
    type=click.Path(path_type=Path),
    default="theta_gamma.db",
    help="Database path",
)
@click.option(
    "--artifacts",
    type=click.Path(path_type=Path),
    default="artifacts",
    help="Artifacts directory",
)
def init(db_path: Path, artifacts: Path) -> None:
    """
    Initialize database and configuration.

    Creates the SQLite database with schema and generates
    default configuration files.
    """
    click.echo("=== Initializing Theta-Gamma ===")

    # Initialize database
    click.echo(f"\nCreating database: {db_path}")
    db = init_database(db_path)
    click.echo("  ✓ Database schema created")

    # Create artifacts directory
    if not artifacts.exists():
        click.echo(f"\nCreating artifacts directory: {artifacts}")
        artifacts.mkdir(parents=True, exist_ok=True)
        click.echo("  ✓ Directory created")

    # Create results directory
    results = Path("results")
    if not results.exists():
        click.echo(f"\nCreating results directory: {results}")
        results.mkdir(parents=True, exist_ok=True)
        click.echo("  ✓ Directory created")

    # Create default config
    config_path = Path("theta_gamma_config.yaml")
    if not config_path.exists():
        click.echo(f"\nCreating default config: {config_path}")
        from theta_gamma.orchestration.config import ConfigLoader
        ConfigLoader.create_default_config(config_path)
        click.echo("  ✓ Config created")

    click.echo("\n=== Initialization Complete ===")
    click.echo("\nNext steps:")
    click.echo("  1. Review and edit theta_gamma_config.yaml")
    click.echo("  2. Place planning artifacts in artifacts/ directory")
    click.echo("  3. Run 'theta-gamma status' to verify setup")
    click.echo("  4. Run 'theta-gamma weekly-loop' to start autonomous operation")


@cli.command()
@click.option(
    "--host",
    type=str,
    default="0.0.0.0",
    help="Host to bind to",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port to bind to",
)
def dashboard(host: str, port: int) -> None:
    """
    Start the web dashboard server.

    Provides a web UI for monitoring pipeline status,
    metrics, gates, and decisions.
    """
    try:
        import uvicorn
        from theta_gamma.dashboard.app import app
    except ImportError:
        click.echo("Dashboard requires fastapi and uvicorn.")
        click.echo("Install with: pip install theta-gamma[dashboard]")
        return

    click.echo("=== Starting Theta-Gamma Dashboard ===")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"URL: http://localhost:{port}")
    click.echo("")
    click.echo("Press Ctrl+C to stop")

    uvicorn.run(app, host=host, port=port, log_level="info")


def main() -> None:
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
