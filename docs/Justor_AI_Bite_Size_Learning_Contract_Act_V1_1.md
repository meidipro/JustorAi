# Justor AI — Bite-Size Learning V1
## Contract Act 1872: Full Content + Visual + UI/UX Implementation Guide

**Version:** 1.0  
**Date:** 29 August 2026  
**Audience:** Taj (content/product) + Mehedi (engineering)  
**Pilot subject:** The Contract Act, 1872 (Bangladesh)  
**V1 size:** 50 cards across 8 micro-topics  
**Primary goal:** Make first-year contract law easy enough to learn in 3–6 minute swipe sessions, then route curiosity/weak areas into Justor AI chat.

---

# 1. Product in One Line

**Bite-Size Learning = curiosity hook → visual memory → scenario → reveal → legal rule → actual provision → swipe signal → AI depth.**

This is not a quiz-first feature. It is a **micro-learning engine**.

---

# 2. Research Basis and Scope

V1 is intentionally built around Contract Law because it is a first-year subject in Bangladesh LLB programs and naturally supports short scenario-based learning. BRAC University’s LAW102 course includes formation, offer, acceptance, counter-offer, invitation to treat, coercion, fraud, misrepresentation, undue influence, mistake, capacity, consideration, validity, void agreements, dissolution and remedies for breach. Dhaka University business-law curricula also cover the formation and core elements of contract law.

The legal rules below are drafted primarily from the **official Laws of Bangladesh text of the Contract Act, 1872** and, where needed, the **Majority Act, 1875**.

## Important correction from earlier planning

Do **not** market Contract Act V1 as directly mapped to the current Bangladesh Bar Council enrolment examination. The current Bangladesh Bar Council enrolment syllabus lists CPC, Specific Relief, CrPC, Penal Code, Evidence, Limitation, and Professional Ethics/Bar Council law—not Contract Act.

## Legal publishing rule

No card goes live merely because it was AI-generated. Every card must pass:

1. `provision_id` resolves to the correct current provision in Justor’s corpus.
2. English rule is legally reviewed.
3. Bangla principle is reviewed for natural language and accuracy.
4. Visual does not imply a materially different rule.
5. If the card relies on common-law doctrine rather than explicit statutory wording, it is tagged `authority_type = doctrine` and requires a reviewer-approved authority note.

---

# 3. V1 Information Architecture

```text
Law Student Workspace
└── Bite-Size Learning
    └── Contract Act 1872
        ├── 01 Foundations                         5 cards
        ├── 02 Offer, Invitation & Revocation      7 cards
        ├── 03 Acceptance                          5 cards
        ├── 04 Consideration                       7 cards
        ├── 05 Capacity to Contract                6 cards
        ├── 06 Free Consent                        7 cards
        ├── 07 Void Agreements                     6 cards
        └── 08 Breach, Discharge & Remedies        7 cards
                                                = 50 cards
```

Each topic should feel finishable in **3–6 minutes**.

---

# 4. Card Types

Use a mix so the deck never feels repetitive.

| Card type | Target count | Purpose |
|---|---:|---|
| Counterintuitive / “Wait, really?” | 15 | Curiosity and retention |
| Bangladesh scenario | 15 | Apply law to everyday situations |
| Myth-buster | 8 | Correct common misconceptions |
| Rule visualizer | 7 | Explain structure/process |
| Edge-case / nuance | 5 | Prevent oversimplification |
| **Total** | **50** | |

Every card still uses the same front/back interaction; “type” only changes the writing style.

---

# 5. Visual Mix — Exact V1 Count

| Visual format | Count | Use |
|---|---:|---|
| **Spline 3D hero scene** | **8** | One memorable concept per topic |
| **Nano Banana static illustration** | **30** | Default visual format |
| **Lottie/light motion** | **12** | Communication, timing, warning, signing, breakage, completion |
| **Total** | **50** | One visual per card |

## Global Nano Banana style prefix

```text
Flat minimalist legal-learning illustration for Justor AI,
clean premium educational UI aesthetic,
deep navy and electric blue accents,
soft off-white highlights,
simple geometric forms,
no written words inside the image,
no watermark,
no photorealistic humans,
clear single concept,
strong silhouette,
mobile-readable at small size,
1:1 square composition,
subject: [CARD-SPECIFIC SCENE]
```

## Spline rules

- 1 dominant object/concept only.
- Very light interaction: hover/touch rotation, small float, snap, break, balance, glow.
- Do not use a full 3D game scene.
- Performance target: poster image first; load interactive scene only when visible or tapped.
- Always store `poster_url` so low-end phones can fall back to static.

## Lottie rules

- 2–4 second seamless loop.
- No embedded legal text.
- Pause when card is offscreen.
- Respect `prefers-reduced-motion`.

---

# 6. Card Writing Rules

## Front

- Label: `DID YOU KNOW`, `TRY THIS`, or `MYTH CHECK`.
- Hook: **max 12 words**.
- Question/scenario: **max 35 words**.
- Do not show the answer accidentally through the image.
- Hook should create curiosity, not merely state a textbook heading.

## Back

- Answer: max 8 words.
- Explanation: **35–65 words**.
- Provision: exact Act + section.
- Bangla key principle: **max 22 words**, natural conversational Bangla.
- CTA: `View provision`.
- Swipe actions: `Got it` and `Review again`—never `Correct/Wrong`.

---

# 7. Full 50-Card Content Pack

> **Status:** Build-ready draft. The statutory propositions are researched, but all 50 should still be human legal-reviewed before public release.

---

## Topic 01 — Foundations (5 cards)

### Card 01 — Not every agreement is a contract
- **Type:** Counterintuitive
- **Visual:** **Spline 3D** — two people agree with a handshake; a glowing “law/enforceability” bridge appears only after the handshake.
- **Hook:** `Not every agreement is a contract.`
- **Question:** `You promise a friend you will meet for tea tomorrow. Is that automatically a legally enforceable contract?`
- **Answer:** `NO — not automatically.`
- **Explanation:** `A contract is an agreement enforceable by law. Section 10 adds the core requirements: free consent, competent parties, lawful consideration, lawful object, and no rule making the agreement void. A social promise may never reach that legal threshold.`
- **Provision:** `Contract Act 1872 — §§2(h), 10`
- **Bangla key:** `সব সমঝোতা চুক্তি নয়—আইনে কার্যকর করার মতো হলে তবেই contract.`
- **Asset prompt:** `two abstract figures shaking hands, a legal bridge lighting up underneath only after agreement`

### Card 02 — Acceptance changes a proposal
- **Type:** Rule visualizer
- **Visual:** **Lottie** — message bubble “offer” flies to another bubble, receives a check mark, then morphs into a sealed document icon.
- **Hook:** `An accepted proposal becomes something new.`
- **Question:** `Rafi offers to sell a desk to Nila for ৳5,000. Nila accepts. What has the proposal become?`
- **Answer:** `A PROMISE.`
- **Explanation:** `The Act says that when the person receiving a proposal signifies assent, the proposal is accepted; once accepted, it becomes a promise. This is the first transformation students should remember in contract formation.`
- **Provision:** `Contract Act 1872 — §2(b)`
- **Bangla key:** `প্রস্তাব গ্রহণ করা হলে সেটি promise বা প্রতিশ্রুতিতে পরিণত হয়.`
- **Asset prompt:** `offer message transforming into a sealed promise document after a check mark`

### Card 03 — Promisor vs promisee
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — two simple figures; one passes a glowing proposal orb, the other accepts it.
- **Hook:** `The buyer is not always the “promisor.”`
- **Question:** `Who is the promisor: the person making the proposal, or the person accepting it?`
- **Answer:** `The proposal-maker.`
- **Explanation:** `Under section 2(c), the person making the proposal is called the promisor, and the person accepting it is the promisee. The labels follow the proposal—not whether someone is buyer or seller.`
- **Provision:** `Contract Act 1872 — §2(c)`
- **Bangla key:** `যিনি proposal দেন তিনি promisor; যিনি গ্রহণ করেন তিনি promisee.`
- **Asset prompt:** `two abstract people, one sending a proposal orb to the other, simple directional arrows`

### Card 04 — Reciprocal promises
- **Type:** Rule visualizer
- **Visual:** **Nano Banana** — two arrows crossing: money one way, goods the other.
- **Hook:** `Many contracts are two promises crossing.`
- **Question:** `You promise to pay ৳2,000 and a seller promises to deliver a chair. What kind of promises are these?`
- **Answer:** `RECIPROCAL PROMISES.`
- **Explanation:** `Promises that form the consideration, or part of the consideration, for each other are reciprocal promises. Everyday sales are easy examples: payment and delivery are connected promises moving in opposite directions.`
- **Provision:** `Contract Act 1872 — §2(f)`
- **Bangla key:** `দুই পক্ষের পরস্পর-নির্ভর প্রতিশ্রুতি reciprocal promises.`
- **Asset prompt:** `money token moving left while chair package moves right, two clean crossing arrows`

