"""
Justor AI — Sprint 3 Bangla Legal Intelligence Tests
"""

import pytest
from backend.legal_normalize import (
    normalize_bengali_text,
    detect_language,
    normalize_section,
    normalize_act_alias,
)
from backend.legal_dictionary import expand_query_with_dictionary


def test_bengali_digit_normalization():
    """Verify that Bengali numerals and section suffixes convert properly."""
    raw = "ধারা ১৭ক অনুযায়ী বায়না দলিলের সময়সীমা কত?"
    norm = normalize_bengali_text(raw)
    
    assert "Section 17A" in norm
    assert "১৭" not in norm


def test_bengali_article_and_order_normalization():
    """Verify that Bengali Article and Order prefixes standardize."""
    art_text = "অনুচ্ছেদ ১০২ এর অধীন রিট"
    assert "Article 102" in normalize_bengali_text(art_text)

    ord_text = "আদেশ ৩৯ বিধি ১ অনুযায়ী নিষেধাজ্ঞা"
    norm_ord = normalize_bengali_text(ord_text)
    assert "Order 39" in norm_ord
    assert "Rule 1" in norm_ord


def test_orthographic_spelling_variants():
    """Verify normalization of orthographic spelling pairs (য় vs য়, ী vs ি)."""
    assert normalize_bengali_text("বায়না") == "বায়না"
    assert normalize_bengali_text("দেওয়ানী") == "দেওয়ানী"
    assert normalize_bengali_text("ফৌজদারী") == "ফৌজদারি"
    assert normalize_bengali_text("তামাদী") == "তামাদি"
    assert normalize_bengali_text("নামজারী") == "নামজারি"


def test_language_detection():
    """Verify language detection across BN, EN, and MIXED scripts."""
    assert detect_language("আমার জমির নামজারি করতে কি লাগবে?") == "BN"
    assert detect_language("What is the limitation period for filing a suit under Section 9?") == "EN"
    assert detect_language("section 17A onujayi baina registration er time koto?") == "MIXED"
    assert detect_language("Article 102 এর অধীন writ petition এর নিয়ম কী?") == "MIXED"


def test_banglish_dictionary_expansion():
    """Verify concept extraction on Banglish / transliterated inputs."""
    res = expand_query_with_dictionary("baina korar pore registration er deadline koto?")
    assert "The Registration Act, 1908" in res["candidate_acts"]
    assert "17A" in res["act_to_sections"]["The Registration Act, 1908"]
