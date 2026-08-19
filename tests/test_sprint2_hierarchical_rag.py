"""
Justor AI — Sprint 2 Hierarchical RAG & Repeal Graph Tests
"""

import pytest
from datetime import date
from backend.hierarchical_retriever import HierarchicalRetriever, REPEAL_REPLACEMENT_GRAPH


def test_repeal_graph_family_courts_act_2023():
    """Verify that Family Courts Ordinance 1985 resolves to Family Courts Act 2023 (Act 26 of 2023)."""
    retriever = HierarchicalRetriever(repository=None, embed_fn=None)
    res = retriever.resolve_repeal_replacement("The Family Courts Ordinance, 1985", date(2026, 8, 19))
    
    assert res["is_repealed"] is True
    assert res["controlling_act"] == "Family Courts Act, 2023"
    assert res["act_number"] == "Act No. 26 of 2023"
    assert "repealed and replaced by the Family Courts Act, 2023" in res["warning"]


def test_repeal_graph_income_tax_act_2023():
    """Verify that Income-tax Ordinance 1984 resolves to Income Tax Act 2023 (Act 12 of 2023)."""
    retriever = HierarchicalRetriever(repository=None, embed_fn=None)
    res = retriever.resolve_repeal_replacement("The Income-tax Ordinance, 1984", date(2026, 8, 19))
    
    assert res["is_repealed"] is True
    assert res["controlling_act"] == "Income Tax Act, 2023"
    assert res["act_number"] == "Act No. 12 of 2023"
    assert "repealed and replaced by the Income Tax Act, 2023" in res["warning"]


def test_historical_query_preserves_pre_repeal_statute():
    """Verify that historical queries prior to repeal date do not trigger repeal substitution."""
    retriever = HierarchicalRetriever(repository=None, embed_fn=None)
    historical_date = date(2020, 1, 1)
    res = retriever.resolve_repeal_replacement("The Family Courts Ordinance, 1985", historical_date)
    
    assert res["is_repealed"] is False
    assert res["controlling_act"] == "The Family Courts Ordinance, 1985"
    assert res["warning"] is None
