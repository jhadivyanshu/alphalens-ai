from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company, Financial, ScoreHistory
from app.services.ai_service import generate_qoq_explanation
from sqlalchemy import desc

router = APIRouter()


@router.get("/company/{symbol}/changes")
def get_qoq_changes(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    financials = db.query(Financial).filter(
        Financial.company_id == company.id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).limit(2).all()

    if len(financials) < 2:
        raise HTTPException(status_code=404, detail="Not enough data")

    latest = financials[0]
    previous = financials[1]

    def safe_change(new, old):
        if new and old and float(old) != 0:
            return round(((float(new) - float(old)) / float(old)) * 100, 1)
        return None

    changes = []
    metrics = [
        ("Revenue", latest.revenue, previous.revenue, "Cr"),
        ("PAT", latest.pat, previous.pat, "Cr"),
        ("PAT Margin", latest.pat_margin, previous.pat_margin, "%"),
        ("EBITDA Margin", latest.ebitda_margin, previous.ebitda_margin, "%"),
    ]

    for name, new_val, old_val, unit in metrics:
        if new_val and old_val:
            change = safe_change(new_val, old_val)
            changes.append({
                "metric": name,
                "from": float(old_val),
                "to": float(new_val),
                "change_percent": change,
                "direction": "up" if change and change > 0 else "down",
                "unit": unit
            })

    q1 = {
        "period": previous.period,
        "revenue": float(previous.revenue) if previous.revenue else None,
        "pat_margin": float(previous.pat_margin) if previous.pat_margin else None,
        "ebitda_margin": float(previous.ebitda_margin) if previous.ebitda_margin else None,
    }
    q2 = {
        "period": latest.period,
        "revenue": float(latest.revenue) if latest.revenue else None,
        "pat_margin": float(latest.pat_margin) if latest.pat_margin else None,
        "ebitda_margin": float(latest.ebitda_margin) if latest.ebitda_margin else None,
    }

    ai_explanation = generate_qoq_explanation(company.name, q1, q2)

    return {
        "success": True,
        "data": {
            "from": previous.period,
            "to": latest.period,
            "changes": changes,
            "ai_explanation": ai_explanation
        }
    }


@router.get("/company/{symbol}/score/why")
def why_score_changed(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    history = db.query(ScoreHistory).filter(
        ScoreHistory.company_id == company.id
    ).order_by(desc(ScoreHistory.calculated_at)).limit(2).all()

    if not history:
        return {
            "success": True,
            "data": {
                "message": "No score history yet. Score will be tracked from next recalculation."
            }
        }

    latest = history[0]
    return {
        "success": True,
        "data": {
            "current_score": float(latest.overall),
            "delta": float(latest.delta) if latest.delta else 0,
            "change_reasons": latest.change_reasons,
            "calculated_at": str(latest.calculated_at)
        }
    }