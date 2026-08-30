# Justor AI UI/UX and Chat Product Audit

**PM handoff report**  
**Audit date:** 28 August 2026  
**Product reviewed:** https://justorai.com  
**Primary audience:** Product Manager, founder, design and engineering leads  
**Status:** Live-browser evidence; no production changes made

> **Executive decision:** Pause cosmetic expansion until the trust model, citation controls and signed-out data boundary are corrected. The visual system is credible, but the current interface makes stronger verification claims than the visible evidence supports.

## Executive summary

Justor AI already has a stronger visual foundation than many early legal-AI products. The role-first homepage is clear, the design system is consistent, the student entry experience is focused, the site behaves responsively without horizontal overflow at the tested widths, and the product openly describes itself as a controlled beta. These are useful foundations.

The weakest point is the product's core promise: “authority beside the answer.” The live interface displays **Verification Active** and **Grounded on verified Bangladesh statutes & Supreme Court records**, while the same answer labels its material **UNREVIEWED CORPUS (LEGACY DB)**, shows the controlling authority as **PENDING VERIFICATION**, and provides source controls that did not open or update a source during testing. This is not a copy problem. It is a product-state and trust-contract problem.

The next serious concern is privacy and session handling. A professional workspace displayed prior research history and full answer content while the top-right control showed **Sign In**. This may be locally cached rather than server-exposed, but the user-visible result is still unsafe: a signed-out screen can reveal previous legal research to the next person using the device.

The third issue is product readiness. The public Legal Library returned zero published records, Citizen Guides showed zero published guides, and Legal Updates returned no records. Honest empty states are better than fabricated content, but the public promise currently exceeds the visible public utility.

### Recommended priority order

1. **Trust and privacy gate:** Make verification labels truthful, make every source action work, and block or clear private history when signed out.
2. **Core chat usability:** Put the usable answer before the process explanation; simplify citation systems; add explicit privacy guidance at the composer.
3. **Role differentiation:** Keep the professional workspace dense, make student output teach, and redesign citizen output around practical steps rather than professional research prose.
4. **Navigation and localization:** Repair the mobile menu, complete Bangla localization, and enforce consistent authentication behavior.
5. **Public usefulness and measurement:** Publish a small verified legal corpus, instrument the activation-to-verification funnel, and then optimize conversion and visual polish.

## Audit scope and evidence

### Surfaces reviewed

- Homepage and role-selection journey
- Start, sign-in and switch-experience flows
- Legal Professional, Law Student and Citizen workspaces
- Existing chat answers, citations, source panel, research history, feedback and composer
- Legal Library, Citizen Guides and Legal Updates
- Trust, About, Contact and feedback pages
- Privacy, Terms and Disclaimer pages
- English and Bangla routes
- Desktop, tablet and mobile responsive behavior
- Keyboard focus order and key accessibility signals

### Tested viewport widths

- 320 px and 390 px mobile
- 768 px tablet
- 1024 px and 1440 px desktop

No horizontal overflow was found on the homepage or professional workspace at these widths. This is a confirmed strength.

### Method and limitations

- Findings are based on direct interaction with the live site in Chrome on 28 August 2026.
- Existing chat content was inspected. No new legal question was submitted, so this audit does not score model accuracy, response latency or streaming behavior.
- Core Web Vitals and production analytics were not available in the browser session. Performance recommendations are therefore requirements, not claims about current metrics.
- The audit is a product and UX review, not a legal opinion or penetration test.
- Severity reflects user harm, trust risk and product blockage, not implementation difficulty.

## PM scorecard

The scores below are expert heuristic judgments, not analytics or moderated-user-test results.

| Area | Score | What drives the score |
|---|---:|---|
| Visual design and consistency | 8/10 | Strong hierarchy, restrained palette, coherent typography and role cards |
| Information architecture | 7/10 | Clear role entry and public nav; mobile menu defect and duplicate entry routes reduce confidence |
| Responsive design | 8/10 | No horizontal overflow at tested widths; several touch targets remain below 44 px |
| Chat usability | 5/10 | Useful structure and quick actions, but long process-first answers and ineffective controls slow users |
| Trust and citation UX | 2/10 | Verification claims contradict visible source states; source actions failed |
| Role differentiation | 5/10 | Student landing is distinct; professional and citizen answer shells are too similar |
| Bangla localization | 4/10 | Routes and some shell copy translate, but core answer, proof and footer content remain English |
| Accessibility readiness | 6/10 | Skip link and visible keyboard focus are present; active chat lacks an H1 and some controls are too small or weakly named |
| Public content readiness | 3/10 | Library, guides and updates are present but return no public records |
| Privacy/session safety | 2/10 | Prior history and answers remained visible in a signed-out presentation state |
| Overall PM readiness | 5/10 | Strong beta design, but trust and privacy issues block broader promotion |

