from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_findings_filtering_and_status_update():
    # 1. Run a scan to generate findings
    scan_res = client.post("/api/scans", json={
        "name": "Findings Filter Test",
        "code": "import os\ndef test(x=[]):\n    os.system('id')\n"
    })
    assert scan_res.status_code == 200
    scan_id = scan_res.json()["id"]

    # 2. Query findings
    findings_res = client.get(f"/api/scans/{scan_id}/findings")
    assert findings_res.status_code == 200
    findings_data = findings_res.json()
    assert findings_data["total"] >= 1
    findings = findings_data["findings"]
    first_id = findings[0]["id"]

    # 3. Filter by severity
    crit_res = client.get(f"/api/scans/{scan_id}/findings?severity=Critical")
    assert crit_res.status_code == 200

    # 4. Update status to accepted with justification
    patch_res = client.patch(f"/api/findings/{first_id}/status", json={
        "status": "accepted",
        "justification": "Approved risk for testing sandbox"
    })
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "accepted"
    assert updated["status_justification"] == "Approved risk for testing sandbox"

    # 5. Explain finding
    explain_res = client.post(f"/api/findings/{first_id}/explain")
    assert explain_res.status_code == 200
    exp = explain_res.json()
    assert exp["explanation"]
    assert exp["why_it_matters"]

    # 6. Suggest fix
    fix_res = client.post(f"/api/findings/{first_id}/suggest-fix")
    assert fix_res.status_code == 200
    fix = fix_res.json()
    assert fix["patch_diff"]
    assert fix["suggested_code"]
