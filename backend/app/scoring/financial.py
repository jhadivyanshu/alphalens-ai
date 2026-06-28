from sqlalchemy.orm import Session
from app.models.models import Company, Financial
from sqlalchemy import desc
from dataclasses import dataclass
from typing import List

@dataclass
class ScoreResult:
    score: float
    reasons: List[str]
    warnings: List[str]


def calculate(company_id: int, db: Session) -> ScoreResult:
    reasons = []
    warnings = []

    # Fetch last 8 quarters
    financials = db.query(Financial).filter(
        Financial.company_id == company_id,
        Financial.period_type == "quarterly"
    ).order_by(desc(Financial.period)).limit(8).all()

    if not financials:
        return ScoreResult(score=50, reasons=["No financial data available"], warnings=[])

    latest = financials[0]

    # --- Revenue Growth Score (25 pts) ---
    revenue_score = 10
    if len(financials) >= 4:
        revenues = [f.revenue for f in financials if f.revenue]
        if len(revenues) >= 4:
            recent = float(revenues[0])
            older = float(revenues[3])
            if older > 0:
                growth = ((recent - older) / older) * 100
                if growth > 25:
                    revenue_score = 25
                    reasons.append(f"Strong revenue growth of {round(growth, 1)}% over last 4 quarters")
                elif growth > 15:
                    revenue_score = 20
                    reasons.append(f"Healthy revenue growth of {round(growth, 1)}% over last 4 quarters")
                elif growth > 10:
                    revenue_score = 15
                    reasons.append(f"Moderate revenue growth of {round(growth, 1)}%")
                elif growth > 0:
                    revenue_score = 10
                else:
                    revenue_score = 5
                    warnings.append(f"Revenue declined {round(abs(growth), 1)}% over last 4 quarters")

    # --- Profitability Score (25 pts) ---
    profit_score = 10
    if latest.pat_margin:
        margin = float(latest.pat_margin)
        if margin > 20:
            profit_score = 25
            reasons.append(f"Excellent PAT margin of {margin}%")
        elif margin > 15:
            profit_score = 20
            reasons.append(f"Strong PAT margin of {margin}%")
        elif margin > 10:
            profit_score = 15
            reasons.append(f"Healthy PAT margin of {margin}%")
        elif margin > 5:
            profit_score = 10
        else:
            profit_score = 5
            warnings.append(f"Low PAT margin of {margin}%")

    # Check margin trend
    margins = [float(f.pat_margin) for f in financials if f.pat_margin]
    if len(margins) >= 4:
        if margins[0] > margins[1] > margins[2] > margins[3]:
            profit_score = min(25, profit_score + 3)
            reasons.append("PAT margins improving consistently")
        elif margins[0] < margins[1] and margins[1] < margins[2]:
            profit_score = max(0, profit_score - 3)
            warnings.append("PAT margins contracting")

    # --- Balance Sheet Score (25 pts) ---
    balance_score = 15
    if latest.debt is not None and latest.revenue:
        debt = float(latest.debt)
        revenue = float(latest.revenue)
        if revenue > 0:
            de_ratio = debt / (revenue * 4)
            if de_ratio < 0.1:
                balance_score = 25
                reasons.append("Virtually debt free")
            elif de_ratio < 0.3:
                balance_score = 20
                reasons.append(f"Low debt with D/E of {round(de_ratio, 2)}")
            elif de_ratio < 0.6:
                balance_score = 15
            elif de_ratio < 1.0:
                balance_score = 10
                warnings.append(f"Moderate debt with D/E of {round(de_ratio, 2)}")
            else:
                balance_score = 5
                warnings.append(f"High debt with D/E of {round(de_ratio, 2)}")

    # Cash flow quality bonus
    if latest.operating_cf and latest.pat:
        if float(latest.operating_cf) > float(latest.pat):
            balance_score = min(25, balance_score + 2)
            reasons.append("Strong cash conversion - operating CF exceeds PAT")

    # --- EBITDA Margin Score (25 pts) ---
    ebitda_score = 10
    if latest.ebitda_margin:
        margin = float(latest.ebitda_margin)
        if margin > 25:
            ebitda_score = 25
            reasons.append(f"Excellent EBITDA margin of {margin}%")
        elif margin > 20:
            ebitda_score = 20
            reasons.append(f"Strong EBITDA margin of {margin}%")
        elif margin > 15:
            ebitda_score = 15
        elif margin > 10:
            ebitda_score = 10
        else:
            ebitda_score = 5
            warnings.append(f"Low EBITDA margin of {margin}%")

    raw_score = revenue_score + profit_score + balance_score + ebitda_score
    final_score = min(100, raw_score)

    return ScoreResult(
        score=round(final_score, 1),
        reasons=reasons,
        warnings=warnings
    )