### Card 05 — Void and voidable are different
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — split screen: one document faded/dead, one document with one party holding an “exit” handle.
- **Hook:** `Void and voidable do NOT mean the same thing.`
- **Question:** `One agreement cannot be enforced at all; another can be avoided by one party. Are they legally the same?`
- **Answer:** `NO.`
- **Explanation:** `A void agreement is not enforceable by law. A voidable contract remains enforceable at the option of one or more parties, but not the other. That difference matters throughout consent and mistake problems.`
- **Provision:** `Contract Act 1872 — §§2(g), 2(i)`
- **Bangla key:** `Void মানে আইনেই অকার্যকর; voidable মানে নির্দিষ্ট পক্ষ চাইলে বাতিল করতে পারে.`
- **Asset prompt:** `split legal documents, one completely faded, another with one-sided exit lever`

---

## Topic 02 — Offer, Invitation & Revocation (7 cards)

### Card 06 — Invitation to treat is not automatically an offer
- **Type:** Counterintuitive / doctrine
- **Visual:** **Nano Banana** — product on shelf with price tag, customer holding an offer bubble toward cashier.
- **Hook:** `A display can invite an offer without making one.`
- **Question:** `A shop displays a laptop with a price. Does the display always mean the shop is legally bound to sell to whoever points at it?`
- **Answer:** `NO — context matters.`
- **Explanation:** `Contract-law courses distinguish a true proposal from an invitation to treat. A display or advertisement may invite customers to make proposals rather than itself create a binding proposal. Because the Contract Act does not expressly define “invitation to treat,” attach a reviewer-approved doctrinal/case authority before publishing.`
- **Provision:** `Contract Act 1872 — §2(a) framework; doctrine requires approved authority`
- **Bangla key:** `দোকানের display সবসময় offer নয়; অনেক সময় এটি offer করার invitation.`
- **Asset prompt:** `store shelf with laptop and price tag, customer sending offer bubble to cashier`
- **Authority tag:** `doctrine_review_required`

### Card 07 — An offer must reach the other person
- **Type:** Scenario
- **Visual:** **Spline 3D** — message card travelling from one phone to another; it only glows when received.
- **Hook:** `An unseen offer has not finished communicating.`
- **Question:** `Sami writes an offer at 10 AM but the message reaches Rupa at 2 PM. When is communication of the proposal complete?`
- **Answer:** `When Rupa knows of it.`
- **Explanation:** `Communication of a proposal is complete when it comes to the knowledge of the person to whom it is made. Writing or sending it is not enough by itself.`
- **Provision:** `Contract Act 1872 — §4`
- **Bangla key:** `Proposal অন্য পক্ষের জানা হলে তার communication complete হয়.`
- **Asset prompt:** `3D message travelling between two phones, glow activates only on recipient phone`

### Card 08 — An offer can be revoked
- **Type:** Rule visualizer
- **Visual:** **Lottie** — offer paper moves forward, then reverse arrow pulls it back before a lock closes.
- **Hook:** `An offer is not untouchable once sent.`
- **Question:** `Can the proposer withdraw a proposal before the acceptance becomes complete against the proposer?`
- **Answer:** `YES.`
- **Explanation:** `Section 5 allows a proposal to be revoked any time before communication of acceptance is complete against the proposer—but not afterwards. Timing is therefore critical.`
- **Provision:** `Contract Act 1872 — §5`
- **Bangla key:** `Acceptance proposer-এর বিরুদ্ধে complete হওয়ার আগে proposal প্রত্যাহার করা যায়.`
- **Asset prompt:** `offer document being pulled back by reverse arrow just before a lock closes`

### Card 09 — Revocation must be communicated
- **Type:** Scenario
- **Visual:** **Nano Banana** — red withdrawal message visibly reaching the recipient.
- **Hook:** `Changing your mind privately changes nothing.`
- **Question:** `You decide at noon to cancel yesterday’s offer but tell nobody. Has the revocation been communicated?`
- **Answer:** `NO.`
- **Explanation:** `A proposal is revoked by communicating notice of revocation to the other party. A private decision inside the proposer’s mind is not enough.`
- **Provision:** `Contract Act 1872 — §6(1)`
- **Bangla key:** `মনে মনে offer বাতিল করলেই হবে না—revocation অন্য পক্ষকে জানাতে হবে.`
- **Asset prompt:** `person thinking red cancel symbol while recipient sees nothing, then a visible cancel message`

### Card 10 — Offers can die with time
- **Type:** Counterintuitive
- **Visual:** **Lottie** — offer card beside a clock; card fades as clock completes.
- **Hook:** `Some offers expire without anyone saying “cancel.”`
- **Question:** `An offer says “accept within 48 hours.” The recipient accepts five days later. Did the original offer survive?`
- **Answer:** `NO — it lapsed.`
- **Explanation:** `A proposal is revoked by lapse of the time prescribed for acceptance. If no time is prescribed, it can lapse after a reasonable time without communication of acceptance.`
- **Provision:** `Contract Act 1872 — §6(2)`
- **Bangla key:** `নির্ধারিত সময় পার হলে offer নিজেই lapse করতে পারে.`
- **Asset prompt:** `offer card fading next to countdown clock, clean motion loop`

### Card 11 — A condition can kill the offer
- **Type:** Scenario
- **Visual:** **Nano Banana** — checklist with one required box missing, causing offer bridge to break.
- **Hook:** `Ignore a required condition and the offer may disappear.`
- **Question:** `An offer requires a ৳1,000 booking deposit before acceptance. The recipient never pays it. Can the failure affect the proposal?`
- **Answer:** `YES.`
- **Explanation:** `A proposal may be revoked by the acceptor’s failure to fulfil a condition precedent to acceptance. The condition must be part of the acceptance setup, not invented later.`
- **Provision:** `Contract Act 1872 — §6(3)`
- **Bangla key:** `Acceptance-এর আগে প্রয়োজনীয় condition না মানলে proposal revoke হতে পারে.`
- **Asset prompt:** `legal checklist with one mandatory deposit box empty and a bridge segment dropping`

### Card 12 — Death does not always instantly erase an offer
- **Type:** Edge case
- **Visual:** **Nano Banana** — offer path continues until recipient receives a notification of death/insanity.
- **Hook:** `Death matters only when the acceptor knows in time.`
- **Question:** `The proposer dies before acceptance, but the acceptor has no knowledge of the death. Does section 6 treat knowledge as relevant?`
- **Answer:** `YES.`
- **Explanation:** `Section 6 provides for revocation by death or insanity of the proposer if the fact comes to the knowledge of the acceptor before acceptance. The knowledge element is important.`
- **Provision:** `Contract Act 1872 — §6(4)`
- **Bangla key:** `Proposer-এর মৃত্যু বা insanity acceptance-এর আগে acceptor-এর জানা গুরুত্বপূর্ণ.`
- **Asset prompt:** `proposal arrow, recipient phone receives serious notification before acceptance button`

---

## Topic 03 — Acceptance (5 cards)

### Card 13 — Acceptance cannot rewrite the offer
- **Type:** Counterintuitive
- **Visual:** **Spline 3D** — puzzle pieces “offer” and “acceptance”; acceptance piece only fits when unchanged.
- **Hook:** `“Yes, but…” may not be acceptance.`
- **Question:** `An offer is ৳20,000. The reply says, “I accept if you reduce it to ৳17,000.” Is that absolute acceptance?`
- **Answer:** `NO.`
- **Explanation:** `To convert a proposal into a promise, acceptance must be absolute and unqualified. A reply that changes the deal is not the clean acceptance section 7 requires.`
- **Provision:** `Contract Act 1872 — §7(1)`
- **Bangla key:** `Acceptance শর্তহীন ও সম্পূর্ণ হতে হবে; নতুন শর্ত দিলে সেটি clean acceptance নয়.`
- **Asset prompt:** `3D puzzle pieces labelled visually by shapes only, one altered piece cannot fit into offer slot`

### Card 14 — The proposer can prescribe a method
- **Type:** Scenario
- **Visual:** **Nano Banana** — three communication channels; one highlighted as the requested method.
- **Hook:** `How you accept can matter.`
- **Question:** `The offer asks for acceptance by signed email, but you send a voice note. Can the prescribed manner become relevant?`
- **Answer:** `YES.`
- **Explanation:** `Section 7 says acceptance should be in the prescribed manner when one is set. If acceptance uses another method, the proposer may insist on the prescribed method within a reasonable time; otherwise the proposer may be treated as accepting the alternative manner.`
- **Provision:** `Contract Act 1872 — §7(2)`
- **Bangla key:** `Offer-এ acceptance-এর নির্দিষ্ট পদ্ধতি থাকলে সেটি গুরুত্বপূর্ণ.`
- **Asset prompt:** `email, voice note and letter icons, one channel highlighted with a legal check`

