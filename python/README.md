# Theta-Gamma v4.1

**Autonomous ML Training Pipeline with Gated Milestone Progression**

[![Tests](https://img.shields.io/badge/tests-131%20passed-green)]()
[![Coverage](https://img.shields.io/badge/coverage-62%25-yellow)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Overview

Theta-Gamma is a production-grade autonomous machine learning training pipeline that implements:

- **Autonomy Contract**: Decision authority tiers (T0-T4) governing autonomous execution
- **Milestone Gates**: G1-G4 gates with statistical confidence requirements
- **Budget Guardrails**: Real-time cost tracking with auto-downgrade cascade
- **Failure Recovery**: State machine for deterministic failure handling
- **Weekly Control Loop**: Automated weekly planning and prioritization
- **Web Dashboard**: Real-time monitoring with FastAPI

## Quick Start

```bash
# Clone the repository
git clone <repository-url> theta-gamma-v4.1
cd theta-gamma-v4.1/python

# Install with all features
pip install -e ".[all]"

# Initialize database and config
theta-gamma init

# Check status
theta-gamma status

# Start web dashboard
theta-gamma dashboard

# Run weekly control loop
theta-gamma weekly-loop --force
```

## Installation

### Basic Installation

```bash
pip install -e .
```

### With Development Tools

```bash
pip install -e ".[dev]"
```

### With All Features

```bash
pip install -e ".[all]"
```

### Optional Dependencies

| Extra | Packages | Purpose |
|-------|----------|---------|
| `dev` | pytest, mypy, ruff | Development and testing |
| `eval` | torch, ray, sklearn | Model evaluation |
| `dashboard` | fastapi, uvicorn, plotly | Web dashboard |
| `distributed` | ray[train], torch | Distributed training |
| `all` | All of the above | Full installation |

## Project Structure

```
theta-gamma-v4.1/
├── python/theta_gamma/       # Main Python package
│   ├── autonomy/             # Decision authority, risk profiles, failure modes
│   ├── evaluation/           # Metrics, gates, eval harness, datasets
│   ├── compute/              # Budget, training tiers, auto-downgrade
│   ├── recovery/             # State machine, incident management
│   ├── compiler/             # Task packet compilation, DAG resolution
│   ├── weekly_loop/          # Weekly control loop, go/no-go decisions
│   ├── decisions/            # Decision packets, multi-channel delivery
│   ├── orchestration/        # Main pipeline orchestrator
│   ├── persistence/          # SQLite storage (metrics, checkpoints, decisions)
│   ├── training/             # PyTorch training loop, FSDP, Ray
│   ├── dashboard/            # FastAPI web UI
│   └── cli/                  # Command-line interface
├── A0-A7/                    # Planning artifacts (specifications)
├── GAP_ANALYSIS_REPORT.md    # Implementation gap analysis
├── .cursor/                  # Cursor IDE configuration
├── .zed/                     # Zed IDE configuration
└── pyproject.toml            # Project configuration
```

## Core Concepts

### Decision Authority Tiers

| Tier | Name | Description |
|------|------|-------------|
| T0 | Full Auto | Proceed without asking |
| T1 | Log & Proceed | Proceed and log rationale |
| T2 | Notify & Proceed | Proceed with async notification |
| T3 | Approval Required | Request human approval |
| T4 | Prohibited | Never execute autonomously |

### Milestone Gates

| Gate | Phase | Primary Metric | Threshold |
|------|-------|---------------|-----------|
| G1 | Baseline | Cross-modal accuracy | ≥ 40% |
| G2 | Mid Training | Cross-modal accuracy | ≥ 60% |
| G3 | Pilot Readiness | Cross-modal accuracy | ≥ 70% |
| G4 | Performance | p95 latency | ≤ 100ms |

### Training Tiers

| Tier | GPUs | Strategy | Daily Cost |
|------|------|----------|------------|
| T1 | 4xA100-80GB | FSDP/DeepSpeed | $35-50 |
| T2 | 2xA100-80GB | ZeRO-2 | $20-35 |
| T3 | 1xA100-80GB | QLoRA | $8-20 |
| T4 | 1xA100-40GB | Eval only | $2-8 |
| T5 | - | Full stop | $0 |

## CLI Commands

```bash
# Initialize database and configuration
theta-gamma init

# Show pipeline status
theta-gamma status

# Run training with evaluation
theta-gamma run --checkpoint ckpt-001 --mode full

# Run evaluation suites
theta-gamma eval --checkpoint ckpt-001 --suite all

# Execute weekly control loop
theta-gamma weekly-loop [--force]

# Start web dashboard
theta-gamma dashboard [--host 0.0.0.0 --port 8000]
```

## API Usage

```python
from theta_gamma import (
    ThetaGammaPipeline,
    AutonomyContract,
    GateEvaluator,
    ComputeBudget,
)

# Initialize pipeline
pipeline = ThetaGammaPipeline()
await pipeline.initialize()

# Run weekly loop
report = await pipeline.run_weekly_loop()
print(f"Decision: {report.go_no_go_decision}")

# Evaluate gate
evaluator = GateEvaluator()
result = evaluator.evaluate_gate("G1", metrics={"M-CM-001": [45.0, 48.0, 52.0]})
if result.all_passed:
    print("Gate G1 passed!")
```

## Testing

```bash
cd python

# Run all tests
pytest

# Run with coverage
pytest --cov=theta_gamma --cov-report=html

# Run specific test file
pytest theta_gamma/tests/test_orchestration.py -v

# Type checking
mypy theta_gamma

# Linting
ruff check theta_gamma
```

## Configuration

Create `theta_gamma_config.yaml`:

```yaml
compute:
  monthly_cap_usd: 500.0
  daily_cap_usd: 50.0

evaluation:
  results_dir: results/eval

weekly_loop:
  loop_day: 0  # Monday
  loop_hour: 9  # 09:00 UTC

decisions:
  deadline_hours: 32  # Tuesday 18:00 UTC
```

## Dashboard

Access the web dashboard at `http://localhost:8000` after running:

```bash
theta-gamma dashboard
```

Features:
- Real-time pipeline status
- Metrics visualization with Chart.js
- Gate progression tracking
- Decision log viewer
- Weekly reports

## Specifications

The A0-A7 directories contain detailed specifications:

| Phase | Directory | Description |
|-------|-----------|-------------|
| A0 | `A0/` | Autonomy contract, decision matrix, operating limits |
| A1 | `A1/` | Metric dictionary, gate definitions, eval harness |
| A2 | `A2/` | Compute budget, training tiers, downgrade rules |
| A3 | `A3/` | Task packet compiler, quality rubrics |
| A4 | `A4/` | Recovery state machine, retry policies |
| A5 | `A5/` | Pilot SOW, validation checklists |
| A6 | `A6/` | Weekly loop runbook, prioritization rules |
| A7 | `A7/` | Decision packets, deadline policies |

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `pytest && mypy && ruff check`
5. Submit a pull request

## Support

- Documentation: See `python/README.md` and A0-A7 specs
- Issues: GitHub Issues
- Discussions: GitHub Discussions
