"""
FastAPI application and routes for Theta-Gamma dashboard.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


def create_app(db_path: Path | None = None) -> FastAPI:
    """
    Create FastAPI application.

    Args:
        db_path: Optional database path

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Theta-Gamma Dashboard",
        description="Autonomous ML Training Pipeline Dashboard",
        version="4.1.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(status_router, prefix="/api/status", tags=["Status"])
    app.include_router(metrics_router, prefix="/api/metrics", tags=["Metrics"])
    app.include_router(gates_router, prefix="/api/gates", tags=["Gates"])
    app.include_router(decisions_router, prefix="/api/decisions", tags=["Decisions"])
    app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])

    # Dashboard UI route
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_ui() -> str:
        """Serve dashboard UI."""
        return get_dashboard_html()

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    return app


# Routers
class StatusResponse(BaseModel):
    """Status response model."""

    state: str
    current_gate: str
    monthly_spend: float
    daily_spend: float
    incidents_active: int
    packets_completed: int
    packets_pending: int
    timestamp: str


from fastapi import APIRouter

status_router = APIRouter()
metrics_router = APIRouter()
gates_router = APIRouter()
decisions_router = APIRouter()
reports_router = APIRouter()

# In-memory store for demo (would use database in production)
_status_data = {
    "state": "running",
    "current_gate": "G1",
    "monthly_spend": 125.50,
    "daily_spend": 15.25,
    "incidents_active": 0,
    "packets_completed": 12,
    "packets_pending": 5,
}

_metrics_data = [
    {"metric_id": "M-CM-001", "values": [42.0, 45.0, 48.0, 52.0, 55.0], "timestamps": []},
    {"metric_id": "M-LAT-002", "values": [120.0, 110.0, 105.0, 98.0, 95.0], "timestamps": []},
]

_gates_data = {
    "G1": {"status": "passed", "threshold": 40.0, "current": 55.0},
    "G2": {"status": "in_progress", "threshold": 60.0, "current": 55.0},
    "G3": {"status": "not_started", "threshold": 70.0, "current": 0.0},
    "G4": {"status": "not_started", "threshold": 100.0, "current": 0.0},
}

_decisions_data = [
    {
        "decision_id": "DEC-001",
        "decision_class": "DC-001",
        "tier": "T0",
        "choice_made": "default",
        "created_at": datetime.now().isoformat(),
    },
]

_reports_data = []