### Card 15 — Actions can accept an offer
- **Type:** Rule visualizer
- **Visual:** **Lottie** — task instruction → person performs action → acceptance check appears.
- **Hook:** `You can accept without saying “I accept.”`
- **Question:** `A reward proposal asks someone to complete a specified task. Can performing the condition amount to acceptance?`
- **Answer:** `YES.`
- **Explanation:** `Performance of the conditions of a proposal, or acceptance of consideration offered with it for a reciprocal promise, can amount to acceptance. Contract formation can therefore happen through conduct.`
- **Provision:** `Contract Act 1872 — §8`
- **Bangla key:** `কাজ করে condition পূরণ করাও acceptance হতে পারে.`
- **Asset prompt:** `simple task card, action performed, glowing acceptance check appears automatically`

### Card 16 — Contracts can be implied
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — passenger boards a bus and pays fare without speech bubbles.
- **Hook:** `A contract does not always need spoken words.`
- **Question:** `You board a service, pay the stated fare and receive the service without negotiating aloud. Can promises be implied?`
- **Answer:** `YES.`
- **Explanation:** `Section 9 distinguishes express promises made in words from implied promises made otherwise than in words. Conduct can communicate contractual intention.`
- **Provision:** `Contract Act 1872 — §9`
- **Bangla key:** `কথা বা লেখা ছাড়াও আচরণ থেকে implied promise তৈরি হতে পারে.`
- **Asset prompt:** `passenger paying fare and receiving service, no speech bubbles, clean implied interaction`

### Card 17 — Postal acceptance has two completion moments
- **Type:** Edge case
- **Visual:** **Nano Banana** — letter leaves acceptor, midpoint marker for proposer, arrives later at proposer.
- **Hook:** `One acceptance can be “complete” at two different times.`
- **Question:** `B posts an acceptance to A. Is communication complete against A and B at exactly the same moment?`
- **Answer:** `NO.`
- **Explanation:** `Under section 4, acceptance is complete against the proposer when it is put into transmission beyond the acceptor’s power. Against the acceptor, it is complete when it comes to the proposer’s knowledge.`
- **Provision:** `Contract Act 1872 — §4`
- **Bangla key:** `Posted acceptance proposer ও acceptor-এর বিরুদ্ধে একই সময়ে complete নাও হতে পারে.`
- **Asset prompt:** `letter route with two milestone markers, send point and receive point`

---

## Topic 04 — Consideration (7 cards)

### Card 18 — Consideration may come from someone else
- **Type:** Counterintuitive
- **Visual:** **Spline 3D** — three nodes; third person provides value while promise connects the other two.
- **Hook:** `Consideration need not come only from the promisee.`
- **Question:** `Can “the promisee or any other person” provide the act, abstinence or promise that counts as consideration?`
- **Answer:** `YES.`
- **Explanation:** `Section 2(d) expressly says consideration may move from the promisee or any other person, so long as it is at the desire of the promisor and fits the statutory definition.`
- **Jurisdiction note:** `Bangladesh law differs from traditional English law here: under §2(d), consideration may move from the promisee or any other person.`
- **Provision:** `Contract Act 1872 — §2(d)`
- **Bangla key:** `Consideration শুধু promisee থেকেই আসতে হবে—এমন নয়.`
- **Asset prompt:** `3D three-node exchange network, third node sends value into a two-party promise connection`

### Card 19 — Consideration can relate to past, present or future acts
- **Type:** Rule visualizer
- **Visual:** **Nano Banana** — timeline with past, now, future icons all connecting to one promise.
- **Hook:** `Consideration is not trapped in the present.`
- **Question:** `The Act says a person “has done,” “does,” or “promises to do” something. What does that suggest?`
- **Answer:** `Timing can vary.`
- **Explanation:** `The language of section 2(d) covers an act or abstinence already done, being done, or promised for the future, provided the statutory requirements are met.`
- **Provision:** `Contract Act 1872 — §2(d)`
- **Bangla key:** `Consideration অতীত, বর্তমান বা ভবিষ্যৎ কাজের সঙ্গে যুক্ত হতে পারে.`
- **Asset prompt:** `simple timeline past present future, each point linked to a central promise icon`

### Card 20 — No consideration is usually a problem
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — promise document with an empty exchange side turning faded.
- **Hook:** `A bare promise is usually not enough.`
- **Question:** `A promises to gift B ৳10,000 later, with no consideration and no applicable exception. Is the agreement generally valid as a contract?`
- **Answer:** `NO — generally void.`
- **Explanation:** `Section 25 starts with the rule that an agreement without consideration is void, then creates specific exceptions. Students should learn both the default rule and the exceptions.`
- **Provision:** `Contract Act 1872 — §25`
- **Bangla key:** `সাধারণ নিয়মে consideration ছাড়া agreement void—তবে section 25-এ exception আছে.`
- **Asset prompt:** `promise document on one side of exchange scale, other side empty, document fading`

### Card 21 — Love can matter, but formalities matter too
- **Type:** Counterintuitive
- **Visual:** **Lottie** — heart between close relatives, then writing and registration stamp icons appear.
- **Hook:** `Love can support a contract—but not by itself.`
- **Question:** `Can natural love and affection between near relatives support an agreement without ordinary consideration?`
- **Answer:** `YES — with formalities.`
- **Explanation:** `Section 25(1) recognizes an exception where the agreement is in writing, registered, and made on account of natural love and affection between parties standing in a near relation. Do not teach this as “love alone is consideration.”`
- **Provision:** `Contract Act 1872 — §25(1)`
- **Bangla key:** `নিকট আত্মীয়ের love and affection exception-এ writing ও registration দুটোই জরুরি.`
- **Asset prompt:** `heart between two family figures, writing document and registration stamp animate into place`

### Card 22 — A later promise can reward a voluntary act
- **Type:** Scenario
- **Visual:** **Nano Banana** — person finds lost wallet, returns it; owner later gives reward promise.
- **Hook:** `A past voluntary act can sometimes support a later promise.`
- **Question:** `You voluntarily return someone’s lost wallet. Afterwards the owner promises you ৳1,000. Can section 25 recognize this?`
- **Answer:** `YES — potentially.`
- **Explanation:** `Section 25(2) covers a promise to compensate, wholly or partly, a person who has already voluntarily done something for the promisor, or something the promisor was legally compellable to do.`
- **Provision:** `Contract Act 1872 — §25(2)`
- **Bangla key:** `Promisor-এর জন্য আগে স্বেচ্ছায় করা কাজের compensation-এর promise বৈধ হতে পারে.`
- **Asset prompt:** `lost wallet returned to owner, later reward promise token appears`

### Card 23 — A time-barred debt can return through a signed promise
- **Type:** Edge case
- **Visual:** **Nano Banana** — old debt file marked expired; signed new promise revives a payment arrow.
- **Hook:** `An old unenforceable debt can still produce a new contract.`
- **Question:** `A debt is time-barred. The debtor signs a written promise to pay part of it. Can section 25 treat that promise as a contract?`
- **Answer:** `YES.`
- **Explanation:** `Section 25(3) recognizes a written and signed promise to pay wholly or partly a debt that could have been enforced but for limitation law. The writing/signature requirements matter.`
- **Provision:** `Contract Act 1872 — §25(3)`
- **Bangla key:** `Time-barred debt-এর লিখিত ও signed repayment promise নতুনভাবে enforceable হতে পারে.`
- **Asset prompt:** `old debt folder with expired clock, signed promise creates new payment arrow`

### Card 24 — Unequal value does not automatically destroy a contract
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — scale with very unequal objects but a green validity ring around the agreement.
- **Hook:** `Bad bargain does not automatically mean no contract.`
- **Question:** `A freely agrees to sell an item worth ৳10,000 for ৳1,000. Is the agreement void merely because the consideration is inadequate?`
- **Answer:** `NO — not merely for that.`
- **Explanation:** `Section 25 says a freely made agreement is not void merely because consideration is inadequate. But serious inadequacy may be relevant when a court asks whether consent was truly free.`
- **Provision:** `Contract Act 1872 — §25, Explanation 2`
- **Bangla key:** `Consideration কম হলেই contract void নয়; তবে free consent যাচাইয়ে তা গুরুত্বপূর্ণ হতে পারে.`
- **Asset prompt:** `unequal balance scale, small coin versus large object, green legal validity ring`

---

## Topic 05 — Capacity to Contract (6 cards)

