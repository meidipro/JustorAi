# Justor AI — A–Z Master Context, Product Strategy & Execution Plan

This is the **canonical founder-level context for Justor AI as of 15 August 2026**. It combines the product decisions, technical architecture, trust philosophy, market strategy, pilot design, pricing, legal-data approach, benchmark lessons, GTM, funding direction, and long-term vision we have developed.

You can use this as the base context for **developers, designers, advisors, lawyers, investors, accelerators, Cursor/Claude/GPT coding agents, pitch decks, grant applications, product documentation, and future Justor planning.**

---

# 1. What Justor AI Is

**Justor AI is an evidence-first, bilingual legal intelligence platform starting in Bangladesh.**

It is not primarily:

- a generic legal chatbot;
- an AI lawyer;
- a ChatGPT wrapper;
- a lawyer marketplace;
- a legal blog;
- or a citizen Q&A website.

The stronger positioning is:

> **Justor is building the legal-intelligence layer for Bangladesh.**

And eventually:

> **Verified legal intelligence infrastructure for underserved legal systems.**

The fundamental philosophy is:

> **Justor should never ask a lawyer to trust Justor. Justor should make it fast for the lawyer to verify Justor.**

That principle should govern **the product, backend, UI, data ingestion, citations, answer generation, legal updates, case research and marketing.**

---

# 2. The Central Problem

Bangladesh's legal information exists, but legal knowledge is fragmented.

A lawyer may need to check:

- an Act;
- a section;
- amendments;
- whether the provision is still current;
- related legislation;
- Supreme Court judgments;
- relevant paragraphs;
- procedural rules;
- government circulars;
- official gazettes;
- secondary explanations.

The problem therefore isn't merely:

> "Can AI answer a legal question?"

The real problem is:

> **Can someone reach the correct current authority, understand it quickly, and independently verify every important proposition?**

That is where Justor should win.

---

# 3. The Three Audiences — But Not Three Equal Businesses

Justor has three experiences:

### 1. Lawyers / Legal Professionals
The **core commercial product**.

### 2. Citizens
The **distribution, awareness, SEO and legal-navigation layer**.

### 3. Law Students
The **education, adoption and future-lawyer acquisition layer**.

This hierarchy is important.

The strategy should not become:

> 33% Citizen + 33% Student + 33% Lawyer.

Instead:

**Lawyer intelligence → main economic engine**

**Citizen legal information → distribution engine**

**Students → adoption/future professional funnel**

---

# 4. Justor's Long-Term Product Architecture

Think of Justor as:

```text id="y778id"
                         JUSTOR
              VERIFIED LEGAL INTELLIGENCE
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
     Citizen           Student           Lawyer
        │                 │                 │
   Navigation         Learning         Research
   Guides             Research         Cases
   Rights             Moots            Statutes
   Authorities        Cases            Documents
   Complaints         Concepts         Amendments
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                   TRUST ENGINE
                          │
              Primary Legal Authorities
                          │
     Statutes • Amendments • Cases • Gazettes
                          │
                     JUSTOR API
                          │
                     JUSTOR MCP
```

Eventually, Justor becomes infrastructure rather than merely a website.

External AI systems could query:

```text id="es0cuo"
get_current_section()
search_cases()
get_case_passage()
find_amendments()
verify_citation()
get_legal_authority()
```

through Justor MCP/API.

---

# 5. The First Screen

When someone enters `/app`, the product should establish context immediately.

Something close to:

## Who are you?

### Citizen
**Understand your rights and what to do next.**

### Law Student
**Learn laws, cases and legal concepts.**

### Lawyer / Legal Professional
**Research laws, cases and authorities faster.**

The mode selected should affect:

- UI;
- retrieval;
- prompts;
- evidence requirements;
- available tools;
- terminology;
- answer format;
- LLM usage;
- pricing;
- telemetry.

This is not just a cosmetic role selector.

It changes how Justor works.

---

# 6. Citizen Mode

Citizen Mode should **not burn expensive LLM tokens on every interaction**.

Much of citizen legal navigation can be deterministic.

The primary experience should therefore be:

## Structured Legal Guides

For example:

```text id="0ly5cs"
My issue
   ↓
What category does it belong to?
   ↓
What authority handles it?
   ↓
What documents do I need?
   ↓
What should I do first?
   ↓
Where do I submit/apply/complain?
   ↓
What happens next?
   ↓
Official sources
```

A citizen should see things such as:

- what the issue generally means;
- relevant authority;
- required documents;
- step-by-step procedure;
- government portal;
- complaint mechanism;
- statutory basis;
- official source;
- relevant office;
- what to do if the first route fails.

Initial guide areas already discussed include things around:

- land/property;
- registration;
- mutation;
- tax;
- consumer complaints;
- public-service grievances;
- common legal procedures.

A **10-guide authority engine** has already been part of the launch planning.

---

# 7. Citizen AI Usage

Citizen AI should exist, but as the second layer.

Example:

```text id="v5f4pz"
Citizen Guide
     ↓
"Does your situation differ?"
     ↓
Ask Justor
     ↓
AI uses approved guide + law + authority sources
```

A recent product direction included approximately:

**3 free contextual AI questions per day for citizens.**

That is much more economical than unlimited citizen chat.

Citizen mode should also be stricter about complex questions.

Where lawyer-level interpretation is needed:

> "This issue may require professional legal advice."

And eventually:

**Find a Lawyer**

can connect the citizen to professionals.

But the marketplace should **not be a launch dependency**.

---

# 8. Student Mode

Student Mode exists between public education and professional research.

It should help students understand:

- Acts;
- sections;
- legal concepts;
- terminology;
- landmark cases;
- case facts;
- issues;
- holdings;
- ratio;
- relevant statutory provisions;
- relationships between statutes.

Example:

> Explain Section X in simple language.

Student answer:

```text id="voq8so"
Simple explanation

What the section says

Key elements

Example

Related provision

Important cases

Source

Read official law
```

---

# 9. Moot / Legal Education Layer

Later Student Mode can develop into something much more interesting:

## Virtual Moot Court

Example workflow:

