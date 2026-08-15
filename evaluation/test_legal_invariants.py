from backend.legal_validation import validate_quote, extract_numeric_tokens
from backend.legal_normalize import normalize_section, split_section_reference, normalize_act_alias
from backend.legal_deadlines import calculate_deadline, evaluate_deadline
from datetime import date

def test_fake_quote_rejected():
    source = "The application shall be made within thirty days."
    fake = "The application may be made within sixty days."
    assert not validate_quote(fake, source)


def test_exact_quote_passes():
    source = "The application shall be made within thirty days."
    quote = "within thirty days"
    assert validate_quote(quote, source)


def test_section_normalization():
    assert normalize_section("Section 17A") == "17A"
    assert normalize_section("sec. 54A") == "54A"
    assert normalize_section("s. 115") == "115"
    assert normalize_section("  Order 39  ") == "ORDER39"


def test_section_splitting():
    root, parts = split_section_reference("17A(2)")
    assert root == "17A"
    assert parts == ["2"]

    root, parts = split_section_reference("55(4)(b)")
    assert root == "55"
    assert parts == ["4", "B"]


def test_act_alias_normalization():
    assert normalize_act_alias("The Registration Act, 1908") == "registrationact1908"
    assert normalize_act_alias("Transfer of Property Act, 1882") == "transferofpropertyact1882"


def test_numeric_token_extraction():
    tokens = extract_numeric_tokens("The application must be filed within thirty days.")
    assert "30" in tokens

    tokens_num = extract_numeric_tokens("Penalty of 500 taka within 60 days.")
    assert "500" in tokens_num
    assert "60" in tokens_num


def test_deadlines():
    start = date(2026, 1, 1)
    target = calculate_deadline(start, 30, "days")
    assert target == date(2026, 1, 31)

    eval_res = evaluate_deadline(start, date(2026, 1, 15), 30, "days")
    assert eval_res["within_period"] is True

    eval_late = evaluate_deadline(start, date(2026, 2, 10), 30, "days")
    assert eval_late["within_period"] is False
    assert eval_late["days_after_deadline"] == 10
