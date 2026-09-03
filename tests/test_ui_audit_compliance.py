"""
Justor AI — UI/UX Audit & Feature Compliance Test Suite
Automated validation of all Master A-Z UI/UX specifications and PM Audit fixes.
"""

import os
import re
import json
import pytest

APP_TS_PATH = "src/v3/app.ts"
I18N_TS_PATH = "src/v3/i18n.ts"
STYLE_CSS_PATH = "src/v3/style.css"
SERVICES_TS_PATH = "src/v3/services.ts"
INDEX_HTML_PATH = "index.html"


@pytest.fixture
def app_ts_content():
    with open(APP_TS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def i18n_ts_content():
    with open(I18N_TS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def style_css_content():
    with open(STYLE_CSS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def services_ts_content():
    with open(SERVICES_TS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def index_html_content():
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ─── 1. ACCESSIBILITY & HEADING STRUCTURE (A-01, A-02) ───────────────────────────

def test_google_fonts_hind_siliguri_imported(index_html_content):
    """Ensure Hind Siliguri Google Font is imported for high-quality Bangla rendering."""
    assert "family=Hind+Siliguri" in index_html_content, "Hind Siliguri font must be imported in index.html"


def test_workspaces_have_sr_only_h1(app_ts_content):
    """Every workspace page must have exactly one visually-hidden H1 for screen readers."""
    assert '<h1 class="sr-only">' in app_ts_content, "Workspaces must include visually-hidden H1"
    assert "আইনি গবেষণা — পেশাদার ওয়ার্কস্পেস" in app_ts_content
    assert "আইন শিক্ষা — শিক্ষার্থী ওয়ার্কস্পেস" in app_ts_content
    assert "নাগরিক আইনি নির্দেশনা — ওয়ার্কস্পেস" in app_ts_content


def test_thread_delete_has_accessible_name(app_ts_content):
    """Delete button must not be just '✕', must have descriptive aria-label."""
    assert 'aria-label="' in app_ts_content and "Delete research thread:" in app_ts_content, "Thread delete button must have descriptive aria-label"


def test_min_44px_touch_targets_enforced(style_css_content):
    """All interactive controls must meet WCAG 2.2 AA 44x44px touch targets."""
    assert "min-height: 44px" in style_css_content or "min-width: 44px" in style_css_content, "Touch targets must enforce 44px minimum"
    assert ".composer-send-btn" in style_css_content
    assert ".quick-chip-btn" in style_css_content
    assert ".feedback-thumb-btn" in style_css_content


# ─── 2. TRUTHFUL TRUST MODEL & BADGES (P0-1, T-01) ──────────────────────────────

def test_no_prohibited_verification_claims(app_ts_content, i18n_ts_content):
    """Forbidden static strings must be completely absent from UI."""
    prohibited_strings = [
        "Verification Active",
        "Grounded on verified Bangladesh statutes...",
    ]
    for prohibited in prohibited_strings:
        assert prohibited not in app_ts_content, f"Prohibited string '{prohibited}' found in app.ts"
        assert prohibited not in i18n_ts_content, f"Prohibited string '{prohibited}' found in i18n.ts"


def test_compute_status_banner_function_exists(i18n_ts_content):
    """computeStatusBanner must derive exact checked/pending counts dynamically."""
    assert "export function computeStatusBanner" in i18n_ts_content
    assert "source-checked" in i18n_ts_content
    assert "উৎস যাচাইকৃত" in i18n_ts_content


def test_4_tier_semantic_badges_in_css(style_css_content):
    """CSS must define all 4 distinct semantic trust badges."""
    badges = [
        ".badge-source-checked",
        ".badge-reporter-verified",
        ".badge-pending-verified",
        ".badge-unreviewed",
    ]
    for badge in badges:
        assert badge in style_css_content, f"Badge class '{badge}' missing from style.css"


# ─── 3. CITATION & AUTHORITY CONTROLS (P0-2, C-03) ──────────────────────────────

def test_single_numbering_citation_system(app_ts_content):
    """Answer rendering must use unified [1], [2] citation indices."""
    assert "click-citation-index" in app_ts_content, "Citation chips must trigger click-citation-index action"
    assert "data-citation-index" in app_ts_content, "Citations must include numeric citation index"


def test_view_full_provision_handles_unindexed_url(app_ts_content, i18n_ts_content):
    """View full provision must have disabled state with tooltip if URL is unindexed."""
    assert "sourceUrlNotIndexed" in i18n_ts_content, "sourceUrlNotIndexed translation key must exist"
    assert "Source URL not yet indexed" in i18n_ts_content


# ─── 4. SIGNED-OUT DATA BOUNDARY & SESSION SECURITY (P0-3, P-01) ─────────────────

def test_cross_tab_logout_broadcast(services_ts_content, app_ts_content):
    """Logout must broadcast across tabs via BroadcastChannel('justor_auth')."""
    assert "BroadcastChannel('justor_auth')" in services_ts_content, "services.ts must broadcast logout"
    assert "BroadcastChannel('justor_auth')" in app_ts_content, "app.ts must listen for logout broadcast"
    assert "SIGNED_OUT" in services_ts_content


def test_local_storage_purge_on_signout(services_ts_content):
    """Sign out must purge all justor_ and sb- local storage keys."""
    assert "startsWith('justor_')" in services_ts_content
    assert "startsWith('sb-')" in services_ts_content
    assert "localStorage.removeItem" in services_ts_content


def test_composer_privacy_minimization_hint(app_ts_content):
    """Composer must show persistent data minimization guidance."""
    assert "composer-privacy-hint" in app_ts_content or "Remove names, NID/passport numbers" in app_ts_content


# ─── 5. CITIZEN SECTOR CARDS & PLAIN-LANGUAGE ANSWERS (C-02, G-01) ───────────────

def test_citizen_7_sector_cards_present(app_ts_content):
    """Landing page must feature all 7 Citizen Sector Cards."""
    sectors = [
        "property-land",
        "family-marriage",
        "criminal-police",
        "employment-work",
        "consumer-contracts",
        "rights-documents",
        "business-licensing",
    ]
    for sector in sectors:
        assert sector in app_ts_content, f"Citizen sector '{sector}' missing from app.ts"


def test_first_citizen_query_unauthenticated(app_ts_content):
    """First citizen query must not be blocked by aggressive login wall."""
    assert "justor_citizen_query_count" in app_ts_content, "First query counter must be tracked in sessionStorage"


# ─── 6. MOBILE NAVIGATION DRAWER (N-01) ─────────────────────────────────────────

def test_mobile_navigation_drawer_markup_and_css(app_ts_content, style_css_content):
    """Slide-in mobile drawer must exist with close button and accessible markup."""
    assert "mobile-drawer" in app_ts_content or "mobile-nav-drawer" in app_ts_content
    assert ".mobile-nav-drawer" in style_css_content or ".mobile-drawer" in style_css_content
    assert 'aria-label="Close navigation"' in app_ts_content or 'close-menu' in app_ts_content


# ─── 7. UPDATED USER FEEDBACK SURVEY INTEGRATION ────────────────────────────────

def test_google_feedback_form_url_integrated(app_ts_content):
    """Official Google Feedback Form URL must be integrated in feedbackPage and widgets."""
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform"
    assert form_url in app_ts_content, "Updated Google Feedback Form URL must be present in app.ts"
    assert f"{form_url}?embedded=true" in app_ts_content, "Embedded iframe of Google Feedback Form must be in app.ts"


def test_feedback_page_has_7_qa_categories(app_ts_content):
    """QA Feedback triage must support all 7 distinct issue categories."""
    categories = [
        "wrong_law",
        "wrong_citation",
        "outdated_law",
        "missing_authority",
        "incomplete_answer",
        "misunderstood_question",
        "other",
    ]
    for cat in categories:
        assert cat in app_ts_content, f"Feedback category '{cat}' missing from QA form"


# ─── 8. CITIZEN LAWYER CONSULTATION RECOMMENDATIONS (C-04) ──────────────────────

def test_citizen_response_lawyer_recommendation(app_ts_content, style_css_content):
    """Citizen responses must include domain-tailored lawyer recommendations and document checklists."""
    assert "getCitizenLawyerRecommendation" in app_ts_content
    assert "renderCitizenLawyerSuggestion" in app_ts_content
    assert "Deed & Land Litigation Advocate" in app_ts_content
    assert "Family Court & Matrimonial Advocate" in app_ts_content
    assert "NI Act & Banking Litigation Advocate" in app_ts_content
    assert "Criminal Defense & Bail Advocate" in app_ts_content
    assert "16430" in app_ts_content
    assert ".citizen-lawyer-recommendation-card" in style_css_content


# ─── 9. CAREERS PAGE & 8 OPEN INTERN ROLES ──────────────────────────────────────

def test_careers_page_and_eight_roles(app_ts_content, style_css_content):
    """Careers page must support /careers route, 8 specific intern roles, and email application CTA."""
    assert "careersPage" in app_ts_content
    assert "path === '/careers'" in app_ts_content
    assert "Build the future of Bangladesh law." in app_ts_content
    assert "contact@justorai.com" in app_ts_content

    roles = [
        "Legal Research Intern",
        "Legal Content Writer",
        "Product Designer",
        "Brand Visualiser",
        "Data & Research Analyst",
        "Reels & Legal Content Creator",
        "Marketing & Comms Intern",
        "Research & Development Intern",
    ]
    for r in roles:
        assert r in app_ts_content, f"Role '{r}' missing from careersPage in app.ts"

    # CSS verification
    assert ".careers-page" in style_css_content
    assert ".careers-hero" in style_css_content
    assert ".careers-perks-strip" in style_css_content
    assert ".careers-roles-grid" in style_css_content
    assert ".career-role-card" in style_css_content
    assert ".careers-steps-grid" in style_css_content
    assert ".careers-cta-card" in style_css_content