@status_router.get("", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Get pipeline status."""
    return StatusResponse(
        **_status_data,
        timestamp=datetime.now().isoformat(),
    )


@metrics_router.get("")
async def get_metrics(
    metric_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    """Get metrics."""
    if metric_id:
        return [m for m in _metrics_data if m["metric_id"] == metric_id]
    return _metrics_data[:limit]


@metrics_router.post("")
async def record_metric(metric_id: str, value: float, checkpoint_id: str = "") -> dict[str, str]:
    """Record a metric value."""
    # Find or create metric entry
    for m in _metrics_data:
        if m["metric_id"] == metric_id:
            m["values"].append(value)
            m["values"] = m["values"][-limit:]  # Keep last N
            return {"status": "recorded", "metric_id": metric_id}

    _metrics_data.append({
        "metric_id": metric_id,
        "values": [value],
        "timestamps": [datetime.now().isoformat()],
    })
    return {"status": "recorded", "metric_id": metric_id}


@gates_router.get("")
async def get_gates() -> dict[str, dict[str, Any]]:
    """Get gate status."""
    return _gates_data


@gates_router.get("/{gate_id}")
async def get_gate(gate_id: str) -> dict[str, Any]:
    """Get specific gate status."""
    if gate_id not in _gates_data:
        raise HTTPException(status_code=404, detail=f"Gate {gate_id} not found")
    return _gates_data[gate_id]


@decisions_router.get("")
async def get_decisions(
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict[str, Any]]:
    """Get decision log."""
    return _decisions_data[-limit:]


@decisions_router.post("")
async def log_decision(
    decision_class: str,
    tier: str,
    choice_made: str,
    rationale: str = "",
) -> dict[str, str]:
    """Log a decision."""
    decision_id = f"DEC-{len(_decisions_data) + 1:03d}"
    _decisions_data.append({
        "decision_id": decision_id,
        "decision_class": decision_class,
        "tier": tier,
        "choice_made": choice_made,
        "rationale": rationale,
        "created_at": datetime.now().isoformat(),
    })
    return {"status": "logged", "decision_id": decision_id}


@reports_router.get("")
async def get_reports(limit: int = Query(default=10, ge=1, le=50)) -> list[dict[str, Any]]:
    """Get weekly reports."""
    return _reports_data[-limit:]


@reports_router.post("")
async def create_report(
    week: str,
    go_no_go_decision: str,
    metrics_summary: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Create a weekly report."""
    report = {
        "week": week,
        "go_no_go_decision": go_no_go_decision,
        "metrics_summary": metrics_summary or {},
        "generated_at": datetime.now().isoformat(),
    }
    _reports_data.append(report)
    return {"status": "created", "week": week}


def get_dashboard_html() -> str:
    """Generate dashboard HTML."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Theta-Gamma Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #334155;
        }
        .header h1 { font-size: 24px; color: #38bdf8; }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            background: #22c55e;
            color: white;
            font-weight: 600;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
        }
        .card h2 {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .card .value {
            font-size: 32px;
            font-weight: 700;
            color: #38bdf8;
        }
        .gate-status {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .gate {
            flex: 1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            background: #334155;
        }
        .gate.passed { background: #22c55e; }
        .gate.in_progress { background: #3b82f6; }
        .gate.not_started { background: #64748b; }
        .gate-label { font-size: 12px; opacity: 0.8; }
        .gate-value { font-size: 20px; font-weight: 700; margin-top: 5px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th { color: #94a3b8; font-size: 12px; text-transform: uppercase; }
        .tier-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .tier-T0 { background: #22c55e; }
        .tier-T1 { background: #3b82f6; }
        .tier-T2 { background: #f59e0b; }
        .tier-T3 { background: #ef4444; }
        .tier-T4 { background: #7f1d1d; }
        .refresh-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .refresh-btn:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Theta-Gamma v4.1 Dashboard</h1>
        <div>
            <span class="status-badge" id="status-badge">Running</span>
            <button class="refresh-btn" onclick="refreshData()" style="margin-left: 10px;">↻ Refresh</button>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Current Gate</h2>
            <div class="value" id="current-gate">G1</div>
        </div>
        <div class="card">
            <h2>Monthly Spend</h2>
            <div class="value" id="monthly-spend">$125.50</div>
        </div>
        <div class="card">
            <h2>Daily Spend</h2>
            <div class="value" id="daily-spend">$15.25</div>
        </div>
        <div class="card">
            <h2>Packets Completed</h2>
            <div class="value" id="packets-completed">12</div>
        </div>
    </div>

    <div class="card" style="margin-bottom: 30px;">
        <h2>Gate Progression</h2>
        <div class="gate-status">
            <div class="gate passed" id="gate-g1">
                <div class="gate-label">G1 Baseline</div>
                <div class="gate-value">55% ≥ 40%</div>
            </div>
            <div class="gate in_progress" id="gate-g2">
                <div class="gate-label">G2 Mid</div>
                <div class="gate-value">55% ≥ 60%</div>
            </div>
            <div class="gate not_started" id="gate-g3">
                <div class="gate-label">G3 Pilot</div>
                <div class="gate-value">0% ≥ 70%</div>
            </div>
            <div class="gate not_started" id="gate-g4">
                <div class="gate-label">G4 Latency</div>
                <div class="gate-value">0ms ≤ 100ms</div>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Cross-Modal Accuracy (M-CM-001)</h2>
            <canvas id="accuracy-chart"></canvas>
        </div>
        <div class="card">
            <h2>Recent Decisions</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Class</th>
                        <th>Tier</th>
                        <th>Choice</th>
                    </tr>
                </thead>
                <tbody id="decisions-table">
                    <tr>
                        <td>DEC-001</td>
                        <td>DC-001</td>
                        <td><span class="tier-badge tier-T0">T0</span></td>
                        <td>default</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Initialize accuracy chart
        const ctx = document.getElementById('accuracy-chart').getContext('2d');
        const accuracyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5'],
                datasets: [{
                    label: 'Cross-Modal Accuracy (%)',
                    data: [42, 45, 48, 52, 55],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });

        // Fetch and update data
        async function refreshData() {
            try {
                const status = await fetch('/api/status').then(r => r.json());
                document.getElementById('current-gate').textContent = status.current_gate;
                document.getElementById('monthly-spend').textContent = '$' + status.monthly_spend.toFixed(2);
                document.getElementById('daily-spend').textContent = '$' + status.daily_spend.toFixed(2);
                document.getElementById('packets-completed').textContent = status.packets_completed;
                document.getElementById('status-badge').textContent = status.state;
            } catch (e) {
                console.error('Failed to fetch status:', e);
            }
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
"""


# Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
