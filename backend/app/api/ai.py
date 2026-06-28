from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company, Financial, Score
from app.services.ai_service import generate_company_summary
from app.services.score_service import calculate_alpha_score
from sqlalchemy import desc

router = APIRouter()

@router.get("/company/{symbol}/summary")
def get_ai_summary(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get latest financials
    latest = db.query(Financial).filter(
        Financial.company_id == company.id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).first()

    # Get or calculate score
    score_data = calculate_alpha_score(company.id, db)

    financials = {}
    if latest:
        financials = {
            "revenue": float(latest.revenue) if latest.revenue else None,
            "pat_margin": float(latest.pat_margin) if latest.pat_margin else None,
            "ebitda_margin": float(latest.ebitda_margin) if latest.ebitda_margin else None,
        }

    summary = generate_company_summary(
        company_name=company.name,
        sector=company.sector or "Unknown",
        financials=financials,
        score={
            "overall": score_data["overall"],
            "financial": score_data["engines"]["financial"]["score"],
            "technical": score_data["engines"]["technical"]["score"],
            "risk": score_data["engines"]["risk"]["score"]
        }
    )

    return {
        "success": True,
        "data": summary
    }