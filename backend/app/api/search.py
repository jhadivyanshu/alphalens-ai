from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company

router = APIRouter()

@router.get("/search")
def search_companies(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    companies = db.query(Company).filter(
        (Company.symbol.ilike(f"%{q}%")) |
        (Company.name.ilike(f"%{q}%"))
    ).limit(10).all()

    return {
        "success": True,
        "data": [
            {
                "symbol": c.symbol,
                "name": c.name,
                "sector": c.sector,
                "exchange": c.exchange,
                "market_cap": c.market_cap
            }
            for c in companies
        ]
    }