```text id="imbd63"
Choose proposition
      ↓
Choose side
      ↓
Prepare argument
      ↓
AI challenges argument
      ↓
Student cites authorities
      ↓
AI questions citations
      ↓
Feedback
```

That could become particularly useful for:

- university legal societies;
- moot competitions;
- classroom learning;
- legal research exercises.

However, this should follow the professional research engine rather than distract from it.

---

# 10. Lawyer Mode — The Flagship

This is where Justor should become exceptional.

A lawyer should be able to ask:

> Is an agreement for sale executed on 1 June still registrable on 25 July under the current law?

and Justor should not merely respond:

> Yes.

It should build an evidence chain.

---

# 11. Ideal Lawyer Answer Structure

A strong response can follow:

## Conclusion

The immediate answer.

## Applicable Law

Exact statutory provisions.

## Analysis

Application of the law to the facts.

## Current-Law Check

Whether the provision has:

- been amended;
- substituted;
- repealed;
- omitted;
- superseded;
- or otherwise changed.

## Relevant Cases

Where appropriate.

## Verification

Every important proposition links back to authority.

Then:

**Open official source**

**View section**

**View amendment**

**View judgment passage**

The lawyer should be able to verify the core answer in seconds.

---

# 12. IRAC Is Useful — But Evidence Matters More

Justor can use:

- Issue;
- Rule;
- Application;
- Conclusion.

But IRAC by itself doesn't create trust.

The correct principle is:

> **Claim → Evidence → Authority**

For every material proposition.

Example:

```text id="khru20"
CLAIM
A document must ordinarily be presented within X period.

EVIDENCE
Section XX states ...

AUTHORITY
Registration Act, 1908
Official Laws of Bangladesh

[Open Section]
```

This should be almost a UI primitive inside Justor.

---

# 13. The Source-Centric Philosophy

Nothing important should require blind trust.

Every major legal proposition should ideally carry:

- statute name;
- section;
- subsection;
- amendment status;
- effective date where relevant;
- exact passage;
- official source;
- direct source link;
- retrieval timestamp/version where useful.

For cases:

- case name;
- court;
- division;
- case number;
- judgment date;
- bench;
- relevant paragraph/page;
- exact supporting passage;
- official judgment PDF.

---

# 14. Justor Source Hierarchy

The hierarchy we've established is:

## Tier 1 — Primary Authorities

Use whenever available.

### Laws of Bangladesh / BD Laws
For legislation.

### Supreme Court / official judgment source
For cases.

### National Board of Revenue
For taxation.

### Ministry of Land
For land services and procedures.

### Registration Directorate
For registration notices/procedure.

### DNCRP
For consumer matters.

### Government GRS
For public-service grievances.

---

## Tier 2 — Other official material

- gazettes;
- circulars;
- notifications;
- government notices;
- rules;
- regulations;
- official administrative materials.

---

## Tier 3 — Reliable secondary sources

Only for:

- explanation;
- historical background;
- context.

Never use:

> randomlegalblog.com

as the authority when the statute itself exists.

---

# 15. Trust Hierarchy Inside the Answer Engine

Source weighting should approximately follow:

```text id="sz6rjp"
Official statute
        ↓
Official amendment/gazette
        ↓
Official Supreme Court judgment
        ↓
Government circular/notification
        ↓
Trusted institutional material
        ↓
Secondary commentary
```

Retrieval should not simply find the most semantically similar paragraph.

It should retrieve the **most authoritative relevant legal evidence**.

---

# 16. The Core Technical Principle

A generic RAG pipeline looks like:

```text id="oe13ke"
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Top chunks
   ↓
LLM
   ↓
Answer
```

That is insufficient for serious legal research.

Justor requires a **legal evidence pipeline**.

---

# 17. Recommended Justor Answer Pipeline

```text id="c4lmch"
USER QUESTION
      │
      ▼
ROLE DETECTION
Citizen / Student / Lawyer
      │
      ▼
INTENT CLASSIFIER
      │
      ▼
LEGAL DOMAIN CLASSIFIER
Land / Civil / Criminal / Tax / Registration / etc.
      │
      ▼
ENTITY EXTRACTION
Act / Section / Case / Date / Legal Issue
      │
      ▼
EXACT LEGAL LOOKUP
      │
      ├── Exact statute
      ├── Exact section
      ├── Exact subsection
      └── Version lookup
      │
      ▼
CURRENT LAW GATE
      │
      ├── Amendment?
      ├── Repeal?
      ├── Omission?
      ├── Substitution?
      └── Effective date?
      │
      ▼
RELATED AUTHORITY RETRIEVAL
      │
      ├── Relevant Acts
      ├── Rules
      ├── Judgments
      └── Gazettes
      │
      ▼
EVIDENCE PACKAGE
      │
      ▼
ANSWER GENERATION
      │
      ▼
CLAIM / CITATION VALIDATION
      │
      ├── supported → continue
      │
      └── unsupported → regenerate
      │
      ▼
SECOND VALIDATION
      │
      ├── passes → output
      │
      └── fails → abstain
      ▼
FINAL SOURCE-LINKED ANSWER
```

This is fundamentally different from an ordinary chatbot.

---

# 18. Exact Section Lookup Must Come Before Vector Search

One of the earlier failure classes involved substring collisions.

For example:

```text id="2bvu0v"
Section 4
```

must not accidentally retrieve:

```text id="wugttx"
Section 14
Section 40
Section 44
```

Therefore explicit statutory references must use canonical matching.

Example conceptually:

```python id="k5yf8x"
.eq("section_number", section)
```

rather than fuzzy matching.

Regression tests should explicitly cover:

**Section 4 ≠ Section 40.**

---

# 19. Subsection Normalization

The system also needs canonical handling for references such as:

```text id="3pfig6"
96(1)
190(1)(b)
53B
Order XXXIX
Rule 1
Rule 2
```

This has already been identified as a benchmark requirement.

A canonical representation might convert:

```text id="3a7pe0"
section 96 ( 1 )
s.96(1)
96(1)
Section 96(1)
```

to the same retrieval key.

---

