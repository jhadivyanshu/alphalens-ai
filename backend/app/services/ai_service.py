import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"


def generate(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI error: {str(e)}"


def generate_company_summary(company_name: str, sector: str, financials: dict, score: dict) -> dict:
    prompt = f"""
You are an expert equity research analyst covering Indian stock markets.

Analyze this company and provide a structured research summary.

Company: {company_name}
Sector: {sector}

Financial Snapshot:
- Revenue: ₹{financials.get('revenue', 'N/A')} crores
- PAT Margin: {financials.get('pat_margin', 'N/A')}%
- EBITDA Margin: {financials.get('ebitda_margin', 'N/A')}%

Alpha Score: {score.get('overall', 'N/A')}/100
- Financial Score: {score.get('financial', 'N/A')}
- Technical Score: {score.get('technical', 'N/A')}
- Risk Score: {score.get('risk', 'N/A')}

Provide your analysis in this exact format:

BUSINESS:
[2-3 sentences about what the company does and its market position]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]

FUTURE_OUTLOOK:
[2-3 sentences about growth prospects]

RISKS:
- [risk 1]
- [risk 2]

AI_VERDICT:
[1 sentence verdict for investors]
"""

    raw = generate(prompt)
    return parse_summary(raw)


def parse_summary(raw: str) -> dict:
    result = {
        "business": "",
        "strengths": [],
        "weaknesses": [],
        "future_outlook": "",
        "risks": [],
        "ai_verdict": ""
    }

    current_section = None
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("BUSINESS:"):
            current_section = "business"
        elif line.startswith("STRENGTHS:"):
            current_section = "strengths"
        elif line.startswith("WEAKNESSES:"):
            current_section = "weaknesses"
        elif line.startswith("FUTURE_OUTLOOK:"):
            current_section = "future_outlook"
        elif line.startswith("RISKS:"):
            current_section = "risks"
        elif line.startswith("AI_VERDICT:"):
            current_section = "ai_verdict"
        elif current_section:
            if current_section in ["strengths", "weaknesses", "risks"]:
                if line.startswith("-"):
                    result[current_section].append(line[1:].strip())
            elif current_section in ["business", "future_outlook", "ai_verdict"]:
                result[current_section] += line + " "

    # Clean up
    for key in ["business", "future_outlook", "ai_verdict"]:
        result[key] = result[key].strip()

    return result
def generate_chat_response(question: str, symbol: str, company_name: str, context: dict) -> str:
    prompt = f"""
You are an expert equity research analyst for Indian stock markets.

You are answering questions about {company_name} ({symbol}).

Company Context:
- Sector: {context.get('sector', 'N/A')}
- Current Price: ₹{context.get('price', 'N/A')}
- Alpha Score: {context.get('overall_score', 'N/A')}/100
- Financial Score: {context.get('financial_score', 'N/A')}
- Technical Score: {context.get('technical_score', 'N/A')}
- Revenue: ₹{context.get('revenue', 'N/A')} crores
- PAT Margin: {context.get('pat_margin', 'N/A')}%

User Question: {question}

Answer in 3-5 sentences. Be specific, data-driven, and helpful.
If the question is not related to this company or investing, politely redirect.
"""
    return generate(prompt)
def generate_qoq_explanation(company_name: str, q1: dict, q2: dict) -> str:
    changes = []
    
    if q1.get('revenue') and q2.get('revenue'):
        change = ((q2['revenue'] - q1['revenue']) / q1['revenue']) * 100
        changes.append(f"Revenue: {'+' if change > 0 else ''}{round(change, 1)}% (₹{round(q1['revenue'])}Cr → ₹{round(q2['revenue'])}Cr)")
    
    if q1.get('pat_margin') and q2.get('pat_margin'):
        change = q2['pat_margin'] - q1['pat_margin']
        changes.append(f"PAT Margin: {'+' if change > 0 else ''}{round(change, 2)}% ({q1['pat_margin']}% → {q2['pat_margin']}%)")
    
    if q1.get('ebitda_margin') and q2.get('ebitda_margin'):
        change = q2['ebitda_margin'] - q1['ebitda_margin']
        changes.append(f"EBITDA Margin: {'+' if change > 0 else ''}{round(change, 2)}% ({q1['ebitda_margin']}% → {q2['ebitda_margin']}%)")

    prompt = f"""
You are an expert equity analyst covering Indian stock markets.

Analyze the quarter on quarter changes for {company_name}:

{chr(10).join(changes)}

From period: {q1.get('period')}
To period: {q2.get('period')}

Explain in 3-4 sentences what changed, why it matters, and what investors should watch.
Be specific and data-driven.
"""
    return generate(prompt)