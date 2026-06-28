from sqlalchemy.orm import Session
from app.models.models import Company
from app.scoring.financial import ScoreResult

SECTOR_SCORES = {
    "IT": {
        "Auto Tech": 90,
        "IT Services": 72,
        "default": 70
    },
    "Pharma": {
        "Specialty Pharma": 85,
        "Generic Pharma": 68,
        "default": 70
    },
    "Banking": {
        "Private Bank": 75,
        "PSU Bank": 55,
        "NBFC": 72,
        "default": 60
    },
    "FMCG": {
        "default": 70
    },
    "Auto": {
        "default": 72
    },
    "Finance": {
        "NBFC": 72,
        "default": 65
    },
    "Infrastructure": {
        "Ports": 75,
        "default": 70
    },
    "Oil & Gas": {
        "default": 55
    },
    "Metals": {
        "default": 55
    },
    "default": 60
}


def calculate(company_id: int, db: Session) -> ScoreResult:
    reasons = []
    warnings = []

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return ScoreResult(score=60, reasons=[], warnings=[])

    sector = company.sector or "default"
    industry = company.industry or "default"

    sector_data = SECTOR_SCORES.get(sector, SECTOR_SCORES["default"])

    if isinstance(sector_data, dict):
        score = sector_data.get(industry, sector_data.get("default", 60))
    else:
        score = sector_data

    if score >= 80:
        reasons.append(f"Strong sector tailwind in {sector} - {industry}")
    elif score >= 70:
        reasons.append(f"Positive sector outlook for {sector}")
    elif score < 60:
        warnings.append(f"Weak sector outlook for {sector}")

    return ScoreResult(
        score=float(score),
        reasons=reasons,
        warnings=warnings
    )