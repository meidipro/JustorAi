# Justor AI — Complete A-Z UI/UX Guide
**Version:** 1.0  
**Date:** August 28, 2026  
**For:** Mehedi Hasan (CTO) + Design  
**Authority:** Taj (CEO)  
**Rule:** This is the single source of truth for all UI/UX decisions. Nothing ships that contradicts this document.

---

## A — Accessibility

### Standard
WCAG 2.2 AA. Non-negotiable. Add automated `axe` checks to CI pipeline.

### Requirements
- Every page has exactly one `<h1>` — chat workspaces must include a visually-hidden H1
- All interactive controls minimum 44×44px touch target
- Visible keyboard focus outline on every focusable element
- Skip-to-content link as first keyboard stop (already exists — preserve it)
- Screen reader accessible names on every button — no `✕` alone, no icon-only buttons without `aria-label`

### Fix list
```
❌ Chat workspace — no H1
Fix: <h1 class="sr-only">আইনি গবেষণা — পেশাদার ওয়ার্কস্পেস</h1>
     <h1 class="sr-only">Legal Research — Professional Workspace</h1>

❌ Delete thread button — ✕ as accessible name
Fix: aria-label="Delete research thread: {title}" / "গবেষণা মুছুন: {শিরোনাম}"

❌ Feedback form hidden in DOM when closed
Fix: aria-hidden="true" + display:none when collapsed

❌ Mobile menu — announces expanded but no links visible
Fix: Full drawer with all links in DOM (see N — Navigation)

❌ Citation chips ~31px, send button ~38px
Fix: min-height:44px; min-width:44px on all controls
```

---

## B — Bangla Localization

### Rule
Every visible interface string comes from the i18n system. Zero hardcoded English strings in components. Bangla route must have zero unapproved English fallbacks.

### Font Stack
```css
/* Bangla primary font */
font-family: 'Hind Siliguri', 'Noto Sans Bengali', 'SolaimanLipi', sans-serif;

/* Use for all Bangla text. Latin characters within Bangla text fall back to Poppins */
/* Minimum font-size on any input: 16px — prevents iOS auto-zoom */
```

### Complete UI String Map (EN → BN)

#### Navigation
| English | বাংলা |
|---|---|
| Legal Professional | আইনি পেশাদার |
| Law Student | আইন শিক্ষার্থী |
| Citizen | সাধারণ নাগরিক |
| Legal Library | আইনি লাইব্রেরি |
| Guides | গাইড |
| Updates | আপডেট |
| Trust | বিশ্বাসযোগ্যতা |
| About | আমাদের সম্পর্কে |
| Team | দল |
| Investors | বিনিয়োগকারী |
| Sign In | সাইন ইন |
| Sign Out | সাইন আউট |
| Start Justor | জাস্টর শুরু করুন |
| Library | লাইব্রেরি |
| Resources | সম্পদ |
| Company | কোম্পানি |
| Product | পণ্য |
| Contact | যোগাযোগ |

#### Homepage
| English | বাংলা |
|---|---|
| Choose how you use Justor. | কীভাবে জাস্টর ব্যবহার করবেন তা বেছে নিন। |
| Research, learn, or find practical legal guidance. | গবেষণা করুন, শিখুন, অথবা ব্যবহারিক আইনি নির্দেশনা খুঁজুন। |
| Research with authority. | কর্তৃত্বের সাথে গবেষণা করুন। |
| Learn from the law itself. | আইন থেকে সরাসরি শিখুন। |
| Know what to do next. | পরবর্তী পদক্ষেপ জানুন। |
| Start with the law. Then use AI. | আইন দিয়ে শুরু করুন। তারপর AI ব্যবহার করুন। |
| Explore Legal Library | আইনি লাইব্রেরি দেখুন |
| Controlled Beta | নিয়ন্ত্রিত বেটা |
| Bangladesh legal intelligence for guidance, learning and professional research. | নির্দেশনা, শিক্ষা ও পেশাদার গবেষণার জন্য বাংলাদেশের আইনি বুদ্ধিমত্তা। |

#### Citizen Sectors
| English | বাংলা |
|---|---|
| Property & Land | সম্পত্তি ও জমি |
| Family & Marriage | পরিবার ও বিবাহ |
| Criminal & Police | অপরাধ ও পুলিশ |
| Employment & Work | চাকরি ও কর্মসংস্থান |
| Consumer & Contracts | ভোক্তা ও চুক্তি |
| Rights & Documents | অধিকার ও দলিল |
| Business & Licensing | ব্যবসা ও লাইসেন্স |

#### Citizen Guide Page Sections
| English | বাংলা |
|---|---|
| What this situation involves | এই পরিস্থিতি কী |
| What to do now | এখন কী করবেন |
| Documents and evidence to keep | কোন কাগজপত্র রাখবেন |
| Where to go | কোথায় যাবেন |
| Important deadlines | গুরুত্বপূর্ণ সময়সীমা |
| When you need a lawyer | কখন আইনজীবী দরকার |
| Still confused? Ask Justor AI → | এখনও বুঝতে পারছেন না? জাস্টর AI-কে জিজ্ঞেস করুন → |

#### Citizen Disclaimer (always shown)
**English:**
> ℹ️ Justor provides a basic overview and general navigation guidance only. This is not legal advice. Consult a qualified lawyer in Bangladesh for advice on your specific case.

**বাংলা:**
> ℹ️ জাস্টর শুধুমাত্র সাধারণ দিকনির্দেশনা এবং প্রাথমিক ধারণা প্রদান করে। এটি আইনি পরামর্শ নয়। আপনার নির্দিষ্ট পরিস্থিতির জন্য একজন যোগ্য বাংলাদেশী আইনজীবীর সাথে পরামর্শ করুন।

#### Chat Workspace
| English | বাংলা |
|---|---|
| New Research | নতুন গবেষণা |
| Recent Research | সাম্প্রতিক গবেষণা |
| Ask a legal question... | একটি আইনি প্রশ্ন করুন... |
| How this answer was produced | এই উত্তর কীভাবে তৈরি হয়েছে |
| Sources | উৎস |
| Pending verification | যাচাই অপেক্ষমান |
| Source-checked | উৎস যাচাইকৃত |
| Unreviewed | পর্যালোচনা করা হয়নি |
| Human legal reviewed | মানব আইনি পর্যালোচনা |
| View full provision | সম্পূর্ণ বিধান দেখুন |
| Delete research thread | গবেষণা মুছুন |
| This is helpful | এটি সহায়ক |
| Report an issue | একটি সমস্যা জানান |
| Copy answer | উত্তর কপি করুন |
| Research with authority | কর্তৃত্বের সাথে গবেষণা করুন |

#### Status Banners
| English | বাংলা |
|---|---|
| {n} authorities: {x} source-checked · {y} pending | {n}টি কর্তৃপক্ষ: {x}টি যাচাইকৃত · {y}টি অপেক্ষমান |
| All sources source-checked | সমস্ত উৎস যাচাইকৃত |
| Some sources not yet verified | কিছু উৎস এখনও যাচাই হয়নি |
| Based on available sources | উপলব্ধ উৎসের ভিত্তিতে |

#### Error & Empty States
| English | বাংলা |
|---|---|
| No results found | কোনো ফলাফল পাওয়া যায়নি |
| Response timed out. Try again. | উত্তর আসতে দেরি হচ্ছে। আবার চেষ্টা করুন। |
| Research unavailable right now. | এই মুহূর্তে গবেষণা পরিষেবা উপলব্ধ নেই। |
| Your daily limit has been reached. | আপনার দৈনিক সীমা শেষ হয়েছে। |
| Sign in to continue. | চালিয়ে যেতে সাইন ইন করুন। |
| Source URL not yet indexed. | উৎস URL এখনও সংযুক্ত করা হয়নি। |
| You're browsing as a guest. Sign in to save your research. | আপনি গেস্ট হিসেবে ব্রাউজ করছেন। গবেষণা সংরক্ষণ করতে সাইন ইন করুন। |

#### Feedback
| English | বাংলা |
|---|---|
| Wrong law cited | ভুল আইন উদ্ধৃত করা হয়েছে |
| Wrong citation | ভুল রেফারেন্স |
| Outdated information | পুরানো তথ্য |
| Missing authority | গুরুত্বপূর্ণ কর্তৃপক্ষ অনুপস্থিত |
| Incomplete answer | অসম্পূর্ণ উত্তর |
| Misunderstood question | প্রশ্ন ভুল বোঝা হয়েছে |
| Other | অন্যান্য |
| Your report has been recorded. | আপনার প্রতিবেদন রেকর্ড করা হয়েছে। |

#### Composer Privacy Hint
**English:** Remove names, NID/passport numbers, phone numbers and case identifiers unless essential.  
**বাংলা:** প্রয়োজন না হলে নাম, এনআইডি/পাসপোর্ট নম্বর, ফোন নম্বর এবং মামলার তথ্য লিখবেন না।

### AI Response Language Rule
```
When locale = 'bn':
  Add to system prompt:
  "The user's interface language is Bangla. Respond entirely in natural, professional Bangla.
  Do not use literal/Google-Translate-style Bangla. Use proper legal Bangla where applicable.
  Official act titles (e.g., 'The Code of Civil Procedure, 1908') and section numbers
  may remain in English as these are official legal designations.
  All explanations, analysis, and guidance must be in Bangla."
```

### Bangla-Specific Layout Rules
- Bangla script is ~20% wider than Latin at equivalent font size
- Line-height for Bangla: minimum 1.7 (Latin: 1.5)
- Test all UI at 320px and 390px with Bangla text loaded
- Never truncate Bangla text with ellipsis on primary navigation items
- Button min-width: 120px when Bangla label is used (Bangla labels are longer)

### Locale Completeness Test
Automated test on every deploy:
- Parse /bn route DOM
- Flag any string containing only Latin characters (except approved proper nouns: court names, act titles, citation references)
- Test must pass before any Bangla-route deployment

---

## C — Citations

### Problem
Two numbering systems: `[ACT-1]` in prose + `[1] Source` in source list. Users must mentally translate.

### Fix: One system throughout
```
In answer prose:    "...under Bangladesh cheque law, the notice period is 30 days [1]..."
In source list:     [1] Negotiable Instruments Act, 1881 — Section 138
In authority panel: [1] highlighted as active when citation chip is clicked
In Bangla mode:     Same number [1], surrounding text in Bangla
```

### Citation Chip Behavior
```
onClick([N]) → {
  find source object where index = N
  update authority panel with:
    - Full act/case name
    - Exact section/rule
    - Verification status badge
    - Source text excerpt (max 200 chars)
    - Official URL (or "URL not yet indexed")
    - Version/effective date
    - Proposition supported
  Response time: < 300ms (data already in answer payload — no new network call)
}
```

### "View Full Provision" Logic
```
if official_url exists AND verification_status != 'unreviewed':
  → Button ENABLED → onClick: open URL in new tab + log source_view event

if official_url is null:
  → Button DISABLED (not hidden)
  → Tooltip EN: "Source URL not yet indexed. Provision text shown above."
  → Tooltip BN: "উৎস URL এখনও সংযুক্ত করা হয়নি। উপরে বিধানের পাঠ দেখুন।"

NEVER show an enabled button that does nothing when clicked.
```

---

## D — Data / Database Search

### Current Problem
Cases, Statutes, Amendments pages filter by `published = true` — no records have that flag. Pages return zero.

### Fix: Query corpus directly

**Cases:**
```sql
SELECT id, name, citation, dlr_reference, court_division,
       bench_judge, case_date, act, section, keywords, verification_status
FROM cases
WHERE name ILIKE '%{query}%'
   OR citation ILIKE '%{query}%'
   OR dlr_reference ILIKE '%{query}%'
   OR act ILIKE '%{query}%'
   OR keywords::text ILIKE '%{query}%'
ORDER BY case_date DESC
LIMIT 50;
```

**Statutes:**
```sql
SELECT id, title, act_number, year, gazette_date, effective_date, status, official_url
FROM legal_instruments
WHERE title ILIKE '%{query}%' OR act_number ILIKE '%{query}%'
ORDER BY year DESC;
```

**Amendments:**
```sql
SELECT ae.id, ae.operation, ae.effective_date, ae.verification_status,
       li.title AS amending_act, p.title AS target_provision
FROM amendment_events ae
JOIN legal_instruments li ON ae.amending_instrument_id = li.id
JOIN provisions p ON ae.target_provision_id = p.id
WHERE li.title ILIKE '%{query}%' OR p.title ILIKE '%{query}%'
ORDER BY ae.effective_date DESC;
```

**Legal Library (unified, vector search):**
```sql
SELECT id, title, type, verification_status,
       1 - (embedding <=> {query_embedding}) AS similarity
FROM (
  SELECT id, title, 'case' as type, verification_status, embedding FROM cases
  UNION ALL
  SELECT id, title, 'statute' as type, status as verification_status, embedding FROM legal_instruments
  UNION ALL
  SELECT id, title, 'provision' as type, verification_status, embedding FROM provisions
) combined
WHERE 1 - (embedding <=> {query_embedding}) > 0.7
ORDER BY similarity DESC LIMIT 30;
```

### Access Rules by Workspace
| Workspace | Filter | Show verification status |
|---|---|---|
| Professional | All corpus records (no published filter) | Yes — prominently |
| Student | All corpus records | Yes — simplified |
| Citizen | verified only | No — hidden from user |

---

## E — Errors & Empty States

### Error Matrix
Every error state needs: plain-language message + recovery action + analytics event.

| State | EN Message | BN Message | Recovery Action |
|---|---|---|---|
| No public records | "Search above — {n} records available" | "উপরে খুঁজুন — {n}টি রেকর্ড পাওয়া যাচ্ছে" | Show suggested searches |
| Search returned no match | "No results for '{query}'" | "'{query}' এর জন্য কোনো ফলাফল নেই" | Suggest alternate search terms |
| AI response timed out | "Response timed out. Try again." | "উত্তর আসতে দেরি হচ্ছে। আবার চেষ্টা করুন।" | Retry button |
| All LLMs failed | "Research unavailable right now. Your question has been saved." | "এই মুহূর্তে গবেষণা সেবা অনুপলব্ধ। আপনার প্রশ্ন সংরক্ষিত হয়েছে।" | Retry later |
| Daily quota reached | "You've reached today's research limit." | "আজকের গবেষণার সীমা শেষ হয়েছে।" | Upgrade CTA or wait |
| Auth expired | "Your session has expired. Sign in again." | "আপনার সেশন শেষ হয়ে গেছে। আবার সাইন ইন করুন।" | Redirect to sign in |
| Source unavailable | "Source URL not yet indexed." | "উৎস URL এখনও সংযুক্ত করা হয়নি।" | Show provision text |
| DB insert failed | "Your research could not be saved. Export manually." | "আপনার গবেষণা সংরক্ষণ করা যায়নি। ম্যানুয়ালি এক্সপোর্ট করুন।" | Export button |

### Empty State Design Rules
- Never show a raw "0 results" with no context
- Always state how many records exist in the corpus
- Always offer 3-5 suggested searches guaranteed to return results
- Never invent "coming soon" dates or content counts

---

## F — Feedback System

### Per-Answer Controls
```
👍 Helpful  |  ⚑ Report issue
```

### On "Report issue" click — show category selector:
| EN | BN |
|---|---|
| Wrong law cited | ভুল আইন উদ্ধৃত |
| Wrong citation | ভুল রেফারেন্স |
| Outdated information | পুরানো তথ্য |
| Missing authority | গুরুত্বপূর্ণ কর্তৃপক্ষ অনুপস্থিত |
| Incomplete answer | অসম্পূর্ণ উত্তর |
| Misunderstood question | প্রশ্ন ভুল বোঝা হয়েছে |
| Other | অন্যান্য |

Optional free-text field after category selection.

### Feedback Payload (DB)
```json
{
  "response_id": "uuid",
  "conversation_id": "uuid",
  "feedback_type": "positive | issue",
  "issue_category": "...",
  "free_text": "string | null",
  "source_status_snapshot": "source_objects_json",
  "model_version": "string",
  "submitted_at": "timestamp"
}
```

### Confirmation Message
- EN: "Your report has been recorded and queued for review."
- BN: "আপনার প্রতিবেদন রেকর্ড করা হয়েছে এবং পর্যালোচনার জন্য রাখা হয়েছে।"

Do NOT say "reviewed by a qualified legal reviewer" while the Legal QA role is vacant.

---

## G — Guides (Citizen)

### Sector Cards (Citizen Landing)
Full-width on mobile, 2-column on tablet+. Large tap targets (min 80px height).

```
🏠  সম্পত্তি ও জমি          Property & Land
    বিরোধ, উত্তরাধিকার, কেনাবেচা, ভাড়া
    Disputes, inheritance, buying, renting

👨👩👧  পরিবার ও বিবাহ          Family & Marriage
    তালাক, হেফাজত, যৌতুক, ভরণপোষণ
    Divorce, custody, dowry, maintenance

⚖️  অপরাধ ও পুলিশ           Criminal & Police
    এজাহার, গ্রেপ্তার, জামিন, অভিযোগ
    FIR, arrest, bail, complaints

💼  চাকরি ও কর্মসংস্থান       Employment & Work
    অবৈধ বরখাস্ত, বকেয়া বেতন, শ্রম অধিকার
    Unfair dismissal, unpaid wages, rights

🛒  ভোক্তা ও চুক্তি           Consumer & Contracts
    প্রতারণা, ঋণ বিরোধ, চুক্তি সমস্যা
    Fraud, loan disputes, contract issues

📋  অধিকার ও দলিল            Rights & Documents
    এনআইডি, পাসপোর্ট, জন্ম নিবন্ধন
    NID, passport, birth certificate

🏢  ব্যবসা ও লাইসেন্স         Business & Licensing
    ব্যবসায়িক অনুমতি, ট্রেড লাইসেন্স
    Permits, trade license issues
```

