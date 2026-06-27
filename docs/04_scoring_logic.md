# AlphaLens AI — Scoring Logic

## Philosophy
No ML. No black box.
Every score is explainable.
Every score has reasons and warnings.
Every score can be audited.

---

## Final Alpha Score Formula

Overall = (Financial × 0.35)
        + (Management × 0.25)
        + (Technical × 0.15)
        + (Sector × 0.15)
        + (Risk × 0.10)

---

## Output Shape (All Engines)

Every engine returns this exact shape:

{
  "score": 82,
  "reasons": [
    "Revenue CAGR 24% over 3 years",
    "Margins expanding for 6 quarters"
  ],
  "warnings": [
    "Rich valuation at 48x PE"
  ]
}

---

# Engine 1 — Financial Engine (35%)

## Inputs
  Revenue (last 8 quarters)
  PAT (last 8 quarters)
  EBITDA Margin (last 8 quarters)
  PAT Margin (last 8 quarters)
  Debt
  Cash
  Operating Cash Flow
  ROCE
  ROE

---

## Sub-scores

### 1. Revenue Growth Score (25 pts)

  Calculate trailing 3 year revenue CAGR.

  CAGR > 25%      →  25 pts
  CAGR 20-25%     →  20 pts
  CAGR 15-20%     →  15 pts
  CAGR 10-15%     →  10 pts
  CAGR < 10%      →   5 pts

  Bonus +3 pts if last 2 quarters both grew > previous quarter.
  Penalty -3 pts if revenue declined in last quarter.

---

### 2. Profitability Score (25 pts)

  Use PAT Margin latest quarter.

  Margin > 20%    →  25 pts
  Margin 15-20%   →  20 pts
  Margin 10-15%   →  15 pts
  Margin 5-10%    →  10 pts
  Margin < 5%     →   5 pts

  Bonus +3 pts if margins improving for 4+ consecutive quarters.
  Penalty -3 pts if margins contracted last 2 quarters.

---

### 3. Return Quality Score (25 pts)

  Use ROCE (preferred) or ROE if ROCE unavailable.

  ROCE > 30%      →  25 pts
  ROCE 20-30%     →  20 pts
  ROCE 15-20%     →  15 pts
  ROCE 10-15%     →  10 pts
  ROCE < 10%      →   5 pts

---

### 4. Balance Sheet Score (25 pts)

  Debt to Equity Ratio.

  D/E < 0.1       →  25 pts   (debt free)
  D/E 0.1-0.3     →  20 pts
  D/E 0.3-0.6     →  15 pts
  D/E 0.6-1.0     →  10 pts
  D/E > 1.0       →   5 pts

  Bonus +3 pts if debt reduced last 2 years.
  Bonus +2 pts if operating cash flow > PAT (quality earnings).
  Penalty -5 pts if debt increased sharply last year.

---

## Financial Score Calculation

  raw = revenue_score + profitability_score
      + return_score + balance_sheet_score

  financial_score = min(100, raw)

---

## Financial Reason Generation

  If CAGR > 20%:
    add reason "Revenue CAGR {X}% over 3 years"

  If margins improving 4+ quarters:
    add reason "Margins expanding for {N} consecutive quarters"

  If ROCE > 25%:
    add reason "High capital efficiency with ROCE of {X}%"

  If D/E < 0.1:
    add reason "Virtually debt free"

  If D/E > 1.0:
    add warning "High leverage with D/E of {X}"

  If margins contracted 2 quarters:
    add warning "Margin contraction in last 2 quarters"

---

# Engine 2 — Technical Engine (15%)

## Inputs
  Daily closing prices (last 1 year)
  Volume (last 1 year)

## Calculated internally
  50 DMA
  200 DMA
  RSI (14 day)
  52 Week High
  52 Week Low

---

## Sub-scores

### 1. Trend Score (30 pts)

  Price > 200 DMA and 50 DMA > 200 DMA  →  30 pts  (strong uptrend)
  Price > 200 DMA only                   →  20 pts  (above long term avg)
  Price < 200 DMA but > 50 DMA           →  10 pts  (mixed)
  Price < both DMAs                      →   5 pts  (downtrend)

---

### 2. Momentum Score (30 pts)

  RSI 50-70    →  30 pts  (healthy momentum)
  RSI 40-50    →  20 pts  (neutral)
  RSI 70-80    →  15 pts  (overbought warning)
  RSI > 80     →   5 pts  (very overbought)
  RSI < 40     →  10 pts  (weak)
  RSI < 30     →   5 pts  (oversold)

---

### 3. Position Score (40 pts)

  Where is price vs 52W range?

  position = (current - 52W low) / (52W high - 52W low)

  position > 0.8    →  40 pts  (near 52W high, strong)
  position 0.6-0.8  →  30 pts
  position 0.4-0.6  →  20 pts
  position 0.2-0.4  →  10 pts
  position < 0.2    →   5 pts  (near 52W low, weak)

---

