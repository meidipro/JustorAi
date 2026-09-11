import pytest
from backend.reranker import legal_reranker
from backend.legal_models import EvidenceItem
from backend.ocr_service import legal_ocr_service
from backend.search_grounding import legal_search_grounding


def test_reranker_prioritizes_specific_section():
    item1 = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Transfer of Property Act, 1882",
        section_number="53",
        heading="Fraudulent transfer",
        legal_text="Every transfer of immoveable property made with intent to defeat creditors...",
        role="SUPPORTING",
        trust_tier="PRIMARY_STATUTE",
    )
    item2 = EvidenceItem(
        evidence_id="ACT-2",
        act_name="The Transfer of Property Act, 1882",
        section_number="53A",
        heading="Part performance",
        legal_text="Where any person contracts to transfer for consideration any immoveable property in writing and transferee takes possession...",
        role="SUPPORTING",
        trust_tier="PRIMARY_STATUTE",
    )
    item3 = EvidenceItem(
        evidence_id="ACT-3",
        act_name="The Transfer of Property Act, 1882",
        section_number="54",
        heading="Sale defined",
        legal_text="Sale is a transfer of ownership in exchange for a price paid or promised...",
        role="SUPPORTING",
        trust_tier="PRIMARY_STATUTE",
    )

    reranked = legal_reranker.rerank_evidence(
        "doctrine of part performance in property law", [item1, item2, item3]
    )
    assert len(reranked) == 3
    assert reranked[0].section_number == "53A"
    assert reranked[0].rerank_score is not None


def test_ocr_service_initialization():
    assert legal_ocr_service is not None
    assert legal_ocr_service.api_key is not None
    endpoint = legal_ocr_service._get_vertex_endpoint("gemini-2.5-flash")
    assert "aiplatform.googleapis.com" in endpoint
    assert "justorai-508321" in endpoint


def test_search_grounding_initialization():
    assert legal_search_grounding is not None
    assert legal_search_grounding.api_key is not None
    endpoint = legal_search_grounding._get_vertex_endpoint("gemini-2.5-flash")
    assert "aiplatform.googleapis.com" in endpoint
    assert "justorai-508321" in endpoint


def test_search_grounding_accepts_bilingual_and_roles():
    import inspect
    sig = inspect.signature(legal_search_grounding.query_live_legal_web)
    params = sig.parameters
    assert "query" in params
    assert "language" in params
    assert "user_role" in params