## What is working and should be preserved

### 1. Role-first positioning

The homepage immediately asks how the user will use Justor and presents the intended order: Legal Professional, Law Student, then Citizen. This reduces generic-AI ambiguity and should remain the primary entry model.

### 2. A coherent visual system

The dark hero, blue accent, restrained borders, wide spacing and serif/sans-serif contrast create a credible legal-research tone. Avoid a redesign for its own sake. Correct the product-state problems inside this system.

### 3. Honest beta and empty-state language

The site uses **Controlled beta**, states that unpublished guides remain private, and describes uncertainty on the Trust page. These are sound instincts. The next step is making the live workspace obey the same rules.

### 4. Strong responsive foundations

At 320, 390, 768, 1024 and 1440 px, the tested pages did not overflow horizontally. Role cards remained inside the viewport, mobile navigation appeared in the workspace, and the main composer remained usable.

### 5. Keyboard basics

The homepage exposes a Skip to content link as the first keyboard stop. Primary navigation, language, authentication and role cards had visible focus styling in the tested sequence.

### 6. Student entry is the clearest role experience

The student landing groups recognizable tasks such as explaining a statute, briefing a case, comparing cases, quizzes and practice problems. It gives the user a mental model before asking for free-form input.

![Homepage role-first visual hierarchy](justor-ai-audit-assets/01-home-desktop.png)

*Figure 1. The homepage is visually coherent and puts the role decision first.*

## Highest-priority findings

### P0-1. Verification claims contradict the visible evidence

**Observed**

- The research card showed **Verification Active**.
- The composer footer stated **Grounded on verified Bangladesh statutes & Supreme Court records**.
- The answer's authority list labeled multiple records **UNREVIEWED CORPUS (LEGACY DB)**.
- Reported judgments stated that primary judgment text was pending verification.
- The controlling-authority panel showed **PENDING VERIFICATION**.

**Why this fails**

The interface encourages reliance precisely where it should encourage caution. A user cannot tell whether “verified” means the source exists, the text is current, the proposition matches the text, or a lawyer reviewed the output. For a legal product, ambiguous verification language is a core product risk.

**Required enhancement**

Replace the single generic verification message with a query-level status summary derived from source data. Example: **7 authorities: 3 source-checked, 4 pending verification, no human legal review**. If any material proposition relies on pending or unreviewed material, do not show a global verified statement.

**Terms the PM must approve before implementation**

- **Material proposition:** a statement that could change the user's understanding of a legal right, duty, deadline, procedure, likely outcome or recommended action if it is wrong.
- **Material citation:** a source presented as support for a material proposition.
- **Source-checked:** the official or approved canonical text was opened, the exact section/excerpt was matched, and the source URL plus version/effective date were recorded when available. This does not mean a lawyer approved the answer.
- **Qualified legal reviewer:** a Bangladesh legal professional authorized by Justor to review the exact response or content version; reviewer identity, scope and date must be recorded.

**Acceptance criteria**

- A response cannot display **Verified**, **Verification Active** or **Grounded on verified** unless every material citation satisfies the defined source-checked contract.
- Pending, unavailable and human-reviewed statuses are visually and textually distinct.
- The status is computed from response data, not hard-coded frontend copy.
- Automated tests fail when the query-level label and individual source states disagree.

### P0-2. Citation and source controls do not deliver the promised action

**Observed**

- Selecting citation controls in the workspace did not populate the controlling-authority panel with the cited act or section.
- The panel remained a generic **Source / PENDING VERIFICATION** state.
- **View full provision** was enabled but caused no navigation, new tab, dialog or visible change.
- On the homepage product-proof demo, selecting another source did not update the displayed authority.

**Why this fails**

The homepage explicitly says citations are controls, not decoration. When those controls do nothing, the proof section becomes evidence against the product promise.

**Required enhancement**

Make each citation chip select a real source object. The side panel must show title, section, source status, source excerpt, official or canonical URL, version date and the proposition it supports.

**Acceptance criteria**

- Clicking or keyboard-activating citation N updates the source panel within 300 ms after data is available.
- The active citation is visually identified and focus remains predictable.
- **View full provision** is disabled with an explanation when no URL or provision is available.
- If enabled, it opens the exact source/provision and records a source-view event.
- The homepage demo uses real working interactions or is replaced by a static labeled illustration.

