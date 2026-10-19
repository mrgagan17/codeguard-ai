from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_api():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "CodeGuard AI" in data["service"]

def test_list_analyzers_api():
    response = client.get("/api/analyzers")
    assert response.status_code == 200
    data = response.json()
    assert "analyzers" in data
    assert len(data["analyzers"]) >= 5
    analyzer_names = [a["name"] for a in data["analyzers"]]
    assert "ast" in analyzer_names
    assert "secret" in analyzer_names
    assert "ruff" in analyzer_names
    assert "bandit" in analyzer_names
    assert "radon" in analyzer_names

def test_create_snippet_scan_api():
    payload = {
        "name": "Test Snippet Scan",
        "language": "python",
        "code": "def bad_fn(x=[]):\n    eval('2 + 2')\n    return x\n"
    }
    response = client.post("/api/scans", json=payload)
    assert response.status_code == 200
    scan_data = response.json()
    assert scan_data["status"] == "completed"
    assert scan_data["total_findings"] >= 2
    assert scan_data["critical_count"] >= 1  # from eval

    scan_id = scan_data["id"]
    # Check scan detail
    detail_res = client.get(f"/api/scans/{scan_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["findings"]) >= 2
    assert len(detail["tool_runs"]) >= 1

def test_empty_code_rejected():
    response = client.post("/api/scans", json={"code": ""})
    assert response.status_code == 400
