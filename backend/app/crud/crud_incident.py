from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.incident import Incident
from app.models.recovery import RecoveryAttempt


def get_incident(db: Session, incident_id: str) -> Optional[Incident]:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_incidents(
    db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 50
) -> List[Incident]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(desc(Incident.created_at)).offset(skip).limit(limit).all()


def get_unresolved_incidents(db: Session) -> List[Incident]:
    return (
        db.query(Incident)
        .filter(Incident.status.in_(["UNRESOLVED", "INVESTIGATING", "RECOVERING"]))
        .order_by(desc(Incident.created_at))
        .all()
    )


def get_incident_recovery_attempts(db: Session, incident_id: str) -> List[RecoveryAttempt]:
    return (
        db.query(RecoveryAttempt)
        .filter(RecoveryAttempt.incident_id == incident_id)
        .order_by(desc(RecoveryAttempt.created_at))
        .all()
    )
