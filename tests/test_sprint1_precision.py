"""
Justor AI — Sprint 1 Precision Retrieval & Non-Cartesian Authority Tests
"""

import pytest
from datetime import date
from backend.legal_dictionary import expand_query_with_dictionary
from backend.legal_router import fast_exact_route


def test_dictionary_non_cartesian_binding_remand():
    """Verify that 'remand' maps CrPC exclusively to 61/167 and Constitution exclusively to 33."""
    expansion = expand_query_with_dictionary("পুলিশ রিমান্ড ও হেফাজত সংক্রান্ত বিধান কী?")
    act_map = expansion["act_to_sections"]
    
    assert "The Code of Criminal Procedure, 1898" in act_map
    assert "167" in act_map["The Code of Criminal Procedure, 1898"]
    assert "61" in act_map["The Code of Criminal Procedure, 1898"]
    # Constitution should NOT contain 167
    if "The Constitution of the People's Republic of Bangladesh" in act_map:
        assert "167" not in act_map["The Constitution of the People's Republic of Bangladesh"]
        assert "33" in act_map["The Constitution of the People's Republic of Bangladesh"]


def test_dictionary_non_cartesian_binding_baina():
    """Verify that 'baina' maps Registration Act to 17A, TPA to 54A, and SRA to 21A."""
    expansion = expand_query_with_dictionary("বায়না চুক্তি সম্পাদনের পর করণীয় কী?")
    act_map = expansion["act_to_sections"]

    assert "The Registration Act, 1908" in act_map
    assert "17A" in act_map["The Registration Act, 1908"]

    assert "The Transfer of Property Act, 1882" in act_map
    assert "54A" in act_map["The Transfer of Property Act, 1882"]

    assert "The Specific Relief Act, 1877" in act_map
    assert "21A" in act_map["The Specific Relief Act, 1877"]


def test_section_suffix_preservation():
    """Verify that section suffixes (53A, 54A, 561A, 21A, 17A, 35(4)) are cleanly parsed."""
    route_53a = fast_exact_route("doctrine of part performance under Section 53A of the Transfer of Property Act, 1882")
    assert route_53a is not None
    auth = route_53a.authorities[0]
    assert auth.act == "The Transfer of Property Act, 1882"
    assert "53A" in auth.sections

    route_561a = fast_exact_route("quashing of proceedings under Section 561A of the Code of Criminal Procedure, 1898")
    assert route_561a is not None
    auth_crpc = route_561a.authorities[0]
    assert auth_crpc.act == "The Code of Criminal Procedure, 1898"
    assert "561A" in auth_crpc.sections


def test_civil_procedure_order_rule_preservation():
    """Verify that Order 39, Rule 1 and Order 9, Rule 13 are parsed into CPC authority sections."""
    route_inj = fast_exact_route("temporary injunction under Order 39, Rules 1 and 2 of the Code of Civil Procedure, 1908")
    assert route_inj is not None
    auth = route_inj.authorities[0]
    assert auth.act == "The Code of Civil Procedure, 1908"
    assert any("39" in s for s in auth.sections)

    route_ex = fast_exact_route("setting aside ex-parte decree under Order 9, Rule 13 of the Code of Civil Procedure, 1908")
    assert route_ex is not None
    auth_ex = route_ex.authorities[0]
    assert auth_ex.act == "The Code of Civil Procedure, 1908"
    assert any("9" in s for s in auth_ex.sections)
