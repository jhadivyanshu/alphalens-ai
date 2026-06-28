import sys
sys.path.insert(0, '.')
from app.database.connection import SessionLocal
from app.services.score_service import calculate_alpha_score
from app.models.models import Company

db = SessionLocal()
company = db.query(Company).filter(Company.symbol == 'TCS').first()
result = calculate_alpha_score(company.id, db)
print('Overall:', result['overall'])
for engine, data in result['engines'].items():
    print(f"{engine}: {data['score']}")
db.close()