### P0-3. Signed-out presentation can expose prior legal research

**Observed**

The professional workspace displayed a **Sign In** action while recent research titles, previous questions and full answers remained visible.

**What is known vs unknown**

- Known: the user-visible signed-out state contained prior research content.
- Unknown: whether the data came from server access, browser cache, local storage or in-memory state.
- This audit does not claim a server authorization bypass. It does identify a screen-privacy and session-boundary failure.

**Required enhancement**

Apply an authentication gate before private workspace data renders. On sign-out or failed session validation, immediately remove prior query content, reset client caches and show a neutral signed-out state.

**Acceptance criteria**

- Protected workspace history and answers never render when the session is unauthenticated.
- Sign-out clears query/history caches and any sensitive local storage before the signed-out screen appears.
- Cross-tab sign-out removes private content in every open tab.
- Back navigation after sign-out cannot reveal cached content.
- QA covers shared-device and browser-restore scenarios.
- A clean browser profile receives no private history from protected endpoints before authentication.
- Expired-token, revoked-session and anonymous requests are rejected server-side and render no protected content.
- The team documents whether anonymous/local history is allowed; if allowed, it is visibly labeled, device-local, user-clearable and never presented as authenticated history.

![Signed-out professional workspace showing prior research](justor-ai-audit-assets/02-professional-desktop.png)

*Figure 2. The top-right action says Sign In while prior research remains visible. Treat as a P0 privacy boundary until root cause is proven safe.*

## End-to-end experience review

### Homepage and positioning

**Strengths**

- Clear headline and role decision.
- Legal Professional is correctly placed first.
- Trust, incubation and controlled-beta signals support credibility.
- Desktop and mobile layouts are visually disciplined.

**Weaknesses**

- The product-proof citation demo is non-functional.
- The homepage describes verification more confidently than the live workspace supports.
- **Human Legal Reviewed** appears as a trust-method category without an immediately visible example of what content actually holds that status.
- Early access routes through email, which adds friction and weakens measurable conversion.

**Recommendation**

Keep the structure, but change the proof section into a real, self-contained verified example. Show the proposition, exact authority, verification state, checked date and a working source action. Replace the mailto-only early-access CTA with a measurable form or waitlist after privacy requirements are defined.

### Start and authentication

**Strengths**

- Google sign-in is simple.
- Role choice before sign-in gives context.
- Public reading is clearly described as available without an account.

**Weaknesses**

- `/` and `/start` repeat the same role decision without explaining when each should be used.
- The session presentation became inconsistent: public pages showed Sign In while protected-looking data remained visible.
- The login page explains protection and quota but not what query data is stored or how to delete it.

**Recommendation**

Use `/start` as a focused onboarding step only when necessary; otherwise send the role card directly to a role-specific preview, then authenticate at the moment of first AI use. Add one short privacy sentence before sign-in and a **Manage/Delete research history** route inside the workspace.

### Legal Library

**Observed state**

Search, categories and URL query state worked, but the library returned zero published records, including for a broad legal query. The page ultimately displayed an honest no-results message.

**UX impact**

The library is positioned as the law-first foundation, so an empty corpus undermines every later claim about source-grounded AI. Users cannot independently browse what the chat says it retrieved.

**Recommendation**

Do not wait for broad coverage. Select the starter corpus from real query logs, interviews, legal-aid demand, court/practice frequency and qualified legal review. The earlier 20-50-act range is only a planning hypothesis, not an evidence-backed target. Publish the smallest set that covers the top validated tasks, clearly version it, state coverage limits and add suggested searches guaranteed to return verified results.

![Legal Library empty state](justor-ai-audit-assets/04-library-empty.png)

*Figure 3. The public law-first promise currently leads to a zero-record state.*

### Citizen Guides and Legal Updates

Citizen Guides showed zero published guides, and Legal Updates showed no records. The empty-state wording is responsible, but neither page offers a useful alternative path.

**Recommendation**

- Add a verified starter set before promoting these destinations in the primary navigation.
- When empty, offer topic subscriptions, request-a-guide, official source links or a transparent coverage roadmap.
- Never convert the zero state into invented “coming soon” counts or dates.

### Trust page

The Trust page contains the right conceptual distinctions: primary source, source checked, human legal reviewed and insufficient evidence. The failure is implementation drift between this page and the workspace.

**Recommendation**

Treat the Trust page as a product contract. Turn every term into the shared multidimensional status model used by the backend, frontend, analytics and QA. Avoid separate marketing copy that can diverge from data.

### About, Contact and conversion

The About page is comprehensive and gives investors and partners useful routes. It is also long and mixes company story, product, team, roadmap, partnership, investor and contact content on one page.

