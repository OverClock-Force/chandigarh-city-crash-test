"""
C3T AI Router — /api/ai/*
--------------------------
Endpoints:
  GET  /api/ai/status         — Check Gemini API status and vision capabilities
  POST /api/ai/analyze        — Generate Gemini narrative from a stress-test result
  POST /api/ai/chat           — Free-form / multimodal Q&A with C3T-AI
  POST /api/ai/complaint      — Gemini-powered complaint text extraction
  POST /api/ai/vision-analyze — Gemini Multimodal image/damage analysis (base64 JSON)
  POST /api/ai/vision-upload  — Gemini Multimodal image/damage analysis (multipart file upload)
  POST /api/ai/report-from-vision — Confirm vision findings & log as C3T civic event
"""

import os
import base64
import logging
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from backend.app.storage import store
from backend.app.schemas.event import CivicReport, CivicReportCreate
from backend.app.services.gemini_service import (
    generate_risk_narrative,
    extract_complaint_with_gemini,
    analyze_image_with_gemini,
    answer_question,
    GEMINI_AVAILABLE,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["Gemini AI & Multimodal Vision"])


# ---------------------------------------------------------------------------
# Schema Models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    risk_result: Dict[str, Any] = Field(
        ..., description="A RiskAssessmentResult dict from the stress-test engine"
    )


class AnalyzeResponse(BaseModel):
    narrative: str
    gemini_available: bool


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional latest stress-test result or sector data for context",
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Optional base64 image (with or without data URI prefix) for visual chat",
    )
    mime_type: Optional[str] = Field(
        default="image/jpeg",
        description="MIME type of the uploaded image",
    )


class ChatResponse(BaseModel):
    answer: str
    gemini_available: bool


class ComplaintRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=1000)


class ComplaintResponse(BaseModel):
    category: str
    severity: str
    sector_id: Optional[str]
    location_description: str
    confidence: float
    user_must_confirm: bool
    notes: str
    gemini_available: bool


class GeminiStatusResponse(BaseModel):
    gemini_available: bool
    model: str
    message: str
    multimodal_vision_supported: bool = True
    supported_hazards: List[str] = [
        "surface_waterlogging",
        "road_damage",
        "drainage_blockage",
        "waste_hotspot",
        "tree_fall",
        "traffic_disruption",
    ]


class VisionAnalyzeRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded photo (data URI or raw string)")
    mime_type: Optional[str] = Field(default="image/jpeg", description="MIME type (image/jpeg, image/png, image/webp)")
    user_notes: Optional[str] = Field(default=None, description="Optional citizen/reporter context or location remarks")
    sector_id: Optional[str] = Field(default=None, description="Optional tagged sector if known")


class VisionAnalyzeResponse(BaseModel):
    hazard_type: str
    category: str
    severity: str
    severity_score: int
    confidence: float
    sector_id: Optional[str] = None
    location_clues: Optional[str] = None
    visual_observations: str
    damage_details: Dict[str, Any]
    recommended_action: str
    action_urgency: str
    user_must_confirm: bool = True
    summary: str
    gemini_available: bool
    data_status: str = "synthetic_demo"
    score_label: str = "Unvalidated demo index (0-100)"


class VisionReportConfirmRequest(BaseModel):
    confirmed_sector_id: str = Field(..., description="User-confirmed sector (e.g. Sector 17)")
    confirmed_category: str = Field(..., description="Confirmed category: Waterlogging, Road disruption, Drain blockage, Waste hotspot, Other")
    confirmed_severity: str = Field(..., description="Confirmed severity: low, moderate, high, critical")
    description: str = Field(..., description="Issue description compiled from multimodal analysis and citizen input")
    confidence: Optional[float] = Field(default=0.90, ge=0.0, le=1.0)
    media_url: Optional[str] = Field(default=None, description="Optional media URL or preview reference")
    recommended_action: Optional[str] = Field(default=None, description="Recommended municipal action from vision analysis")


# ---------------------------------------------------------------------------
# Helper function
# ---------------------------------------------------------------------------

def _strip_and_decode_base64(b64_str: str) -> bytes:
    """Strip data URI header if present and return raw bytes."""
    if "," in b64_str:
        b64_str = b64_str.split(",", 1)[1]
    return base64.b64decode(b64_str)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status", response_model=GeminiStatusResponse)
