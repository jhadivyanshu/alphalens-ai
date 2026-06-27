# AlphaLens AI — Architecture

## Project Type
AI Equity Research Terminal for Indian Markets

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React, Recharts, TailwindCSS |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL (Supabase free tier) |
| Vector DB | ChromaDB (local, free) |
| AI | Gemini API (free tier) |
| Embeddings | Gemini Embedding API |
| Data | yfinance, nsepython, Screener scraper |
| Deploy | Vercel (frontend), Railway (backend) |

---

## Folder Structure

alphalens-ai/
│
├── backend/
│   └── app/
│       ├── api/              # Route handlers only, no logic
│       │   ├── company.py
│       │   ├── search.py
│       │   ├── score.py
│       │   ├── ai.py
│       │   ├── news.py
│       │   └── chat.py
│       │
│       ├── services/         # Business logic
│       │   ├── stock_service.py
│       │   ├── news_service.py
│       │   ├── ai_service.py
│       │   ├── rag_service.py
│       │   └── report_service.py
│       │
│       ├── scoring/          # Independent scoring engines
│       │   ├── financial.py
│       │   ├── technical.py
│       │   ├── risk.py
│       │   ├── management.py
│       │   └── sector.py
│       │
│       ├── ingestion/        # Data fetching scripts
│       │   ├── yfinance.py
│       │   ├── news.py
│       │   ├── reports.py
│       │   └── concalls.py
│       │
│       ├── prompts/          # All LLM prompts as .txt files
│       │   ├── summary.txt
│       │   ├── compare.txt
│       │   ├── report.txt
│       │   ├── timeline.txt
│       │   └── quarter.txt
│       │
│       ├── models/           # SQLAlchemy table models
│       ├── schemas/          # Pydantic request/response schemas
│       ├── database/         # DB connection, session
│       └── utils/            # Helpers, constants
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Company.jsx
│       │   ├── Compare.jsx
│       │   ├── Chat.jsx
│       │   └── Report.jsx
│       ├── components/
│       ├── hooks/
│       └── services/         # API call functions
│
├── docs/
│   ├── 01_architecture.md
│   ├── 02_database_schema.md
│   ├── 03_api_contract.md
│   └── 04_scoring_logic.md
│
├── scripts/                  # One-time data population scripts
├── tests/
├── README.md
├── CHANGELOG.md
└── ROADMAP.md

---

## Service Boundaries

### Rule
API layer has zero business logic.
Services have zero database queries.
Database layer has zero business logic.

### Flow
Request → API → Service → DB
                      ↓
                  Scoring Engine
                      ↓
                  AI Orchestrator → Prompt Builder → Gemini → Parser

---

## AI Orchestrator Pattern

### Never do this
company.py → Gemini API directly

### Always do this
API endpoint
    ↓
ai_service.py          # decides what to do
    ↓
prompt_builder.py      # builds the prompt from template
    ↓
gemini_client.py       # single place that calls Gemini
    ↓
response_parser.py     # cleans and structures the output
    ↓
API response

### Why
- Swap Gemini for GPT in one file
- All prompts in one place
- Structured outputs always parsed the same way
- Easy to debug when AI returns garbage

---

## RAG Pipeline

PDF / Concall transcript
    ↓
Text extraction
    ↓
Chunking (500 tokens, 50 overlap)
    ↓
Gemini Embeddings
    ↓
ChromaDB (stored by company)
    ↓
Query → Top 5 chunks retrieved
    ↓
Gemini answers using chunks as context

---

## Scoring Architecture

Each engine is independent.
Each engine returns the same shape:

{
  "score": 82,
  "reasons": [
    "Revenue CAGR 24% over 3 years",
    "Debt-to-equity improving",
    "Margins expanding"
  ],
  "warnings": [
    "Rich valuation vs peers"
  ]
}

Final Alpha Score = weighted average:
  Financial    35%
  Management   25%
  Technical    15%
  Sector       15%
  Risk         10%

---

## MVP Cutoff

After Milestone 3 the product is already impressive:
- Search any NSE company
- Financial dashboard
- Alpha Score with reasons
- AI summary
- Ask questions about annual reports
- News sentiment

Everything after is a bonus.
