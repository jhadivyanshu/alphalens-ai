import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.models import Company

companies = [
    {"symbol": "KPIT", "name": "KPIT Technologies Ltd", "sector": "IT", "industry": "Auto Tech", "exchange": "NSE"},
    {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "INFY", "name": "Infosys Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "WIPRO", "name": "Wipro Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "HCLTECH", "name": "HCL Technologies Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "PERSISTENT", "name": "Persistent Systems Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "LTIM", "name": "LTIMindtree Ltd", "sector": "IT", "industry": "IT Services", "exchange": "NSE"},
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Oil & Gas", "industry": "Conglomerate", "exchange": "NSE"},
    {"symbol": "HDFC", "name": "HDFC Bank Ltd", "sector": "Banking", "industry": "Private Bank", "exchange": "NSE"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking", "industry": "Private Bank", "exchange": "NSE"},
    {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Banking", "industry": "Private Bank", "exchange": "NSE"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking", "industry": "PSU Bank", "exchange": "NSE"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Auto", "industry": "Automobile", "exchange": "NSE"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Auto", "industry": "Automobile", "exchange": "NSE"},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "Finance", "industry": "NBFC", "exchange": "NSE"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "sector": "Pharma", "industry": "Specialty Pharma", "exchange": "NSE"},
    {"symbol": "DRREDDY", "name": "Dr Reddys Laboratories Ltd", "sector": "Pharma", "industry": "Generic Pharma", "exchange": "NSE"},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG", "industry": "FMCG", "exchange": "NSE"},
    {"symbol": "ITC", "name": "ITC Ltd", "sector": "FMCG", "industry": "FMCG", "exchange": "NSE"},
    {"symbol": "ADANIPORTS", "name": "Adani Ports and SEZ Ltd", "sector": "Infrastructure", "industry": "Ports", "exchange": "NSE"},
]

def seed():
    db = SessionLocal()
    try:
        for c in companies:
            exists = db.query(Company).filter(Company.symbol == c["symbol"]).first()
            if not exists:
                company = Company(**c)
                db.add(company)
        db.commit()
        print(f"Seeded {len(companies)} companies successfully")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()