## Technical Score Calculation

  technical_score = trend_score + momentum_score + position_score
  technical_score = min(100, technical_score)

---

# Engine 3 — Management Engine (25%)

## Inputs
  Promoter holding (current + last 4 quarters)
  Concall sentiment (last 4 quarters)
  Management promises vs actuals
  Pledge percentage

---

## Sub-scores

### 1. Promoter Holding Score (40 pts)

  Holding > 60% and increasing   →  40 pts
  Holding > 60% and stable       →  35 pts
  Holding 40-60% and increasing  →  30 pts
  Holding 40-60% and stable      →  25 pts
  Holding decreasing             →  10 pts
  Pledge > 20%                   →  -10 pts penalty

---

### 2. Guidance Accuracy Score (40 pts)

  Track last 4 quarters.
  Did management meet their own guidance?

  4 of 4 met      →  40 pts
  3 of 4 met      →  30 pts
  2 of 4 met      →  20 pts
  1 of 4 met      →  10 pts
  0 of 4 met      →   0 pts

  Note: This requires concall data.
  If concall data unavailable default to 25 pts (neutral).

---

### 3. Concall Sentiment Score (20 pts)

  Average sentiment of last 4 concalls.

  All positive          →  20 pts
  Mostly positive       →  15 pts
  Mixed                 →  10 pts
  Mostly negative       →   5 pts

---

## Management Score Calculation

  management_score = holding_score + guidance_score + sentiment_score
  management_score = min(100, management_score)

---

# Engine 4 — Sector Engine (15%)

## Inputs
  Company sector (from companies table)
  Hardcoded sector scores (updated manually quarterly)

## Sector Score Table

  IT - Auto Tech          →  90
  IT - General            →  72
  Pharma - Specialty      →  85
  Pharma - Generic        →  68
  Banking - Private       →  75
  Banking - PSU           →  55
  FMCG                    →  70
  Capital Goods           →  80
  Infrastructure          →  72
  Real Estate             →  60
  Telecom                 →  58
  Metals                  →  55
  Oil and Gas             →  50

## Note
  Sector scores are the simplest engine.
  They represent macro tailwind or headwind.
  Update this table once per quarter manually.
  Over time this can be AI-generated from news.

---

# Engine 5 — Risk Engine (10%)

## Note
  Risk engine is inverted.
  High risk = low score.
  Low risk = high score.

## Inputs
  PE Ratio
  Debt (from financials)
  Revenue concentration (if available)
  Promoter pledge

---

## Sub-scores

### 1. Valuation Risk (40 pts)

  PE < 15     →  40 pts  (cheap)
  PE 15-25    →  35 pts
  PE 25-40    →  25 pts
  PE 40-60    →  15 pts
  PE > 60     →   5 pts  (very expensive)
  PE negative →  10 pts  (loss making)

---

### 2. Debt Risk (40 pts)

  D/E < 0.1   →  40 pts
  D/E 0.1-0.3 →  35 pts
  D/E 0.3-0.6 →  25 pts
  D/E 0.6-1.0 →  15 pts
  D/E > 1.0   →   5 pts

---

### 3. Other Risk (20 pts)

  Start at 20 pts.

  Pledge > 10%          →  -5 pts
  Pledge > 30%          →  -10 pts
  Revenue from top
  client > 30%          →  -5 pts
  Auditor changed
  last year             →  -5 pts
  Promoter selling
  consistently          →  -5 pts

  Minimum 0 pts.

---

## Risk Score Calculation

  risk_score = valuation_risk + debt_risk + other_risk
  risk_score = min(100, risk_score)

---

# Final Alpha Score

  alpha = (financial   × 0.35)
        + (management  × 0.25)
        + (technical   × 0.15)
        + (sector      × 0.15)
        + (risk        × 0.10)

  alpha = round(alpha, 1)

---

# Score Change Detection

Run after every recalculation.

  delta = new_overall - old_overall

  If delta > 2 or delta < -2:
    trigger "Why did score change?" explanation

  Compare each engine score individually.
  Find which engines moved the most.
  Generate natural language reason.

  Example:
    Financial went from 78 to 86  →  "Revenue growth accelerated"
    Technical went from 80 to 68  →  "Price fell below 200 DMA"

---

# Score Interpretation

  90-100   →  Exceptional. Rare.
  80-89    →  Strong. High conviction.
  70-79    →  Good. Worth watching.
  60-69    →  Average. Mixed signals.
  50-59    →  Weak. Caution advised.
  Below 50 →  Poor. Avoid or short.

---

# Implementation Notes

  Each engine lives in its own file:
    scoring/financial.py
    scoring/technical.py
    scoring/management.py
    scoring/sector.py
    scoring/risk.py

  Each file exposes one function:
    def calculate(company_id, db) -> ScoreResult

  ScoreResult is a Pydantic model:
    score: float
    reasons: list[str]
    warnings: list[str]

  score_service.py calls all 5 engines
  and combines them into the final Alpha Score.