### Card 25 — Majority is usually 18, but know the exception
- **Type:** Edge case
- **Visual:** **Spline 3D** — age gate at 18, with a smaller side path marked by guardian/court icon extending to 21.
- **Hook:** `“Adult at 18” has a statutory exception.`
- **Question:** `For people domiciled in Bangladesh, is 18 always the only majority age mentioned by the Majority Act?`
- **Answer:** `NO.`
- **Explanation:** `The general rule is majority at 18. But section 3 of the Majority Act provides a 21-year rule in specified situations involving a court-appointed guardian of person/property or Court of Wards superintendence. Contract Act section 11 ties capacity to the applicable age of majority.`
- **Provision:** `Contract Act 1872 — §11; Majority Act 1875 — §3`
- **Bangla key:** `সাধারণভাবে majority ১৮; তবে Majority Act-এর নির্দিষ্ট guardian/Court of Wards ক্ষেত্রে ২১ হতে পারে.`
- **Asset prompt:** `3D age gate 18 with side branch to 21 beside court guardian icon`

### Card 26 — Capacity requires more than age
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — three gates: majority, sound mind, no legal disqualification.
- **Hook:** `Being 18+ is not the whole capacity test.`
- **Question:** `If someone has reached majority, are they automatically competent to contract in every case?`
- **Answer:** `NO.`
- **Explanation:** `Section 11 requires three things: age of majority under the applicable law, sound mind, and no legal disqualification from contracting. Age is only one part of the capacity test.`
- **Provision:** `Contract Act 1872 — §11`
- **Bangla key:** `Capacity-এর জন্য majority, sound mind এবং কোনো legal disqualification না থাকা দরকার.`
- **Asset prompt:** `three clean gates in sequence: age, clear mind, legal permission`

### Card 27 — Sound mind is tested at the time of contracting
- **Type:** Counterintuitive
- **Visual:** **Lottie** — brain clarity meter fluctuates over time, contract sign appears only during clear state.
- **Hook:** `Capacity can change from one hour to another.`
- **Question:** `A person is usually of unsound mind but has a lucid interval. Can they contract during that interval?`
- **Answer:** `YES — if capable then.`
- **Explanation:** `Section 12 focuses on the person’s ability at the time of the contract: can they understand it and form a rational judgment about its effect on their interests? A usually unsound person may contract during a sound interval.`
- **Provision:** `Contract Act 1872 — §12`
- **Bangla key:** `Contract-এর সময় বোঝার ও rational judgment করার ক্ষমতাই মূল test.`
- **Asset prompt:** `brain clarity meter changing from cloudy to clear, contract can be signed only in clear phase`

### Card 28 — Intoxication can affect capacity
- **Type:** Scenario
- **Visual:** **Nano Banana** — blurred decision screen beside a contract, with clarity indicator below threshold.
- **Hook:** `Being drunk can become a contract-capacity issue.`
- **Question:** `A person is so drunk that they cannot understand the terms or judge the effect on their interests. Are they competent at that moment?`
- **Answer:** `NO.`
- **Explanation:** `Section 12 specifically illustrates that a normally sane person who is so drunk—or delirious from fever—that they cannot understand the contract or form a rational judgment cannot contract while that condition lasts.`
- **Provision:** `Contract Act 1872 — §12`
- **Bangla key:** `এত intoxicated হলে যে terms বোঝা যায় না, সেই সময়ে contractual capacity থাকে না.`
- **Asset prompt:** `blurred contract interface, low clarity gauge, simple non-glamorized intoxication symbol`

### Card 29 — Legal disqualification is a separate capacity block
- **Type:** Rule visualizer
- **Visual:** **Nano Banana** — adult and clear-mind icons pass, but a legal prohibition barrier blocks final step.
- **Hook:** `Age and sanity can still be insufficient.`
- **Question:** `Can a person be of majority age and sound mind yet still lack competence because another law disqualifies them?`
- **Answer:** `YES.`
- **Explanation:** `Section 11 expressly includes a third requirement: the person must not be disqualified from contracting by any law to which they are subject.`
- **Provision:** `Contract Act 1872 — §11`
- **Bangla key:** `অন্য কোনো আইন contract করতে নিষেধ করলে age ও sound mind থাকলেও capacity নাও থাকতে পারে.`
- **Asset prompt:** `age and clear-mind checkpoints passed, final legal barrier stops contract`

### Card 30 — Necessaries do not create ordinary personal liability
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — medicine/food/books supplied to incapable person; reimbursement arrow points to property, not the person.
- **Hook:** `Necessaries can be reimbursed from property.`
- **Question:** `A person incapable of contracting receives necessaries suited to their condition in life. From where can the supplier seek reimbursement under section 68?`
- **Answer:** `From that person’s property.`
- **Explanation:** `Section 68 creates a reimbursement rule for necessaries supplied to a person incapable of contracting, or someone they are legally bound to support. The statutory claim is against the incapable person’s property.`
- **Provision:** `Contract Act 1872 — §68`
- **Bangla key:** `Incapable person-কে necessaries দিলে reimbursement তার property থেকে পাওয়া যেতে পারে.`
- **Asset prompt:** `essential items delivered, repayment arrow points to property/asset box instead of person icon`

---

## Topic 06 — Free Consent (7 cards)

### Card 31 — Consent is not automatically free consent
- **Type:** Rule visualizer
- **Visual:** **Spline 3D** — central consent sphere surrounded by five pressure/error forces: coercion, undue influence, fraud, misrepresentation, mistake.
- **Hook:** `Saying “yes” does not always mean free consent.`
- **Question:** `Which five legal problems can prevent consent from being “free” under the Contract Act?`
- **Answer:** `Five listed causes.`
- **Explanation:** `Section 14 says consent is free when it is not caused by coercion, undue influence, fraud, misrepresentation, or mistake subject to sections 20–22. The issue is whether consent would have been given but for the improper cause.`
- **Provision:** `Contract Act 1872 — §14`
- **Bangla key:** `Coercion, undue influence, fraud, misrepresentation বা relevant mistake থাকলে consent free নাও হতে পারে.`
- **Asset prompt:** `3D central agreement sphere pressured by five distinct abstract forces`

### Card 32 — Coercion can involve property, not only physical threats
- **Type:** Counterintuitive
- **Visual:** **Lottie** — locked property icon used as pressure until contract is signed.
- **Hook:** `Coercion can target property too.`
- **Question:** `Someone unlawfully detains your property to force you into an agreement. Can that fit statutory coercion?`
- **Answer:** `YES.`
- **Explanation:** `Section 15 includes committing or threatening an act forbidden by the Penal Code and unlawfully detaining or threatening to detain property, when done to cause someone to enter an agreement.`
- **Provision:** `Contract Act 1872 — §15`
- **Bangla key:** `শুধু শারীরিক threat নয়—property unlawfully আটকিয়েও contract করালে coercion হতে পারে.`
- **Asset prompt:** `property box locked by pressure lever, contract signature appears under pressure`

### Card 33 — Influence becomes “undue” when will is dominated
- **Type:** Scenario
- **Visual:** **Nano Banana** — one larger figure controlling a decision lever connected to a vulnerable figure.
- **Hook:** `Trust can become legal pressure.`
- **Question:** `A person who can dominate another’s will uses that position to obtain an unfair advantage. What issue should you spot?`
- **Answer:** `UNDUE INFLUENCE.`
- **Explanation:** `Section 16 focuses on a relationship where one party is in a position to dominate the will of another and uses that position to obtain an unfair advantage. Certain authority, fiduciary, age, illness or distress situations may trigger the analysis.`
- **Provision:** `Contract Act 1872 — §16`
- **Bangla key:** `কারও will dominate করে unfair advantage নিলে undue influence হতে পারে.`
- **Asset prompt:** `one figure controlling a decision lever connected to a smaller vulnerable figure, abstract not violent`

### Card 34 — A promise you never intend to keep can be fraud
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — smiling promise card in front, hidden crossed-out intention behind it.
- **Hook:** `A fake future promise can be fraud.`
- **Question:** `At the moment of promising, a person already has no intention of performing and uses the promise to induce the contract. Can that be fraud?`
- **Answer:** `YES.`
- **Explanation:** `Section 17 includes a promise made without any intention of performing it as one form of fraud, when committed with intent to deceive or induce the other party into the contract.`
- **Provision:** `Contract Act 1872 — §17(3)`
- **Bangla key:** `শুরু থেকেই পালন করার intention না থাকা promise fraud-এর অংশ হতে পারে.`
- **Asset prompt:** `front-facing promise card with hidden crossed intention symbol behind it`

