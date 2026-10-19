from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_export_all_report_formats():
    # 1. Run a scan with simulated credential
    scan_res = client.post("/api/scans", json={
        "name": "Report Export Test",
        "code": "API_KEY = 'AKIA1234567890ABCDEF'\ndef foo(x=[]): pass\n"
    })
    assert scan_res.status_code == 200
    scan_id = scan_res.json()["id"]

    # 2. JSON format
    json_res = client.get(f"/api/scans/{scan_id}/report?format=json")
    assert json_res.status_code == 200
    assert "application/json" in json_res.headers["content-type"]
    json_text = json_res.text
    assert "AKIA1234567890ABCDEF" not in json_text
    assert "[REDACTED]" in json_text

    # 3. CSV format
    csv_res = client.get(f"/api/scans/{scan_id}/report?format=csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "AKIA1234567890ABCDEF" not in csv_res.text

    # 4. Markdown format
    md_res = client.get(f"/api/scans/{scan_id}/report?format=markdown")
    assert md_res.status_code == 200
    assert "# CodeGuard AI Security & Quality Report" in md_res.text
    assert "AKIA1234567890ABCDEF" not in md_res.text

    # 5. HTML format
    html_res = client.get(f"/api/scans/{scan_id}/report?format=html")
    assert html_res.status_code == 200
    assert "<!DOCTYPE html>" in html_res.text
    assert "CodeGuard AI" in html_res.text
    assert "AKIA1234567890ABCDEF" not in html_res.text
