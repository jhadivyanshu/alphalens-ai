# AlphaLens AI — API Contract

## Base URL
http://localhost:8000/api        (development)
https://alphalens.railway.app/api (production)

## Response Format
Every response follows this shape:

{
  "success": true,
  "data": { ... },
  "error": null
}

On error:

{
  "success": false,
  "data": null,
  "error": "Company not found"
}

---

## Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /search | Search companies |
| GET | /company/{symbol} | Company overview |
| GET | /company/{symbol}/financials | Financial data |
| GET | /company/{symbol}/prices | Price history |
| GET | /company/{symbol}/score | Alpha score |
| GET | /company/{symbol}/score/history | Score changes |
| GET | /company/{symbol}/summary | AI summary |
| GET | /company/{symbol}/news | News + sentiment |
| GET | /company/{symbol}/concall | Concall summary |
| GET | /company/{symbol}/changes | QoQ changes |
| GET | /company/{symbol}/story | Company timeline |
| POST | /chat | AI chat |
| POST | /compare | Compare two companies |
| POST | /report | Generate research report |

---

## 1. Search

GET /search?q=KPIT

Response:
{
  "success": true,
  "data": [
    {
      "symbol": "KPIT",
      "name": "KPIT Technologies Ltd",
      "sector": "IT",
      "market_cap": 45000,
      "overall_score": 82
    }
  ]
}

---

## 2. Company Overview

GET /company/KPIT

Response:
{
  "success": true,
  "data": {
    "symbol": "KPIT",
    "name": "KPIT Technologies Ltd",
    "sector": "IT",
    "industry": "Auto Tech",
    "exchange": "NSE",
    "price": {
      "current": 1842.50,
      "open": 1820.00,
      "high": 1860.00,
      "low": 1810.00,
      "volume": 1200000,
      "week_52_high": 2100.00,
      "week_52_low": 1200.00,
      "change_percent": 1.24
    },
    "ratios": {
      "pe": 48.2,
      "pb": 12.4,
      "market_cap": 45000,
      "dividend_yield": 0.4
    },
    "score": {
      "overall": 82,
      "financial": 86,
      "technical": 74,
      "management": 78,
      "sector": 90,
      "risk": 61
    }
  }
}

---

## 3. Financials

GET /company/KPIT/financials?type=quarterly&limit=8

Query params:
  type     quarterly / annual   default quarterly
  limit    number of periods    default 8

Response:
{
  "success": true,
  "data": [
    {
      "period": "Q2FY25",
      "period_type": "quarterly",
      "revenue": 1420,
      "pat": 210,
      "ebitda": 310,
      "ebitda_margin": 21.8,
      "pat_margin": 14.7,
      "eps": 7.2,
      "roe": 28.4,
      "roce": 32.1,
      "debt": 180,
      "cash": 420,
      "operating_cf": 240
    }
  ]
}

---

## 4. Price History

GET /company/KPIT/prices?period=1y

Query params:
  period    1m / 3m / 6m / 1y / 3y    default 1y

Response:
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "open": 1820.00,
      "high": 1860.00,
      "low": 1810.00,
      "close": 1842.50,
      "volume": 1200000
    }
  ]
}

---

## 5. Alpha Score

GET /company/KPIT/score

Response:
{
  "success": true,
  "data": {
    "overall": 82,
    "engines": {
      "financial": {
        "score": 86,
        "reasons": [
          "Revenue CAGR 24% over 3 years",
          "PAT margins improving for 6 quarters",
          "Debt reducing consistently"
        ],
        "warnings": [
          "Cash conversion cycle increasing"
        ]
      },
      "technical": {
        "score": 74,
        "reasons": [
          "Trading above 200 DMA",
          "RSI at healthy 58"
        ],
        "warnings": [
          "Below 52W high by 12%"
        ]
      },
      "management": {
        "score": 78,
        "reasons": [
          "Promoter holding stable at 40%",
          "Guidance met in 4 of last 5 quarters"
        ],
        "warnings": []
      },
      "sector": {
        "score": 90,
        "reasons": [
          "EV software spending accelerating globally",
          "KPIT is market leader in this niche"
        ],
        "warnings": []
      },
      "risk": {
        "score": 61,
        "reasons": [],
        "warnings": [
          "Revenue concentrated in top 3 clients",
          "Rich valuation at 48x PE",
          "Global auto slowdown risk"
        ]
      }
    },
    "calculated_at": "2024-11-15T10:30:00Z"
  }
}

---

## 6. Score History

GET /company/KPIT/score/history?limit=10

Response:
{
  "success": true,
  "data": [
    {
      "overall": 83,
      "delta": +7,
      "change_reasons": [
        "Revenue growth accelerated",
        "Margins improved 2.3%",
        "Promoter bought shares"
      ],
      "calculated_at": "2024-11-15T10:30:00Z"
    },
    {
      "overall": 76,
      "delta": -2,
      "change_reasons": [
        "Valuation increased sharply",
        "One large client deferred orders"
      ],
      "calculated_at": "2024-08-10T10:30:00Z"
    }
  ]
}

