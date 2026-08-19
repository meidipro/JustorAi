from __future__ import annotations

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

TemporalMode = Literal[
    "CURRENT",
    "AS_OF_DATE",
    "HISTORICAL",
    "COMPARE_VERSIONS",
    "AMENDMENT_HISTORY",
]

AuthorityRole = Literal[
    "CONTROLLING",
    "SUPPORTING",
    "GENERAL",
    "BACKGROUND",
]

ClaimType = Literal[
    "legal_rule",
    "procedure",
    "deadline",
    "amendment",
    "case_law",
    "application",
    "conclusion",
    "general",
]

TrustTier = Literal[
    "PRIMARY_STATUTE",
    "LEGACY_CORPUS",
    "VERIFIED_JUDGMENT",
    "UNVERIFIED_REPORTER_CITATION",
    "UNVERIFIED",
    "ABSTAIN",
]

class ProvenanceMetadata(BaseModel):
    reviewer: str | None = None
    reviewed_at: date | None = None
    source_url: str | None = None
    source_hash: str | None = None
    provision_checked: bool = False
    amendment_checked: bool = False
    effective_date_checked: bool = False
    decision: str = "PENDING_AUDIT"

class CandidateAuthority(BaseModel):
    act: str
    sections: list[str] = Field(default_factory=list)
    role: AuthorityRole = "SUPPORTING"
    reason: str = ""

class LegalIssue(BaseModel):
    issue: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class LegalRoute(BaseModel):
    jurisdiction: str = "Bangladesh"
    legal_domain: str = ""
    issues: list[LegalIssue] = Field(default_factory=list)
    authorities: list[CandidateAuthority] = Field(default_factory=list)
    needs_case_law: bool = False
    temporal_mode: TemporalMode = "CURRENT"
    as_of_date: date | None = None

class EvidenceItem(BaseModel):
    evidence_id: str
    instrument_id: str = ""
    provision_id: str = ""
    version_id: str = ""
    act_name: str
    section_number: str = ""
    heading: str | None = None
    role: AuthorityRole = "SUPPORTING"
    legal_text: str = ""
    official_url: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    current_for_query_date: bool = True
    official_source_verified: bool = False
    exact_section_verified: bool = False
    version_verified: bool = False
    provenance: ProvenanceMetadata | None = None
    
    # Case law & Trust Hierarchy attributes
    item_type: Literal["statute", "case"] = "statute"
    case_title: str | None = None
    citation: str | None = None
    court: str | None = None
    year: int | None = None
    ratio_decidendi: str | None = None
    trust_tier: TrustTier = "UNVERIFIED"
    trust_badge: str | None = None

    def get_badge(self) -> str:
        if self.trust_badge:
            return self.trust_badge
        if self.trust_tier == "LEGACY_CORPUS":
            return "`UNREVIEWED CORPUS (LEGACY DB)`"
        if self.item_type == "statute" and self.trust_tier == "PRIMARY_STATUTE":
            if self.official_source_verified and self.version_verified and self.exact_section_verified:
                return "`PRIMARY SOURCE ✓` `SOURCE CHECKED ✓`"
            return "`OFFICIAL LEGISLATION (UNAUDITED VERSION)`"
        if self.item_type == "case":
            if self.trust_tier == "VERIFIED_JUDGMENT":
                return "`PRIMARY JUDGMENT ✓` `RATIO VERIFIED ✓`"
            return "`REPORTER CITATION AVAILABLE ⚠️` *(Primary judgment text pending verification)*"
        return "`UNVERIFIED`"

class EvidencePack(BaseModel):
    query: str
    persona: str
    as_of_date: date
    temporal_mode: TemporalMode
    issues: list[LegalIssue]
    authorities: list[EvidenceItem]

from pydantic import BaseModel, Field, field_validator, model_validator


class DraftParagraph(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_string_to_paragraph(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"text": data, "evidence_ids": []}
        return data


class DraftClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: "C-1")
    text: str
    claim_type: str = "general"
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("claim_type", mode="before")
    @classmethod
    def _normalize_claim_type(cls, v: Any) -> str:
        valid = {"legal_rule", "procedure", "deadline", "amendment", "case_law", "application", "conclusion", "general"}
        s = str(v).lower().strip()
        if s in valid:
            return s
        if "rule" in s or "doctrine" in s:
            return "legal_rule"
        if "case" in s or "precedent" in s:
            return "case_law"
        if "proc" in s:
            return "procedure"
        return "general"


class LegalAnswerDraft(BaseModel):
    issue: str = ""
    rules: list[DraftParagraph] = Field(default_factory=list)
    doctrine: list[DraftParagraph] = Field(default_factory=list)
    application: list[DraftParagraph] = Field(default_factory=list)
    conclusion: DraftParagraph = Field(default_factory=lambda: DraftParagraph(text=""))
    key_points: list[DraftParagraph] = Field(default_factory=list)
    claims: list[DraftClaim] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_draft_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        # Normalize conclusion if string
        if isinstance(data.get("conclusion"), str):
            data["conclusion"] = {"text": data["conclusion"], "evidence_ids": []}
            
        # Normalize paragraph lists if they contain strings
        for field in ["rules", "doctrine", "application", "key_points"]:
            items = data.get(field)
            if isinstance(items, list):
                norm_items = []
                for it in items:
                    if isinstance(it, str):
                        norm_items.append({"text": it, "evidence_ids": []})
                    else:
                        norm_items.append(it)
                data[field] = norm_items
        return data

class ValidationError(BaseModel):
    code: str
    severity: Literal["low", "medium", "high", "critical"]
    claim_id: str | None = None
    message: str

class ValidationResult(BaseModel):
    passed: bool
    errors: list[ValidationError] = Field(default_factory=list)