### Card 35 — Silence is usually not fraud
- **Type:** Myth-buster
- **Visual:** **Lottie** — silent speech bubble stays neutral, then turns warning-red only when duty-to-speak icon appears.
- **Hook:** `Silence is usually NOT fraud.`
- **Question:** `A seller knows a fact that could affect a buyer. Is silence automatically fraud every time?`
- **Answer:** `NO.`
- **Explanation:** `Section 17 says mere silence about facts likely to affect willingness to contract is not fraud. Exceptions arise where the circumstances create a duty to speak or where silence itself is equivalent to speech. Teach the exception carefully.`
- **Provision:** `Contract Act 1872 — §17, Explanation`
- **Bangla key:** `Mere silence সাধারণত fraud নয়; duty to speak বা silence-as-speech হলে exception হতে পারে.`
- **Asset prompt:** `silent speech bubble neutral, then warning activates only after duty-to-speak symbol appears`

### Card 36 — Honest falsehood can still be misrepresentation
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — person sincerely passes wrong information from a faulty info card, without deception symbol.
- **Hook:** `You can misrepresent without trying to deceive.`
- **Question:** `A person states something untrue believing it to be true, but without adequate basis, and it misleads the other party. Could this be misrepresentation?`
- **Answer:** `YES.`
- **Explanation:** `Section 18 includes positive assertions not warranted by the maker’s information even when the maker believes them true, along with other innocent misleading conduct described in the section.`
- **Provision:** `Contract Act 1872 — §18`
- **Bangla key:** `ইচ্ছাকৃত deception না থাকলেও ভুল assertion misrepresentation হতে পারে.`
- **Asset prompt:** `person passes incorrect info from a faulty source card, no malicious symbols`

### Card 37 — Both parties can be wrong enough to make the agreement void
- **Type:** Scenario
- **Visual:** **Nano Banana** — buyer and seller both point to an item that is already destroyed/offline.
- **Hook:** `A shared mistake can erase the agreement.`
- **Question:** `Both parties contract for a specific item, unaware it had already been destroyed. What can happen if the fact was essential?`
- **Answer:** `The agreement is void.`
- **Explanation:** `Section 20 makes an agreement void where both parties are under a mistake about a fact essential to the agreement. By contrast, section 22 says one party’s factual mistake alone does not merely by itself make the contract voidable.`
- **Provision:** `Contract Act 1872 — §§20, 22`
- **Bangla key:** `Essential fact নিয়ে দুই পক্ষই ভুল হলে agreement void হতে পারে; এক পক্ষের mistake alone যথেষ্ট নয়.`
- **Asset prompt:** `buyer and seller both pointing to a product that is already broken or unavailable, shared error symbol`

---

## Topic 07 — Void Agreements (6 cards)

### Card 38 — Illegal purpose destroys the agreement
- **Type:** Scenario
- **Visual:** **Nano Banana** — normal contract path blocked by law shield when object becomes illegal.
- **Hook:** `A perfectly clear deal can still be void.`
- **Question:** `Two competent adults freely agree on clear terms, but the object of the agreement is forbidden by law. Is clarity enough to save it?`
- **Answer:** `NO.`
- **Explanation:** `Section 23 requires lawful consideration and lawful object. If the object or consideration is forbidden by law, defeats law, is fraudulent, injures person/property, or is regarded by the court as immoral or opposed to public policy, it is unlawful and the agreement is void.`
- **Provision:** `Contract Act 1872 — §23`
- **Bangla key:** `Terms clear হলেও object বা consideration unlawful হলে agreement void.`
- **Asset prompt:** `clean contract pathway hits a strong law shield due to illegal object icon`

### Card 39 — One illegal piece can poison the whole single bargain
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — one red illegal segment contaminates a connected multi-part contract chain.
- **Hook:** `One unlawful part can sink a combined agreement.`
- **Question:** `A single consideration supports several connected objects, and part of that consideration or an object is unlawful. Can the agreement be void?`
- **Answer:** `YES.`
- **Explanation:** `Section 24 provides that if part of a single consideration for one or more objects—or part of one of several considerations for a single object—is unlawful, the agreement is void.`
- **Provision:** `Contract Act 1872 — §24`
- **Bangla key:** `একটি combined agreement-এর consideration/object-এর অংশ unlawful হলেও পুরো agreement void হতে পারে.`
- **Asset prompt:** `multi-link contract chain, one red illegal link spreads warning through all connected links`

### Card 40 — Restraint of trade is generally void to that extent
- **Type:** Myth-buster
- **Visual:** **Nano Banana** — professional walking toward work while a contract tries to chain the pathway; a small goodwill-sale exception gate appears.
- **Hook:** `A contract cannot freely ban your lawful trade forever.`
- **Question:** `An agreement restrains someone from exercising a lawful profession, trade or business. What is the general statutory rule?`
- **Answer:** `Void to that extent.`
- **Explanation:** `Section 27 makes agreements restraining lawful profession, trade or business void to that extent, subject to the statutory goodwill-sale exception and its reasonableness/local-limit conditions.`
- **Provision:** `Contract Act 1872 — §27`
- **Bangla key:** `Lawful profession/trade/business restrain করা agreement সাধারণভাবে ওই অংশে void.`
- **Asset prompt:** `professional path blocked by contract chain, small goodwill sale exception gateway nearby`

### Card 41 — You generally cannot contract away ordinary legal enforcement absolutely
- **Type:** Scenario
- **Visual:** **Nano Banana** — contract tries to lock courthouse door; arbitration side-door remains visible.
- **Hook:** `A contract cannot simply erase the courthouse.`
- **Question:** `A clause absolutely prevents a party from enforcing contractual rights through ordinary tribunals. Is that automatically safe?`
- **Answer:** `NO.`
- **Explanation:** `Section 28 makes such absolute restrictions void to that extent and also addresses clauses limiting the time for enforcing rights. The section preserves specified arbitration agreements, so do not teach it as an anti-arbitration rule.`
- **Provision:** `Contract Act 1872 — §28`
- **Bangla key:** `Court-এ contractual right enforce করা একেবারে বন্ধ করে দেওয়া clause সাধারণভাবে void; arbitration exception আছে.`
- **Asset prompt:** `courthouse door blocked by contract lock, separate arbitration route remains open`

### Card 42 — Unclear terms can make an agreement void
- **Type:** Rule visualizer
- **Visual:** **Lottie** — blurry contract object becomes clear when specification appears; without it, red void pulse.
- **Hook:** `Too vague can mean no contract.`
- **Question:** `A agrees to sell B “100 tons of oil,” with nothing showing what kind of oil is intended. What issue appears?`
- **Answer:** `UNCERTAINTY.`
- **Explanation:** `Section 29 says agreements whose meaning is not certain, or capable of being made certain, are void. Context can sometimes make apparently broad wording certain.`
- **Provision:** `Contract Act 1872 — §29`
- **Bangla key:** `Agreement-এর meaning certain বা certain করা সম্ভব না হলে তা void.`
- **Asset prompt:** `blurry oil container and contract becoming clear only when specification icon appears`

### Card 43 — Wagering agreements are void
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — two people stake money on uncertain event; contract stamp fades to void.
- **Hook:** `Winning the bet does not make the wager enforceable.`
- **Question:** `Two people make an agreement purely by way of wager on an uncertain event. What is the Contract Act’s rule?`
- **Answer:** `The agreement is void.`
- **Explanation:** `Section 30 says agreements by way of wager are void and bars suits for recovering something alleged to be won on a wager or entrusted to a person to abide by the result.`
- **Provision:** `Contract Act 1872 — §30`
- **Bangla key:** `Wagering agreement void; জেতা অর্থ contract claim হিসেবে recover করা যায় না.`
- **Asset prompt:** `two abstract figures staking coins on uncertain event wheel, legal document fades to void`

---

## Topic 08 — Breach, Discharge & Remedies (7 cards)

### Card 44 — Refusing the whole promise can let the other party end the contract
- **Type:** Counterintuitive
- **Visual:** **Spline 3D** — contract chain breaks when one party pulls away; other party receives an exit option.
- **Hook:** `A serious refusal can end the deal before completion.`
- **Question:** `One party refuses to perform the promise entirely or disables themselves from performing it. Can the promisee put an end to the contract?`
- **Answer:** `YES — generally.`
- **Explanation:** `Section 39 allows the promisee to end the contract where the other party refuses to perform the promise wholly or disables themselves from performing it, unless the promisee has signified acquiescence in continuing the contract.`
- **Provision:** `Contract Act 1872 — §39`
- **Bangla key:** `পুরো promise perform করতে refusal হলে promisee contract শেষ করতে পারে—যদি continuation-এ acquiesce না করে.`
- **Asset prompt:** `3D contract chain breaks as one side pulls away, exit option lights up for other side`

