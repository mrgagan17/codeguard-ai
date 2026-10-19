from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.tool_run import ToolRun
from app.services.report_service import ReportService

router = APIRouter(tags=["Reports"])

@router.get("/scans/{scan_id}/report")
def export_scan_report(
    scan_id: str,
    format: str = Query("json", pattern="^(json|csv|markdown|html|pdf)$"),
    db: Session = Depends(get_db)
):
    """Export a comprehensive scan report in JSON, CSV, Markdown, HTML, or PDF format with safe secret redaction."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    findings = db.query(Finding).filter(Finding.scan_id == scan_id).order_by(Finding.start_line.asc()).all()
    tool_runs = db.query(ToolRun).filter(ToolRun.scan_id == scan_id).all()

    if format == "json":
        content = ReportService.generate_json_report(scan, findings, tool_runs)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="codeguard_report_{scan_id[:8]}.json"'}
        )
    elif format == "csv":
        content = ReportService.generate_csv_report(scan, findings)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="codeguard_report_{scan_id[:8]}.csv"'}
        )
    elif format == "markdown":
        content = ReportService.generate_markdown_report(scan, findings, tool_runs)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="codeguard_report_{scan_id[:8]}.md"'}
        )
    elif format in ("html", "pdf"):
        is_pdf = format == "pdf"
        content = ReportService.generate_html_report(scan, findings, tool_runs, auto_print=is_pdf)
        disposition = "inline" if is_pdf else "attachment"
        return Response(
            content=content,
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f'{disposition}; filename="codeguard_report_{scan_id[:8]}.html"'}
        )
