from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import search, company, score, ai, news, chat, intelligence

load_dotenv()

app = FastAPI(
    title="AlphaLens AI",
    description="AI Equity Research Terminal for Indian Markets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api")
app.include_router(company.router, prefix="/api")
app.include_router(score.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "AlphaLens AI is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}