# 20. Current-Law Gate

This may ultimately become one of Justor's strongest moats.

The system should know that:

```text id="ilc7i8"
LAW ≠ STATIC TEXT
```

A section exists inside a timeline.

Example model:

```text id="ei60a6"
Act
 │
 ├── Original provision
 │
 ├── Amendment 1
 │
 ├── Amendment 2
 │
 └── Current provision
```

Metadata should eventually include:

```text id="44j78m"
act
section
version
effective_from
effective_to
amendment_act
gazette
status
source_url
```

Then Justor can answer:

> Current as of 15 August 2026.

rather than blindly retrieving an old provision.

---

# 21. Answer Validation

This is critical.

The LLM should never be permitted to invent citations and have another layer silently make them look valid.

The architecture should be:

```text id="v2gkk6"
Generate
   ↓
Extract claims
   ↓
Extract citations
   ↓
Validate against retrieved evidence
   ↓
Unsupported?
   ↓
Regenerate
   ↓
Still unsupported?
   ↓
ABSTAIN
```

The correct response is sometimes:

> I couldn't verify this proposition from the approved sources currently available.

That is better than plausible legal misinformation.

---

# 22. The Justor Trust Contract

Every legal response should end in one of three states:

### 1. Supported answer

Enough evidence exists.

### 2. Clarification

Important facts are missing.

### 3. Abstention

Available evidence does not support a reliable answer.

Never:

### 4. Confident improvisation.

---

# 23. Database Architecture

The database decision is important because Supabase limits already became a real constraint.

The preferred separation is:

## Project A — Core Legal Intelligence

Contains:

- users;
- authentication;
- statutes;
- sections;
- law versions;
- amendments;
- citizen guides;
- workflows;
- feedback;
- telemetry;
- advisor reviews;
- benchmark metadata.

---

## Project B — Cases

Contains:

- Supreme Court judgments;
- case metadata;
- judgment text;
- page passages;
- embeddings;
- ratio/headnotes where properly generated;
- citations;
- case relationships.

Project B should **not be exposed directly to the frontend**.

The API accesses it.

This separation also prevents the existing law corpus from consuming all capacity needed for cases.

---

# 24. Case Data Strategy

The Supreme Court ingestion architecture discussed is approximately:

```text id="crhzcg"
Official case list
      ↓
PDF
      ↓
Text extraction
      ↓
OCR fallback
      ↓
Metadata extraction
      ↓
Paragraph/page segmentation
      ↓
Embedding
      ↓
Case database
```

Important metadata:

```text id="mkypb4"
case_title
court
division
case_number
judgment_date
bench
judges
acts_cited
sections_cited
page_number
paragraph
ratio
source_url
```

Embedding direction discussed:

**BGE-M3, 1024 dimensions.**

But exact deployments should be verified against the live database before migrations are run.

---

# 25. Case Corpus Status

There has been staging/review work around roughly **25 Supreme Court cases**.

A much larger **100–250 case ingestion target** has also been discussed.

The current strategic decision should remain:

> **Do not race toward hundreds of cases until the evidence validation, security, case isolation and benchmark pipeline work properly.**

Quality first.

Twenty-five verified cases can be more useful for a pilot than 5,000 badly structured judgments.

---

# 26. Document Intelligence V1

This is one of the highest-priority professional features.

Workflow:

```text id="wg5omc"
Upload document
      ↓
Extract structure
      ↓
Identify document type
      ↓
Identify important clauses/facts
      ↓
Generate structured summary
      ↓
Ask questions
      ↓
Answer from document
      ↓
Citation to exact page
```

Example documents eventually include:

- contracts;
- petitions;
- agreements;
- deeds;
- judgments;
- notices;
- pleadings;
- case files.

The initial version should focus on:

> **Understand → structure → summarize → question → verify.**

Not automated legal drafting of everything.

---

# 27. Lawyer Document Intelligence Should Be Evidence-Linked

A lawyer should see:

> The termination clause requires 30 days' notice.

And immediately:

**Page 7 · Clause 12.2**

rather than getting an unsupported summary.

This matches Justor's entire trust philosophy.

---

# 28. MCP Strategy

MCP is strategically important to Justor.

But not because:

> MCP magically makes API calls cheaper.

Its real benefits are:

- interoperability;
- modularity;
- model independence;
- controlled tool access;
- reduced context duplication;
- observability;
- external distribution;
- structured legal retrieval.

Initial MCP should remain:

**private + read-only.**

Possible first tools:

```text id="6e18gb"
search_law()
get_section()
search_cases()
```

or similar minimal evidence-backed operations.

Later:

```text id="vnjcyi"
get_current_section
find_amendments
search_judgments
get_judgment_passage
verify_legal_citation
resolve_authority
```

---

# 29. MCP Can Eventually Become Distribution

The long-term scenario is powerful.

A user might ask another AI product:

> What's the current Bangladesh law on X?

That model calls:

```text id="7wq2z2"
Justor MCP
```

which returns verified Bangladesh legal evidence.

At that point Justor is no longer merely competing for chatbot traffic.

It becomes **legal infrastructure**.

---

# 30. Legal Updates — A Major Professional Feature

Another strong Justor product direction is:

## Legal Updates

Not generic legal news.

Instead:

> **What changed in the law, why it matters, and where can I verify it?**

Initial launch areas we selected:

### Registration
### CrPC
### CPC
### Cyber

These categories quickly demonstrate the value.

---

# 31. Lawyer Legal Update Format

The first screen should provide a **30-second scan**.

Example:

## Registration Act amended in 2026

**Update:** Amendment  
**Jurisdiction:** Bangladesh  
**Affected provision:** Section X  
**Effective:** DATE  
**Impact:** Presentation period changed from X → Y

Then:

### What changed

**Before**

Old language.

**Now**

New language.

### What practitioners should check

Practical implications.

### Primary authority

Official Gazette

Official Act

Official source

Then a complete article underneath.

---

# 32. Legal Updates Must Be Bilingual

Every major update should support:

**English**

and

**বাংলা**

But both languages must point back to the **same evidence graph**.

Do not independently generate two unsupported legal articles.

Conceptually:

```text id="g94ydb"
Verified legal facts
      │
      ├── English presentation
      │
      └── Bangla presentation
```

That prevents translation drift.

---

# 33. News Versus Legal Intelligence

Eventually Justor may have a legal-news subscription.

But launch should focus on:

> **Law changed → show exactly what changed → explain implications → provide source.**

That is more defensible than trying to become a general legal newspaper.

---

# 34. Bilingual Strategy

Bangla is a major differentiator.

Citizens often need Bangla.

Students benefit from both.

Lawyers may prefer:

- statutes and case quotations in their authoritative language;
- explanation in English or Bangla;
- bilingual summaries.

The original legal text should **never be silently translated and presented as though it were the statutory wording.**

Always distinguish:

**Official text**

from

**Justor explanation/translation.**

---

# 35. UI Philosophy

The product should feel less like ChatGPT and more like:

> **Legal intelligence software with conversational access.**

Important UI primitives should include:

- source cards;
- authority badges;
- amendment badges;
- current-law status;
- case cards;
- quoted passage;
- page number;
- section references;
- source drawer;
- evidence panel;
- related authorities;
- confidence/verification status;
- save research;
- research history.

---

# 36. Lawyer Research Screen

A strong layout:

```text id="e53z7s"
┌──────────────────────────────────────────────┐
│ Ask Justor                                  │
└──────────────────────────────────────────────┘

Conclusion

Applicable Law
[Registration Act — §23] VERIFIED
[TPA — §54A] VERIFIED

Analysis

Relevant Cases

──────────────────────────────────────────────

Sources (4)

1. Registration Act, 1908
   Official Law
   [View §23]

2. Amendment Act, 2026
   Official Gazette
   [View amendment]

3. Supreme Court Case
   Page 14
   [View judgment]
```

Evidence should remain visible rather than hidden behind tiny superscript numbers.

---

# 37. Citizen UI Should Be Completely Different

Citizen:

```text id="l7yjue"
What do you need help with?

🏠 Land
📄 Registration
💰 Tax
🛒 Consumer complaint
🏛 Government service
...
```

Then:

```text id="ze5jrq"
Your next step

Documents needed

Where to go

What it may cost

What happens next

Official source

Need more help?
Ask Justor
```

This is simpler, cheaper and more useful than giving every citizen a blank chat box.

---

# 38. Law Student UI

Student interface can emphasize:

```text id="1bd12i"
Understand
Research
Cases
Moot
Saved Notes
```

The design should feel educational while retaining professional source credibility.

---

# 39. Security Is Part of Product Quality

A major issue previously found was an exposed frontend key:

`VITE_GROQ_API_KEY`

Any provider secret must be removed from frontend code immediately.

All privileged AI requests should go:

```text id="pa2ylg"
Frontend
   ↓
Backend
   ↓
Provider
```

never:

```text id="1sj3s6"
Frontend → secret API key
```

---

# 40. Authentication Strategy

Pilot stage:

**Closed, invite-only alpha.**

Do not open unrestricted signup yet.

Use:

- Supabase Auth;
- JWT validation;
- backend-derived user identity;
- role validation;
- Row Level Security;
- rate limiting;
- controlled CORS.

Do not trust:

```json id="mvmvy9"
{
  "user_id": "whatever-the-client-sends"
}
```

The backend derives user identity from verified authentication.

---

# 41. Privacy

Particularly important once lawyer documents are introduced.

Early pilot rules should include:

- no real confidential client files where avoidable;
- redact names;
- NIDs;
- phone numbers;
- TINs;
- home addresses;
- confidential case details;
- short retention;
- deletion controls;
- redacted telemetry;
- limited staff access.

Later Justor needs a serious privacy architecture because lawyers may upload highly confidential documents.

---

# 42. Safety Principle

Don't market:

> Zero hallucination.

That cannot responsibly be guaranteed.

Instead:

> **Source-linked answers with deterministic validation and abstention where evidence is insufficient.**

That's a much stronger claim.

---

# 43. What Went Wrong With Earlier Benchmarks

This is an important part of Justor history.

An earlier benchmark appeared much better than reality.

For approximately 45 questions, automated results appeared around:

- **29/45 “no red flags” — ~64.4%**
- strict section correctness roughly **15/45 — ~33.3%**

Some apparent 83–94% numbers were later discovered to be inflated because of evaluator/parser issues.

A later human review around 49 questions showed approximately:

- **17/49 strictly correct — 34.7%**
- **14/49 partial — 28.6%**
- **17/49 fail — 34.7%**
- **1 abstention**

This was an extremely useful discovery.

It proved:

> Don't optimize the score. Fix the evidence system.

---

# 44. Known Benchmark Weaknesses

Problems identified included:

- wrong Act classification;
- wrong section;
- substring section collision;
- inheritance-domain contamination;
- weak CrPC results;
- weak NAT results;
- incorrect golden answers;
- citation parser errors;
- incorrect evaluator logic;
- amendment/current-law failures.

Specific problematic benchmark items included things around:

`Q01`, `Q02`, `Q34`, `Q050`, `Q59`, `Q37`, `Q38`, `Q23`, `Q55`.

Contamination issues appeared around:

`Q17 / Q46`.

Important golden-answer corrections included matters involving:

- Land Reform §4;
- §96;
- CPC Order XXXIX.

The broader lesson matters more than the IDs:

> **The benchmark dataset itself must also be legally reviewed.**

---

# 45. Benchmark Philosophy Going Forward

The new benchmark should measure several independent dimensions.

Example:

```text id="lw05oy"
1. Correct legal domain
2. Correct Act
3. Correct section
4. Correct current version
5. Correct answer
6. Correct quotation
7. Citation exists
8. Citation supports claim
9. Relevant case authority
10. Unsupported claim count
11. Appropriate abstention
```

A lawyer-graded benchmark should precede any public claim such as:

> 92% legal accuracy.

---

# 46. Golden Answers Are Evidence Assets

Golden answers shouldn't merely be AI-generated ideal responses.

For each benchmark:

```text id="g2rlvp"
Question
Correct answer
Correct Act
Correct section
Correct version
Supporting evidence
Official citation
Common failure
Human legal review
```

The "human corrections" approach previously used in the CSV was directionally correct.

---

# 47. Regression Tests

At minimum, backend regression tests should include:

### Exact sections

`4 != 40`

### Role safety

Citizen queries cannot accidentally unlock unsupported professional case analysis.

### Citation binding

Quoted words must exist in the cited source.

### Current law

Old version cannot silently override current version.

### Whitelist

Related legislation must pass allowed relationship rules.

### Abstention

No supporting evidence must produce abstention.

These tests are more important than simply adding more prompts.

---

# 48. Current Product Stage

Justor should currently be treated as:

**early-stage / pre-revenue / controlled pilot.**

Not:

> market-leading legal AI with thousands of lawyers.

Do not oversell traction in grant or accelerator applications.

That honesty will actually help.

---

# 49. Pilot Strategy

The strongest approach remains:

> **Execution first.**

Instead of spending another three months building every feature:

1. make the trust pipeline reliable;
2. select a narrow corpus;
3. invite controlled users;
4. observe real failures;
5. improve;
6. generate evidence;
7. use that evidence for grants/investors.

---

# 50. Pilot Cohorts

Several rollout numbers have been discussed at different stages.

The disciplined interpretation is:

## Initial smoke test

Approximately:

- 2 lawyers;
- 3 students;
- 5 citizens.

≈10 controlled testers.

Then expand.

One earlier core pilot design targeted:

- **10 citizens**
- **5 students**
- **5 lawyers**

= **20 controlled product accounts.**

Longer controlled waves can move toward:

- 20 lawyers;
- 40 students;
- 100 citizens.

Those larger numbers should happen only after reliability improves.

---

# 51. Market Survey Is Not Product Usage

This distinction is critical.

The separate market-validation target discussed was roughly:

- 500 citizens;
- 100 students;
- 50 lawyers.

Those people should **not** automatically be described as:

> 650 Justor users.

Survey responses ≠ activated product accounts.

Demo views ≠ active users.

Survey willingness ≠ retention.

Keep product telemetry and market-validation data separate.

---

# 52. Pilot Success Metrics

Useful metrics include:

### Activation

Did the user complete a meaningful legal query?

### Evidence engagement

Did they open a citation/source?

### Helpful rate

Was the answer actually useful?

### Wrong-law rate

Did the system retrieve the wrong Act/domain?

### Unsupported-claim rate

Were statements unsupported by evidence?

### Abstention quality

Did it refuse when it should?

### Repeat usage

Did the user come back?

### Research time saved

Especially for lawyers.

### Source clicks

A particularly important Justor metric.

### Retention

Ultimately more meaningful than survey enthusiasm.

---

# 53. Original Pilot Targets

Earlier targets included:

> **>70% helpful**

and

> **<10% wrong**

with repeat use and NPS measured.

Those are useful pilot gates.

But the long-term target is obviously much higher.

The aspiration we discussed is:

> **8–9+/10 professional answer quality.**

That will depend more on evidence architecture than prompt engineering.

---

# 54. Telemetry

Telemetry is one of the immediate priority features.

Every answer should permit:

👍 Helpful  
👎 Not helpful

For negative feedback:

```text id="3dgyhe"
What was wrong?

□ Wrong law
□ Wrong section
□ Outdated law
□ Citation doesn't support answer
□ Missing authority
□ Incorrect interpretation
□ Other
```

This creates a **legal intelligence feedback dataset**.

Over time that itself becomes valuable.

---

# 55. Advisor Review Layer

A proposed Legal Advisory Council could contain specialists covering approximately:

- property/land;
- income tax;
- civil/appellate;
- criminal/procedure;
- technology/privacy/commercial.

Advisors do **not** need to manually approve every Justor answer.

Instead they can review:

- benchmark answers;
- answer templates;
- sensitive workflows;
- high-impact legal updates;
- representative research cards;
- major corpus issues.

Reviews should be logged.

---

# 56. Team Context

Core team context has included:

### Tajuddin Ahamed
Founder & CEO.

Primary responsibilities:

- vision;
- product;
- strategy;
- GTM;
- partnerships;
- fundraising;
- legal-tech positioning.

### Mehedi Hasan
CTO / technical execution.

Responsibilities around:

- backend;
- architecture;
- deployment;
- database;
- retrieval;
- engineering.

### Anisur Rahman Sanjib
COO / Legal QA direction.

Legal-quality and operational involvement.

An ESOP range around **5–8%** has been discussed, but this should remain treated as a company decision rather than a finalized fact unless formally executed.

---

# 57. Current Strategic Priority

The strongest current product sequence is:

### 1. Trust / RAG hardening

### 2. Lawyer Research

### 3. Document Intelligence V1

### 4. Telemetry

### 5. Lawyer Mode

### 6. Auth + dashboard

### 7. Corrected benchmark

### 8. Private MCP

### 9. Legal Updates

### 10. Controlled expansion

Not:

> marketplace → mobile app → enterprise → 20 countries.

---

# 58. What We Should Deliberately NOT Build Yet

Do not let Justor become bloated.

Defer:

- full marketplace;
- bidding system;
- native apps;
- huge social network;
- complex enterprise integrations;
- unrestricted legal drafting;
- international law databases;
- thousands of unverified cases;
- consumer subscription optimization;
- fancy analytics;
- public MCP;
- broad agent autonomy.

The company does not need 50 features.

It needs one thing lawyers repeatedly use.

---

# 59. The First Serious Lawyer Job-to-Be-Done

A strong formulation:

> **Find the current law and the authorities supporting it faster.**

That is narrower and stronger than:

> AI for lawyers.

Lawyers pay when Justor saves:

- research time;
- verification time;
- case discovery time;
- amendment checking;
- document reading time.

---

# 60. Document Intelligence Can Become Job #2

After research:

> **Understand a legal document and find the exact evidence inside it faster.**

Together:

```text id="e4qbkl"
External legal research
+
Internal document intelligence
```