def gemini_status():
    """Check whether Gemini API is configured and verify multimodal vision support."""
    return GeminiStatusResponse(
        gemini_available=GEMINI_AVAILABLE,
        model=os.getenv("GEMINI_MODEL", "gemini-flash-latest") if GEMINI_AVAILABLE else "simulated-multimodal",
        message=(
            "Gemini Multimodal Vision API is active and ready."
            if GEMINI_AVAILABLE
            else "GEMINI_API_KEY is not set. Operating in high-fidelity simulated demo mode."
        ),
        multimodal_vision_supported=True,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_risk(request: AnalyzeRequest):
    """
    Send a stress-test result to Gemini and get a plain-English narrative
    with key findings and recommended actions.
    """
    try:
        narrative = generate_risk_narrative(request.risk_result)
        return AnalyzeResponse(narrative=narrative, gemini_available=GEMINI_AVAILABLE)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Ask C3T-AI any question about urban risks, sectors, or the C3T system.
    Supports multimodal queries with optional uploaded photo context.
    """
    try:
        image_bytes = None
        if request.image_base64:
            image_bytes = _strip_and_decode_base64(request.image_base64)

        answer = answer_question(
            question=request.question,
            context=request.context,
            image_bytes=image_bytes,
            mime_type=request.mime_type or "image/jpeg",
        )
        return ChatResponse(answer=answer, gemini_available=GEMINI_AVAILABLE)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/complaint", response_model=ComplaintResponse)
def extract_complaint(request: ComplaintRequest):
    """
    Use Gemini to intelligently extract structured data from a citizen
    complaint text (category, severity, sector, confidence).
    Always returns user_must_confirm=True for safety.
    """
    try:
        data = extract_complaint_with_gemini(request.text)
        return ComplaintResponse(
            **data,
            gemini_available=GEMINI_AVAILABLE,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/vision-analyze", response_model=VisionAnalyzeResponse)
def vision_analyze_json(request: VisionAnalyzeRequest):
    """
    Multimodal Vision Analysis endpoint (Base64 JSON payload).
    Analyzes citizen photo of urban damage (waterlogging, road damage, drain blockage, waste hotspot).
    Returns structured visual findings, water depth estimate, severity, and recommended municipal actions.
    """
    try:
        image_bytes = _strip_and_decode_base64(request.image_base64)
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image data provided.")

        result = analyze_image_with_gemini(
            image_bytes=image_bytes,
            mime_type=request.mime_type or "image/jpeg",
            user_notes=request.user_notes,
            sector_hint=request.sector_id,
        )
        return VisionAnalyzeResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("vision_analyze_json failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {exc}")


@router.post("/vision-upload", response_model=VisionAnalyzeResponse)
async def vision_analyze_upload(
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    sector: Optional[str] = Form(None),
):
    """
    Multimodal Vision Analysis endpoint (Multipart file upload).
    Accepts direct image file upload from citizen mobile browser or camera.
    """
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        mime_type = file.content_type or "image/jpeg"
        result = analyze_image_with_gemini(
            image_bytes=contents,
            mime_type=mime_type,
            user_notes=notes,
            sector_hint=sector,
        )
        return VisionAnalyzeResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("vision_analyze_upload failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"File upload vision analysis failed: {exc}")


@router.post("/report-from-vision", response_model=CivicReport)
def create_report_from_vision(payload: VisionReportConfirmRequest):
    """
    Confirmed Vision Intake:
    Takes citizen/operator confirmed multimodal vision findings,
    saves it directly as a C3T CivicReport event in the data store with source='vision_ai'.
    This automatically triggers downstream visibility across City Overview and Risk cascade!
    """
    try:
        # Standardize category for backend schema
        cat_lower = payload.confirmed_category.strip().lower()
        if "water" in cat_lower:
            backend_cat = "waterlogging_onset"
        elif "drain" in cat_lower or "clog" in cat_lower:
            backend_cat = "drainage_blockage"
        elif "waste" in cat_lower or "garbage" in cat_lower or "dump" in cat_lower:
            backend_cat = "waste_dumping"
        elif "debris" in cat_lower:
            backend_cat = "debris_hotspot"
        elif "road" in cat_lower or "pothole" in cat_lower or "disruption" in cat_lower or "traffic" in cat_lower:
            backend_cat = "traffic_slowdown"
        else:
            backend_cat = "other"

        # Standardize severity ("low", "medium", "high", "critical")
        sev_lower = payload.confirmed_severity.strip().lower()
        if sev_lower in ["moderate", "mod"]:
            sev_lower = "medium"
        elif sev_lower not in ["low", "medium", "high", "critical"]:
            sev_lower = "medium"

        # Format sector ID e.g. "sector-17"
        sec_clean = payload.confirmed_sector_id.lower().replace("sector", "").replace("-", "").strip()
        sector_id = f"sector-{sec_clean}" if sec_clean else "sector-17"

        location_desc = payload.description.strip()
        if len(location_desc) < 3:
            location_desc = f"{payload.confirmed_category} reported near {sector_id}"
        if payload.recommended_action:
            location_desc = f"{location_desc} [Dispatch: {payload.recommended_action}]"

        report_in = CivicReportCreate(
            sector_id=sector_id,
            category=backend_cat,
            severity=sev_lower,
            location_description=location_desc,
            source="vision_ai",
            confidence=payload.confidence or 0.90,
            media_url=payload.media_url,
        )

        created_report = store.add_event(report_in)
        return created_report

    except Exception as exc:
        logger.error("create_report_from_vision failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to create civic report from vision: {exc}")
