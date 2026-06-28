from sqlalchemy.orm import Session
from app.models.models import Company, Price
from sqlalchemy import desc
from app.scoring.financial import ScoreResult
import statistics


def calculate(company_id: int, db: Session) -> ScoreResult:
    reasons = []
    warnings = []

    # Fetch last 1 year of prices
    prices = db.query(Price).filter(
        Price.company_id == company_id
    ).order_by(desc(Price.date)).limit(365).all()

    if not prices or len(prices) < 20:
        return ScoreResult(score=50, reasons=["Insufficient price data"], warnings=[])

    closes = [float(p.close) for p in prices]
    current_price = closes[0]

    # --- 52 Week High/Low ---
    week_52_high = max(closes)
    week_52_low = min(closes)
    position = (current_price - week_52_low) / (week_52_high - week_52_low) if week_52_high != week_52_low else 0.5

    position_score = 0
    if position > 0.8:
        position_score = 40
        reasons.append(f"Trading near 52W high - strong momentum")
    elif position > 0.6:
        position_score = 30
        reasons.append(f"Trading in upper half of 52W range")
    elif position > 0.4:
        position_score = 20
    elif position > 0.2:
        position_score = 10
        warnings.append("Trading in lower half of 52W range")
    else:
        position_score = 5
        warnings.append("Trading near 52W low - weak momentum")

    # --- Moving Averages ---
    trend_score = 0
    ma_50 = statistics.mean(closes[:50]) if len(closes) >= 50 else None
    ma_200 = statistics.mean(closes[:200]) if len(closes) >= 200 else None

    if ma_50 and ma_200:
        if current_price > ma_200 and ma_50 > ma_200:
            trend_score = 30
            reasons.append("Price above 200 DMA with golden cross - strong uptrend")
        elif current_price > ma_200:
            trend_score = 20
            reasons.append("Price above 200 DMA")
        elif current_price > ma_50:
            trend_score = 10
            warnings.append("Price below 200 DMA but above 50 DMA")
        else:
            trend_score = 5
            warnings.append("Price below both 50 and 200 DMA - downtrend")
    elif ma_50:
        if current_price > ma_50:
            trend_score = 15
            reasons.append("Price above 50 DMA")
        else:
            trend_score = 8
            warnings.append("Price below 50 DMA")

    # --- RSI (14 day) ---
    rsi_score = 0
    rsi = calculate_rsi(closes[:15])

    if rsi:
        if 50 <= rsi <= 70:
            rsi_score = 30
            reasons.append(f"RSI at healthy {round(rsi, 1)} - good momentum")
        elif 40 <= rsi < 50:
            rsi_score = 20
        elif 70 < rsi <= 80:
            rsi_score = 15
            warnings.append(f"RSI at {round(rsi, 1)} - slightly overbought")
        elif rsi > 80:
            rsi_score = 5
            warnings.append(f"RSI at {round(rsi, 1)} - overbought")
        elif rsi < 30:
            rsi_score = 10
            warnings.append(f"RSI at {round(rsi, 1)} - oversold")
        else:
            rsi_score = 15

    raw_score = position_score + trend_score + rsi_score
    final_score = min(100, raw_score)

    return ScoreResult(
        score=round(final_score, 1),
        reasons=reasons,
        warnings=warnings
    )


def calculate_rsi(closes: list, period: int = 14) -> float:
    if len(closes) < period + 1:
        return None

    deltas = [closes[i] - closes[i+1] for i in range(len(closes)-1)]
    gains = [d for d in deltas[:period] if d > 0]
    losses = [abs(d) for d in deltas[:period] if d < 0]

    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi