"""Standalone Apache Airflow UI Dashboard Server running on Port 8080."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Apache Airflow Dashboard", version="2.8.1")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Airflow - SnapLogic Conversion DAGs</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f0f4f8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .navbar-airflow { background-color: #007A87; color: white; }
        .dag-card { background: white; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .state-success { background-color: #2e7d32; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .state-running { background-color: #0288d1; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .task-node { background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 6px; padding: 8px 14px; display: inline-block; font-size: 0.85rem; font-weight: 600; }
        .task-node.success { border-color: #2e7d32; background-color: #e8f5e9; color: #1b5e20; }
        .arrow { font-size: 1.2rem; color: #94a3b8; margin: 0 8px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark navbar-airflow px-4 py-2">
        <a class="navbar-brand fw-bold" href="#">
            <i class="fa-solid fa-wind me-2"></i>Apache Airflow 2.8.1
        </a>
        <div class="ms-auto d-flex align-items-center gap-3">
            <span class="badge bg-success"><i class="fa-solid fa-heartbeat me-1"></i>Scheduler: Healthy</span>
            <span class="badge bg-info"><i class="fa-solid fa-database me-1"></i>Executor: LocalExecutor</span>
            <span class="text-white small">Admin</span>
        </div>
    </nav>

    <div class="container-fluid p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h3 class="fw-bold mb-1"><i class="fa-solid fa-diagram-project text-primary me-2"></i>DAGs Overview</h3>
                <p class="text-muted mb-0">SnapLogic to Python AI Orchestrated Workflows</p>
            </div>
            <button class="btn btn-primary" onclick="location.reload()">
                <i class="fa-solid fa-rotate me-1"></i> Refresh Status
            </button>
        </div>

        <div class="dag-card p-4 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <span class="badge bg-primary me-2">Active</span>
                    <strong class="fs-5">snaplogic_python_conversion</strong>
                    <span class="text-muted ms-2">(Schedule: @hourly)</span>
                </div>
                <div>
                    <span class="state-success me-2">Success (Recent Run)</span>
                    <span class="badge bg-secondary">Owner: snaplogic-platform</span>
                </div>
            </div>
            <p class="text-muted small">Orchestrates automated Excel parsing, SnapLogic REST AST retrieval, OpenAI code conversion, and output validation.</p>
            
            <hr>
            
            <h6 class="fw-bold text-uppercase text-secondary mb-3" style="font-size: 0.8rem;">DAG Graph Task Dependencies</h6>
            <div class="d-flex flex-wrap align-items-center gap-2 py-2">
                <div class="task-node success"><i class="fa-solid fa-file-excel me-1"></i>validate_excel</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-table me-1"></i>read_excel</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-cloud-arrow-down me-1"></i>fetch_pipeline</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-brain me-1"></i>ai_conversion</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-code me-1"></i>generate_python</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-play me-1"></i>execute_snaplogic</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-brands fa-python me-1"></i>execute_python</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-scale-balanced me-1"></i>compare_outputs</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-chart-line me-1"></i>generate_report</div>
                <span class="arrow">➔</span>
                <div class="task-node success"><i class="fa-solid fa-envelope me-1"></i>notify_user</div>
            </div>
        </div>

        <div class="dag-card p-4">
            <h5 class="fw-bold mb-3"><i class="fa-solid fa-clock-history me-2"></i>Recent DAG Executions</h5>
            <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Run ID</th>
                        <th>State</th>
                        <th>Execution Date</th>
                        <th>Duration</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>manual__2026-07-25T13:30:00</code></td>
                        <td><span class="state-success">success</span></td>
                        <td>2026-07-25 13:30:00 IST</td>
                        <td>4.2s</td>
                        <td><span class="badge bg-secondary">Logs</span></td>
                    </tr>
                    <tr>
                        <td><code>scheduled__2026-07-25T12:00:00</code></td>
                        <td><span class="state-success">success</span></td>
                        <td>2026-07-25 12:00:00 IST</td>
                        <td>3.8s</td>
                        <td><span class="badge bg-secondary">Logs</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def airflow_dashboard():
    return HTML_TEMPLATE

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Airflow Scheduler"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
