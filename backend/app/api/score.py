from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company, Score, ScoreHistory
from app.services.score_service import calculate_alpha_score
from sqlalchemy import desc

router = APIRouter()

@router.get("/company/{symbol}/score")
def get_score(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    result = calculate_alpha_score(company.id, db)

    return {
        "success": True,
        "data": result
    }


@router.get("/company/{symbol}/score/history")
def get_score_history(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    history = db.query(ScoreHistory).filter(
        ScoreHistory.company_id == company.id
    ).order_by(desc(ScoreHistory.calculated_at)).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "overall": float(h.overall),
                "delta": float(h.delta) if h.delta else 0,
                "change_reasons": h.change_reasons,
                "calculated_at": str(h.calculated_at)
            }
            for h in history
        ]
    }