---

## 7. AI Summary

GET /company/KPIT/summary

Response:
{
  "success": true,
  "data": {
    "business": "KPIT Technologies is a pure-play automotive software company...",
    "strengths": [
      "Market leader in EV powertrain software",
      "Deep relationships with global OEMs",
      "Asset-light model with high margins"
    ],
    "weaknesses": [
      "High client concentration",
      "Limited geographic diversification"
    ],
    "future_outlook": "EV adoption tailwinds remain strong...",
    "risks": [
      "Global auto slowdown could defer IT spending",
      "Rich valuation leaves little margin of safety"
    ],
    "ai_verdict": "Strong business in a high-growth niche trading at premium valuation."
  }
}

---

## 8. News

GET /company/KPIT/news?limit=10

Response:
{
  "success": true,
  "data": [
    {
      "title": "KPIT wins new EV contract with European OEM",
      "source": "Economic Times",
      "url": "https://...",
      "published_at": "2024-11-10T08:00:00Z",
      "summary": "KPIT Technologies announced a multi-year contract...",
      "sentiment": "positive"
    }
  ]
}

---

## 9. Concall Summary

GET /company/KPIT/concall?quarter=Q2FY25

Response:
{
  "success": true,
  "data": {
    "quarter": "Q2FY25",
    "summary": "Management highlighted strong deal wins...",
    "positives": [
      "Deal pipeline at all time high",
      "Margin guidance maintained"
    ],
    "negatives": [
      "One client pushed orders to next quarter"
    ],
    "management_promises": [
      "Will cross $500M revenue by FY26",
      "Hiring 2000 engineers in next 6 months"
    ],
    "sentiment": "positive"
  }
}

---

## 10. Quarter on Quarter Changes

GET /company/KPIT/changes

Response:
{
  "success": true,
  "data": {
    "from": "Q1FY25",
    "to": "Q2FY25",
    "changes": [
      {
        "metric": "Revenue",
        "from": 1210,
        "to": 1420,
        "change_percent": 17.4,
        "direction": "up"
      },
      {
        "metric": "PAT Margin",
        "from": 13.2,
        "to": 14.7,
        "change_percent": 11.4,
        "direction": "up"
      }
    ],
    "ai_explanation": "Revenue grew 17% driven by new EV contracts
     signed in Q1 finally contributing. Margin expansion came from
     operating leverage as headcount growth slowed."
  }
}

---

## 11. Company Story

GET /company/KPIT/story

Response:
{
  "success": true,
  "data": [
    {
      "year": 2019,
      "quarter": null,
      "event": "Separated from Cummins, became pure-play auto software",
      "impact": "positive",
      "category": "business"
    },
    {
      "year": 2021,
      "quarter": "Q3",
      "event": "Won first major EV contract with European OEM",
      "impact": "positive",
      "category": "deal"
    },
    {
      "year": 2022,
      "quarter": null,
      "event": "Promoter increased holding by 2%",
      "impact": "positive",
      "category": "management"
    }
  ]
}

---

## 12. AI Chat

POST /chat

Request:
{
  "question": "Why is KPIT considered a good long-term business?",
  "symbol": "KPIT",
  "history": [
    {
      "role": "user",
      "content": "Tell me about KPIT"
    },
    {
      "role": "assistant",
      "content": "KPIT is a pure-play automotive software company..."
    }
  ]
}

Response:
{
  "success": true,
  "data": {
    "answer": "KPIT operates in a niche that very few companies...",
    "sources": [
      "Annual Report FY2024",
      "Q2FY25 Earnings Call"
    ]
  }
}

---

## 13. Compare Two Companies

POST /compare

Request:
{
  "symbols": ["KPIT", "PERSISTENT"]
}

Response:
{
  "success": true,
  "data": {
    "companies": ["KPIT", "PERSISTENT"],
    "comparison": {
      "financials": {
        "KPIT": { "revenue_growth": 24, "pat_margin": 14.7 },
        "PERSISTENT": { "revenue_growth": 38, "pat_margin": 17.2 }
      },
      "scores": {
        "KPIT": { "overall": 82, "financial": 86 },
        "PERSISTENT": { "overall": 79, "financial": 81 }
      }
    },
    "ai_verdict": "Persistent has stronger revenue growth and margins.
     KPIT has a more defensible niche in EV software.
     For long-term investors KPIT's positioning is harder to replicate."
  }
}

---

## 14. Generate Research Report

POST /report

Request:
{
  "symbol": "KPIT"
}

Response:
{
  "success": true,
  "data": {
    "report_url": "/reports/KPIT_2024_11_15.pdf",
    "sections": [
      "Business Overview",
      "Financial Analysis",
      "Management Assessment",
      "Technical View",
      "Risk Factors",
      "Sector Outlook",
      "AI Verdict"
    ]
  }
}
