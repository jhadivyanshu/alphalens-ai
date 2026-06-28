from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company, News
from sqlalchemy import desc

router = APIRouter()

@router.get("/company/{symbol}/news")
def get_news(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    news = db.query(News).filter(
        News.company_id == company.id
    ).order_by(desc(News.published_at)).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "title": n.title,
                "source": n.source,
                "url": n.url,
                "published_at": str(n.published_at),
                "summary": n.summary,
                "sentiment": n.sentiment
            }
            for n in news
        ]
    }