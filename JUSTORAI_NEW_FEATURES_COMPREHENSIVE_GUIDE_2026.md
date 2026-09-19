# 🚀 Justor AI — New Features Team Handbook & Product Guide (2026)
**Confidential · For Justor AI Team (Engineering, Legal Domain, Product & Growth)**  
**Version:** 2.0.0 · **Release Date:** September 2026 · **Jurisdiction:** Bangladesh

---

## 🎯 Quick Navigation: Read According to Your Role

| If You Are... | Focus On These Sections | Why It Matters To You |
| :--- | :--- | :--- |
| 👔 **Founders & Product Leads** | Sections 1, 2, 4, 11 | Understand market positioning against Southeast Asian competitors and our core value prop. |
| ⚖️ **Legal Experts & Advocates** | Sections 3, 5, 6, 7, 8 | Verify procedural accuracy (CPC, CrPC, NI Act, Limitation Act, DLR/BLD citations). |
| 💻 **Engineering & QA** | Sections 2, 9, 10 | Backend endpoints, multi-model LLM fallback cascade, local storage schema, and testing. |
| 📢 **Growth, Sales & Marketing** | Sections 3, 4, 11, 12 | 60-second client demo scripts, elevator pitches, and common objection handling. |

---

## 1. Executive Overview: What Did We Build & Why?

### The Core Problem:
Until now, legal AI in South Asia has mostly been **generic question-and-answer search boxes** or simple translation bots. But real lawyers don't just "search"—they:
1. Rush between 15–30 courtroom hearings every morning in District and High Court benches.
2. Sift through messy, conflicting bundles of deeds, notices, and pleadings.
3. Dictate quick notes in transit or conduct 30-minute client interviews.
4. Spend hours drafting formal legal memoranda and research grounds.

### The Justor AI Solution:
We evolved Justor AI into an **Integrated Chambers Operating System (Chambers OS) + 24/7 Citizen Legal Helpline**. 

We benchmarked and borrowed the highest-performing paradigms from Southeast Asia:
* **Indonesia’s Hukumonline AIlex:** Source-linked IRAC legal memoranda with direct statutory passages.
* **Singapore’s GPT-Legal & Pair-a-Legal:** Rapid courtroom hearing packs and witness cross-examination strategies.
* **Philippines’ Causa & Intellegal:** Cross-document contradiction finders and evidentiary proof matrices.
* **Thailand’s Administrative Court AI:** Strict factual timeline extraction and limitation tracking.

---

## 2. System Architecture: How It Works Under the Hood

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Justor AI Client (Vite + TypeScript)                      │
│   • 8-Tab Chambers Workspace Modal  • 24/7 WhatsApp Interactive Simulator    │
│   • Mobile Responsive UI (<768px)   • Touch-friendly Tables & Audio Drop     │
│   • Privacy Guarantee: localStorage['justor_matters_v1'] (Client-side)       │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ REST APIs / JSON
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Daemon (Port 10000)                         │
│   • /api/matter/hearing-pack         • /api/matter/consistency-check         │
│   • /api/matter/legal-memo           • /api/matter/chronology                │
│   • /api/matter/voice-note           • /api/matter/audio-consultation        │
│   • /api/matter/document-summary     • /api/whatsapp/* (Simulate / Twilio)   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ 6-12s Failover Cascade
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               Bulletproof Multi-Model LLM Resilience Layer                   │
│   1. Primary: Google Gemini 2.5 Flash (Google AI Studio API)                 │
│   2. Fast Fallback 1: Groq (Llama-3.3-70B-Versatile / OpenAI-OSS)            │
│   3. Fast Fallback 2: OpenRouter (DeepSeek / Claude 3.5 Sonnet)              │
│   4. Fast Fallback 3: Alibaba Cloud DashScope (Qwen 2.5 72B)                 │
│   👉 Zero dropped advocate requests, even under strict 429 quota limits!     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Big 4: Chamber Intelligence Suite 2.0 Features

### 🏛️ Feature 1: One-Click Courtroom Hearing Preparation Pack
* **Endpoint:** `POST /api/matter/hearing-pack`
* **What it does:** In 1 click, prepares a complete trial-ready briefing pack for an advocate heading into court today.
* **Hearing Focus Modes:** General Hearing, Bail / Anticipatory Bail (s.498 CrPC), Ad-Interim Injunction (Order 39 CPC), Charge Framing / Discharge (s.241A / 265C CrPC), Witness Deposition & Cross-Exam, Final Arguments.

#### What’s Inside the Pack:
1. **Today’s Core Tactical Objective:** The single most important outcome the lawyer must achieve before the Judge (e.g. *"Secure an ad-interim injunction restraining the Defendant from altering land character"*).
2. **Bench Brief:** 3–4 sentence executive orientation to read to the Judge when the matter is called.
3. **Key Chronology Highlights:** The 3–5 crucial dates (e.g., date of Bainapatra, date of notice, date of refusal).
4. **Evidence Battle Board:** Two parallel columns:
   - ✅ **In Hand (Ready for Bench):** Exhibits physically ready to submit.
   - ⚠️ **Missing / Risky Proofs:** Weak points or uncertified copies opponent counsel will attack.
5. **Argument Battle Matrix:** Anticipated opposing arguments mapped directly to statutory counter-arguments.
6. **Witness Cross-Examination Deck:** Exact questions to put to hostile witnesses, what admission each question elicits, and a caution alert if the witness goes evasive.
7. **Stand-Up Closing Submission / Prayer:** A word-for-word courtroom speech with a **📋 Copy Prayer** button.

---

### ⚖️ Feature 2: Matter Consistency Checker & Evidence Matrix
* **Endpoint:** `POST /api/matter/consistency-check`
* **What it does:** Cross-examines all notes, audio transcripts, and pleadings in the case to catch factual contradictions and proof gaps before the opposing counsel or court finds them.

#### What’s Inside the Audit:
1. **Case Integrity Score:** An instant percentage rating (e.g., `85%`) plus an executive litigation verdict.
2. **Factual Contradictions Finder:**
   - **Date Clashes:** Notice claimed dispatched on the 12th, but postal receipt shows booking on the 18th.
   - **Financial Sum Mismatches:** Cheque amount vs. legal notice demand vs. stated debt in petition.
   - **Property Identity Clashes:** Discrepancies between CS, SA, RS, and BS Dag/Khatian numbers or Mouza boundaries.
   - **Severity Badges:** `CRITICAL` (jeopardizes maintainability/limitation), `WARNING`, and `ADVISORY`.
   - **Remedy / Cure:** Step-by-step practical action the advocate can take to resolve the flaw before filing.
3. **Evidentiary Proof Matrix Table:**
   - Breaks down the claim or defense into essential statutory elements.
   - Displays: *Legal Issue* → *Supporting Evidence* → *Status Pill (`PROVED`, `PARTIAL`, `VULNERABLE`, `MISSING`)* → *Evidence Gap to Cure*.

---

### 📝 Feature 3: Source-Linked Legal Memo Generator (IRAC Method)
* **Endpoint:** `POST /api/matter/legal-memo`
* **What it does:** Generates a formal, partner-level legal memorandum analyzing any complex legal question grounded strictly in the matter facts.

#### Formal Memo Sections:
* **Chambers Header:** TO (Senior Advocates & Briefing Counsel), FROM (Justor AI), MATTER, DATE, QUESTION PRESENTED.
* **Executive Short Answer:** Direct conclusion in 2–3 sentences.
* **Material Facts Considered:** Bulleted factual matrix extracted from the case file.
* **Controlling Statutory Provisions:** Full statutory rules from the Bangladesh Code (Penal Code, CrPC, CPC, Limitation Act, Specific Relief Act, NI Act, etc.).
* **Binding Supreme Court Precedents:** High Court & Appellate Division citations with official law reports (**DLR, BLD, BLC, ALR**).
* **IRAC Legal Analysis:** Deep analytical reasoning (*Issue*, *Rule of Law*, *Application to Client Facts*, *Conclusion*).
* **Counterarguments & Vulnerabilities:** What judges or adversaries will push back on.
* **Practical Recommendations:** Concrete advocate action items.
* **Exact Source Quotations:** Specific statutory sections and precedential ratio snippets with 1-click citation copy.

---

### 🚀 Feature 4: Matter-Aware Legal Research Bridge
* **What it does:** Connects the active matter file directly to Justor AI's deep legal RAG chat without forcing the advocate to re-explain the case.
* **How it works:** Clicking **"Research in Justor AI"** builds a rich background dossier containing parties, case number, court forum, facts, timeline, and statutes, and loads it into the main chat composer ready for instant exploration.

---

## 4. Chamber Intelligence Foundation (Suite 1.0) Recap

For new teammates, here are the core Chamber OS tools that form the foundation:

| Feature | Endpoint | User Value |
| :--- | :--- | :--- |
| **🎙️ Lawyer Dictaphone** | `POST /api/matter/voice-note` | Lawyers speak into their mic in Bengali or English; AI extracts parties, amounts, property details, and next steps into structured cards. |
| **🎧 Consultation Audio** | `POST /api/matter/audio-consultation` | Upload a 20–30 min client consultation recording (up to 25MB); AI provides verbatim transcript, executive summary, mentioned documents, and legal red flags. |
| **📄 Case in 60 Seconds** | `POST /api/matter/document-summary` | Summarizes complex judgments/petitions in 60s, isolating the authoritative **Ratio Decidendi**, operative decree, and student-mode FIRAC. |
| **⏳ Matter Chronology** | `POST /api/matter/chronology` | Converts messy dispute facts into a sorted timeline while alerting to **Limitation Act, 1908** statutory deadlines (`active`, `urgent`, `expired`). |
| **📁 Matter Vault** | Client-Side Storage | Saves all notes, audio, briefs, hearing packs, and memos locally in `localStorage['justor_matters_v1']` with zero privacy leak. |

---

## 5. WhatsApp 24/7 Legal Helpline & Case Status Bot

* **Endpoints:** `POST /api/whatsapp/simulate`, `/twilio`, `/meta`
* **Sandbox Interface:** Accessible via the topbar WhatsApp button (`src/v3/whatsapp-modal.ts`).
* **Key Use Cases for Citizens & Advocates:**
  1. **Instant Legal Q&A:** Answers questions on divorce, inheritance, bail, cheque dishonour, land title, and labour law in bilingual Bengali & English.
  2. **Cause-List Status:** Inquires about High Court Division and District Court hearing dates and order updates.
  3. **Voice Note & Document Ingestion:** Citizens can send voice notes or photograph summons/notices on WhatsApp; Justor AI parses and explains them in simple language.

---

## 6. Mobile Responsiveness & Courtroom Usability

Advocates spend 70% of their workday away from a desktop. Justor AI is fully optimized for mobile devices (`<768px`):
* **Drawer Navigation:** Responsive slide-over modal that fills mobile viewports with comfortable touch padding.
* **Scrollable Tabs Bar:** Horizontal scrolling with hidden scrollbars for smooth one-thumb navigation.
* **Dual-Grid Stacking:** Evidence boards and argument matrices automatically stack into single-column vertical cards on phones.
* **Touch-Friendly Tables:** Evidence Matrix table is wrapped in `-webkit-overflow-scrolling: touch` to allow smooth horizontal inspection without page distortion.
* **Large Tap Targets:** Minimum 44px height on all buttons, mic toggles, and dropdown selectors.

---

## 7. Technical Cheat Sheet: API Endpoints & Payloads

### 1. Hearing Preparation Pack
```bash
POST /api/matter/hearing-pack
Content-Type: application/json

{
  "matter": {
    "title": "Rahim v. Karim",
    "caseNumber": "Title Suit No. 104 of 2023",
    "court": "Joint District Judge, 1st Court, Dhaka",
    "clientName": "Md. Rahim Uddin",
    "matterType": "civil",
    "notes": [...],
    "chronology": [...]
  },
  "hearing_type": "injunction",   # general | bail | injunction | charge_hearing | cross_examination | final_argument
  "language": "en"               # en | bn
}
```

### 2. Consistency & Evidence Audit
```bash
POST /api/matter/consistency-check
Content-Type: application/json

{
  "matter": { ... },
  "language": "en"
}
```

### 3. Legal Memo Generator
```bash
POST /api/matter/legal-memo
Content-Type: application/json

{
  "matter": { ... },
  "question_presented": "Whether the suit is barred by limitation under Article 113 of Limitation Act in light of part performance under s.53A TPA?",
  "language": "en"
}
```

---

## 8. Step-by-Step 60-Second Demo Script (For Sales, Pitches & Demos)

When demoing Justor AI to an advocate, bar association leader, or investor, use this exact sequence:

1. **Open Matter Intelligence:**
   - Click **"Chamber OS"** in the top navigation.
   - Show how matters are cleanly organized by client and case title.
2. **Show the Lawyer Dictaphone (15s):**
   - Click the **Dictaphone** tab.
   - Click **"ভয়েস টাইপিং / Start Speaking"** and say:  
     *"Client Abdur Rahman came today regarding a registered Bainapatra of Mirpur land dated 12 March 2018. Cheque of 10 lakh taka bounced last week."*
   - Click **"Structure into Matter Note"** → Point out how parties, amounts, and relevant laws appear automatically!
3. **Run the Consistency Checker (15s):**
   - Click the **"Consistency & Proof"** tab.
   - Click **"Run Consistency & Evidence Audit"**.
   - Show the **Factual Contradictions** alert (e.g. date discrepancies) and the **Evidentiary Proof Matrix** (missing deeds vs. proved facts). Advocates are instantly wowed by this!
4. **Generate the Courtroom Hearing Pack (15s):**
   - Click the **"Hearing Pack"** tab.
   - Select **"Ad-Interim Injunction (Order 39 CPC)"** and click **"Generate"**.
   - Show the **Bench Objective**, **Evidence in Hand vs. Risky**, **Cross-Examination questions**, and the **Stand-up Closing Submission** with 1-click copy!
5. **Draft the Legal Memo (15s):**
   - Click the **"Legal Memo"** tab.
   - Click the quick chip: **"NI Act Security Cheque"**.
   - Click **"Generate Legal Memo"** → Scroll through the formal IRAC structure, Supreme Court DLR citations, and quotable passages.
   - Conclude: *"This saves a chamber associate 4 to 6 hours of drafting time every single day."*

---

## 9. Frequently Asked Questions (FAQ) & Talking Points

### Q: "Is client confidential data stored on your cloud servers?"
> **Answer:** **No.** All matter dossiers, audio notes, and witness details live in the advocate's own browser storage (`localStorage: justor_matters_v1`). Payloads sent for AI analysis are processed statelessly in memory and are never saved or trained upon.

### Q: "What if the AI hallucinates a non-existent statute or precedent?"
> **Answer:** Justor AI is strictly grounded in the official **Bangladesh Code** and reported decisions of the Supreme Court of Bangladesh (**DLR, BLD, BLC**). Our prompts enforce verifiable legal provisions and source quotations.

### Q: "Does it support both Bengali and English?"
> **Answer:** **Yes, 100%.** Every single feature—from voice dictation and audio consultations to courtroom hearing packs and legal memoranda—can be run in legal Bengali (বাংলা) or professional legal English.

### Q: "What happens if Gemini hits a rate limit or goes down?"
> **Answer:** Justor AI has an automated **4-tier resilience fallback cascade**. If Gemini is slow or unavailable, the system automatically and instantly routes the prompt to Groq (Llama 3.3 70B / OpenAI-OSS), OpenRouter, or Alibaba DashScope within seconds with zero dropped requests.

---

## 10. Verification & Quality Checklist

- [x] **Backend Syntax & Compilation:** `py_compile` passes with exit code 0.
- [x] **Live Inference Verified:** Live tests confirmed on `/api/matter/hearing-pack`, `/api/matter/consistency-check`, and `/api/matter/legal-memo`.
- [x] **Frontend Type-Check:** `tsc --noEmit` returns 0 errors.
- [x] **Asset Bundler:** `npm run build` succeeds cleanly in <1s.
- [x] **Mobile Responsiveness:** Verified on viewport widths down to 360px.
- [x] **Git Repository:** Committed and synchronized to `main`.

---

## 11. Team Contact & Feature Ownership

* **Product & Architecture:** Justor AI Core Engineering Team
* **Legal Domain & Regulatory Alignment:** Supreme Court & District Bar Advisors
* **Backend & Fallback Engine:** `backend/matter_service.py` & `backend/backend.py`
* **Frontend Chambers Workspace:** `src/v3/matter-workspace.ts` & `src/v3/style.css`
* **WhatsApp Bot & Simulator:** `backend/whatsapp_service.py` & `src/v3/whatsapp-modal.ts`

*Justor AI — Empowering the Legal Mind with Sovereign Intelligence.*