**Recommendation**

- Keep the company story but move investor-specific content to a concise investor page or downloadable brief.
- Replace mailto-only high-value CTAs with trackable forms once privacy and consent language are ready.
- Add a clear product status section: what works today, what is limited, and what is not yet public.

## Chat UX review

### Current chat structure

The desktop professional and citizen chat uses:

1. Left navigation and recent research
2. User question
3. A large Research Process card
4. Long structured answer
5. Inline citation chips
6. A controlling-authority panel
7. Authority list and feedback controls
8. Sticky quick actions and composer

The structure is ambitious, but the answer is buried below product-process language. On mobile, the Research Process card consumes most of the first screen after the question.

### Recommended answer hierarchy

1. **Status banner:** what is checked and what remains pending
2. **Direct answer:** two to four sentences
3. **Recommended next action:** role-specific
4. **Key legal basis:** three to five propositions with citations
5. **Sources:** inspectable authority list
6. **Deeper analysis:** expandable sections
7. **Limits and professional-help trigger**

Move the four-step Research Process into an expandable **How this answer was produced** control. It should not be the first content block after every question.

### Citation-system simplification

The answer currently uses labels such as `[ACT-1]` inside the prose and a second list labeled `[1] Source`. Two numbering systems force the user to translate between them.

**Recommendation**

Use one citation ID throughout. Example: `[1]` in the answer, `[1] The Code of Criminal Procedure, 1898 - section X` in the source list, and the same `[1]` selected in the side panel.

### Composer and privacy

The composer has useful role-specific prompts and a visible allowance. It does not show an immediate warning against unnecessary sensitive information, even though the Trust and Privacy pages advise caution.

**Recommendation**

Add concise composer guidance: **Remove names, phone numbers, NID/passport numbers, exact addresses and case identifiers unless strictly necessary.** Provide a short link explaining storage and deletion. This must not imply that all legal facts are forbidden; it should teach data minimization.

### Feedback

Positive and issue-reporting controls are a strong inclusion. Improve them by:

- Binding feedback to response ID, citation ID, model/version and source-status snapshot
- Offering issue categories without exposing hidden forms in the accessibility tree when closed
- Confirming submission and explaining whether a human legal reviewer will see it
- Avoiding the absolute claim that every report is reviewed unless the workflow can prove that state

### History, deletion and recovery

The recent research sidebar is useful, but controls need stronger behavior and naming.

- **New Research** did not visibly reset the selected thread during testing.
- Delete buttons were represented by `✕`; add an explicit accessible name such as **Delete research thread: [title]**.
- **Clear** is potentially destructive; require confirmation and explain scope.
- Add archive, rename and search before adding more history features.

## Role-specific UX requirements

The role formats below are product hypotheses derived from the live interface and common task structure. They are not validated user preferences yet; Stage 1 testing must confirm or revise them before engineering treats them as final schemas.

### Legal Professional

**User:** Lawyers, legal researchers, law-firm staff and in-house counsel.  
**Core job:** Reach a defensible starting point faster while keeping authority and version state visible.  
**Current strength:** Dense research organization and source-focused vocabulary.  
**Main failure:** The product looks more verified than its source state supports.

**Required professional features**

- Query jurisdiction and date-as-of control
- Matter or research folder
- Proposition-to-source mapping
- Copy/export with verification status retained
- Compare authorities and amendments
- Saved sources and research history
- Clear distinction between primary text, reporter citation and secondary explanation
- Draft label when any material source is unreviewed

**Do not build yet**

Do not prioritize document drafting, full matter management or decorative AI agents until citation opening, source state and private-history boundaries work reliably.

### Law Student

**User:** Undergraduate and postgraduate law students, moot participants and exam candidates.  
**Core job:** Understand law, retain concepts and practice applying authority.  
**Current strength:** The landing page exposes study tasks instead of a blank chat.  
**Main risk:** If study answers inherit unverified professional outputs, students may learn incorrect rules with high confidence.

**Required student output modes**

- Plain-language explanation
- Case brief: facts, issue, rule, reasoning, holding and significance
- Statute breakdown by section
- Compare concepts or authorities
- Quiz and answer review
- Moot practice with argument/counterargument
- “Open the source” reading step before completion

### Citizen

**User:** People with a legal problem who may not know the correct legal term.  
**Core job:** Understand the next safe step, evidence to keep, authority to contact and when professional help is urgent.  
**Current failure:** The citizen response uses the same professional **Research Analysis**, domain abbreviations and long authority structure. That raises reading effort without improving actionability.

**Required citizen answer format**

1. What this situation may involve
2. What to do now
3. Documents/evidence to keep
4. Official office or service route
5. Deadlines or urgent warnings
6. When to contact a lawyer or emergency service
7. Sources in a separate, readable section

Avoid unexplained abbreviations such as CPC, CrPC, SRA and MFLO in the first-view citizen response.

## Bangla localization

### Observed

- The Bangla homepage route and role headings translated.
- The document language changed to `bn`.
- Product-proof examples, trust labels, footer group names and the general disclaimer remained in English.
- The Bangla professional workspace kept the main answer, research process, source controls, feedback labels and history content in English; only selected shell text and the composer placeholder were translated.

### Recommendation

Define localization completeness as a release requirement, not a routing feature.

**Acceptance criteria**

- Every visible interface string comes from the localization system.
- Generated-answer language follows the user's selected language unless the user asks otherwise.
- Source titles may remain in their official language, but surrounding explanations are localized.
- Bangla typography, wrapping and minimum control sizes are tested at 320 and 390 px.
- A locale-completeness test fails when English fallback text appears on a Bangla route, excluding approved proper names and source text.

## Mobile and responsive UX

### What passed

- No horizontal overflow at 320, 390, 768, 1024 or 1440 px on the tested homepage and professional workspace.
- Role cards measured approximately 87 px high at 320 px, providing strong tap areas.
- Workspace navigation changed to a mobile bottom bar.
- Composer and quick actions remained visible.

### What failed or needs refinement

- The homepage Menu button reported an expanded state, but no menu links appeared in the DOM or viewport.
- Quick-action chips measured about 31 px high and the send button about 38 px, below the 44 px touch-target recommendation.
- On mobile, the Research Process card dominates the first useful answer viewport.
- The fixed composer and bottom navigation leave a small reading window and risk covering status text.

**Acceptance criteria**

- Mobile menu displays all primary links, traps no focus, closes with Escape and restores focus to the Menu button.
- All primary touch targets are at least 44 by 44 CSS pixels, or have an equivalent non-overlapping hit area.
- The direct answer and trust status appear before the process card on mobile.
- The last answer line can scroll fully above the composer and bottom navigation.

![Professional workspace at mobile width](justor-ai-audit-assets/05-professional-mobile.png)

*Figure 4. The layout fits, but the process card consumes most of the first answer view and several controls are undersized.*

![Expanded mobile menu without visible navigation links](justor-ai-audit-assets/06-mobile-menu-expanded-no-links.png)

*Figure 5. The Menu control entered an expanded state, but no mobile navigation became visible.*

## Accessibility review

### Confirmed strengths

- Skip-to-content link is the first keyboard stop.
- Primary navigation and role cards expose visible focus outlines.
- Main public pages use a single H1.
- Mobile menu exposes an expanded state.

### Issues

- Loaded professional and citizen chat states had no H1.
- Delete-thread buttons use `✕` as the accessible name instead of describing the target.
- Some interactive controls are below 44 px on mobile.
- Raw Markdown symbols are visible in the authority section, reducing readability and screen-reader clarity.
- Repeated source and feedback controls create a very long focus sequence.
- The mobile menu announces expanded without exposing the expected navigation.

### Target standard

Adopt WCAG 2.2 AA as the release target. Add automated axe checks to CI, but require manual keyboard, screen-reader, zoom and touch testing for each role.

## Content design and terminology

### Replace ambiguous language

| Current phrase | Problem | Recommended pattern |
|---|---|---|
| Verification Active | Sounds current and complete without defining scope | Source status: 3 checked, 4 pending |
| Grounded on verified… | Contradicted by unreviewed and pending records | Draft based on available sources; verify pending items |
| Controlling Authority: Source | Generic and non-informative | Exact act/case, section, version and status |
| Human Legal Reviewed | Can be interpreted as platform-wide review | Human legal reviewed for this version on [date] |
| Research Process | Occupies prime answer space | How this answer was produced (expandable) |

### Fix raw rendering

The authority list exposed formatting markers such as double asterisks and backticks. Render structured source data as components instead of passing Markdown-like strings through the UI.

## Privacy, legal and security UX

The public Privacy, Terms and Disclaimer pages exist and communicate basic limits. They are too general for a production legal-research product.

### Product requirements to add

- Effective date and version history
- What query, account, feedback and usage data is collected
- Why it is collected and who can access it
- Retention periods or clearly defined retention rules
- How users export, correct and delete history
- Whether data is used for model training or evaluation
- Vendor/processors and cross-border handling, where applicable
- Contact and complaint route
- Clear emergency and deadline warning inside citizen chat, not only on a separate page

