# AlphaLens AI — Database Schema

## Database
PostgreSQL (Supabase free tier)

---

## Tables Overview
| Table | Purpose |
|-------|---------|
| companies | Master list of all companies |
| prices | Daily historical prices |
| financials | Quarterly + annual financial data |
| news | News articles per company |
| documents | Annual reports + concall transcripts |
| scores | Alpha scores per company |
| score_history | Score changes over time |

---

## 1. companies
Master table. Every other table references this.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| symbol | VARCHAR(20) UNIQUE | KPIT, TCS, INFY |
| name | VARCHAR(200) | KPIT Technologies Ltd |
| sector | VARCHAR(100) | IT |
| industry | VARCHAR(100) | Auto Tech |
| market_cap | BIGINT | In crores |
| exchange | VARCHAR(10) | NSE / BSE |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMP | |

---

## 2. prices
One row per company per day.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id | |
| date | DATE | |
| open | NUMERIC(12,2) | |
| high | NUMERIC(12,2) | |
| low | NUMERIC(12,2) | |
| close | NUMERIC(12,2) | |
| volume | BIGINT | |
| created_at | TIMESTAMP | |

Index: (company_id, date)

---

## 3. financials
Quarterly and annual both stored here.
period_type distinguishes them.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id | |
| period | VARCHAR(20) | Q1FY24, FY2024 |
| period_type | VARCHAR(10) | quarterly / annual |
| revenue | NUMERIC(15,2) | In crores |
| pat | NUMERIC(15,2) | Profit after tax |
| ebitda | NUMERIC(15,2) | |
| ebitda_margin | NUMERIC(6,2) | % |
| pat_margin | NUMERIC(6,2) | % |
| eps | NUMERIC(10,2) | |
| roe | NUMERIC(6,2) | % |
| roce | NUMERIC(6,2) | % |
| debt | NUMERIC(15,2) | |
| cash | NUMERIC(15,2) | |
| operating_cf | NUMERIC(15,2) | Operating cash flow |
| created_at | TIMESTAMP | |

Index: (company_id, period_type, period)

---

## 4. news
One row per news article.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id | |
| title | TEXT | |
| source | VARCHAR(100) | |
| url | TEXT | |
| published_at | TIMESTAMP | |
| summary | TEXT | AI generated |
| sentiment | VARCHAR(10) | positive/negative/neutral |
| created_at | TIMESTAMP | |

Index: (company_id, published_at)

---

## 5. documents
Annual reports and concall transcripts.
PDFs stored as file path or URL.
Embeddings stored in ChromaDB, not here.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id | |
| doc_type | VARCHAR(20) | annual_report / concall |
| year | INT | 2024 |
| quarter | VARCHAR(10) | Q1FY24, null for annual |
| file_path | TEXT | Local path or URL |
| raw_text | TEXT | Extracted text |
| summary | TEXT | AI generated |
| sentiment | VARCHAR(10) | For concalls |
| management_promises | JSONB | Extracted promises |
| is_embedded | BOOLEAN | Has ChromaDB entry? |
| created_at | TIMESTAMP | |

Index: (company_id, doc_type, year)

---

## 6. scores
Latest score per company.
One row per company, updated on recalculation.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id UNIQUE | |
| financial | NUMERIC(5,2) | 0-100 |
| technical | NUMERIC(5,2) | 0-100 |
| management | NUMERIC(5,2) | 0-100 |
| sector | NUMERIC(5,2) | 0-100 |
| risk | NUMERIC(5,2) | 0-100 |
| overall | NUMERIC(5,2) | Weighted average |
| reasons | JSONB | Per engine reasons |
| warnings | JSONB | Per engine warnings |
| calculated_at | TIMESTAMP | |

---

## 7. score_history
Every time score is recalculated, old score is saved here.
Powers the "Why did my score change?" feature.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PRIMARY KEY | |
| company_id | INT → companies.id | |
| financial | NUMERIC(5,2) | |
| technical | NUMERIC(5,2) | |
| management | NUMERIC(5,2) | |
| sector | NUMERIC(5,2) | |
| risk | NUMERIC(5,2) | |
| overall | NUMERIC(5,2) | |
| delta | NUMERIC(5,2) | Change from previous |
| change_reasons | JSONB | What drove the change |
| calculated_at | TIMESTAMP | |

Index: (company_id, calculated_at)

---

## Relationships

companies
    │
    ├── prices          (one to many)
    ├── financials      (one to many)
    ├── news            (one to many)
    ├── documents       (one to many)
    ├── scores          (one to one)
    └── score_history   (one to many)

---

## Notes

### On JSONB
reasons, warnings, management_promises, change_reasons
are stored as JSONB because their structure varies
per company and per scoring run.
PostgreSQL JSONB is queryable and indexed.

### On ChromaDB
Embeddings are NOT stored in PostgreSQL.
ChromaDB runs alongside the backend.
documents.is_embedded tracks what has been embedded.
ChromaDB collection name = company symbol (KPIT, TCS)

### On Supabase free tier
500MB limit.
Prices table will be the largest.
Store max 2 years of daily prices per company.
For 200 companies that is roughly 200 x 500 x 7 cols
= manageable within free tier.
