import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ExtractedComplaint(BaseModel):
    category: str = Field(description="Incident category: drainage_blockage, surface_waterlogging, waste_hotspot, traffic_disruption, other")
    severity: str = Field(description="Incident severity: low, moderate, high")
    sector_id: Optional[str] = Field(default=None, description="Explicit sector ID (e.g. 'sector-17'). None if not explicitly stated.")
    location_description: str = Field(description="Extracted landmark or descriptive location note.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for NLP extraction.")
    user_must_confirm: bool = Field(default=True, description="Strict rule: Citizen/field agent must confirm every field.")
    notes: str = Field(description="Explanation of extraction basis and safety flags.")


CATEGORY_KEYWORDS = {
    "drainage_blockage": ["drain", "gully", "grate", "grating", "silt", "clogged", "choked", "blocked drain", "sewer"],
    "surface_waterlogging": ["waterlogging", "water logged", "pooling", "flooded", "standing water", "inundated", "submerged"],
    "waste_hotspot": ["garbage", "debris", "waste", "leaf litter", "plastic", "dump", "trash", "refuse"],
    "traffic_disruption": ["traffic", "jam", "gridlock", "bottleneck", "vehicle", "roundabout", "congestion", "slowed"],
}

SEVERITY_KEYWORDS = {
    "high": ["severe", "completely", "critical", "danger", "heavy", "impassable", "overflowing", "rapid", "deep", "emergency"],
    "moderate": ["moderate", "partial", "slow", "backing up", "medium", "half"],
    "low": ["minor", "slight", "small", "shallow", "manageable", "low"],
}

SECTOR_REGEX = re.compile(r"\bsector[- ]?([0-9]{1,2}|ia[12]?|industrial area)\b", re.IGNORECASE)


class ComplaintExtractor:
    """
    Rule-guided NLP complaint extractor with ethical guardrails.
    Adheres strictly to C3T specification:
    - User confirms every field.
    - NEVER guesses location if ambiguous or unstated.
    """

    def extract(self, text: str) -> ExtractedComplaint:
        lower_text = text.lower()

        # 1. Category identification
        matched_category = "other"
        highest_cat_matches = 0
        for cat, keywords in CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in lower_text)
            if matches > highest_cat_matches:
                highest_cat_matches = matches
                matched_category = cat

        # 2. Severity determination
        matched_severity = "moderate"  # default safe fallback
        for sev, keywords in SEVERITY_KEYWORDS.items():
            if any(kw in lower_text for kw in keywords):
                matched_severity = sev
                break

        # 3. Sector extraction (STRICT: Never guess location)
        sector_match = SECTOR_REGEX.search(lower_text)
        sector_id: Optional[str] = None
        sector_note = ""

        if sector_match:
            raw_sec = sector_match.group(1).lower()
            if "industrial" in raw_sec or raw_sec.startswith("ia"):
                sector_id = "sector-ia1"
            else:
                sector_num = int(raw_sec)
                sector_id = f"sector-{sector_num}"
            sector_note = f"Sector explicitly identified as '{sector_id}'."
        else:
            sector_id = None
            sector_note = "No explicit sector found. Strictly not guessed (user must select location)."

        # 4. Confidence scoring
        confidence = 0.50
        if highest_cat_matches > 0:
            confidence += 0.25
        if sector_id is not None:
            confidence += 0.20
        confidence = round(min(0.95, confidence), 2)

        return ExtractedComplaint(
            category=matched_category,
            severity=matched_severity,
            sector_id=sector_id,
            location_description=text.strip(),
            confidence=confidence,
            user_must_confirm=True,
            notes=f"{sector_note} All fields flagged for user verification."
        )


extractor = ComplaintExtractor()
