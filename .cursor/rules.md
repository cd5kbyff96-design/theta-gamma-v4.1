# Theta-Gamma v4.1 — Cursor Rules

## Project Overview

Theta-Gamma v4.1 is an autonomous ML training pipeline with gated milestone progression. It implements:

- **Autonomy Contract**: Decision authority tiers (T0-T4) governing autonomous execution
- **Milestone Gates**: G1-G4 gates with statistical confidence requirements
- **Budget Guardrails**: Real-time cost tracking with auto-downgrade cascade
- **Failure Recovery**: State machine for deterministic failure handling
- **Weekly Control Loop**: Automated weekly planning and prioritization

## Key Directories

```
theta-gamma-v4.1/
├── python/theta_gamma/       # Main package
│   ├── autonomy/             # Decision authority, risk profiles
│   ├── evaluation/           # Metrics, gates, eval harness
│   ├── compute/              # Budget, training tiers, downgrade
│   ├── recovery/             # State machine, incidents
│   ├── compiler/             # Task packet compilation
│   ├── weekly_loop/          # Weekly control loop
│   ├── decisions/            # Decision packets, delivery
│   ├── orchestration/        # Main pipeline orchestrator
│   ├── persistence/          # SQLite storage
│   ├── training/             # PyTorch training loop
│   ├── dashboard/            # FastAPI web UI
│   └── cli/                  # Command-line interface
├── A0-A7/                    # Planning artifacts (specs)
└── GAP_ANALYSIS_REPORT.md    # Implementation gap analysis
```

## Coding Conventions

### Python Style
- Use type hints for all function signatures
- Follow PEP 8 with 100-char line length
- Use dataclasses for data containers
- Use Pydantic BaseModel for validated configs
- Docstrings required for all public classes/functions

### Testing
- All new code must have tests in `theta_gamma/tests/`
- Use pytest with async support
- Aim for 80%+ coverage on new code

### Architecture Patterns
- Components are loosely coupled via interfaces
- Use dependency injection for testability
- Async/await for I/O operations
- State machines for complex workflows

## Common Commands

```bash
# Run tests
cd python && pytest

# Run with coverage
cd python && pytest --cov=theta_gamma --cov-report=html

# Type check
cd python && mypy theta_gamma

# Lint
cd python && ruff check theta_gamma

# Start dashboard
theta-gamma dashboard

# Run weekly loop
theta-gamma weekly-loop --force
```

## AI Assistant Guidelines

1. **Always check existing code** before suggesting changes
2. **Reference spec files** in A0-A7/ when implementing features
3. **Maintain backward compatibility** when modifying APIs
4. **Add tests** for all new functionality
5. **Update GAP_ANALYSIS_REPORT.md** when closing implementation gaps
6. **Use unified diffs** for code changes
7. **Prefer composition over inheritance**

## Key Design Decisions

- **Decision Tiers**: T0 (full auto) to T4 (prohibited)
- **Gates**: G1 (40%) → G2 (60%) → G3 (70%) + G4 (latency ≤100ms)
- **Budget**: $500/month cap with auto-downgrade cascade
- **Weekly Loop**: Monday 09:00 UTC, 7-step automated process
- **Decisions**: Top-5 packet delivered weekly, defaults auto-apply