### Card 45 — Late performance does not always have the same effect
- **Type:** Scenario
- **Visual:** **Lottie** — deadline clock splits into two animated paths: “time essential” breaks contract; “not essential” shows compensation route.
- **Hook:** `Missing a deadline does not always kill the contract.`
- **Question:** `A promised date is missed. Does the contract always become voidable?`
- **Answer:** `NO — intention matters.`
- **Explanation:** `Section 55 distinguishes contracts where time was intended to be essential from those where it was not. If time is essential, the unperformed part may become voidable at the promisee’s option; otherwise compensation for loss from delay may be available instead.`
- **Provision:** `Contract Act 1872 — §55`
- **Bangla key:** `Deadline miss করলেই সব contract বাতিল হয় না—time essential ছিল কি না দেখতে হবে.`
- **Asset prompt:** `deadline clock branching into two legal paths, voidable versus compensation`

### Card 46 — A valid contract can later become void through impossibility or unlawfulness
- **Type:** Counterintuitive
- **Visual:** **Nano Banana** — contract starts green; unexpected barrier makes performance impossible, document turns neutral/void.
- **Hook:** `A valid contract can become void later.`
- **Question:** `After a contract is made, an uncontrollable event makes the promised act impossible or unlawful. What can happen?`
- **Answer:** `It becomes void then.`
- **Explanation:** `Section 56 says an agreement to do an act impossible in itself is void. It also says a contract later becomes void when the act becomes impossible or unlawful due to an event the promisor could not prevent.`
- **Provision:** `Contract Act 1872 — §56`
- **Bangla key:** `পরে performance impossible বা unlawful হলে contract সেই সময় থেকে void হতে পারে.`
- **Asset prompt:** `green contract path suddenly blocked by unavoidable barrier, document changes to void state`

### Card 47 — Parties can replace the old contract
- **Type:** Rule visualizer
- **Visual:** **Nano Banana** — old document slides out while a new document snaps into the same slot.
- **Hook:** `A new contract can extinguish the old one.`
- **Question:** `The parties agree to substitute a new contract, or to rescind or alter the old one. Must the original still be performed?`
- **Answer:** `NO.`
- **Explanation:** `Section 62 provides that where the parties agree to substitute a new contract, rescind the contract, or alter it, the original contract need not be performed.`
- **Provision:** `Contract Act 1872 — §62`
- **Bangla key:** `Novation, rescission বা alteration হলে original contract perform করতে নাও হতে পারে.`
- **Asset prompt:** `old contract slides out, new contract snaps into same legal slot, transformation arrows`

### Card 48 — Damages focus on foreseeable/direct loss, not every consequence
- **Type:** Counterintuitive
- **Visual:** **Lottie** — breach creates ripple; near/direct losses glow, distant ripple fades and is blocked.
- **Hook:** `Breach does NOT make you liable for every loss.`
- **Question:** `A breach indirectly triggers a distant chain of losses nobody contemplated. Are remote and indirect losses automatically compensable?`
- **Answer:** `NO.`
- **Explanation:** `Section 73 allows compensation for loss that naturally arose in the usual course or that the parties knew, when contracting, was likely from breach. It excludes remote and indirect loss and says available means of remedying inconvenience should be considered.`
- **Provision:** `Contract Act 1872 — §73`
- **Bangla key:** `Breach-এর natural/known likely loss recoverable হতে পারে; remote indirect loss নয়.`
- **Asset prompt:** `breach impact ripple, nearby losses highlighted, distant ripple fades behind legal boundary`

### Card 49 — A penalty amount is not automatically the payout
- **Type:** Counterintuitive
- **Visual:** **Spline 3D** — oversized penalty block drops onto a justice scale; the scale settles at a smaller “reasonable compensation” block beneath the contractual cap.
- **Hook:** `A written penalty is not automatically what you receive.`
- **Question:** `A contract names ৳500,000 payable for breach. Does section 74 automatically award the full ৳500,000?`
- **Answer:** `NO.`
- **Explanation:** `Section 74 allows reasonable compensation when a sum is named or a penalty is stipulated, but compensation cannot exceed the amount named or penalty stipulated. The written figure acts as a ceiling, not an automatic award in every case.`
- **Provision:** `Contract Act 1872 — §74`
- **Bangla key:** `Penalty amount পুরোটা automatic নয়; reasonable compensation হবে, named amount-এর বেশি নয়.`
- **Asset prompt:** `large penalty number on contract, balance scale adjusts it downward to reasonable amount cap`

### Card 50 — Rightful rescission can still lead to compensation
- **Type:** Scenario
- **Visual:** **Lottie** — contract is cleanly cancelled; compensation tokens flow to the party harmed by non-fulfilment.
- **Hook:** `Cancelling rightly does not erase your loss.`
- **Question:** `You rightfully rescind a contract because the other side fails to fulfil it. Can you still claim compensation for resulting damage?`
- **Answer:** `YES.`
- **Explanation:** `Section 75 provides that a person who rightfully rescinds a contract is entitled to compensation for damage sustained through the non-fulfilment of the contract.`
- **Provision:** `Contract Act 1872 — §75`
- **Bangla key:** `Rightfully rescind করলেও non-fulfilment-এর damage-এর compensation পাওয়া যেতে পারে.`
- **Asset prompt:** `contract cancellation animation followed by compensation tokens flowing to harmed party`

---

# 8. Asset Production Manifest

## 8 Spline hero cards

1. Card 01 — Agreement → enforceable contract bridge
2. Card 07 — Proposal communication/reception
3. Card 13 — Absolute acceptance puzzle
4. Card 18 — Consideration from third person
5. Card 25 — Age/capacity gate 18 ↔ exceptional 21 path
6. Card 31 — Five threats to free consent
7. Card 44 — Refusal/breach chain break
8. Card 49 — Penalty cap / reasonable compensation scale

## 12 Lottie cards

02, 08, 10, 15, 21, 27, 32, 35, 42, 45, 48, 50.

## 30 Nano Banana cards

All remaining cards.

---

# 9. UI/UX Implementation — Use the Current Justor Student Workspace

## 9.1 Entry point

Add a new sidebar/navigation item inside **Law Student Workspace**:

```text
[icon] Bite-Size Learning
```

Recommended icon: stacked cards / spark-book icon. Do not add another top-level product or separate login flow.

### Desktop

```text
┌──────────────────────────────────────────────────────────────────┐
│ JUSTOR AI                                                       │
├───────────────┬──────────────────────────────────────────────────┤
│ Student Home  │                                                  │
│ Ask Justor    │          Bite-Size Learning                      │
│ Library       │          existing workspace content area          │
│ Saved         │                                                  │
│ Bite-Size  ←  │                                                  │
│ ...           │                                                  │
└───────────────┴──────────────────────────────────────────────────┘
```

Keep the existing global sidebar, header, account state and language system. Bite-Size should feel like **one native workspace module**, not a microsite.

### Mobile

When a student starts a swipe session, switch to a near-full-screen learning canvas so browser chrome/sidebar does not compete with the card.

---

## 9.2 Screen A — Subject Browser

V1 shows one active course and future subjects as disabled/coming soon.

```text
BITE-SIZE LEARNING
Learn one legal idea at a time.

[ Contract Act 1872 ]
8 topics · 50 cards · Year 1
Continue: Offer & Revocation  43%

[ Constitutional Law ] Coming soon
[ Penal Code ]         Coming soon
[ Evidence ]           Coming soon
```

### Subject card fields

- Subject name
- One-line description
- Topic count
- Card count
- Intended level tag (`Year 1`)
- Overall progress
- `Continue` when progress exists
- `Start` when new

Do not label Contract Act as current Bar Council syllabus.

---

## 9.3 Screen B — Topic Browser

Use a vertical list on mobile and 2-column cards on wide desktop.

Each row shows:

```text
02  Offer, Invitation & Revocation
    7 cards · ~5 min
    █████░░  71%
    [Continue →]
```

### Topic state

- `not_started`
- `in_progress`
- `complete`
- `has_review_queue`

Completed topics receive a subtle check, not confetti every time.

---

## 9.4 Screen C — Swipe Session

### Mobile layout

```text
← Offer & Revocation                      EN | বাংলা
Card 3 of 7
███████████░░░░░░░░

        ┌────────────────────────┐
        │                        │
        │      VISUAL AREA       │
        │                        │
        │ DID YOU KNOW           │
        │                        │
        │ Some offers expire     │
        │ without “cancel.”      │
        │                        │
        │ Scenario/question      │
        │                        │
        │ [Tap to reveal]        │
        └────────────────────────┘

        ↻ Review    ⚑    ✓ Got it
```

### Desktop

Do not stretch the swipe card to full content width. Center it at approximately **420–520 px**, with supporting progress/shortcuts around it.

### Card sizing

