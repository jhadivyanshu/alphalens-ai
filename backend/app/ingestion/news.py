import feedparser
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connection import SessionLocal
from app.models.models import Company, News
from app.services.ai_service import generate
from datetime import datetime


def fetch_news(symbol: str, company_name: str, db):
    # Google News RSS
    query = f"{company_name} stock NSE"
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)

    if not feed.entries:
        print(f"No news found for {symbol}")
        return

    company = db.query(Company).filter(Company.symbol == symbol).first()
    if not company:
        return

    count = 0
    for entry in feed.entries[:5]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        published = entry.get("published", "")

        # Parse date
        try:
            published_at = datetime(*entry.published_parsed[:6])
        except:
            published_at = datetime.utcnow()

        # Check if already exists
        existing = db.query(News).filter(News.url == url).first()
        if existing:
            continue

        # AI sentiment + summary
        prompt = f"""
Analyze this news headline about {company_name}:
"{title}"

Respond in this exact format:
SENTIMENT: positive/negative/neutral
SUMMARY: [one sentence summary]
"""
        ai_response = generate(prompt)
        sentiment = "neutral"
        summary = title

        for line in ai_response.split("\n"):
            if line.startswith("SENTIMENT:"):
                s = line.replace("SENTIMENT:", "").strip().lower()
                if s in ["positive", "negative", "neutral"]:
                    sentiment = s
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()

        news = News(
            company_id=company.id,
            title=title,
            source="Google News",
            url=url,
            published_at=published_at,
            summary=summary,
            sentiment=sentiment
        )
        db.add(news)
        count += 1

    db.commit()
    print(f"Stored {count} news articles for {symbol}")


if __name__ == "__main__":
    db = SessionLocal()
    companies = [
        ("TCS", "Tata Consultancy Services"),
        ("INFY", "Infosys"),
        ("KPIT", "KPIT Technologies"),
        ("RELIANCE", "Reliance Industries"),
        ("ICICIBANK", "ICICI Bank"),
    ]
    for symbol, name in companies:
        fetch_news(symbol, name, db)
    db.close()