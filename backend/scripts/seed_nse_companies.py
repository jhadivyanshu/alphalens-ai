import sys
import os
sys.path.insert(0, '.')
import requests
import csv
from io import StringIO
from app.database.connection import SessionLocal
from app.models.models import Company

def seed_nse_companies():
    db = SessionLocal()
    
    # NSE equity list CSV
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.text
        reader = csv.DictReader(StringIO(content))
        
        count = 0
        for row in reader:
            symbol = row.get('SYMBOL', '').strip()
            name = row.get('NAME OF COMPANY', '').strip()
            
            if not symbol or not name:
                continue
            
            # Check if already exists
            existing = db.query(Company).filter(
                Company.symbol == symbol
            ).first()
            
            if not existing:
                company = Company(
                    symbol=symbol,
                    name=name,
                    sector="Unknown",
                    industry="Unknown",
                    exchange="NSE"
                )
                db.add(company)
                count += 1
        
        db.commit()
        print(f"Added {count} new companies from NSE")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_nse_companies()