### Guide Content Rules
- Titles: problem-first language, not legal topic names
  - ✅ "আমার বাড়িওয়ালা জামানত ফেরত দিচ্ছে না" (My landlord won't return my deposit)
  - ❌ "Tenancy Law Overview"
- Each guide must have all 6 sections (see Citizen spec)
- Disclaimer always visible at bottom
- "Ask Justor AI" button at bottom of every guide

### Guide Page Section Order
1. এই পরিস্থিতি কী (What this involves)
2. এখন কী করবেন (What to do now)
3. কোন কাগজপত্র রাখবেন (Documents to keep)
4. কোথায় যাবেন (Where to go)
5. গুরুত্বপূর্ণ সময়সীমা (Important deadlines)
6. কখন আইনজীবী দরকার (When you need a lawyer)
7. DISCLAIMER BOX (always visible)
8. "এখনও বুঝতে পারছেন না? জাস্টর AI-কে জিজ্ঞেস করুন →" button

---

## H — History

### Rules
- Research history only visible to authenticated users — never on signed-out screen
- Sign-out clears all history from client (localStorage + state)
- Thread controls: rename, archive, delete (with confirmation)
- Delete button: `aria-label="Delete research thread: {title}"` / `"গবেষণা মুছুন: {শিরোনাম}"`
- "New Research" must visibly reset thread AND composer AND authority panel
- Soft delete: 30-day recovery window before permanent deletion
- Full data export on user request

### Persistence Schema
```sql
-- On query submit
INSERT INTO conversations (id, user_id, workspace_type, title, created_at)
VALUES (uuid, auth.uid(), 'professional', first_50_chars, now());

-- User message
INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES (uuid, conv_id, 'user', query_text, now());

-- Assistant message (on completion, not start)
INSERT INTO messages (id, conversation_id, role, content, sources, model_version, created_at)
VALUES (uuid, conv_id, 'assistant', full_answer, source_json, model_id, now());
```

---

## I — Information Architecture

### Global Structure
```
justorai.com
├── / (Homepage — role selection)
├── /professional (Legal Professional workspace)
├── /student (Law Student workspace)
├── /citizen (Citizen landing — sector cards)
│   ├── /citizen/guides (all sectors)
│   ├── /citizen/guides/{sector} (sector page)
│   └── /citizen/guides/{sector}/{guide} (individual guide)
├── /library (Legal Library)
│   ├── /library/cases
│   ├── /library/statutes
│   ├── /library/amendments
│   └── /library/updates
├── /trust
├── /about
├── /team
├── /investors
└── /sign-in
```

### Remove /start route
- /start duplicates / without adding value
- Send role cards directly from / to workspace
- Authenticate at moment of first AI query, not before

---

## J — Journey / User Flows

### Citizen Journey (correct order)
```
/ → "For Citizens" → /citizen (sector cards)
  → Pick sector → /citizen/guides/{sector}
  → Pick guide → /citizen/guides/{sector}/{guide}
  → Read guide → "Ask Justor AI" (optional)
  → /citizen/chat (context pre-loaded from guide)
  → Login prompt ONLY when: saving chat, accessing history
```

### Professional Journey
```
/ → "Legal Professional" → /professional
  → Sign in (required for research)
  → New research or continue from history
  → Query → Answer + authority panel
  → Citation chips → source panel
  → Follow-up in same thread
```

### Student Journey
```
/ → "Law Student" → /student
  → Choose study mode (explain / case brief / compare / quiz)
  → Query → Learning-format answer
  → "Open the source" reading step before completion (if available)
```

### Authentication Trigger Rules
| Action | Login Required? |
|---|---|
| Browse homepage | ❌ No |
| Read guide | ❌ No |
| Ask Citizen AI (first answer) | ❌ No |
| Save research / access history | ✅ Yes |
| Professional workspace | ✅ Yes |
| Student workspace | ✅ Yes |
| Upgrade to paid | ✅ Yes |

---

## K — Keyboard & Touch

### Touch Target Rules
```css
/* All interactive controls */
min-height: 44px;
min-width: 44px;

/* Quick-action chips */
.quick-action-chip {
  min-height: 44px;
  padding: 10px 16px;
}

/* Send button */
.send-button {
  min-height: 44px;
  min-width: 44px;
}

/* Citation chips */
.citation-chip {
  min-height: 32px;
  padding: 6px 12px;
  /* If visual size < 44px, expand hit area: */
  position: relative;
}
.citation-chip::before {
  content: '';
  position: absolute;
  top: -6px; bottom: -6px;
  left: -6px; right: -6px;
}
```

### Keyboard Rules
- Modal/drawer: trap focus inside when open
- Close on Escape, return focus to trigger element
- Tab order follows visual reading order
- No keyboard traps outside modals

---

## L — Legal Library

### Current State
Empty — zero records returned because `published = true` filter blocks all corpus records.

### Fix
- Remove `published = true` filter for professional workspace
- Query corpus directly (see D — Data)
- Show verification_status badge on every result card
- Unified search across cases + statutes + provisions using vector similarity (BGE-M3 already in stack)

### Result Card Design
```
[CASE] ● Source-Checked
BLAST v Bangladesh
68 DLR AD 1 · Appellate Division · 2016
Acts: Constitution · High Court Division
───────────────────────────────────
[STATUTE] ○ Pending
Negotiable Instruments (Amendment) Act 2026
Act No. XX of 2026 · Effective: March 2026
```

### Suggested Searches (pre-populate on empty state)
Show 5 searches guaranteed to return results:
- EN: "Section 138 Negotiable Instruments" | "Order XXXIX CPC" | "Property Transfer" | "Employment Termination" | "Bail CrPC"
- BN: "চেক ডিজঅনার আইন" | "নিষেধাজ্ঞা" | "সম্পত্তি হস্তান্তর" | "চাকরি বরখাস্ত" | "জামিন আবেদন"

---

## M — Mobile UX

### What Is Working (preserve)
- No horizontal overflow at 320/390/768/1024/1440px tested widths ✅
- Role cards ~87px height — strong tap areas ✅
- Bottom navigation bar in workspace ✅
- Composer and quick actions visible ✅
- Skip-to-content link ✅

### What Must Be Fixed

**Mobile menu (broken):**
```
Hamburger → full-width slide-in drawer from right
Drawer contains:
  × Close button (top right, aria-label="Close menu" / "মেনু বন্ধ করুন")
  Logo
  ─────────────────
  For Citizens / সাধারণ নাগরিক
  Legal Library / আইনি লাইব্রেরি
  Guides / গাইড
  Updates / আপডেট
  ─────────────────
  For Lawyers / আইনি পেশাদার
  For Students / আইন শিক্ষার্থী
  ─────────────────
  EN | বাংলা
  Sign In / সাইন ইন
  ─────────────────
Close: Escape key | tap outside | × button
Focus: trapped inside drawer, returns to hamburger on close
aria-expanded: true ONLY when links are in DOM and visible
```

**Mobile answer hierarchy:**
- Status banner + first 2 sentences of direct answer visible at 390px without scrolling
- Research Process card NEVER appears before the answer on mobile
- Fixed composer + bottom nav must leave sufficient reading area (test with long Bangla text)
- Last line of answer must be scrollable above the composer

**Touch targets at 320px and 390px:**
- All primary actions: min 44×44px ✅
- Quick-action chips: min 44px height ✅
- Send button: min 44px ✅

---

## N — Navigation

### Desktop Nav Order (left → right)
```
[Justor AI logo] ........ [For Citizens] [Library] [Guides] [For Lawyers] [For Students] ...... [EN | বাংলা] [Sign In / Avatar]
```

### Mobile Nav
- Top bar: logo + language toggle + hamburger
- Bottom bar (in workspace): Home | Library | [Role] | History | Profile

### Logo Behavior
```
In workspace: logo → workspace root (/professional | /student | /citizen)
In public pages: logo → / (homepage)
```

### Language Toggle
- Label: `EN | বাংলা` (not a dropdown — direct toggle)
- Persists across sessions via localStorage `justor_locale`
- Position: right side of nav, before Sign In

### Sign In Position
- Always last item in desktop nav (far right)
- On mobile: bottom of hamburger drawer
- Never appears as a primary CTA in the product navigation
- Soft nudge only: "Sign in to save your research" banner inside workspace

---

## O — Onboarding & Authentication

### Flow
```
Homepage role card → workspace preview (no login required for preview)
First AI query → allowed without login (citizen workspace)
First save / history access → login prompt with reason shown
```

### Sign-In Page
One short sentence before Google button:
- EN: "Your research is encrypted and stored securely. You control what you share."
- BN: "আপনার গবেষণা এনক্রিপ্টেড এবং নিরাপদে সংরক্ষিত। আপনি নিয়ন্ত্রণ করেন কী শেয়ার করা হবে।"

Link: "How we store your data →" (Privacy page)

### Remove /start
- Merge /start into / — one entry point
- Do not show role choice twice

---

## P — Privacy & Session

### Session Security Rules

**On sign-out:**
```javascript
async function signOut() {
  // 1. Clear all Justor localStorage keys
  Object.keys(localStorage)
    .filter(k => k.startsWith('justor_'))
    .forEach(k => localStorage.removeItem(k));

  // 2. Sign out Supabase
  await supabase.auth.signOut();

  // 3. Reset all stores
  useAuthStore.getState().reset();
  useResearchStore.getState().reset();

  // 4. Broadcast to all tabs
  new BroadcastChannel('justor_auth').postMessage({ type: 'SIGNED_OUT' });

  // 5. Redirect
  router.push('/');
}
```

**In every workspace component:**
```javascript
useEffect(() => {
  const channel = new BroadcastChannel('justor_auth');
  channel.onmessage = (e) => {
    if (e.data.type === 'SIGNED_OUT') {
      useAuthStore.getState().reset();
      useResearchStore.getState().reset();
      router.push('/');
    }
  };
  return () => channel.close();
}, []);
```

**Supabase RLS (required):**
```sql
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user owns conversations"
  ON conversations FOR ALL USING (user_id = auth.uid());

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user owns messages"
  ON messages FOR ALL USING (
    conversation_id IN (SELECT id FROM conversations WHERE user_id = auth.uid())
  );
```

### Acceptance Criteria
- Fresh browser → /professional → zero history visible
- Sign out → back button → no research visible
- Sign out Tab A → Tab B clears within 2 seconds
- Expired token → 401, no history rendered

---

## Q — Query Composer

### Composer Design
```
┌─────────────────────────────────────────────────────┐
│  Ask a legal question about Bangladesh law...       │
│  আইনি প্রশ্ন করুন...                                │
│                                                     │
│  [Quick actions: Explain statute | Brief case | ... ]│
└─────────────────────────────────────────────────────┘
ℹ️ Remove names, NIDs, phone numbers unless essential.
   নাম, এনআইডি, ফোন নম্বর প্রয়োজন না হলে লিখবেন না।
[N queries remaining today] [How we protect your data →]
```

### Loading State (after submit)
```
[Spinner / subtle animation]
EN: "Researching Bangladesh law..."
BN: "বাংলাদেশের আইন খোঁজা হচ্ছে..."
```

### States
| State | EN | BN |
|---|---|---|
| Loading | Researching... | খোঁজা হচ্ছে... |
| Timeout | Response timed out. Try again. | উত্তর দেরি হচ্ছে। আবার চেষ্টা করুন। |
| Error | Research unavailable right now. | গবেষণা পরিষেবা এই মুহূর্তে অনুপলব্ধ। |
| Quota | Daily limit reached. | দৈনিক সীমা শেষ। |
| Cancel | [Cancel button visible during loading] | [বাতিল] |

---

## R — Role Differentiation

### Professional Workspace
- Entry: requires sign in
- Terminology: Matters (not Chats), Research (not Questions)
- Answer format: professional (see W — Workspace)
- Authority panel: visible, full detail, 4-tier verification badges
- Daily limit: 50 queries
- History: full, searchable, exportable
- Source panel: always visible

### Student Workspace
- Entry: requires sign in
- Output modes available:
  - Plain-language explanation
  - Case brief: facts / issue / rule / reasoning / holding
  - Statute breakdown by section
  - Compare concepts or authorities
  - Quiz and answer review
  - Moot practice: argument / counterargument
- "Open the source" reading step on completion when URL available
- Daily limit: 30 queries
- Do not expose unverified sources without clear warning label

### Citizen Workspace
- Entry: NO sign in required to browse guides or get first answer
- Flow: Guides first → AI last (fallback only)
- No source panel, no citation chips, no section numbers, no case references
- Answer format: practical steps (see G — Guides)
- Daily limit: 3 AI queries (guides are unlimited)
- Disclaimer: always visible on every guide and every AI answer
- Legal abbreviations: NEVER used in first-view content (CPC, CrPC, SRA, etc.)

---

## S — Search

### Global Search Rules
- Minimum 1 character to trigger search
- Debounce: 300ms
- Show result count: "{n} results for '{query}'"
- BN: "'{query}' এর জন্য {n}টি ফলাফল"
- Never show empty state without offering suggested searches
- All search uses pgvector + BGE-M3 for semantic similarity (already in stack)

### Citizen Search
- Citizen-facing library search: only verified corpus
- Citizen search bar suggestion: show guide titles, not statute sections
- If no guides match: "Try asking Justor AI → {query}"

---

## T — Trust & Verification

### The Problem
Current UI shows "Verification Active" + "Grounded on verified…" while sources show UNREVIEWED CORPUS and PENDING VERIFICATION. This is a hard contradiction.

### Fix: Remove these strings immediately
```
DELETE FROM UI:
❌ "Verification Active"
❌ "Grounded on verified Bangladesh statutes & Supreme Court records"
❌ Any global "verified" badge not computed from source data
```

### Replace with: Computed Status Banner

**Formula:**
```javascript
function computeStatusBanner(sources, locale) {
  const total = sources.length;
  const checked = sources.filter(s => s.verification_status === 'verified').length;
  const pending = sources.filter(s => s.verification_status === 'pending').length;
  const unreviewed = sources.filter(s => s.verification_status === 'unreviewed').length;
  const humanReviewed = sources.every(s => s.human_review_status === 'reviewed');

  if (humanReviewed) {
    return locale === 'bn'
      ? `মানব আইনি পর্যালোচনা — সমস্ত উৎস যাচাইকৃত`
      : `Human legal reviewed — all sources verified`;
  }
  if (unreviewed > 0) {
    return locale === 'bn'
      ? `${total}টি কর্তৃপক্ষ: ${checked}টি যাচাইকৃত · ${pending}টি অপেক্ষমান · ${unreviewed}টি পর্যালোচনা করা হয়নি`
      : `${total} authorities: ${checked} source-checked · ${pending} pending · ${unreviewed} unreviewed`;
  }
  return locale === 'bn'
    ? `${total}টি কর্তৃপক্ষ: ${checked}টি যাচাইকৃত · ${pending}টি যাচাই অপেক্ষমান`
    : `${total} authorities: ${checked} source-checked · ${pending} pending verification`;
}
```

### Verification Badge System (4 tiers)

| Badge | Symbol | EN Label | BN Label | Meaning |
|---|---|---|---|---|
| Verified | ● (green) | Source-checked | উৎস যাচাইকৃত | Official text matched, URL recorded |
| Reporter Verified | ◐ (blue) | Reporter verified | রিপোর্টার যাচাইকৃত | Confirmed in law reporter |
| Pending | ○ (yellow) | Pending verification | যাচাই অপেক্ষমান | Retrieved, not yet checked |
| Unreviewed | ✕ (grey) | Unreviewed corpus | পর্যালোচনা করা হয়নি | Legacy data, use with caution |

### Automated Test (CI)
Fail build when: any answer banner status contradicts any source's verification_status field.

---

## U — UI Color System

### Current Problem (from live screenshots)
Mobile menu: near-invisible dark grey section labels on black background. Navigation links reading as disabled because they're grey instead of near-white.

### Fixed Color Palette

```css
/* ── Brand Colors ── */
--justor-navy:      #1C2D44;    /* Primary brand dark */
--justor-blue:      #1E38C8;    /* Primary brand blue / accent */

/* ── Dark Background Theme ── */
--bg-primary:       #0D0F14;    /* Main background (current — keep) */
--bg-card:          #131827;    /* Card / elevated surface */
--bg-card-hover:    #1A2035;    /* Card hover state */
--bg-role-card:     #1A2240;    /* Role selection cards */

/* ── Text on Dark Background ── */
--text-primary:     #F1F5F9;    /* Primary text — near white (nav links, headings) */
--text-secondary:   #94A3B8;    /* Secondary text — body, descriptions */
--text-muted:       #64748B;    /* Section labels (PRODUCT, RESOURCES, COMPANY) */
--text-disabled:    #374151;    /* Disabled / inactive */

/* ── Text on Light Background ── */
--text-on-light-primary:   #0F172A;   /* Headings on white sections */
--text-on-light-secondary: #475569;   /* Body on white sections */

/* ── Accent / Interactive ── */
--accent-blue:      #1E38C8;    /* Primary buttons, links */
--accent-blue-hover:#2545E8;    /* Button hover */
--accent-blue-light:#E8EEFF;    /* Chat icon background, soft highlights */
--accent-blue-muted:#3B5BDB;    /* Inline citation chips */

/* ── Status Colors ── */
--status-verified:  #22C55E;    /* Green — verified badge */
--status-pending:   #EAB308;    /* Yellow — pending badge */
--status-unreviewed:#6B7280;    /* Grey — unreviewed badge */
--status-conflict:  #EF4444;    /* Red — conflict badge */

/* ── Borders ── */
--border-subtle:    #1E2535;    /* Subtle dividers */
--border-card:      #2A3550;    /* Role card borders */
--border-focus:     #1E38C8;    /* Focus ring color */
```

### Specific Fixes from Screenshots

**Mobile menu section labels (PRODUCT, RESOURCES, COMPANY):**
```css
/* Before: ~#2A3040 — near invisible */
/* After: */
.menu-section-label {
  color: #64748B;  /* --text-muted */
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
```

**Mobile menu navigation links:**
```css
/* Before: ~#9AA0B0 — reads as disabled */
/* After: */
.menu-nav-link {
  color: #F1F5F9;  /* --text-primary — near white */
  font-size: 16px;
  font-weight: 500;
  padding: 14px 0;
}
.menu-nav-link:hover {
  color: #FFFFFF;
}
```

**Mobile menu body text (tagline, CONTROLLED BETA):**
```css
.menu-tagline {
  color: #94A3B8;  /* --text-secondary */
}
.menu-beta-badge {
  color: #64748B;
  border: 1px solid #2A3550;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
}
```

**Floating chat icon (too dark):**
```css
/* Before: near-black */
/* After: */
.assistant-message-icon {
  background-color: #E8EEFF;  /* --accent-blue-light */
  color: #1E38C8;              /* --justor-blue */
  border-radius: 50%;
  padding: 6px;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  align-self: flex-start;
  box-shadow: none;
}
```

**Role cards (homepage — currently working, preserve this):**
```css
.role-card {
  background: #1A2240;         /* --bg-role-card */
  border: 1px solid #2A3550;   /* --border-card */
  border-radius: 12px;
  padding: 20px;
}
.role-card-label {             /* LEGAL PROFESSIONAL */
  color: #1E38C8;              /* --justor-blue */
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.role-card-title {             /* Research with authority. */
  color: #F1F5F9;
  font-size: 20px;
  font-weight: 700;
}
.role-card-desc {              /* Research laws and authority. */
  color: #94A3B8;
  font-size: 14px;
}
```

**White section (below role cards — "Start with the law. Then use AI."):**
```css
.light-section-heading {
  color: #0F172A;    /* --text-on-light-primary */
}
.light-section-link {
  color: #1E38C8;    /* --justor-blue */
}
```

---

## V — Verification Labels (Language Rules)

### What Is Allowed vs Forbidden

| Label | Allowed when | BN equivalent |
|---|---|---|
| "Source-checked" | official_url exists AND text/section matched | "উৎস যাচাইকৃত" |
| "Pending verification" | Retrieved but URL/text not yet matched | "যাচাই অপেক্ষমান" |
| "Unreviewed corpus" | Legacy data without any check | "পর্যালোচনা করা হয়নি" |
| "Human legal reviewed" | Qualified reviewer, scope, date ALL recorded | "মানব আইনি পর্যালোচনা" |
| "Verified" (global) | NEVER — computed per-source only | "যাচাইকৃত" — কখনো বৈশ্বিকভাবে নয় |
| "Grounded on verified…" | NEVER — removed from UI | সরানো হয়েছে |
| "Verification Active" | NEVER — removed from UI | সরানো হয়েছে |

---

## W — Workspace Answer Structure

### Professional / Student Answer Order
```
1. STATUS BANNER (computed)
   EN: "7 authorities: 3 source-checked · 4 pending verification"
   BN: "৭টি কর্তৃপক্ষ: ৩টি যাচাইকৃত · ৪টি যাচাই অপেক্ষমান"

2. DIRECT ANSWER
   2–4 sentences. First content visible in viewport. No process language.
   
3. KEY LEGAL BASIS
   3–5 propositions with citation chips [1] [2] [3]
   BN: সংশ্লিষ্ট আইনি ভিত্তি

4. SOURCES (collapsible — collapsed by default on mobile)
   EN: Sources | BN: উৎস
   
5. [▼ HOW THIS ANSWER WAS PRODUCED] — expandable accordion
   EN: "How this answer was produced"
   BN: "এই উত্তর কীভাবে তৈরি হয়েছে"
   Contains: 4-step research process. NEVER first block after question.
   
6. [▼ FULL ANALYSIS] — expandable
   EN: Full analysis | BN: বিস্তারিত বিশ্লেষণ

7. PROFESSIONAL HELP TRIGGER (always visible)
   EN: "This involves [topic]. Consult a qualified Bangladesh lawyer for [specific reason]."
   BN: "এটি [বিষয়] সংক্রান্ত। [নির্দিষ্ট কারণে] একজন যোগ্য বাংলাদেশী আইনজীবীর সাথে পরামর্শ করুন।"
```

### Citizen Answer Structure (completely different)
```
NO source panel  |  NO citation chips  |  NO section numbers  |  NO case citations

1. এই পরিস্থিতি কী (What this involves) — 2 sentences, plain language
2. এখন কী করবেন (What to do now) — numbered steps
3. কোন কাগজপত্র রাখবেন (Documents to keep)
4. কোথায় রাখবেন (Where to go)
5. গুরুত্বপূর্ণ সময়সীমা (Deadlines)
6. কখন আইনজীবী দরকার (When to see a lawyer)
7. DISCLAIMER (always visible, hardcoded)
```

---

## X — Export

### Not yet — sequence after P0-2 (citation controls) is working

When built:
- Export must include: answer text + source citations + verification status + retrieved date + model version
- EN format: "[1] Negotiable Instruments Act, 1881 — Section 138 — Pending verification — Retrieved 28 Aug 2026"
- BN format: "[১] Negotiable Instruments Act, 1881 — ধারা ১৩৮ — যাচাই অপেক্ষমান — সংগ্রহ: ২৮ আগস্ট ২০২৬"
- Never strip citation context from copied text

---

## Y — Yesterday / Timestamps

- All research threads: show relative time ("2 hours ago" / "২ ঘণ্টা আগে")
- Hover/tap on relative time → show exact timestamp
- Source verification dates: always exact ("Verified 15 Aug 2026" / "যাচাই: ১৫ আগস্ট ২০২৬")
- Amendment dates: always exact (legal precision required)

---

## Z — Zero States

### Rules
- Never display raw "0 results" with no context
- Always state how many records exist in the corpus
- Always offer 3–5 suggested searches that will return results
- Never use invented "coming soon" dates or estimated counts

### Zero State Templates

**Library (EN):**
> "No results for '{query}'. The corpus contains {n} cases and {m} statutes.  
> Try: Section 138 NI Act · Order XXXIX CPC · Transfer of Property"

**Library (BN):**
> "'{query}' এর জন্য কোনো ফলাফল নেই। এই কর্পাসে {n}টি মামলা এবং {m}টি আইন রয়েছে।  
> চেষ্টা করুন: চেক ডিজঅনার · নিষেধাজ্ঞা · সম্পত্তি হস্তান্তর"

**Citizen Guides (EN):**
> "No guides found for this topic. Ask Justor AI directly →"

**Citizen Guides (BN):**
> "এই বিষয়ে কোনো গাইড পাওয়া যায়নি। সরাসরি জাস্টর AI-কে জিজ্ঞেস করুন →"

---

## Analytics Events

Track all with: role, locale, device_class, session_id (anonymous)

```
role_selected
auth_started | auth_succeeded | auth_failed
first_query_started | query_completed | query_failed | query_cancelled | query_retried
citation_selected | source_opened | source_open_failed
feedback_positive | feedback_issue_started | feedback_submitted
language_switched (en→bn | bn→en)
guide_sector_opened | guide_opened | guide_to_ai_clicked
library_search | zero_results_returned
history_deleted | history_cleared
sign_out
daily_limit_reached
```

---

## Stage 2 Release Gate

All must be TRUE before controlled pilot begins:

- [ ] Zero contradictions: status banner vs source states (automated test)
- [ ] Every enabled citation chip → authority panel update < 300ms
- [ ] "View full provision" never enabled when it has no valid URL
- [ ] Signed-out: zero protected history visible (reload | back | cross-tab | expired token)
- [ ] Supabase RLS: anonymous client returns 401 on protected endpoints
- [ ] Direct answer visible in first mobile viewport (390px, no scroll)
- [ ] Mobile menu: all links visible, keyboard-operable, focus-managed
- [ ] All primary touch targets ≥ 44px at 320px viewport
- [ ] H1 on every workspace page
- [ ] Accessible names on all delete/action buttons
- [ ] Composer shows data-minimization guidance before first input
- [ ] Analytics minimum events firing: first_query, citation_selected, source_opened, auth_expiry, feedback_submitted
- [ ] Named owner confirmed: Taj (product) | Mehedi (engineering)

---

## What NOT to Build Yet

| Feature | Reason |
|---|---|
| Document drafting (bail, memorials) | Citation accuracy must work first |
| Full matter management | Complexity vs current scale |
| Autonomous Gazette ingestion | Human-in-loop required |
| Student quiz builder | Need reliable sources first |
| PDPA compliance features | Requires legal counsel review |
| Advanced dashboards | Collect baseline data first |
| Overbuild citizen AI | Fix accuracy first |

---

*Justor AI A-Z UI/UX Guide v1.0 — August 28, 2026*  
*Single source of truth. All UI/UX decisions defer to this document.*
