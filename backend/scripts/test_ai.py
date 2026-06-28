import sys
sys.path.insert(0, '.')
from app.services.ai_service import generate_company_summary

result = generate_company_summary(
    company_name="Tata Consultancy Services",
    sector="IT Services",
    financials={
        "revenue": 67087,
        "pat_margin": 15.89,
        "ebitda_margin": 23.84
    },
    score={
        "overall": 57,
        "financial": 57,
        "technical": 25,
        "risk": 75
    }
)

for key, value in result.items():
    print(f"\n{key.upper()}:")
    print(value)