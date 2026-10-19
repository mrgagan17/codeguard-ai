from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.scan import Scan
from app.models.finding import Finding

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Calculate aggregated metrics from actual stored scan and finding records."""
    total_scans = db.query(func.count(Scan.id)).scalar() or 0
    total_findings = db.query(func.count(Finding.id)).scalar() or 0

    if total_scans == 0:
        return {
            "has_data": False,
            "total_scans": 0,
            "total_findings": 0,
            "severity_counts": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0},
            "status_counts": {"open": 0, "accepted": 0, "fixed": 0, "false_positive": 0, "resolved": 0},
            "category_distribution": [],
            "recent_scans": [],
            "average_duration_ms": 0,
            "historical_trends": []
        }

    # Severities
    sev_rows = db.query(Finding.severity, func.count(Finding.id)).group_by(Finding.severity).all()
    severity_map = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    for sev, count in sev_rows:
        if sev in severity_map:
            severity_map[sev] = count

    # Statuses (Open vs Resolved)
    status_rows = db.query(Finding.status, func.count(Finding.id)).group_by(Finding.status).all()
    status_map = {"open": 0, "accepted": 0, "fixed": 0, "false_positive": 0, "resolved": 0}
    for st, count in status_rows:
        if st in status_map:
            status_map[st] = count

    # Categories
    cat_rows = db.query(Finding.category, func.count(Finding.id)).group_by(Finding.category).order_by(func.count(Finding.id).desc()).all()
    category_dist = [{"category": cat, "count": count} for cat, count in cat_rows]

    # Average scan duration
    avg_dur = db.query(func.avg(Scan.duration_ms)).scalar() or 0

    # Recent scans (last 5)
    recent_scans_objs = db.query(Scan).order_by(Scan.created_at.desc()).limit(5).all()
    recent_scans = [
        {
            "id": s.id,
            "target_name": s.target_name,
            "trigger_type": s.trigger_type,
            "status": s.status,
            "total_findings": s.total_findings,
            "critical_count": s.critical_count,
            "high_count": s.high_count,
            "duration_ms": s.duration_ms,
            "created_at": s.created_at.isoformat()
        }
        for s in recent_scans_objs
    ]

    # Historical trends (last 10 scans)
    trend_scans = db.query(Scan).order_by(Scan.created_at.asc()).limit(15).all()
    historical_trends = [
        {
            "scan_id": s.id[:8],
            "target": s.target_name[:15],
            "findings": s.total_findings,
            "critical": s.critical_count,
            "high": s.high_count,
            "medium": s.medium_count,
            "low": s.low_count,
            "date": s.created_at.strftime("%m/%d %H:%M")
        }
        for s in trend_scans
    ]

    return {
        "has_data": True,
        "total_scans": total_scans,
        "total_findings": total_findings,
        "severity_counts": severity_map,
        "status_counts": status_map,
        "category_distribution": category_dist,
        "recent_scans": recent_scans,
        "average_duration_ms": int(avg_dur),
        "historical_trends": historical_trends
    }
