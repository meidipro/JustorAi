-- Bite-Size Learning (Contract Act V1). Apply on Project A (laws + auth).
-- Guest progress is device-local; signed-in rows use user_id.

CREATE TABLE IF NOT EXISTS learning_subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title_en TEXT NOT NULL,
    title_bn TEXT NOT NULL,
    description_en TEXT,
    description_bn TEXT,
    level_tag TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS learning_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES learning_subjects(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    title_en TEXT NOT NULL,
    title_bn TEXT NOT NULL,
    description_en TEXT,
    description_bn TEXT,
    estimated_minutes INT DEFAULT 5,
    sort_order INT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    UNIQUE (subject_id, slug)
);

CREATE TABLE IF NOT EXISTS learning_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID NOT NULL REFERENCES learning_sections(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    sort_order INT NOT NULL,
    card_type TEXT NOT NULL,
    label TEXT,
    hook_en TEXT NOT NULL,
    hook_bn TEXT NOT NULL,
    question_en TEXT NOT NULL,
    question_bn TEXT NOT NULL,
    answer_en TEXT NOT NULL,
    answer_bn TEXT NOT NULL,
    explanation_en TEXT NOT NULL,
    explanation_bn TEXT NOT NULL,
    key_principle_en TEXT,
    key_principle_bn TEXT NOT NULL,
    act_name TEXT NOT NULL,
    section_label TEXT NOT NULL,
    authority_type TEXT NOT NULL DEFAULT 'statute',
    authority_note TEXT,
    asset_type TEXT NOT NULL DEFAULT 'image',
    asset_url TEXT,
    poster_url TEXT,
    accent_color TEXT DEFAULT '#1E38C8',
    review_status TEXT NOT NULL DEFAULT 'pending',
    content_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (section_id, sort_order),
    UNIQUE (section_id, slug)
);

CREATE TABLE IF NOT EXISTS user_card_progress (
    user_id UUID,
    guest_id TEXT,
    card_id UUID NOT NULL REFERENCES learning_cards(id) ON DELETE CASCADE,
    state TEXT NOT NULL CHECK (state IN ('got_it', 'review_again')),
    seen_count INT NOT NULL DEFAULT 1,
    reveal_count INT NOT NULL DEFAULT 1,
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT user_card_progress_actor CHECK (
        (user_id IS NOT NULL AND guest_id IS NULL)
        OR (user_id IS NULL AND guest_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_learning_progress_user
    ON user_card_progress (user_id, card_id) WHERE user_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_learning_progress_guest
    ON user_card_progress (guest_id, card_id) WHERE guest_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    guest_id TEXT,
    section_id UUID NOT NULL REFERENCES learning_sections(id),
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    cards_seen INT DEFAULT 0,
    got_it_count INT DEFAULT 0,
    review_count INT DEFAULT 0,
    go_deeper_clicked BOOLEAN DEFAULT false,
    language TEXT DEFAULT 'en'
);

CREATE TABLE IF NOT EXISTS learning_card_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES learning_cards(id),
    user_id UUID,
    guest_id TEXT,
    issue_type TEXT NOT NULL,
    note TEXT,
    card_version INT NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE learning_subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_card_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_card_reports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learning_subjects_read ON learning_subjects;
CREATE POLICY learning_subjects_read ON learning_subjects
    FOR SELECT USING (status = 'published');

DROP POLICY IF EXISTS learning_sections_read ON learning_sections;
CREATE POLICY learning_sections_read ON learning_sections
    FOR SELECT USING (status = 'published');

DROP POLICY IF EXISTS learning_cards_read ON learning_cards;
CREATE POLICY learning_cards_read ON learning_cards
    FOR SELECT USING (review_status = 'approved');

DROP POLICY IF EXISTS learning_progress_own ON user_card_progress;
CREATE POLICY learning_progress_own ON user_card_progress
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS learning_sessions_own ON learning_sessions;
CREATE POLICY learning_sessions_own ON learning_sessions
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS learning_reports_own ON learning_card_reports;
CREATE POLICY learning_reports_own ON learning_card_reports
    FOR INSERT WITH CHECK (user_id IS NULL OR user_id = auth.uid());
