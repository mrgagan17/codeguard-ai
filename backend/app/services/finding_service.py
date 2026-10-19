from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.finding import Finding
from app.schemas.finding import FindingFilter, FindingStatusUpdate

class FindingService:
    @staticmethod
    def get_findings_for_scan(
        db: Session,
        scan_id: str,
        filters: Optional[FindingFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Finding], int]:
        query = db.query(Finding).filter(Finding.scan_id == scan_id)

        if filters:
            if filters.severity:
                query = query.filter(Finding.severity == filters.severity.value)
            if filters.category:
                query = query.filter(Finding.category == filters.category.value)
            if filters.status:
                query = query.filter(Finding.status == filters.status.value)
            if filters.tool:
                query = query.filter(Finding.tool == filters.tool)
            if filters.file_path:
                query = query.filter(Finding.file_path.ilike(f"%{filters.file_path}%"))
            if filters.query:
                q = f"%{filters.query}%"
                query = query.filter(
                    or_(
                        Finding.title.ilike(q),
                        Finding.description.ilike(q),
                        Finding.rule_id.ilike(q),
                        Finding.file_path.ilike(q)
                    )
                )

        total = query.count()
        findings = query.order_by(Finding.start_line.asc()).offset(skip).limit(limit).all()
        return findings, total

    @staticmethod
    def get_finding_by_id(db: Session, finding_id: str) -> Optional[Finding]:
        return db.query(Finding).filter(Finding.id == finding_id).first()

    @staticmethod
    def update_finding_status(
        db: Session,
        finding_id: str,
        update_data: FindingStatusUpdate
    ) -> Optional[Finding]:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            return None

        finding.status = update_data.status.value
        if update_data.justification:
            finding.status_justification = update_data.justification

        db.commit()
        db.refresh(finding)
        return finding
