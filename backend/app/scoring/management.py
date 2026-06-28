from sqlalchemy.orm import Session
from app.models.models import Company
from app.scoring.financial import ScoreResult


def calculate(company_id: int, db: Session) -> ScoreResult:
    reasons = []
    warnings = []

    # Management scoring is limited without concall data
    # We will enhance this in Milestone 3 when we add concall ingestion
    # For now we use a neutral base score with available data

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return ScoreResult(score=50, reasons=[], warnings=[])

    # Base score — neutral until concall data is available
    score = 60

    reasons.append("Management score will improve after concall data is ingested")

    return ScoreResult(
        score=float(score),
        reasons=reasons,
        warnings=warnings
    )