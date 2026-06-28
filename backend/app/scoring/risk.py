from sqlalchemy.orm import Session
from app.models.models import Company, Financial, Price
from sqlalchemy import desc
from app.scoring.financial import ScoreResult


def calculate(company_id: int, db: Session) -> ScoreResult:
    reasons = []
    warnings = []

    company = db.query(Company).filter(Company.id == company_id).first()

    # Fetch latest financials
    latest = db.query(Financial).filter(
        Financial.company_id == company_id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).first()

    # Fetch latest price
    latest_price = db.query(Price).filter(
        Price.company_id == company_id
    ).order_by(desc(Price.date)).first()

    if not latest:
        return ScoreResult(score=50, reasons=["No data available"], warnings=[])

    # --- Valuation Risk (40 pts) ---
    valuation_score = 20
    if company.market_cap and latest.pat:
        annual_pat = float(latest.pat) * 4 * 10000000
        if annual_pat > 0:
            pe = company.market_cap / annual_pat
            if pe < 15:
                valuation_score = 40
                reasons.append(f"Attractive valuation at {round(pe, 1)}x PE")
            elif pe < 25:
                valuation_score = 35
                reasons.append(f"Reasonable valuation at {round(pe, 1)}x PE")
            elif pe < 40:
                valuation_score = 25
            elif pe < 60:
                valuation_score = 15
                warnings.append(f"Rich valuation at {round(pe, 1)}x PE")
            else:
                valuation_score = 5
                warnings.append(f"Very expensive at {round(pe, 1)}x PE")
        else:
            valuation_score = 10
            warnings.append("Company is loss making")

    # --- Debt Risk (40 pts) ---
    debt_score = 20
    if latest.debt is not None and latest.revenue:
        debt = float(latest.debt)
        revenue = float(latest.revenue) * 4
        if revenue > 0:
            de_ratio = debt / revenue
            if de_ratio < 0.1:
                debt_score = 40
                reasons.append("Virtually debt free - low financial risk")
            elif de_ratio < 0.3:
                debt_score = 35
                reasons.append(f"Low debt levels")
            elif de_ratio < 0.6:
                debt_score = 25
            elif de_ratio < 1.0:
                debt_score = 15
                warnings.append("Moderate debt levels")
            else:
                debt_score = 5
                warnings.append("High debt - elevated financial risk")

    # --- Other Risk (20 pts) ---
    other_score = 20

    raw_score = valuation_score + debt_score + other_score
    final_score = min(100, raw_score)

    return ScoreResult(
        score=round(final_score, 1),
        reasons=reasons,
        warnings=warnings
    )