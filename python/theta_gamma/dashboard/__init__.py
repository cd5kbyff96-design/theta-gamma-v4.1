"""
Dashboard — FastAPI web dashboard for Theta-Gamma.

Provides a web UI for:
- Pipeline status monitoring
- Metrics visualization
- Gate progression tracking
- Decision log viewing
- Weekly reports
"""

from theta_gamma.dashboard.app import create_app, app
from theta_gamma.dashboard.routes import (
    router as api_router,
    status_router,
    metrics_router,
    gates_router,
    decisions_router,
    reports_router,
)

__all__ = [
    "create_app",
    "app",
    "api_router",
    "status_router",
    "metrics_router",
    "gates_router",
    "decisions_router",
    "reports_router",
]
