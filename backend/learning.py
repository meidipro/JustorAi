"""Bite-Size Learning APIs. Catalog is bundled; guest progress stays on the client."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/learning", tags=["Bite-Size Learning"])

CATALOG_PATH = Path(__file__).resolve().parent.parent / "src/v3/learning/contract-act-v1.json"
_catalog: Optional[dict[str, Any]] = None


def load_catalog() -> dict[str, Any]:
    global _catalog
    if _catalog is None:
        if not CATALOG_PATH.exists():
            raise HTTPException(503, "Learning catalog is not available.")
        _catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return _catalog


class CardProgressBody(BaseModel):
    state: str = Field(..., pattern="^(got_it|review_again)$")
    session_id: Optional[str] = None
    time_spent_ms: Optional[int] = None
    revealed: bool = True


class CardReportBody(BaseModel):
    issue_type: str = Field(..., min_length=3, max_length=80)
    note: Optional[str] = Field(None, max_length=2000)
    card_version: int = 1


class GoDeeperBody(BaseModel):
    subject_id: str
    section_id: str
    got_it_card_ids: list[str] = Field(default_factory=list)
    review_card_ids: list[str] = Field(default_factory=list)
    language: str = "en"


def _section(slug: str) -> dict[str, Any]:
    catalog = load_catalog()
    for section in catalog["sections"]:
        if section["slug"] == slug:
            return section
    raise HTTPException(404, "Topic not found.")


def _card(card_id: str) -> dict[str, Any]:
    catalog = load_catalog()
    for section in catalog["sections"]:
        for card in section["cards"]:
            if card["id"] == card_id:
                return card
    raise HTTPException(404, "Card not found.")


@router.get("/subjects")
async def list_subjects():
    catalog = load_catalog()
    subject = catalog["subject"]
    return {
        "subjects": [
            {
                **{k: subject[k] for k in ("id", "slug", "title_en", "title_bn", "description_en", "description_bn", "level_tag", "status")},
                "topic_count": len(catalog["sections"]),
                "card_count": sum(len(s["cards"]) for s in catalog["sections"]),
                "coming_soon": subject.get("coming_soon", []),
            }
        ]
    }


@router.get("/subjects/{slug}/sections")
async def list_sections(slug: str):
    catalog = load_catalog()
    if catalog["subject"]["slug"] != slug:
        raise HTTPException(404, "Subject not found.")
    return {
        "subject": catalog["subject"],
        "sections": [
            {**{k: s[k] for k in s if k != "cards"}, "card_count": len(s["cards"])}
            for s in catalog["sections"]
        ],
    }


@router.get("/sections/{slug}")
async def get_section(slug: str):
    return _section(slug)


@router.put("/cards/{card_id}/progress")
async def record_progress(card_id: str, body: CardProgressBody, x_guest_id: Optional[str] = Header(None)):
    _card(card_id)
    return {"ok": True, "card_id": card_id, "state": body.state, "guest": bool(x_guest_id)}


@router.post("/cards/{card_id}/report")
async def report_card(card_id: str, body: CardReportBody):
    card = _card(card_id)
    logger.info("learning report card=%s type=%s version=%s", card_id, body.issue_type, body.card_version)
    return {"ok": True, "card_id": card["id"]}


@router.post("/go-deeper")
async def go_deeper(body: GoDeeperBody):
    section = _section(body.section_id)
    cards = {c["id"]: c for c in section["cards"]}
    bn = body.language == "bn"

    def titles(ids: list[str]) -> list[str]:
        lines = []
        for cid in ids:
            card = cards.get(cid)
            if not card:
                continue
            hook = card["hook_bn"] if bn else card["hook_en"]
            lines.append(f"- {hook} ({card['act_name']} {card['section_label']})")
        return lines or ["- (none)"]

    topic = section["title_bn"] if bn else section["title_en"]
    prompt = (
        f'I just completed “{topic}” in Contract Act 1872.\n\n'
        "I marked these as understood:\n"
        + "\n".join(titles(body.got_it_card_ids))
        + "\n\nI marked these for review:\n"
        + "\n".join(titles(body.review_card_ids))
        + "\n\nTeach the review concepts more deeply using Bangladesh law. "
        "Start simply, then show the exact statutory provisions and practical examples. "
        "Ask me one short check-for-understanding question at the end. "
        "Do not rely on the learning-card wording as the legal source — retrieve current statutory text."
    )
    return {"query": prompt, "section_id": body.section_id, "subject_id": body.subject_id}