- Mobile width: `calc(100vw - 32px)` max 430px
- Desktop max width: 480px
- Min height: 480px mobile where viewport allows
- Border radius: 20–24px
- Visual area: 35–42% of front
- Never put more than ~5 short lines in the explanation before scroll/clamp

---

## 9.5 Front state

Show:

1. visual
2. micro label
3. hook
4. scenario
5. `Tap to reveal`

**Do not allow right/left classification before reveal.** First swipe/tap can reveal; only after back is shown should `Got it` / `Review again` record progress.

---

## 9.6 Back state

```text
ANSWER
NO — context matters.

[plain-language explanation]

SOURCE CHECKED
Contract Act 1872 · Section 6(2)
[View provision →]

বাংলা key principle

↻ Review again      ✓ Got it
```

Recommended trust badge:

`SOURCE CHECKED`

Use `HUMAN LEGAL REVIEWED` only when a reviewer actually approved that version.

---

## 9.7 Gestures

```text
Tap card          → reveal back
Swipe right       → Got it
Swipe left        → Review again
Button right      → Got it fallback
Button left       → Review fallback
Flag button       → report sheet
```

Do not require swipe gestures; all actions must have visible buttons for accessibility and desktop use.

### Motion

- threshold: 72–88px horizontal
- exit: 280–360ms
- card rotation: max ±12–16°, not exaggerated Tinder-style ±30°
- next card: opacity + scale `0.97 → 1`
- flip: 300–420ms
- reduced-motion mode: dissolve front/back, no 3D rotation

### Stack illusion

Render two lightweight card backs behind active card:

```text
active: scale(1.00)
next:   scale(0.975) translateY(8px)
third:  scale(0.95)  translateY(16px)
```

---

## 9.8 Review semantics

Do **not** use `right/wrong` labels.

Use:

- `Got it`
- `Review again`

A card is teaching, not grading. Later quiz mode can score correctness.

---

## 9.9 Topic Complete screen

```text
Topic complete
Offer, Invitation & Revocation

7 cards reviewed
✓ 5 Got it
↻ 2 Review again

[Review 2 again]
[Go deeper with Justor AI →]
[Next topic]
```

Primary CTA depends on review state:

- if review > 0: `Review 2 again`
- secondary: `Go deeper with Justor AI`
- tertiary: `Next topic`

After the review queue reaches zero, promote `Go deeper` as primary.

---

# 10. Go Deeper → Justor AI Chat

Pass structured context rather than only a prefilled string.

```ts
interface LearningHandoff {
  subjectId: string;
  sectionId: string;
  sessionId: string;
  gotItCardIds: string[];
  reviewCardIds: string[];
  language: 'en' | 'bn';
}
```

Then generate a prompt server-side:

```text
I just completed “Offer, Invitation & Revocation” in Contract Act 1872.

I marked these as understood:
- ...

I marked these for review:
- ...

Teach the review concepts more deeply using Bangladesh law.
Start simply, then show the exact statutory provisions and practical examples.
Ask me one short check-for-understanding question at the end.
```

### Important

The LLM must re-run Justor’s normal legal retrieval/current-law/source-validation pipeline. Never trust the card text as the only legal source just because it came from the learning module.

---

# 11. Language UX

V1 should store **both English and Bangla for every student-facing sentence**, not only the hook.

Recommended schema fields:

```text
hook_en
hook_bn
question_en
question_bn
answer_en
answer_bn
explanation_en
explanation_bn
key_principle_en
key_principle_bn
```

Provision titles/source text remain linked to the official corpus; display official English text first if an official Bangla equivalent is unavailable in the corpus.

Fonts:

- Current Justor UI font for English
- `Hind Siliguri` or your existing Bangla production font for Bangla
- minimum body 15–16px mobile

Avoid machine-literal Bangla. Legal terms such as `offer`, `acceptance`, `consideration`, `void`, `voidable`, `coercion` can show English in parentheses during early learning.

---

# 12. Revised Database Schema

The old `image_url`-only idea is too restrictive. Use a flexible asset model.

```sql
create type learning_asset_type as enum (
  'image',
  'lottie',
  'spline',
  'icon'
);

create table learning_subjects (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title_en text not null,
  title_bn text not null,
  description_en text,
  description_bn text,
  level_tag text,
  corpus_act_id uuid,
  status text not null default 'draft',
  sort_order int default 0,
  created_at timestamptz default now()
);

create table learning_sections (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references learning_subjects(id) on delete cascade,
  slug text not null,
  title_en text not null,
  title_bn text not null,
  description_en text,
  description_bn text,
  estimated_minutes int default 5,
  sort_order int not null,
  status text not null default 'draft',
  unique(subject_id, slug)
);

create table learning_cards (
  id uuid primary key default gen_random_uuid(),
  section_id uuid not null references learning_sections(id) on delete cascade,
  sort_order int not null,
  card_type text not null,

  hook_en text not null,
  hook_bn text not null,
  question_en text not null,
  question_bn text not null,
  answer_en text not null,
  answer_bn text not null,
  explanation_en text not null,
  explanation_bn text not null,
  key_principle_en text,
  key_principle_bn text not null,

  act_name text not null,
  section_label text not null,
  provision_id uuid,
  authority_type text not null default 'statute',
  authority_note text,

  asset_type learning_asset_type not null default 'image',
  asset_url text,
  poster_url text,
  alt_en text,
  alt_bn text,
  accent_color text default '#1E38C8',

  review_status text not null default 'pending',
  reviewed_by text,
  reviewed_at timestamptz,
  content_version int not null default 1,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),

  unique(section_id, sort_order)
);

create table user_card_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id uuid not null references learning_cards(id) on delete cascade,
  state text not null check (state in ('got_it','review_again')),
  seen_count int not null default 1,
  reveal_count int not null default 1,
  last_seen_at timestamptz default now(),
  primary key (user_id, card_id)
);

create table learning_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  section_id uuid not null references learning_sections(id),
  started_at timestamptz default now(),
  completed_at timestamptz,
  cards_seen int default 0,
  got_it_count int default 0,
  review_count int default 0,
  go_deeper_clicked boolean default false,
  language text default 'en'
);

create table learning_card_reports (
  id uuid primary key default gen_random_uuid(),
  card_id uuid not null references learning_cards(id),
  user_id uuid references auth.users(id),
  issue_type text not null,
  note text,
  card_version int not null,
  status text not null default 'open',
  created_at timestamptz default now(),
  resolved_at timestamptz
);
```

## RLS

- Public/authenticated students: read only `review_status = 'approved'` + active subject/section.
- User may read/write only their own progress/sessions/reports.
- Content-admin role can create/update cards.
- Never expose unpublished drafts through normal student APIs.

---

# 13. Frontend Component Map

```text
features/bite-size/
├── pages/
│   ├── LearningHome.tsx
│   ├── SubjectPage.tsx
│   └── LearningSessionPage.tsx
├── components/
│   ├── SubjectCard.tsx
│   ├── TopicRow.tsx
│   ├── TopicProgress.tsx
│   ├── SwipeDeck.tsx
│   ├── LearningCard.tsx
│   ├── CardFront.tsx
│   ├── CardBack.tsx
│   ├── LearningAsset.tsx
│   ├── SwipeControls.tsx
│   ├── SourceBadge.tsx
│   ├── ReportSheet.tsx
│   ├── SessionSummary.tsx
│   └── LanguageToggle.tsx
├── hooks/
│   ├── useLearningSession.ts
│   ├── useSwipeGesture.ts
│   └── useLearningProgress.ts
├── api/
│   └── learning.ts
└── types.ts
```

### `LearningAsset.tsx`

```tsx
switch (card.asset_type) {
  case 'image':
    return <img ... />;
  case 'lottie':
    return <LazyLottie ... />;
  case 'spline':
    return <LazySpline poster={card.poster_url} ... />;
  default:
    return <IconFallback ... />;
}
```

Lazy-load Spline and Lottie so normal image cards stay fast.

---

# 14. API Contract

## Subject list

```http
GET /api/learning/subjects
```

Returns active subjects + user progress.

## Topic list

```http
GET /api/learning/subjects/:slug/sections
```

## Start/resume session

```http
POST /api/learning/sections/:id/session
```

Server returns only approved cards.

## Record card state

```http
PUT /api/learning/cards/:id/progress
{
  "state": "got_it" | "review_again",
  "session_id": "...",
  "time_spent_ms": 8100,
  "revealed": true
}
```

Use upsert for progress and an append-only analytics event for behavior data.

## Report

```http
POST /api/learning/cards/:id/report
{
  "issue_type": "wrong_legal_content",
  "note": "...",
  "card_version": 3
}
```

## Complete

```http
POST /api/learning/sessions/:id/complete
```

