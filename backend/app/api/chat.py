from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.connection import get_db
from app.models.models import Company, Financial, Price, Score
from app.services.ai_service import generate_chat_response
from app.services.score_service import calculate_alpha_score
from sqlalchemy import desc

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    symbol: str

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == request.symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Build context
    latest_price = db.query(Price).filter(
        Price.company_id == company.id
    ).order_by(desc(Price.date)).first()

    latest_financial = db.query(Financial).filter(
        Financial.company_id == company.id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).first()

    score_data = calculate_alpha_score(company.id, db)

    context = {
        "sector": company.sector,
        "price": float(latest_price.close) if latest_price else "N/A",
        "overall_score": score_data["overall"],
        "financial_score": score_data["engines"]["financial"]["score"],
        "technical_score": score_data["engines"]["technical"]["score"],
        "revenue": float(latest_financial.revenue) if latest_financial and latest_financial.revenue else "N/A",
        "pat_margin": float(latest_financial.pat_margin) if latest_financial and latest_financial.pat_margin else "N/A",
    }

    answer = generate_chat_response(
        question=request.question,
        symbol=request.symbol,
        company_name=company.name,
        context=context
    )

    return {
        "success": True,
        "data": {
            "question": request.question,
            "answer": answer,
            "company": company.name
        }
    }