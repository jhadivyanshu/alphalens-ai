from sqlalchemy.orm import Session
from app.models.models import Company, Score, ScoreHistory
from app.scoring import financial, technical, risk, sector, management
from datetime import datetime


def calculate_alpha_score(company_id: int, db: Session) -> dict:

    # Run all 5 engines
    financial_result = financial.calculate(company_id, db)
    technical_result = technical.calculate(company_id, db)
    risk_result = risk.calculate(company_id, db)
    sector_result = sector.calculate(company_id, db)
    management_result = management.calculate(company_id, db)

    # Weighted average
    overall = round(
        (financial_result.score * 0.35) +
        (management_result.score * 0.25) +
        (technical_result.score * 0.15) +
        (sector_result.score * 0.15) +
        (risk_result.score * 0.10),
        1
    )

    # Save to DB
    existing = db.query(Score).filter(Score.company_id == company_id).first()

    if existing:
        # Save to history before updating
        history = ScoreHistory(
            company_id=company_id,
            financial=existing.financial,
            technical=existing.technical,
            management=existing.management,
            sector=existing.sector,
            risk=existing.risk,
            overall=existing.overall,
            delta=round(overall - float(existing.overall), 1),
            change_reasons=detect_changes(existing, financial_result, technical_result),
            calculated_at=datetime.utcnow()
        )
        db.add(history)

        existing.financial = financial_result.score
        existing.technical = technical_result.score
        existing.management = management_result.score
        existing.sector = sector_result.score
        existing.risk = risk_result.score
        existing.overall = overall
        existing.reasons = {
            "financial": financial_result.reasons,
            "technical": technical_result.reasons,
            "management": management_result.reasons,
            "sector": sector_result.reasons,
            "risk": risk_result.reasons
        }
        existing.warnings = {
            "financial": financial_result.warnings,
            "technical": technical_result.warnings,
            "management": management_result.warnings,
            "sector": sector_result.warnings,
            "risk": risk_result.warnings
        }
        existing.calculated_at = datetime.utcnow()
    else:
        score = Score(
            company_id=company_id,
            financial=financial_result.score,
            technical=technical_result.score,
            management=management_result.score,
            sector=sector_result.score,
            risk=risk_result.score,
            overall=overall,
            reasons={
                "financial": financial_result.reasons,
                "technical": technical_result.reasons,
                "management": management_result.reasons,
                "sector": sector_result.reasons,
                "risk": risk_result.reasons
            },
            warnings={
                "financial": financial_result.warnings,
                "technical": technical_result.warnings,
                "management": management_result.warnings,
                "sector": sector_result.warnings,
                "risk": risk_result.warnings
            },
            calculated_at=datetime.utcnow()
        )
        db.add(score)

    db.commit()

    return {
        "overall": overall,
        "engines": {
            "financial": {
                "score": financial_result.score,
                "reasons": financial_result.reasons,
                "warnings": financial_result.warnings
            },
            "technical": {
                "score": technical_result.score,
                "reasons": technical_result.reasons,
                "warnings": technical_result.warnings
            },
            "management": {
                "score": management_result.score,
                "reasons": management_result.reasons,
                "warnings": management_result.warnings
            },
            "sector": {
                "score": sector_result.score,
                "reasons": sector_result.reasons,
                "warnings": sector_result.warnings
            },
            "risk": {
                "score": risk_result.score,
                "reasons": risk_result.reasons,
                "warnings": risk_result.warnings
            }
        }
    }


def detect_changes(existing, financial_result, technical_result) -> list:
    changes = []

    if abs(financial_result.score - float(existing.financial)) > 3:
        direction = "improved" if financial_result.score > float(existing.financial) else "declined"
        changes.append(f"Financial score {direction}")

    if abs(technical_result.score - float(existing.technical)) > 3:
        direction = "improved" if technical_result.score > float(existing.technical) else "declined"
        changes.append(f"Technical score {direction}")

    return changes if changes else ["Routine recalculation"]