These are requirements for counsel and privacy review; this report does not declare legal compliance or non-compliance.

## Analytics and research plan

### Instrument the real funnel

Track these events with role, locale, device class and anonymous/session-safe identifiers:

- `role_selected`
- `auth_started`, `auth_succeeded`, `auth_failed`
- `first_query_started`, `query_completed`, `query_failed`, `query_cancelled`
- `citation_selected`, `source_opened`, `source_open_failed`
- `feedback_positive`, `feedback_issue_started`, `feedback_submitted`
- `language_switched`
- `library_search`, `zero_results`
- `guide_opened`, `update_opened`
- `history_deleted`, `history_cleared`

### Decision metrics

- Activation: role selected to first completed query
- Time to first useful answer
- Citation-selection rate and successful source-open rate
- Query-to-follow-up rate
- Error and abandonment rate
- Feedback issue rate by source status
- Seven-day return rate by role
- Zero-result rate in Library, Guides and Updates

Do not set public performance claims before collecting a baseline. An initial internal hypothesis may be that at least 60% of signed-in users should reach a completed first query within three minutes, but this must be validated with real data.

### User research before feature expansion

Run five moderated sessions per role with realistic tasks. This is not statistically conclusive, but it is enough to expose major comprehension and workflow failures. Allow about one week if participants are already available, or longer if recruitment must start from zero.

- Professionals: find and verify a controlling provision; compare two authorities
- Students: brief a case and explain a statutory concept
- Citizens: identify next steps, evidence and an official route for a common problem

An initial pass threshold for the controlled beta is at least four of five participants in each role able to state what is checked versus pending, open the exact source and complete the role task without moderator help. Treat this as an internal release gate, not a public performance claim.

## Prioritized implementation backlog

| ID | Severity | Issue | Recommended owner | Effort | Release test |
|---|---|---|---|---|---|
| T-01 | P0 | Verified labels conflict with pending/unreviewed sources | Product + backend + frontend + legal QA | 3-5 days | Status-mismatch integration tests are zero |
| T-02 | P0 | Citation selection and full-provision action fail | Frontend + backend | 3-7 days | Every enabled citation opens exact source |
| P-01 | P0 | Signed-out UI displays prior research | Auth/backend + frontend | 2-5 days | No private content before auth on reload/back/cross-tab |
| N-01 | P1 | Mobile menu expands without links | Frontend | 0.5-1 day | Links visible, keyboard-operable and screen-reader announced |
| L-01 | P1 | Bangla experience is partially English | Product + localization + frontend | 5-10 days | Approved locale-completeness test passes |
| D-01 | P1 | Public Library, Guides and Updates are empty | Content/legal data + backend | 2-6 weeks | Verified starter corpus is searchable and versioned |
| C-01 | P1 | Research Process precedes the usable answer | Product design + frontend | 2-4 days | Direct answer and status visible in first answer viewport |
| C-02 | P1 | Citizen output mirrors professional research | Product + content design + frontend | 5-10 days | Citizen template passes task-based usability test |
| C-03 | P1 | Two citation numbering systems | Product + frontend | 1-3 days | One ID follows proposition to source panel |
| C-04 | P1 | New Research did not visibly reset thread | Frontend | 1-2 days | New state is clear and does not alter old thread |
| P-02 | P1 | No data-minimization guidance at composer | Product + privacy + frontend | 0.5-1 day | Guidance visible before first input on all roles |
| A-01 | P1 | Chat lacks H1; delete controls weakly named | Frontend | 1-2 days | Accessibility tree and keyboard audit pass |
| A-02 | P1 | Chips/send controls under 44 px on mobile | Design + frontend | 1-2 days | Hit areas meet 44 px at 320/390 widths |
| R-01 | P1 | Raw Markdown visible in source list | Frontend | 1-2 days | Structured sources render without markup tokens |
| F-01 | P2 | Feedback page title is generic and workflow claim is absolute | Product + frontend | 0.5-1 day | Specific title; review-state copy matches operations |
| O-01 | P2 | `/` and `/start` duplicate role choice | Product | 1-2 days | One intentional onboarding path per user state |
| M-01 | P2 | No Core Web Vitals/UX telemetry verified | Engineering + analytics | 2-4 days | RUM dashboard segmented by route/role/device |
| X-01 | P2 | No professional export/share workflow | Product + frontend | 5-10 days | Export preserves source/status context |

Effort assumes an existing codebase and one experienced engineer with product/design support. Monetary cost is not estimated because team rates and backend readiness were not provided.