---

# 15. Report Sheet

Options:

```text
Wrong legal content
Wrong provision/source
Outdated law
Bangla translation problem
Visual is misleading
Explanation is confusing
Technical issue
Other
```

Add `Visual is misleading`; legal-learning images can create misconceptions even when text is correct.

If a card receives repeated serious reports, admin can set:

```text
review_status = 'flagged'
```

and it disappears from new sessions until re-approved.

---

# 16. Analytics

Track:

```text
learning_opened
learning_subject_opened
learning_topic_opened
learning_session_started
learning_card_revealed
learning_card_action
learning_card_reported
learning_topic_completed
learning_review_started
learning_review_completed
learning_go_deeper_clicked
learning_llm_handoff_started
learning_llm_first_response
learning_language_toggled
```

Useful payload:

```json
{
  "subject_id": "...",
  "section_id": "...",
  "card_id": "...",
  "card_version": 2,
  "action": "review_again",
  "time_to_reveal_ms": 4200,
  "time_after_reveal_ms": 6100,
  "asset_type": "spline",
  "language": "bn"
}
```

## V1 product metrics

1. **Cards viewed/session:** target ≥ 6
2. **Topic completion:** target ≥ 60%
3. **Go Deeper click:** target ≥ 25%
4. **7-day learning return:** target ≥ 30%
5. **Report rate:** target < 5%, but investigate by severity rather than only volume
6. **Review-again rate by card:** high values identify confusing concepts/cards
7. **Time to reveal:** helps identify weak hooks
8. **LLM follow-up rate after Go Deeper:** stronger metric than click alone

---

# 17. Content/Admin Workflow

```text
Draft card
   ↓
Provision link attached
   ↓
Legal reviewer checks rule + scenario
   ↓
Bangla reviewer checks natural translation
   ↓
Visual generated/built
   ↓
Visual QA against rule
   ↓
Approved
   ↓
Published
   ↓
Student reports / metrics
   ↓
Versioned correction if needed
```

Do not overwrite a published card silently. Increment `content_version` so reports/analytics can identify which version students saw.

---

# 18. Three-Week Implementation Plan

## Week 1 — Engine + first content

### Mehedi
- Add sidebar route/nav item.
- Apply DB migration + RLS.
- Build subject/topic APIs.
- Build `LearningCard`, front/back states, progress.
- Implement image asset path first.
- Add session persistence/resume.

### Taj/content
- Legal-review cards 01–25.
- Produce global visual style reference using 3 sample images.
- Generate approved Nano Banana assets only after the style reference is locked.
- Build first 4 Spline hero scenes.

## Week 2 — Full interaction + remaining content

### Mehedi
- Swipe gestures + button fallbacks.
- Review queue.
- Report sheet.
- EN/বাংলা complete fields.
- Lazy Spline/Lottie renderer.
- Topic completion screen.

### Taj/content
- Legal-review cards 26–50.
- Finish 8 Spline scenes.
- Finish 30 static images.
- Select/produce 12 Lottie motions.
- Bangla review all 50 cards.

## Week 3 — LLM handoff + QA

### Mehedi
- Structured Go Deeper handoff.
- Analytics events.
- Admin/report status hooks.
- Performance polish + prefetch.
- Accessibility/reduced-motion.

### Taj + reviewers
- Full mobile UX QA.
- Provision-link QA for every card.
- Visual legal-meaning QA.
- Test with 10–20 law students before wider pilot.

---

# 19. Performance Requirements

- First learning page interactive in <2.5s on normal mobile 4G target.
- Static image: WebP/AVIF preferred, roughly 50–150KB target.
- Spline: poster-first; do not preload all scenes in a topic.
- Lottie: lazy-load and pause offscreen.
- Prefetch only the next 1–2 cards.
- Cache active section JSON and static assets for resumed sessions.
- Keep swipe logic local; sync progress optimistically and retry on failure.

If the network fails after a swipe:

```text
UI action succeeds locally
→ queue progress event
→ small offline/sync indicator
→ sync when online
```

Do not block learning on every Supabase write.

---

# 20. Accessibility

- Visible `Got it` / `Review again` buttons; swipe is optional.
- Keyboard: left/right arrows after reveal; Space/Enter reveals.
- `aria-live` for answer reveal and session progress.
- Descriptive alt text for educational images.
- Do not depend on red/green alone; use text/icon + color.
- Respect `prefers-reduced-motion`.
- Minimum touch target 44px; preferred main actions 56–64px.
- Bangla line height ≥ 1.55.

---

# 21. Product Decisions to Lock Before Mehedi Starts

1. **Sidebar location:** place `Bite-Size Learning` under the existing student study/navigation group.
2. **Language:** V1 should support full EN/BN card text, not only a Bangla summary.
3. **Review policy:** no card becomes active without legal reviewer approval.
4. **Asset schema:** support image/Lottie/Spline from day one.
5. **Doctrinal card:** Card 06 (`Invitation to Treat`) needs an approved authority note before public release.
6. **Monetization:** make swipe learning generous/unlimited in pilot; let Go Deeper use normal Justor AI query limits. Validate engagement before adding artificial learning limits.
7. **No Bar Council claim:** do not label Contract Act as current enrolment-exam coverage.

---

# 22. Definition of Done — V1 Launch Checklist

## Content
- [ ] 50/50 cards legal-reviewed
- [ ] 50/50 provision links resolve correctly
- [ ] 50/50 English text approved
- [ ] 50/50 Bangla text approved
- [ ] Card 06 doctrinal authority approved
- [ ] no card contains unsupported “always/never” language

## Visual
- [ ] 8 Spline hero assets with poster fallback
- [ ] 30 Nano Banana images
- [ ] 12 Lottie/light motion assets
- [ ] all 50 visuals checked for misleading implications
- [ ] reduced-motion fallback works

## UI
- [ ] sidebar entry exists
- [ ] subject browser works
- [ ] topic progress works
- [ ] tap reveal works
- [ ] swipe + buttons work
- [ ] review queue works
- [ ] report sheet works
- [ ] `View provision` works
- [ ] Go Deeper handoff works
- [ ] mobile 320px tested
- [ ] Android Chrome tested
- [ ] iOS Safari tested
- [ ] desktop keyboard tested

## Data/analytics
- [ ] RLS verified
- [ ] draft/flagged cards cannot leak
- [ ] progress resumes across sessions
- [ ] card version captured in reports/events
- [ ] topic completion event fires once
- [ ] Go Deeper → LLM first-response funnel measurable

---

# 23. What NOT to Build in V1

- Leaderboards
- Streak economy/gamification coins
- Certificates
- Full spaced-repetition algorithm
- AI-generated cards live at runtime
- 200-card Contract Act library before pilot validation
- Multiple courses at launch
- Full 3D on every card
- Video lectures
- Scored MCQ exam mode
- User-generated public cards

First prove: **students open → swipe → complete → return → go deeper.**

---

# 24. After V1 Validates

Recommended expansion order:

1. Add 50 more Contract Act cards: performance, quasi-contract, indemnity, guarantee, bailment, agency.
2. Add quiz mode generated from already-reviewed learning objects.
3. Add weak-topic dashboard.
4. Add proper spaced review scheduling.
5. Add course-level roadmap.
6. Add next subject based on student demand and strongest existing Justor corpus coverage.
7. Only then scale toward 200+ cards.

---

# 25. Source Notes Used for This Plan

- **Laws of Bangladesh, Ministry of Law, Justice and Parliamentary Affairs — The Contract Act, 1872 (Act No. IX of 1872).** Primary legal source for sections 2–30, 39, 55–56, 62, 68, and 73–75 used above.
- **Laws of Bangladesh — The Majority Act, 1875 (Act No. IX of 1875), section 3.** Used for majority-age nuance.
- **BRAC University — Bachelor of Laws (LL.B. Hons.), LAW102 Obligations: Contract Law.** Used to verify first-year curriculum fit and topic coverage including invitation to treat and remedies.
- **University of Dhaka program/course materials.** Used as secondary support that formation, offer/acceptance, consideration, capacity, free consent and breach/remedies are core Bangladesh legal/business-law teaching topics.
- **Bangladesh Bar Council — Enrolment Examination Syllabus.** Used to verify that Contract Act should not currently be advertised as a Bar Council enrolment-exam subject.

---

# Final Product Principle

**Do not optimize Bite-Size Learning for the number of cards produced. Optimize it for the number of legal concepts genuinely remembered.**

The strongest Justor loop is:

```text
SURPRISE
→ UNDERSTAND
→ VERIFY THE LAW
→ SIGNAL “GOT IT / REVIEW”
→ ASK JUSTOR FOR DEPTH
→ RETURN TO LEARN AGAIN
```

That is the product to build.
