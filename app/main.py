import time
from typing import Optional
from fastapi import FastAPI, Query, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    TrustScoreRequest, TrustScoreResponse, BatchTrustScoreRequest, BatchTrustScoreResponse
)
from core.trust_engine import TrustEngine

app = FastAPI(
    title="VeriPulse Trust Intelligence API",
    description="Unified Dual-Engine B2B Signup Fraud Defense & Bot Blocker by VeriPulse Labs. Synthesizes email deliverability and telecom carrier intelligence into an automated 0-100 Trust Score.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoring"])
async def health():
    return {
        "status": "healthy",
        "service": "veripulse-trust-intelligence",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.post("/v1/trust-score", response_model=TrustScoreResponse, tags=["Trust Intelligence"])
@app.get("/v1/trust-score", response_model=TrustScoreResponse, tags=["Trust Intelligence"])
async def evaluate_trust_score(
    email: Optional[str] = Query(None, description="Email address to evaluate"),
    phone: Optional[str] = Query(None, description="Phone number to evaluate"),
    country_code: Optional[str] = Query("US", description="Default ISO country code for phone validation"),
    payload: Optional[TrustScoreRequest] = Body(None)
):
    """
    Unified Signup Fraud Defense & Bot Detection Endpoint.
    Evaluates email and phone signals concurrently to return a single 0-100 Trust Score.
    """
    target_email = (payload.email if payload and payload.email else email) or None
    target_phone = (payload.phone if payload and payload.phone else phone) or None
    target_country = (payload.country_code if payload and payload.country_code else country_code) or "US"

    if not target_email and not target_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one identifier (email or phone) must be provided for trust evaluation."
        )

    return await TrustEngine.evaluate(
        email=target_email,
        phone=target_phone,
        country_code=target_country
    )

@app.post("/v1/batch-score", response_model=BatchTrustScoreResponse, tags=["Trust Intelligence"])
@app.post("/v1/trust-score/batch", response_model=BatchTrustScoreResponse, tags=["Trust Intelligence"])
async def batch_evaluate(payload: BatchTrustScoreRequest):
    """
    High-throughput batch trust scoring for bulk signup audits.
    """
    results = []
    for item in payload.items:
        res = await TrustEngine.evaluate(
            email=item.email,
            phone=item.phone,
            country_code=item.country_code or "US"
        )
        results.append(res)

    return BatchTrustScoreResponse(
        total_processed=len(results),
        results=results
    )