## Delivery roadmap

Before work starts, the PM must name one accountable owner for each P0, assign a target date and record the release decision in the backlog.

### Stage 1: Manual/no-code validation - 1 to 2 weeks

- Define the exact meaning of each trust status with product, engineering and qualified legal reviewers.
- Red-team the three observed P0 issues on shared devices and fresh sessions.
- Test revised citizen and professional answer hierarchy as clickable mockups.
- Interview five users per role before committing to broad feature expansion.

This range assumes an existing participant pool and parallel product, legal/privacy and engineering support. Recruitment from zero extends the schedule.

### Stage 2: MVP trust and usability release - 2 to 4 weeks

- Enforce truthful source-state labels.
- Repair citation and source actions.
- Enforce signed-out privacy boundaries.
- Move direct answers above process explanations.
- Repair mobile menu, control sizing, H1 and accessible names.
- Add composer privacy guidance and consistent error/retry states.
- Record the minimum trust events required by the Stage 2 release gate: first query, citation selection, source open/open failure, authentication expiry and issue feedback.

### Stage 3: Scalable content and role system - 4 to 8 weeks

- Publish and version a verified starter legal corpus.
- Build role-specific response schemas.
- Complete Bangla localization and locale QA.
- Add production dashboards, role/locale/device segmentation, retention analysis and broader product events on top of the Stage 2 minimum trust telemetry.
- Add professional export, saved authorities and research organization only after source reliability passes.

**Stage 3 exit gate:** corpus selection is tied to validated demand; at least one verified search path exists for every published coverage category; each role reaches the four-of-five task-completion threshold; Bangla routes contain no unapproved English UI fallback; and production dashboards report the trust events below.

### Stage 4: Advanced/AI-powered expansion - after trust metrics pass

- Document analysis and comparison
- Matter workspace and citation workspace
- Student quizzes, moot practice and concept maps
- Citizen OCR/document explanation and official-route tracking
- Personalized retrieval and proactive legal updates

Do not enter Stage 4 while citation-open success, authentication boundaries or status consistency remain unreliable.

**Recommended Stage 4 entry thresholds**

- Zero query/source status mismatches in automated release fixtures and the legal-QA release sample.
- Zero protected-history exposures across the unauthenticated reload, back, restore, expired-token and cross-tab test matrix.
- 100% of enabled citations open the correct source in release testing; production source-open success is at least 99% for seven consecutive days, with explained disabled states excluded.
- At least four of five moderated participants in every role correctly interpret checked versus pending status and open the supporting source without help.
- Every material proposition in the release sample maps to a source object, and qualified legal QA approves the sample and the status-language rules.

These are proposed internal gates. The PM, engineering owner and qualified legal/privacy owner must approve or revise them before Stage 2 begins.

## Developer-friendly requirements

### Source object contract

Every citation should provide at minimum:

- Stable citation ID
- Authority type: act, section, judgment, gazette or official guidance
- Official/canonical title
- Exact section or paragraph
- Source URL or explicit unavailable reason
- Source text excerpt
- Version/effective date when known
- Retrieval date
- Verification dimensions
- Proposition supported
- Human-review metadata only when a qualified review actually occurred

### Verification status model - not one enum

Availability, checking, proposition support, evidence sufficiency and human review can overlap. Do not compress them into one mutually exclusive status. Store separate dimensions:

| Dimension | Suggested values | Meaning |
|---|---|---|
| Source availability | `available`, `unavailable` | Whether the underlying source can be retrieved |
| Text/location check | `unchecked`, `checked` | Whether the exact source text and location were matched |
| Version certainty | `known_current`, `known_historical`, `unknown` | Whether the effective/version date is known and appropriate to the query |
| Proposition support | `unsupported`, `partial`, `supported` | Whether this source supports the linked proposition |
| Evidence sufficiency | `insufficient`, `partial`, `sufficient` | Whether the response has enough support overall |
| Human review | `not_reviewed`, `reviewed` | Whether a qualified reviewer approved this exact version |

Derive response-level copy from these fields with one shared rules engine. **Human reviewed** requires reviewer, scope, timestamp and content-version metadata. Retrieval success or source count alone must never produce **verified** copy.

### Authentication and cache requirements

- Validate the session before rendering protected history.
- Store private queries only in a defined authenticated cache.
- Clear client cache, in-memory state and sensitive local storage on sign-out.
- Broadcast sign-out to all tabs.
- Use no-store/private cache headers as appropriate for protected responses.
- Add automated tests for reload, back, restore and cross-tab cases.

### Error and empty-state matrix

Design separate states for:

- No public records exist
- Search returned no match
- Legal data service unavailable
- Source exists but cannot be opened
- Query timed out
- AI response failed
- Quota reached
- Authentication expired
- Partial answer with insufficient evidence

Each state needs a plain-language explanation, recovery action and telemetry event.

## What the PM should ask the team

1. What exact database fields generate **verified**, **pending** and **human reviewed** labels?
2. Can an answer ever be globally verified when one material citation is pending?
3. Why did citation and full-provision controls have no visible action?
4. Where is research history stored, and why can it render while Sign In is shown?
5. What is cleared on sign-out across tabs, caches and browser restore?
6. Which public laws and guides can be published with verified version dates in the next two weeks?
7. Does the citizen response use a different schema or only different prompt text?
8. Which Bangla strings are generated, translated, fallback or source-original?
9. What events currently measure first-query activation and source verification?
10. What must be true before the product can claim source-grounded or verified output publicly?

## A-Z enhancement checklist

- **A - Accessibility:** WCAG 2.2 AA, meaningful headings, 44 px targets and named controls.
- **B - Bangla:** Complete UI and generated-answer localization, not route-only translation.
- **C - Citations:** One numbering system, working selection and exact source details.
- **D - Data:** Publish a narrow verified corpus before advertising broad coverage.
- **E - Errors:** Distinguish no data, no match, service failure and insufficient evidence.
- **F - Feedback:** Bind reports to response/source versions and show review status honestly.
- **G - Guides:** Start with a small approved citizen set and actionable official routes.
- **H - History:** Search, rename, archive and delete safely; never expose it signed out.
- **I - Information architecture:** Preserve role-first entry and reduce duplicate onboarding paths.
- **J - Journey:** Measure landing to role to auth to first query to source open.
- **K - Keyboard:** Verify focus order, menu behavior, citation controls and sticky composer.
- **L - Legal limits:** Put relevant warnings in the moment of use, not only footer pages.
- **M - Mobile:** Keep no-overflow strength; enlarge controls and shorten first-view answers.
- **N - Navigation:** Repair the mobile menu and keep role-specific navigation consistent.
- **O - Onboarding:** Preview the role value before authentication and explain data handling.
- **P - Privacy:** Minimize sensitive input, enforce session boundaries and provide deletion controls.
- **Q - Query composer:** Add scope hints, privacy guidance, loading, cancel, retry and quota states.
- **R - Role differentiation:** Professional research, student learning and citizen action require different outputs.
- **S - Search:** Add guaranteed examples, coverage filters, version dates and useful zero states.
- **T - Trust:** Make the Trust page a shared data contract, not separate marketing language.
- **U - User research:** Test five realistic users per role before advanced feature expansion.
- **V - Verification:** Compute labels from source states and block contradictory claims.
- **W - Workspace:** Put the answer first, move process detail behind disclosure and reduce density.
- **X - Export:** Preserve citations, dates and verification states in professional exports.
- **Y - Yesterday/relative dates:** Add exact timestamps on hover/detail for research auditability.
- **Z - Zero states:** Offer an honest next step without invented content or unsupported counts.

## Definition of done for the Stage 2 controlled-test release

Stage 2 is ready for controlled user testing only when all of the following are true:

- Status-mismatch tests report zero contradictions between response labels and source dimensions.
- Every enabled citation and source action opens the correct target by mouse, keyboard and touch; unavailable actions are disabled with a reason.
- The unauthenticated reload, back, restore, expired-token and cross-tab matrix exposes zero protected-history items, and protected endpoints reject anonymous requests.
- The direct answer and current trust status appear before the process explanation.
- Mobile navigation exposes its links; primary actions have adequate hit areas; chat has a meaningful H1 and named controls.
- Composer data-minimization guidance is visible before first input.
- Chat has clear loading, timeout, retry, quota and insufficient-evidence states.
- Analytics records first query, citation selection, source open/open failure, authentication expiry and issue feedback.
- One named product owner, engineering owner and qualified legal/privacy owner approve the release evidence, status rules and data-handling copy.

Role-specific schemas, the verified public corpus and complete Bangla localization are Stage 3 exit requirements, not blockers for the narrower Stage 2 controlled test. They remain blockers for broader beta promotion.

## Final recommendation

Justor AI does not need a visual redesign. It needs a trust-contract correction. Preserve the strong role selection, restrained visual system and responsive foundation. Make every verification claim traceable to data, make every source control work, protect prior research at authentication boundaries, and give each role an answer shape that matches its real job. Once those conditions are met, the current design can support a credible controlled beta and a much stronger PM roadmap.
