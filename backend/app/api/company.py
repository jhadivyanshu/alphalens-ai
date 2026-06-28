from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Company, Price, Financial
from sqlalchemy import desc

router = APIRouter()

@router.get("/company/{symbol}")
def get_company(symbol: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Latest price
    latest_price = db.query(Price).filter(
        Price.company_id == company.id
    ).order_by(desc(Price.date)).first()

    # Latest financials
    latest_financial = db.query(Financial).filter(
        Financial.company_id == company.id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).first()

    return {
        "success": True,
        "data": {
            "symbol": company.symbol,
            "name": company.name,
            "sector": company.sector,
            "industry": company.industry,
            "exchange": company.exchange,
            "market_cap": company.market_cap,
            "price": {
                "current": float(latest_price.close) if latest_price else None,
                "high": float(latest_price.high) if latest_price else None,
                "low": float(latest_price.low) if latest_price else None,
                "volume": latest_price.volume if latest_price else None,
                "date": str(latest_price.date) if latest_price else None,
            } if latest_price else None,
            "latest_financials": {
                "period": latest_financial.period if latest_financial else None,
                "revenue": float(latest_financial.revenue) if latest_financial and latest_financial.revenue else None,
                "pat": float(latest_financial.pat) if latest_financial and latest_financial.pat else None,
                "ebitda_margin": float(latest_financial.ebitda_margin) if latest_financial and latest_financial.ebitda_margin else None,
                "pat_margin": float(latest_financial.pat_margin) if latest_financial and latest_financial.pat_margin else None,
            } if latest_financial else None
        }
    }


@router.get("/company/{symbol}/prices")
def get_prices(symbol: str, period: str = "1y", db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from datetime import datetime, timedelta
    period_map = {
        "1m": 30, "3m": 90, "6m": 180,
        "1y": 365, "3y": 1095
    }
    days = period_map.get(period, 365)
    from_date = datetime.now().date() - timedelta(days=days)

    prices = db.query(Price).filter(
        Price.company_id == company.id,
        Price.date >= from_date
    ).order_by(Price.date).all()

    return {
        "success": True,
        "data": [
            {
                "date": str(p.date),
                "open": float(p.open) if p.open else None,
                "high": float(p.high) if p.high else None,
                "low": float(p.low) if p.low else None,
                "close": float(p.close) if p.close else None,
                "volume": p.volume
            }
            for p in prices
        ]
    }


@router.get("/company/{symbol}/financials")
def get_financials(symbol: str, type: str = "quarterly", limit: int = 8, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.symbol == symbol.upper()
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    financials = db.query(Financial).filter(
        Financial.company_id == company.id,
        Financial.period_type == type
    ).order_by(desc(Financial.period)).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "period": f.period,
                "revenue": float(f.revenue) if f.revenue else None,
                "pat": float(f.pat) if f.pat else None,
                "ebitda": float(f.ebitda) if f.ebitda else None,
                "ebitda_margin": float(f.ebitda_margin) if f.ebitda_margin else None,
                "pat_margin": float(f.pat_margin) if f.pat_margin else None,
                "debt": float(f.debt) if f.debt else None,
                "cash": float(f.cash) if f.cash else None,
            }
            for f in financials
        ]
    }