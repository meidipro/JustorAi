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
    instrument_id: str
    provision_id: str
    version_id: str
    act_name: str
    section_number: str
    heading: str | None = None
    role: AuthorityRole = "SUPPORTING"
    legal_text: str
    official_url: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    current_for_query_date: bool = True
    official_source_verified: bool = False
    exact_section_verified: bool = False
    version_verified: bool = False

class EvidencePack(BaseModel):
    query: str
    persona: str
    as_of_date: date
    temporal_mode: TemporalMode
    issues: list[LegalIssue]
    authorities: list[EvidenceItem]

class DraftClaim(BaseModel):
    claim_id: str
    text: str
    claim_type: ClaimType
    evidence_ids: list[str] = Field(default_factory=list)

class DraftParagraph(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)

class LegalAnswerDraft(BaseModel):
    issue: str
    rules: list[DraftParagraph] = Field(default_factory=list)
    doctrine: list[DraftParagraph] = Field(default_factory=list)
    application: list[DraftParagraph] = Field(default_factory=list)
    conclusion: DraftParagraph
    key_points: list[DraftParagraph] = Field(default_factory=list)
    claims: list[DraftClaim] = Field(default_factory=list)

class ValidationError(BaseModel):
    code: str
    severity: Literal["low", "medium", "high", "critical"]
    claim_id: str | None = None
    message: str

class ValidationResult(BaseModel):
    passed: bool
    errors: list[ValidationError] = Field(default_factory=list)
