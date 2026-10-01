import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService

app = FastAPI(title="PhishGuard API", version="0.1.0", description="Explainable phishing and social-engineering intelligence.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000"), "http://127.0.0.1:3000"],
    allow_origin_regex=r"^(https?://(localhost|127\.0\.0\.1)(:\d+)?|chrome-extension://.*)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
service = AnalysisService(db_path=os.getenv("DATABASE_PATH", "phishguard.db"))

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health():
    return {
        "api": True,
        "ollama": bool(os.getenv("OLLAMA_BASE_URL")),
        "virustotal": bool(os.getenv("VIRUSTOTAL_API_KEY")),
        "safebrowsing": bool(os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")),
        "urlhaus": bool(os.getenv("URLHAUS_API_KEY")) and os.getenv("ENABLE_URLHAUS", "false").lower() == "true",
        "rdap": True
    }

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        return await service.analyze(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/api/v1/analyze-url", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest):
    if not request.url:
        raise HTTPException(status_code=422, detail="url is required")
    return await service.analyze(request)

@app.get("/api/v1/scans")
async def get_scans(limit: int = 50):
    return service.get_scans(limit=limit)

@app.get("/api/v1/scans/{scan_id}")
async def get_scan_details(scan_id: str):
    scan = service.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