become an excellent professional foundation.

---

# 61. Business Model

The cleanest eventual business model is:

```text id="gyj7lh"
Citizens
Mostly free
      │
      ▼
Students
Affordable
      │
      ▼
Lawyers
Professional subscription
      │
      ▼
Law firms
Team / institutional plans
      │
      ▼
API / MCP
Infrastructure pricing
```

---

# 62. Citizen Pricing

Citizen willingness-to-pay testing included roughly:

**৳99–199/month.**

But I would not optimize citizen subscriptions at launch.

Citizen is strategically more valuable as:

- distribution;
- SEO;
- awareness;
- trust-building;
- referral channel;
- market-data source.

---

# 63. Student Pricing

Options tested/discussed include approximately:

**৳200/month**

and potentially higher packages around:

**৳500/month**

depending on feature depth.

Again, students are not the immediate economic center.

---

# 64. Lawyer Pricing

Research explored ranges such as:

- ৳500–1,000/month;
- ৳1,000–2,500;
- ৳2,500–5,000;
- ৳5,000+.

A **৳200 founding pilot** has also been considered as a low-friction validation offer.

Important distinction:

৳200 should be framed as something like:

> **Founding Pilot Access**

rather than necessarily setting the permanent market price.

---

# 65. Future Lawyer Monetization

Eventually pricing could reflect:

### Solo
Individual advocate.

### Professional
Research + cases + document intelligence.

### Chambers
Multiple lawyers.

### Firm
Institutional legal intelligence.

### API
Developer/system access.

### MCP
Usage/infrastructure access.

But do not over-design pricing before repeat use exists.

---

# 66. GTM — Lawyers

The initial lawyer GTM should be founder-led.

Not Facebook ads.

Find 20 lawyers.

Watch them use it.

Ask:

> What were you researching yesterday?

Then actually solve that.

Potential acquisition channels:

- personal introductions;
- chamber relationships;
- bar networks;
- legal advisors;
- law faculties;
- NSU ecosystem;
- legal seminars;
- direct demos;
- referrals.

---

# 67. GTM — Citizens

Citizen growth is more content/search-led.

Example searches:

> জমি নামজারি কিভাবে করবো?

> property registration Bangladesh

> consumer complaint Bangladesh

> land mutation documents

> income tax return Bangladesh

Build source-backed guides around actual high-intent problems.

This creates organic discovery.

---

# 68. SEO + GEO Strategy

Every citizen article should be optimized for both:

## Search engines

and

## Generative engines.

Structure:

```text id="1yncur"
Question
Direct answer
Steps
Documents
Authority
Law
FAQ
Official sources
Last verified
```

This gives search engines and AI systems easily extractable factual units.

---

# 69. GTM — Students

Students can spread Justor through:

- universities;
- moot clubs;
- legal societies;
- case research;
- exam/study workflows;
- ambassador programs later.

Students become tomorrow's lawyers already familiar with Justor.

That creates a useful long-term moat.

---

# 70. Institutional Strategy

Universities can eventually be useful not just as customers but as:

- research partners;
- testing grounds;
- legal QA networks;
- student distribution;
- academic credibility.

Similarly, chambers and law firms can eventually contribute to professional validation.

---

# 71. NSU Startups Next

Justor has been developed in the context of **NSU Startups Next / Founders' Lab Cohort 4**.

Use that ecosystem for:

- mentors;
- pilot introductions;
- validation;
- pitch feedback;
- advisors;
- grant readiness;
- investor exposure.

But traction claims should remain factual.

---

# 72. Founder Pitch Lesson

One useful mentor lesson was:

Avoid opening with:

> Imagine...

Instead show the existing pain directly.

For example:

> A lawyer researching one legal question may have to search statutes, amendments and judgments across multiple sources before being comfortable that the answer is current.

Then demonstrate Justor.

Pain → workflow → evidence → outcome.

---

# 73. The Pitch

A strong short pitch:

> **Justor AI is building an evidence-first legal intelligence platform for Bangladesh. Lawyers can research current statutes, amendments and cases with every important proposition linked directly to the underlying authority. Citizens get structured legal navigation instead of an expensive unlimited chatbot, while law students get source-backed legal learning. We are starting with Bangladesh and building toward verified legal intelligence infrastructure for underserved legal systems.**

---

# 74. Even Shorter Positioning

For lawyer audiences:

> **Bangladesh legal research, with the evidence attached.**

Or:

> **Find the law. See what changed. Verify the authority.**

---

# 75. The Brand Promise

A strong internal product promise:

> **Nothing important in Justor should require blind trust.**

That should appear everywhere internally.

It is more important than saying:

> Powered by advanced AI.

---

# 76. Competitive Moat

The moat cannot simply be:

> We use GPT.

Everyone can.

The moat should develop from:

### 1. Versioned Bangladesh legislation

### 2. Amendment relationships

### 3. Structured Supreme Court corpus

### 4. Claim-bound citations

### 5. Legal authority graph

### 6. Human-corrected benchmark

### 7. User feedback dataset

### 8. Legal query telemetry

### 9. Bilingual legal understanding

### 10. Verification UX

### 11. MCP/API distribution

### 12. Institutional adoption

That combination becomes harder to replicate.

---

# 77. Legal Knowledge Graph — Long-Term

Eventually laws shouldn't exist merely as isolated chunks.

They should form a graph.

```text id="ag86b8"
Registration Act
      │
      ├── Section 23
      │      │
      │      ├── amended by Act X
      │      ├── interpreted in Case A
      │      └── related to Section Y
      │
      └── Section 24
```

Cases similarly connect:

```text id="dkpvzt"
Case
 ├── statute cited
 ├── section interpreted
 ├── precedent followed
 ├── precedent distinguished
 └── proposition established
```

This is far more powerful than embeddings alone.

---

# 78. Future Firm Product

Once individual research works, Justor can evolve into:

> **Institutional Legal Memory**

A firm could have:

```text id="9t53cg"
Public legal intelligence
+
Firm documents
+
Past matters
+
Internal precedents
+
Legal research
```

Then a lawyer asks:

> Have we handled a similar matter before?

Justor searches the firm's private knowledge alongside public legal authority.

That could become a high-value B2B product.

---

# 79. Long-Term Network Vision

Eventually:

```text id="9btaky"
Citizen
   ↓
Understands problem
   ↓
Needs professional help
   ↓
Verified lawyer

Lawyer
   ↓
Uses Justor research
   ↓
Handles case

Student
   ↓
Learns through Justor
   ↓
Becomes lawyer

Law firm
   ↓
Builds institutional memory

External AI
   ↓
Uses Justor legal API/MCP
```

At that stage Justor becomes a network.

But that is the destination, not the MVP.

---

# 80. Geographic Expansion Strategy

Bangladesh is the starting market.

Long-term target thesis:

> **Legal intelligence infrastructure for countries where law is fragmented, poorly indexed, multilingual or underserved by global legal-tech companies.**

Potential expansion directions we've considered include:

- MENA;
- ASEAN;
- Africa;
- UK adjacency where relevant.

But international expansion should follow evidence that the Bangladesh engine works.

---

# 81. Why Bangladesh Can Be the Wedge

Large global legal-AI companies focus heavily on markets such as the US and UK.

Bangladesh presents a different problem:

- fragmented information;
- Bengali + English;
- limited structured legal datasets;
- weak search UX;
- public legal-information gap;
- limited specialized AI infrastructure.

If Justor can solve these problems, the underlying architecture may transfer to other underserved jurisdictions.

---

# 82. Accelerator / Funding Strategy

Programs previously considered strong fits include:

- iDEA Pre-Seed;
- Hub71+ AI;
- 500 Global / Sanabil ecosystem;
- NVIDIA Inception;
- Startup Qatar;
- MBRIF;
- other MENA/ASEAN/Africa/UK accelerators.

The strategic funding narrative should be:

> We are not raising money to discover whether legal professionals need reliable information.

Instead:

> We are validating whether an evidence-first architecture can dramatically reduce legal research and verification time in underserved jurisdictions.

---

# 83. iDEA / Grant Evidence

For grant applications, focus on evidence:

- prototype;
- controlled users;
- legal advisors;
- benchmark;
- government-source integrations;
- product analytics;
- feedback;
- pilot outcomes;
- safety architecture.

Not exaggerated TAM alone.

---

# 84. Investor Story

The investor story should progress through four layers.

### Layer 1 — Bangladesh lawyer tool

Immediate use case.

### Layer 2 — Bangladesh legal network

Citizens + students + lawyers + institutions.

### Layer 3 — Legal intelligence infrastructure

Data + evidence + APIs + MCP.

### Layer 4 — Emerging-market expansion

Repeat infrastructure country by country.

That creates venture-scale upside while keeping the present product focused.

---

# 85. The Biggest Risks

## Risk 1 — Legal accuracy

The most important risk.

Mitigation:

- primary authorities;
- deterministic retrieval;
- current-law gate;
- citation validation;
- abstention;
- lawyer benchmark.

---

## Risk 2 — Bad underlying legal data

A great LLM cannot fix corrupted law.

Mitigation:

versioned ingestion + human review.

---

## Risk 3 — Overbuilding

Trying to build citizen + student + lawyer + marketplace + mobile + MCP simultaneously.

Mitigation:

lawyer core first.

---

## Risk 4 — Privacy

Particularly lawyer documents.

Mitigation:

strict storage architecture and data policies.

---

## Risk 5 — Weak willingness to pay

Lawyers may like the product but not pay.

Mitigation:

founder-led paid pilot.

---

## Risk 6 — Trust

Lawyers distrust AI.

Mitigation:

**don't ask them to trust the AI. Give them the evidence.**

---

# 86. Current Core Engineering Priorities

If I were turning all previous discussion into one technical priority list, it is:

### P0

Remove frontend secrets.

### P0

Authentication/JWT/RLS.

### P0

Exact statute/section retrieval.

### P0

Current-law gate.

### P0

Citation validation.

### P0

Abstention.

### P1

Correct domain classifier.

### P1

Case Project B.

### P1

Case passage retrieval.

### P1

Telemetry.

### P1

Correct benchmark.

### P2

Document Intelligence.

### P2

Private MCP.

### P2

Legal Updates.

Everything else comes afterward.

---

# 87. 30-Day Execution Direction

A disciplined near-term plan would look like:

## Week 1 — Trust foundation

Fix:

- secrets;
- auth;
- classifier;
- section lookup;
- subsection parser;
- current-law checking;
- citation validator;
- abstention;
- regression tests.

---

## Week 2 — Professional research

Build/polish:

- Lawyer Mode;
- evidence cards;
- case lookup;
- related authorities;
- source drawer;
- telemetry.

Run corrected benchmark.

---

## Week 3 — Controlled users

Start with a narrow invited cohort.

Collect:

- research queries;
- feedback;
- wrong-law reports;
- citation clicks;
- repeat use;
- research-time estimates.

---

## Week 4 — Improve + paid validation

Fix top recurring failures.

Introduce:

**Founding Lawyer Pilot**

Begin charging at least some users.

The first ৳200 earned from genuine repeated utility is strategically more valuable than another 100 features.

---

# 88. 90-Day Objective

By roughly three months, Justor should aim to prove:

### Product

Lawyers repeatedly use the research product.

### Trust

Answers are materially more verifiable than generic AI.

### Data

The legal corpus is structured and version-aware.

### Cases

A curated judgment corpus works.

### Revenue

At least a small number of lawyers pay.

### Retention

Some lawyers repeatedly return.

### Distribution

Citizen guides bring relevant search traffic.

### Students

University adoption experiments exist.

### Infrastructure

Private MCP works.

### Evidence

There is credible accelerator/investor data.

---

# 89. One-Year Direction

If the first three months work:

```text id="ypqo69"
Lawyer Research
      +
Document Intelligence
      +
Legal Updates
      +
Case Intelligence
      +
Firm Knowledge
      +
MCP/API
```

Then begin testing additional jurisdictions.

---

# 90. Justor's North-Star Metric

Long term I would avoid using:

> Number of answers generated.

A better north-star concept is:

> **Verified legal research sessions completed.**

Supporting metrics:

- source opened;
- citation verified;
- research saved;
- question resolved;
- user returned;
- lawyer paid.

This aligns the metric with Justor's actual value.

---

# 91. The Product Quality Standard

For lawyer answers, the target should eventually be:

> **9+/10 professional usefulness with independently verifiable evidence.**

But don't chase 9/10 by manipulating prompts.

A 9/10 answer requires:

```text id="w73g9l"
Correct question understanding
+
Correct legal domain
+
Correct statute
+
Correct section
+
Correct version
+
Correct supporting cases
+
Correct interpretation
+
Correct citation
+
Current source
+
Good writing
```

That is a systems problem.

---

# 92. What Justor Should Never Do

Never fabricate:

- statutes;
- sections;
- case names;
- quotations;
- amendments;
- dates;
- judges;
- gazettes;
- citations.

Never silently transform an incorrect generated citation into another citation.

Never present a paraphrase as statutory wording.

Never hide an old law version.

Never imply secondary commentary is primary authority.

Never call survey respondents "users."

Never claim legal accuracy without a lawyer-reviewed benchmark.

Never claim "zero hallucination."

---

# 93. What Justor Should Always Do

Whenever possible:

**Show the authority.**

**Show the exact provision.**

**Show what changed.**

**Show the case passage.**

**Show where the answer came from.**

**Show uncertainty.**

**Abstain when necessary.**

That is the operating system of the company.

---

# 94. The Strongest Justor Flywheel

Eventually:

```text id="67la40"
More professional users
        ↓
More real legal questions
        ↓
More failure telemetry
        ↓
Better benchmark
        ↓
Better retrieval
        ↓
Better evidence graph
        ↓
Higher trust
        ↓
More professional users
```

That is much more defensible than a generic LLM wrapper.

---

# 95. The Strategic Endgame

The biggest version of Justor is not:

> A legal chatbot for Bangladesh.

It is:

> **The trusted machine-readable legal intelligence infrastructure for jurisdictions that global legal-tech platforms have underserved.**

Starting with:

**Bangladesh.**

Starting customer:

**Lawyers.**

Distribution:

**Citizens.**

Future users:

**Students, firms and AI systems.**

Core asset:

**Verified legal evidence.**

Interface:

**Research + conversational intelligence.**

Infrastructure:

**API + MCP.**

Moat:

**structured legal data + versioning + authority graph + citations + feedback + workflow integration.**

---

# 96. Justor's One-Sentence Strategy

> **Build the most trustworthy way to research and verify Bangladesh law for lawyers first, use structured citizen legal information and students to create distribution, turn the resulting legal data and evidence infrastructure into API/MCP capabilities, and then expand that infrastructure into other underserved legal systems.**

---

# 97. The Internal Justor Doctrine

If the team remembers only ten things, remember these:

1. **Lawyers are the core business.**
2. **Citizens are navigation and distribution, not unlimited LLM chat.**
3. **Students are a future-lawyer acquisition channel.**
4. **Primary authority beats generated confidence.**
5. **Exact legal retrieval beats semantic similarity when a provision is known.**
6. **Current law matters more than merely finding law.**
7. **Every important claim must be verifiable.**
8. **Unsupported answers must abstain.**
9. **Do not scale the corpus before the trust pipeline works.**
10. **Justor's moat is legal intelligence infrastructure—not the model.**

---

# 98. Canonical Context for Future AI/Coding Sessions

When giving Justor to another AI agent, the essential context is:

> **Justor AI is an evidence-first bilingual legal intelligence platform starting in Bangladesh. Its core paying customer is the practicing lawyer. Citizens primarily use structured, source-linked legal guides and limited contextual AI; students use source-backed learning and legal research. Lawyer Mode provides current statutory research, amendment awareness, Supreme Court case retrieval, exact passages, IRAC-style synthesis and direct primary-authority verification. Justor's governing principle is: “Justor should never ask a lawyer to trust Justor; Justor should make it fast for the lawyer to verify Justor.”**
>
> **The architecture uses a FastAPI trust gateway and separate Supabase projects: Project A for users, statutes, versions, amendments, workflows and telemetry; Project B for Supreme Court cases. Explicit Act/section requests use deterministic canonical lookup before vector search. The pipeline performs role detection, legal-domain classification, Act/section extraction, exact retrieval, current-law/amendment checking, related-authority retrieval, evidence packaging, answer generation, claim-bound citation validation, regeneration and hard abstention. Primary sources are preferred: Laws of Bangladesh, official Supreme Court judgments, gazettes and relevant government authorities.**
>
> **The product is currently a controlled invite-only alpha/pilot, not an unrestricted public legal-AI service. Current priorities are security, authentication, exact section retrieval, current-law validation, citation enforcement, corrected lawyer-reviewed benchmarks, Lawyer Mode, Document Intelligence V1, telemetry, curated Supreme Court case ingestion, private read-only MCP and source-centric bilingual legal updates. Do not prioritize marketplace, mobile apps, unrestricted drafting, enterprise integrations or international expansion before core lawyer research demonstrates repeat usage and willingness to pay.**
>
> **The company should not claim zero hallucination or unsupported accuracy metrics. Every important legal proposition must be independently verifiable. Where approved evidence cannot support an answer, Justor must clarify or abstain. Long term, Justor aims to become verified legal intelligence infrastructure for underserved legal systems through structured legislation, amendments, cases, authority graphs, professional workflows, APIs and MCP.**

---

## Where Justor stands right now

The most important thing is that the company has moved past the question **“what should Justor be?”**

The answer is now fairly clear.

The next phase is execution:

**Trust engine → Lawyer research → corrected benchmark → controlled lawyers → repeat usage → paid validation → Document Intelligence → Legal Updates → MCP → institutional expansion.**

The company does **not** need another major strategic pivot at this stage.

It needs to make the lawyer experience **so source-centric and verifiable that comparing Justor with a generic LLM becomes obviously unfair.** That is the product standard I would use for every decision from this point forward. memcite
