from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import ingest, abstracts, search, export, review, evaluation

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinical Trial NLP API",
    description="Backend service extracting structured evidence (NER, RE, AD) from PubMed abstracts.",
    version="1.0.0"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest.router)
app.include_router(abstracts.router)
app.include_router(search.router)
app.include_router(export.router)
app.include_router(review.router)
app.include_router(evaluation.router)

@app.get("/")
def root():
    return {
        "system": "Clinical Trial NLP API",
        "status": "online",
        "patent_reference": "US20250252261A1",
        "documentation": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
