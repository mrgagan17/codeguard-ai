import io
import csv
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.finding import Finding
from app.models.tool_run import ToolRun
from app.core.security import redact_text

class ReportService:
    @staticmethod
    def generate_json_report(scan: Scan, findings: List[Finding], tool_runs: List[ToolRun]) -> str:
        report_data = {
            "application": "CodeGuard AI",
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "scan_id": scan.id,
            "target_name": scan.target_name,
            "trigger_type": scan.trigger_type,
            "status": scan.status,
            "duration_ms": scan.duration_ms,
            "summary": {
                "total_files": scan.total_files,
                "total_lines": scan.total_lines,
                "total_findings": scan.total_findings,
                "critical": scan.critical_count,
                "high": scan.high_count,
                "medium": scan.medium_count,
                "low": scan.low_count,
                "informational": scan.info_count
            },
            "analyzers": [
                {
                    "tool": tr.tool_name,
                    "version": tr.version,
                    "status": tr.status,
                    "duration_ms": tr.duration_ms,
                    "findings_count": tr.findings_count
                }
                for tr in tool_runs
            ],
            "findings": [
                {
                    "id": f.id,
                    "rule_id": f.rule_id,
                    "title": f.title,
                    "category": f.category,
                    "severity": f.severity,
                    "confidence": f.confidence,
                    "file_path": f.file_path,
                    "start_line": f.start_line,
                    "end_line": f.end_line,
                    "snippet": redact_text(f.snippet or ""),
                    "tool": f.tool,
                    "status": f.status,
                    "why_it_matters": f.why_it_matters,
                    "remediation": f.recommended_remediation,
                    "references": f.references
                }
                for f in findings
            ]
        }
        return json.dumps(report_data, indent=2)

    @staticmethod
    def generate_csv_report(scan: Scan, findings: List[Finding]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Finding ID", "Severity", "Category", "Rule ID", "Title",
            "File Path", "Start Line", "End Line", "Tool", "Status",
            "Remediation", "Snippet"
        ])
        for f in findings:
            writer.writerow([
                f.id,
                f.severity,
                f.category,
                f.rule_id,
                f.title,
                f.file_path,
                f.start_line,
                f.end_line,
                f.tool,
                f.status,
                f.recommended_remediation or "",
                redact_text(f.snippet or "").replace("\n", " ")
            ])
        return output.getvalue()

    @staticmethod
    def generate_markdown_report(scan: Scan, findings: List[Finding], tool_runs: List[ToolRun]) -> str:
        md = []
        md.append(f"# CodeGuard AI Security & Quality Report")
        md.append(f"**Target:** `{scan.target_name}` | **Scan ID:** `{scan.id}` | **Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        md.append("## Executive Summary")
        md.append(f"- **Scan Status:** {scan.status.upper()}")
        md.append(f"- **Files Analyzed:** {scan.total_files} ({scan.total_lines} lines of code)")
        md.append(f"- **Total Findings:** {scan.total_findings}")
        md.append(f"- **Critical:** {scan.critical_count} | **High:** {scan.high_count} | **Medium:** {scan.medium_count} | **Low:** {scan.low_count} | **Info:** {scan.info_count}")
        md.append(f"- **Execution Time:** {scan.duration_ms} ms\n")

        md.append("## Active Analyzers")
        md.append("| Analyzer | Version | Status | Duration | Findings |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for tr in tool_runs:
            md.append(f"| {tr.tool_name.capitalize()} | {tr.version or 'N/A'} | {tr.status} | {tr.duration_ms} ms | {tr.findings_count} |")
        md.append("")

        md.append("## Detailed Findings")
        if not findings:
            md.append("No security vulnerabilities or quality violations detected. Code passed all analyzer checks.\n")
        else:
            for idx, f in enumerate(findings, start=1):
                md.append(f"### {idx}. [{f.severity}] {f.title}")
                md.append(f"- **File:** `{f.file_path}:{f.start_line}`")
                md.append(f"- **Rule ID:** `{f.rule_id}` (Analyzer: `{f.tool}`)")
                md.append(f"- **Category:** `{f.category}` | **Status:** `{f.status}`")
                if f.snippet:
                    md.append(f"```python\n{redact_text(f.snippet)}\n```")
                if f.why_it_matters:
                    md.append(f"> **Why it matters:** {f.why_it_matters}\n")
                if f.recommended_remediation:
                    md.append(f"**Remediation:** {f.recommended_remediation}\n")
                if f.references:
                    md.append(f"**References:** {f.references}\n")
                md.append("---\n")

        md.append("> *Report generated automatically by CodeGuard AI. Sensitive values have been safely redacted.*")
        return "\n".join(md)

    @staticmethod
    def generate_html_report(scan: Scan, findings: List[Finding], tool_runs: List[ToolRun], auto_print: bool = False) -> str:
        findings_html = []
        for f in findings:
            sev_class = {
                "Critical": "#dc2626",
                "High": "#ea580c",
                "Medium": "#d97706",
                "Low": "#2563eb",
                "Informational": "#475569"
            }.get(f.severity, "#475569")

            snippet_block = ""
            if f.snippet:
                snippet_block = f"""
                <div style="margin-top: 10px; background: #0f172a; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; color: #e2e8f0; overflow-x: auto;">
                    <pre style="margin: 0;">{redact_text(f.snippet)}</pre>
                </div>
                """

            findings_html.append(f"""
            <div style="border: 1px solid #334155; background: #1e293b; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="background: {sev_class}; color: #ffffff; padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: bold; text-transform: uppercase;">
                        {f.severity}
                    </span>
                    <span style="color: #94a3b8; font-size: 12px; font-family: monospace;">Rule: {f.rule_id} | Tool: {f.tool}</span>
                </div>
                <h3 style="color: #f8fafc; margin: 0 0 6px 0; font-size: 16px;">{f.title}</h3>
                <div style="color: #60a5fa; font-size: 13px; font-family: monospace; margin-bottom: 8px;">
                    File: {f.file_path} (Lines {f.start_line}-{f.end_line})
                </div>
                <p style="color: #cbd5e1; font-size: 14px; margin: 0 0 8px 0;">{f.description}</p>
                {snippet_block}
                <div style="margin-top: 10px; padding: 10px; background: #0f172a; border-left: 3px solid #3b82f6; border-radius: 4px;">
                    <strong style="color: #93c5fd; font-size: 12px;">Recommended Remediation:</strong>
                    <p style="color: #e2e8f0; font-size: 13px; margin: 4px 0 0 0;">{f.recommended_remediation or 'Review flagged code.'}</p>
                </div>
            </div>
            """)

        footer_text = "Generated by CodeGuard AI &bull; Confidential &bull; All secrets redacted automatically"
        auto_script = (
            "window.addEventListener('load', function() { setTimeout(function() { window.print(); }, 350); });"
            if auto_print
            else "if (window.location.search.includes('print=true') || window.location.search.includes('pdf=true')) { window.addEventListener('load', function() { setTimeout(function() { window.print(); }, 350); }); }"
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CodeGuard AI Report — {scan.target_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 24px; margin-bottom: 30px; }}
        .badge {{ background: #3b82f6; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 12px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 30px; }}
        .stat-card {{ background: #1e293b; border: 1px solid #334155; padding: 16px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #f8fafc; }}
        .stat-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }}
        .print-btn {{
            background: #2563eb;
            color: #ffffff;
            border: none;
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }}
        .print-btn:hover {{ background: #1d4ed8; }}

        @media print {{
            body {{ background-color: #ffffff !important; color: #0f172a !important; padding: 10px !important; }}
            .no-print {{ display: none !important; }}
            .header {{ border-bottom: 2px solid #0f172a !important; }}
            .header h1 {{ color: #0f172a !important; }}
            .stat-card {{ background: #f8fafc !important; border: 1px solid #cbd5e1 !important; }}
            .stat-value {{ color: #0f172a !important; }}
            div[style*="background: #1e293b"] {{ background: #ffffff !important; border: 1px solid #cbd5e1 !important; page-break-inside: avoid; }}
            h3[style*="color: #f8fafc"] {{ color: #0f172a !important; }}
            div[style*="background: #0f172a"] {{ background: #f1f5f9 !important; color: #0f172a !important; border: 1px solid #e2e8f0; }}
            pre {{ color: #0f172a !important; }}
            footer {{ border-top: 1px solid #cbd5e1 !important; color: #64748b !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin: 0; font-size: 24px; color: #60a5fa;">CodeGuard AI — Scan Report</h1>
                <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 14px;">Target: {scan.target_name} &bull; Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <button onclick="window.print()" class="print-btn no-print">
                    🖨️ Save as PDF
                </button>
                <span class="badge">STATUS: {scan.status.upper()}</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-value">{scan.total_files}</div><div class="stat-label">Files</div></div>
            <div class="stat-card"><div class="stat-value">{scan.total_findings}</div><div class="stat-label">Total Findings</div></div>
            <div class="stat-card"><div class="stat-value" style="color: #ef4444;">{scan.critical_count}</div><div class="stat-label">Critical</div></div>
            <div class="stat-card"><div class="stat-value" style="color: #f97316;">{scan.high_count}</div><div class="stat-label">High</div></div>
            <div class="stat-card"><div class="stat-value" style="color: #eab308;">{scan.medium_count}</div><div class="stat-label">Medium</div></div>
            <div class="stat-card"><div class="stat-value" style="color: #3b82f6;">{scan.low_count}</div><div class="stat-label">Low</div></div>
            <div class="stat-card"><div class="stat-value">{scan.duration_ms} ms</div><div class="stat-label">Duration</div></div>
        </div>

        <h2 style="font-size: 18px; color: #e2e8f0; margin-bottom: 16px;">Detected Findings ({len(findings)})</h2>
        {''.join(findings_html) if findings_html else '<p style="color: #10b981;">No issues found. Code is clean!</p>'}
        
        <footer style="margin-top: 40px; border-top: 1px solid #1e293b; padding-top: 20px; text-align: center; color: #64748b; font-size: 12px;">
            {footer_text}
        </footer>
    </div>
    <script class="no-print">
        {auto_script}
    </script>
</body>
</html>"""
        return html
