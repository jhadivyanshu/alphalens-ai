import yfinance as yf
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.models.models import Company, Price, Financial
from datetime import datetime

# Some NSE symbols differ on yfinance
SYMBOL_MAP = {
    "KPIT": "KPITTECH",
}

def get_yf_symbol(symbol: str) -> str:
    mapped = SYMBOL_MAP.get(symbol, symbol)
    return f"{mapped}.NS"


def fetch_and_store_prices(symbol: str, db):
    ticker = yf.Ticker(get_yf_symbol(symbol))
    hist = ticker.history(period="2y")

    if hist.empty:
        print(f"No price data for {symbol}")
        return

    for date, row in hist.iterrows():
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            continue

        existing = db.query(Price).filter(
            Price.company_id == company.id,
            Price.date == date.date()
        ).first()

        if not existing:
            price = Price(
                company_id=company.id,
                date=date.date(),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
                volume=int(row["Volume"])
            )
            db.add(price)

    db.commit()
    print(f"Prices stored for {symbol}")


def fetch_and_store_financials(symbol: str, db):
    ticker = yf.Ticker(get_yf_symbol(symbol))
    info = ticker.info

    company = db.query(Company).filter(Company.symbol == symbol).first()
    if not company:
        return

    market_cap = info.get("marketCap")
    if market_cap:
        company.market_cap = market_cap
        db.commit()

    try:
        quarterly = ticker.quarterly_financials
        quarterly_balance = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow

        for col in quarterly.columns[:8]:
            period = col.strftime("Q%m%Y") if hasattr(col, 'strftime') else str(col)

            revenue = quarterly.loc["Total Revenue", col] if "Total Revenue" in quarterly.index else None
            pat = quarterly.loc["Net Income", col] if "Net Income" in quarterly.index else None
            ebitda = quarterly.loc["EBITDA", col] if "EBITDA" in quarterly.index else None

            pat_margin = None
            if revenue and pat and float(revenue) > 0:
                pat_margin = round((float(pat) / float(revenue)) * 100, 2)

            ebitda_margin = None
            if revenue and ebitda and float(revenue) > 0:
                ebitda_margin = round((float(ebitda) / float(revenue)) * 100, 2)

            debt = None
            if not quarterly_balance.empty and "Total Debt" in quarterly_balance.index:
                if col in quarterly_balance.columns:
                    debt = quarterly_balance.loc["Total Debt", col]

            cash = None
            if not quarterly_balance.empty and "Cash And Cash Equivalents" in quarterly_balance.index:
                if col in quarterly_balance.columns:
                    cash = quarterly_balance.loc["Cash And Cash Equivalents", col]

            operating_cf = None
            if not quarterly_cashflow.empty and "Operating Cash Flow" in quarterly_cashflow.index:
                if col in quarterly_cashflow.columns:
                    operating_cf = quarterly_cashflow.loc["Operating Cash Flow", col]

            existing = db.query(Financial).filter(
                Financial.company_id == company.id,
                Financial.period == period,
                Financial.period_type == "quarterly"
            ).first()

            if not existing:
                financial = Financial(
                    company_id=company.id,
                    period=period,
                    period_type="quarterly",
                    revenue=float(revenue) / 10000000 if revenue else None,
                    pat=float(pat) / 10000000 if pat else None,
                    ebitda=float(ebitda) / 10000000 if ebitda else None,
                    pat_margin=pat_margin,
                    ebitda_margin=ebitda_margin,
                    debt=float(debt) / 10000000 if debt else None,
                    cash=float(cash) / 10000000 if cash else None,
                    operating_cf=float(operating_cf) / 10000000 if operating_cf else None,
                )
                db.add(financial)

        db.commit()
        print(f"Financials stored for {symbol}")

    except Exception as e:
        print(f"Error fetching financials for {symbol}: {e}")
        db.rollback()


def ingest_company(symbol: str):
    db = SessionLocal()
    try:
        print(f"Ingesting {symbol}...")
        fetch_and_store_prices(symbol, db)
        fetch_and_store_financials(symbol, db)
    finally:
        db.close()


if __name__ == "__main__":
    symbols = ["KPIT", "TCS", "INFY", "PERSISTENT", "HCLTECH", "RELIANCE", "HDFC", "ICICIBANK"]
    for symbol in symbols:
        ingest_company(symbol)
    print("Ingestion complete")