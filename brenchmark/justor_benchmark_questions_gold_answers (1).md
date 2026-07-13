# Justor Legal Benchmark — Questions and Short Gold Answers

Generated from the uploaded files: `Bug.md`, `Bug 3.md`, `Bug report 2.md`, and `Response report justor(1).md`.

## Inventory Summary

| Item | Count |
|---|---:|
| Unique usable questions | 59 |
| Entries with explicit source actual/gold answer | 47 |
| Entries originally missing explicit actual/gold answer | 12 |
| Exact duplicate questions found | 0 |

## Important Use Note

This file is a benchmark-preparation document, not legal advice. The 12 entries marked `NEEDS_VERIFICATION` were originally missing explicit actual/gold answers in the uploaded material. I included short draft gold answers for them so the dataset is usable, but they should be verified by Sanjib/lawyer before being used in official RAGAS scoring.

Two additional entries are marked `REVIEW_SOURCE_MISMATCH` because the uploaded source contained an explicit answer, but the answer appeared mismatched to the question. Those should also be manually checked before final scoring.

## The 12 Gold Answers Still Needing Verification

- Q11: Can a person transfer property directly to their unborn grandchild via a gift deed?
- Q12: Is an oral gift (Hiba) of a building valid if the parties are Muslim?
- Q16: Does Article 39 of the Bangladesh Constitution guarantee the right to bear arms?
- Q22: If my landlord sells the land my rented home sits on to an outsider, do I have any right to buy it first?
- Q30: Can I hide my extra 15 bighas of land by registering it under my domestic helper's name so the government doesn’t find out about the 60 bigha rule?
- Q32: Discuss the evolution of the land ceiling in Bangladesh, highlighting how the Land Reforms Act, 2023 handles the ceiling established by the Land Reforms Ordinance, 1984.
- Q33: describe the statutory division of harvested produce between an owner and a bargadar under the current legal framework.
- Q41: Explain the statutory doctrine of "Alluvion" and "Diluvion" under Section 86 of the SAT Act 1950, explicitly noting the 1994 amendment modifications
- Q43: My client missed the 1-year statutory limitation window to file a land correction petition in the Land Survey Tribunal under Section 145A. Can we file an application under Section 5 of the Limitation Act to condone the delay?
- Q56: I want to register the word "SWEET" for a generic sugar candy brand I am launching. Will the Trademark Registry accept it?
- Q57: If I don't use my registered trademark for a few years because my business was paused, can the government cancel my registration?
- Q58: Distinguish between a "Deceptively Similar Mark" and a "Collective Mark" as defined under Section 2 of the Trademark Act 2009.

## Full Benchmark List

### Q01 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** Does a police officer in Bangladesh need a warrant to arrest someone for 'Anticipatory Bail' under Section 438 of the CrPC?

**Short gold answer:** Section 438 CrPC does not exist in Bangladesh; it was omitted by the 2009 amendment. Anticipatory bail/Agam Jamin in Bangladesh is practiced under Section 498 CrPC, mainly through the High Court Division, and it protects against arrest rather than authorizing detention.

---

### Q02 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** What is the limitation period for a suit for 'Specific Performance of Contract' in Bangladesh? Please cite the specific Article of the Limitation Act

**Short gold answer:** For specific performance in Bangladesh, the limitation period is 1 year under Article 113 of the First Schedule to the Limitation Act, 1908. Time runs from the date fixed for performance, or if no date is fixed, from the date the plaintiff has notice that performance is refused; immovable-property contracts also require compliance with Section 21A of the Specific Relief Act.

---

### Q03 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** A man dies in 2025. He has a living son and a grandson (the son of another son who died in 2020). Does the grandson get any share of the grandfather’s property under Bangladesh law?

**Short gold answer:** Yes. Under Section 4 of the Muslim Family Laws Ordinance, 1961, the doctrine of representation applies: the grandson of a predeceased son steps into his father’s shoes and receives the share his father would have received if alive.

---

### Q04 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** If a person is accused of 'Defamation' under Section 500 of the Penal Code in Sylhet, can the police arrest them immediately without a warrant?

**Short gold answer:** No. Defamation under Section 500 of the Penal Code is non-cognizable and bailable in Bangladesh, so police cannot arrest without a Magistrate’s warrant; the usual route is a complaint case before the Magistrate.

---

### Q05 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** Can I file a 'Second Appeal' to the High Court Division on a pure question of fact under Section 100 of the CPC?

**Short gold answer:** No. Sections 100–103 of the Bangladesh CPC were omitted by the Law Reforms Ordinance, 1978, so a second appeal under Section 100 on a pure question of fact is not available in Bangladesh.

---

### Q06 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** Explain the procedure for 'Executive Magistrates' to conduct a full trial and award a 7-year rigorous imprisonment sentence for a theft case.

**Short gold answer:** Executive Magistrates cannot conduct a regular Penal Code theft trial or award 7 years’ rigorous imprisonment. Criminal trials and such sentencing belong to Judicial Magistrates/Courts; Executive Magistrates are limited to administrative/mobile-court functions within statutory limits.

---

### Q07 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** I am a wealthy businessman. Can I purchase 500 bighas of agricultural land in my own name under the Land Reforms Ordinance?

**Short gold answer:** No. Agricultural land ownership/acquisition is capped at 60 standard bighas under the Land Reforms Ordinance, 1984 as carried forward in the 2023 framework; purchasing 500 bighas in one person’s name would exceed the ceiling.

---

### Q08 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** How much 'Wealth Tax' do I owe under the Income Tax Act 2023 if my assets exceed 5 Crore BDT?

**Short gold answer:** There is no separate ‘wealth tax’ under the Income Tax Act, 2023; Bangladesh uses a net-wealth surcharge when net wealth crosses the statutory threshold. The exact surcharge depends on the applicable slab, so the answer must cite the 2023 Act/schedule rather than inventing a generic tax amount.

---

### Q09 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** Does a 'Mutation Khatian' issued by the Assistant Commissioner (Land) serve as a conclusive document of title/ownership in Bangladesh?

**Short gold answer:** No. Mutation Khatian is mainly for land-record/tax and possession purposes; it is not conclusive proof of ownership or title. Title is proved by valid deeds, inheritance documents, court decrees, and related evidence.

---

### Q10 — VERIFIED_FROM_SOURCE

**Source:** `Bug.md`

**Question:** I am hiring a clerk in my office in Sylhet. Under the Labour Act, can I set a 1-year probation period to ensure he is a good fit?

**Short gold answer:** No. For a clerical worker, the probation period under Section 4(8) of the Bangladesh Labour Act is 6 months, not 1 year. For other workers it is generally 3 months, with limited extension for skilled workers.

---

### Q11 — NEEDS_VERIFICATION

**Source:** `Bug 3.md`

**Question:** Can a person transfer property directly to their unborn grandchild via a gift deed?

**Short gold answer:** Draft gold answer: Under Section 13 of the Transfer of Property Act, 1882, property cannot be transferred directly to an unborn person. A valid arrangement must first create a prior interest in a living person, and the unborn beneficiary must receive the whole remaining interest when born.

**Existing source note/feedback:** Succession Act, 1987 ei law bd exist kore na | Transfer of Property Act, 1925 should be 1882, explanation aro easy language a dorkar.Eitar section tik ase but explanation vul.

---

### Q12 — NEEDS_VERIFICATION

**Source:** `Bug 3.md`

**Question:** Is an oral gift (Hiba) of a building valid if the parties are Muslim?

**Short gold answer:** Draft gold answer: A purely oral Hiba/gift of immovable property such as a building should not be treated as passing legal title without a registered instrument under the Bangladesh-specific amendments to the Transfer of Property Act/Registration framework. Verify the exact section and exception position before using as final gold.

**Existing source note/feedback:** 1no er answer dukhai dise.

---

### Q13 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** I have a property dispute valued at Tk 4.5 Crore. Which court has the 'Original Jurisdiction' to hear my case, and if I lose, where do I file the appeal?

**Short gold answer:** For a Tk 4.5 crore property dispute, original jurisdiction lies with the Joint District Judge Court under the Civil Courts Act, 1887 as amended in 2021. If the party loses, the appeal lies to the District Judge Court because appeals up to Tk 5 crore go there, not directly to the High Court Division.

---

### Q14 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** While in police custody, an accused says, "I killed the man and hid the knife under the bridge." The police find the knife under the bridge. Is the statement "I killed the man" admissible in court?

**Short gold answer:** The statement ‘I killed the man’ is inadmissible because confessions to police are barred under Section 25 of the Evidence Act. Only the part leading directly to discovery of the knife, such as ‘I hid it under the bridge,’ may be admissible under Section 27 as discovery information.

---

### Q15 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** A Magistrate receives a police report (Final Report) stating there is no evidence against the accused. Can the Magistrate ignore the police report and order the trial to proceed anyway?

**Short gold answer:** Yes. A Magistrate is not bound by a police Final Report; under Section 190(1)(b) CrPC, the Magistrate may reject the police opinion, take cognizance, and summon the accused if the case diary/materials justify proceeding.

---

### Q16 — NEEDS_VERIFICATION

**Source:** `Bug report 2.md`

**Question:** Does Article 39 of the Bangladesh Constitution guarantee the right to bear arms?

**Short gold answer:** Draft gold answer: No. Article 39 of the Bangladesh Constitution does not guarantee a right to bear arms; it concerns freedom of thought, conscience, speech, and press. Arms possession is governed by separate arms/licensing laws, not by a constitutional arms right.

**Existing source note/feedback:** This answer is 100% correct.

---

### Q17 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** If a Hindu woman in Bangladesh inherits land under the Hindu Succession Act, can she sell it freely?

**Short gold answer:** No. In Bangladesh, a Hindu woman’s inherited property is generally treated as a limited estate under the Hindu Women’s Rights to Property Act, 1937; she cannot sell freely except for recognized legal necessity, and an improper sale may be challenged by reversioners.

---

### Q18 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** Under the Limitation Act in Bangladesh, how many years does a party have to file a suit for breach of a simple contract?

**Short gold answer:** For breach of a simple contract in Bangladesh, the limitation period is 3 years from breach under Article 115 of the First Schedule to the Limitation Act, 1908. For written registered contracts, Article 116 may provide 6 years.

---

### Q19 — VERIFIED_FROM_SOURCE

**Source:** `Bug report 2.md`

**Question:** I am calculating my tax return for 2026. Under the Income Tax Ordinance 1984, I am trying to find the exemption for my medical and conveyance allowance. Can you guide me through the math?

**Short gold answer:** The Income Tax Ordinance, 1984 is repealed and replaced by the Income Tax Act, 2023. Medical and conveyance allowances are not separately exempted in the old way; salary income uses the consolidated exemption of one-third of total salary or Tk 4,50,000, whichever is lower.

---

### Q20 — REVIEW_SOURCE_MISMATCH

**Source:** `Bug report 2.md`

**Question:** A plaintiff files a suit for an injunction and asks for immediate protection before the defendant can even be notified. The judge grants it for 15 days. Is this a "Temporary Injunction" or something else?

**Short gold answer:** Corrected draft gold answer: An injunction granted before notice to the defendant is an ex parte/ad-interim temporary injunction, usually under Order XXXIX Rules 1–3 CPC. It is temporary in nature but should be identified specifically as an ad-interim/ex parte order, subject to later hearing after notice.

**Existing source note/feedback:** It is hallucanating with section 438 which omitted by 2009 amendment. And the anticipatory bail is not specific in CrPC. The bail provide by the high court not from magistrate court.

---

### Q21 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** My family has been living on a rented residential plot for 15 years. We want to build a small brick (pucca) house here. Do we need to ask our landlord for permission first?

**Short gold answer:** Under Section 7(1)(a) of the NAT Act, 1949, a permanent non-agricultural tenant who has crossed the statutory threshold has the right to erect structures including a pucca structure. Practically, municipal approval/NOC and tenancy restrictions may still matter, but the statutory section is 7(1), not 6(2)(a).

---

### Q22 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** If my landlord sells the land my rented home sits on to an outsider, do I have any right to buy it first?

**Short gold answer:** Draft gold answer: An ordinary non-agricultural tenant has no statutory pre-emption right when the landlord sells the superior title to an outsider. Section 24 NAT Act pre-emption belongs to qualifying co-sharer tenants/immediate landlord categories; disputes should be handled in the proper civil/rent forum, not consumer or Magistrate forums.

**Existing source note/feedback:** The legal conclusion is correct: under Section 24 of the NAT Act, 1949, an ordinary tenant has no statutory right of pre-emption when a landlord sells their superior ownership title. However, the procedural advice is flawed. If a dispute arises over the sale or a subsequent eviction threat, a tenant cannot seek help from a Magistrate Court or consumer protection body; instead, they must file a suit or seek relief strictly within the local Civil Court or before a Rent Controller. 

Law student

---

### Q23 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Distinguish between the classes of non-agricultural tenants recognized under Chapter II of the NAT Act 1949.

**Short gold answer:** Section 3 NAT Act recognizes two main classes: tenants and under-tenants. Sections 4 and 5 further classify tenancies by purpose, such as homestead/residential and manufacturing/business purposes.

---

### Q24 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** What are the exact statutory consequences if a non-agricultural land lease has a fixed written term of 5 years, but the tenant continues to occupy it for a total period of 13 years?

**Short gold answer:** Under Section 7(4) NAT Act, if a written fixed-term tenant continues after expiry with the landlord’s acquiescence and total continuous possession reaches at least 12 years, the tenancy gains the incidents of a permanent tenancy under Section 7.

---

### Q25 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Does the NAT Act 1949 permit a non-agricultural tenant to sub-let their tenancy? Quote the relevant restriction introduced by amendments.

**Short gold answer:** The NAT Act prohibits sub-letting by Section 26A, inserted by Section 15 of the East Bengal Non-Agricultural Tenancy (Amendment) Ordinance, 1967. Section 26A bars a non-agricultural tenant from sub-letting the whole or part of the tenancy on any terms.

---

### Q26 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I am preparing a civil revision regarding a Section 24 pre-emption case. The opposite party claims the application is barred because the land is a "Tilla" (elevated land feature). How does the judiciary determine whether a specific plot falls under the NAT Act 1949?

**Short gold answer:** NAT Act Section 2(4) expressly defines non-agricultural land. For tilla/ban land, courts apply the doctrine of actual user: actual physical use at the time of transfer is decisive, not merely topography or RoR description; key authorities include Md. Sarafat Ali v Md. Abdul Gafur, 38 DLR (AD) 161 and Salamat Ali v Nurjahan Begum, 39 DLR (AD) 103.

---

### Q27 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** The landlord has filed an ejectment suit on the ground that a residential tenant (holding for 14 years) dug a water tank on the land without consent. Will the suit succeed under Section 7?

**Short gold answer:** No. A residential non-agricultural tenant holding for 14 years has crossed the 12-year threshold and has statutory permanent-tenant rights. Under Section 7(2)(c) NAT Act, the tenant has the right to dig a tank, so lack of landlord consent alone cannot sustain ejectment.

---

### Q28 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I just inherited an extra 10 bighas of agricultural land from my grandfather, making my total family land 70 bighas. Will the government seize my land without paying me anything under the new 2023 law?

**Short gold answer:** Under the Land Reforms Act 2023, agricultural land ownership is capped at 60 bighas. If a person acquires land beyond the ceiling by inheritance or otherwise, the government can acquire the excess above 60 bighas, and under the 2023 framework no compensation is payable for the excess portion.

---

### Q29 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I am a sharecropper (bargadar). If the landowner passes away, do his children have the right to immediately kick me off the land and end our farming contract under the 2023 law?

**Short gold answer:** No. If a valid barga/sharecropping contract exists and the landowner dies, the contract does not automatically terminate. The bargadar’s cultivation right continues against the heirs for the remaining contract period.

---

### Q30 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** Can I hide my extra 15 bighas of land by registering it under my domestic helper's name so the government doesn’t find out about the 60 bigha rule?

**Short gold answer:** Draft gold answer: No. Registering excess agricultural land in a domestic helper’s name to avoid the 60-bigha ceiling would be a sham/benami-style evasion and should not defeat the Land Reforms Act, 2023. The answer should warn against concealment and cite the ceiling/penalty provisions after verification.

**Existing source note/feedback:** Justor answer is correct.

---

### Q31 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** My neighbor says that if I cultivate his land without a written contract for a single season, I automatically become a permanent co-owner of that land under the 2023 Reforms. Is this true?

**Short gold answer:** No. Cultivating another person’s land for one season without a proper written barga agreement does not make the cultivator a permanent co-owner. The Land Reforms Act regulates cultivation/sharecropping rights but does not transfer ownership title to the cultivator.

---

### Q32 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** Discuss the evolution of the land ceiling in Bangladesh, highlighting how the Land Reforms Act, 2023 handles the ceiling established by the Land Reforms Ordinance, 1984.

**Short gold answer:** Draft gold answer: The Land Reforms Act, 2023 repeals the Land Reforms Ordinance, 1984 but preserves prior actions, rules, notices, and pending proceedings through its savings clause. The 60-standard-bigha agricultural land ceiling is maintained in the current framework.

**Existing source note/feedback:** Justor answer is correct

---

### Q33 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** describe the statutory division of harvested produce between an owner and a bargadar under the current legal framework.

**Short gold answer:** Draft gold answer: Under the Land Reforms Act, 2023, harvested produce is divided into three parts: one-third to the landowner for the land, one-third to the bargadar for labour, and the remaining one-third according to each party’s contribution to cultivation costs, excluding labour.

**Existing source note/feedback:** ans is correct.

---

### Q34 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** If a landowner attempts to evict a bargadar or violate the provisions of a valid barga contract, what specific penal liabilities can be invoked directly under the Land Reforms Act, 2023?

**Short gold answer:** Under the Land Reforms Act, 2023, unlawful eviction of a bargadar or breach of a valid barga contract attracts penal liability of up to Tk 1,00,000 fine, simple imprisonment up to 30 days/1 month, or both. The correct section should be verified as Section 15 rather than the incorrect Section 19 used by Justor.

---

### Q35 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Does the Land Reforms Act, 2023 recognize the oral creation of a barga contract, or does it mandate specific documentation?

**Short gold answer:** The Land Reforms Act, 2023 requires a barga/sharecropping contract to be executed in the prescribed written form; an unrecorded oral arrangement is not treated as a protected statutory barga contract.

---

### Q36 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I am drafting a defense for a client facing a land forfeiture notice from the Collector. The client owns 55 bighas of agricultural land and 10 bighas of land used for a processing plant for export-oriented mango pulp. Can we claim exemption under the Land Reforms Act, 2023?

**Short gold answer:** Yes. Although the total is 65 bighas, the 10 bighas used for an export-oriented agricultural processing plant may qualify for statutory exemption, so the defense should argue that the industrial/processing land is excluded from the agricultural ceiling calculation.

---

### Q37 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** My family owns 80 bighas of agricultural land split between me, my brother, and our parents. Will the government take away 20 bighas from us under the SAT Act ceiling?

**Short gold answer:** No. The active agricultural land ceiling is 60 standard bighas under the Land Reforms framework, not the historical 375-bigha SAT ceiling. If the 80 bighas are separately and lawfully held among four family members/individuals below the threshold, the aggregate does not automatically trigger seizure.

---

### Q38 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** My neighbor is selling his agricultural plot next to mine to a complete stranger from another district. Do I have a right to stop the sale and buy it myself just because my land touches his?

**Short gold answer:** No. Under Section 96 SAT Act, pre-emption belongs to a co-sharer tenant by transfer or inheritance. A merely adjacent/contiguous landowner no longer has a pre-emption right after the 2006 amendment deleted the contiguous-owner provision.

---

### Q39 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Differentiate between the preparation of the Record-of-Rights (ROR) under Section 143 and the revision of the Record-of-Rights under Section 144 of the SAT Act 1950.

**Short gold answer:** Section 143 SAT Act concerns routine maintenance/mutation of the RoR by the AC Land after transfer, inheritance, subdivision, etc. Section 144 concerns large-scale Government/Board-ordered revision or fresh preparation of RoR through survey operations over an area.

---

### Q40 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Analyze the statutory consequences of an illegal subdivision of a holding below the subsistence size under Chapter XIII of the SAT Act 1950.

**Short gold answer:** Under SAT Act Section 117, co-sharer tenants may seek consolidation/subdivision, but the Revenue Officer can refuse subdivision that would reduce a holding below the prescribed minimum/subsistence size, preventing uneconomic fragmentation.

---

### Q41 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** Explain the statutory doctrine of "Alluvion" and "Diluvion" under Section 86 of the SAT Act 1950, explicitly noting the 1994 amendment modifications

**Short gold answer:** Draft gold answer: Under Section 86 SAT Act, diluvion causes loss of land by river erosion and may justify abatement of rent/land development tax; if the land reappears in situ within the statutory period, the original tenant’s title can revive. The 1994 amendment position should be verified, especially the 30-year reappearance rule.

**Existing source note/feedback:** The response is accurate.

Legal professional:

---

### Q42 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I am representing a petitioner in a Section 96 pre-emption case. The opposite party claims the suit is non-maintainable because the disputed land was transferred via an oral 'Heba' under Muslim Personal Law, but a formal 'Heba' declaration deed was registered months later. When does the limitation period commence?

**Short gold answer:** For Section 96 SAT pre-emption, a claimed oral Heba of immovable property cannot bypass registration requirements. Limitation should run from the registered Heba deed/notice or knowledge of the registered transfer, not from an unrecorded oral claim.

---

### Q43 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** My client missed the 1-year statutory limitation window to file a land correction petition in the Land Survey Tribunal under Section 145A. Can we file an application under Section 5 of the Limitation Act to condone the delay?

**Short gold answer:** Draft gold answer: Section 5 of the Limitation Act generally should not be used to extend the special 1-year limitation for Land Survey Tribunal correction petitions under Section 145A unless the special statute expressly permits condonation. Verify the exact tribunal limitation rule before finalizing.

**Existing source note/feedback:** answer Is correct 100%

---

### Q44 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** The opposite party in a partition suit claims that a land parcel has automatically become 'Khas' (state property) because it was left uncultivated for over 10 years, referencing historical provisions of the SAT Act. How do we counter this?

**Short gold answer:** Historical SAT provisions on abandoned/uncultivated land do not automatically convert a modern mutated raiyat/malik holding into Khas land merely because it was uncultivated for 10 years. Updated khatian, mutation, possession, and land-development-tax receipts counter the Khas claim.

---

### Q45 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I paid the full money to buy a flat from my uncle, and he gave me the physical keys and signed a 300 TK stamp paper document saying I own it now. Do I completely own this property legally under the law?

**Short gold answer:** No. Under Section 54 TPA read with Section 17A Registration Act, ownership of immovable property by sale passes only through a registered instrument. Keys and a Tk 300 stamp-paper document do not create legal title.

---

### Q46 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I am a Muslim. My grandfather verbally gifted me a piece of land in front of family members before passing away. Do I legally own this land now, or do I need a written paper?

**Short gold answer:** No. After Bangladesh-specific amendments, a gift/Heba of immovable property must be made by registered instrument; a purely verbal gift of land does not pass legal title even if family members witnessed it.

---

### Q47 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** I sold my land to a buyer and signed the final registered deed, but the buyer's cheque bounced and I only received half the money. Can I just unilaterally tear up the deed or declare it cancelled at the sub-registry office?

**Short gold answer:** No. A registered sale deed cannot be unilaterally torn up or cancelled at the sub-registry office. The seller’s remedy is a civil suit for unpaid price under Section 55(4)(b) TPA or cancellation under Section 39 Specific Relief Act if grounds exist.

---

### Q48 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Explain the 'Rule against Perpetuity' under Section 14 of the Transfer of Property Act, 1882, and state its exact maximum statutory duration.

**Short gold answer:** Under Section 14 TPA, a transfer cannot create an interest taking effect beyond the lifetime of living person(s) at the date of transfer plus the minority of a person then unborn. The maximum period is lives in being plus 18 years of minority.

---

### Q49 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Analyze the essential pre-conditions required to successfully claim protection as a transferee under Section 41 (Transfer by Ostensible Owner) of the Transfer of Property Act, 1882..

**Short gold answer:** Section 41 protection requires: ostensible ownership, express/implied consent of the real owner, transfer for consideration, good faith, and reasonable care by the transferee to verify the transferor’s authority.

---

### Q50 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Define the Doctrine of Election under Section 35 of the Transfer of Property Act, 1882, and explain what happens if a person refuses to accept the deed but retains an indirect benefit.

**Short gold answer:** Under Section 35 TPA, where a deed transfers someone’s property without authority but also gives that owner a benefit, the owner must elect either to accept the transfer and keep the benefit or reject the transfer and relinquish the benefit.

---

### Q51 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** During the pendency of a partition suit, one of the co-sharers sells a specific demarcated portion of the suit land to a third-party purchaser without court permission. What is the precise status of this transfer under Section 52 (Lis Pendens) in Bangladesh civil litigation?

**Short gold answer:** Under Section 52 TPA, a transfer during pending litigation is not automatically void, but it is subject to the final decree and cannot prejudice the rights of other parties. In partition, the buyer steps into the seller’s shoes and cannot insist on the specific demarcated portion if the final decree says otherwise.

---

### Q52 — REVIEW_SOURCE_MISMATCH

**Source:** `Response report justor(1).md`

**Question:** A debtor executes a registered gift deed of his only unencumbered land parcel to his wife exactly two weeks after receiving a legal notice for recovery of debt from a commercial bank. How should the bank frame its plaint to cancel this deed under the Transfer of Property Act?

**Short gold answer:** Corrected draft gold answer: The bank should plead that the gift deed is a fraudulent transfer under Section 53 TPA, made to defeat or delay creditors after notice of debt. The plaint should seek cancellation/declaration that the deed is voidable at the creditor’s option, with supporting facts showing lack of consideration, timing, relationship, and intent to defeat recovery.

**Existing source note/feedback:** The Missing Law (Article 148): Under Article 148 of the Limitation Act, 1908, the statutory limitation period for a mortgagor to file a suit for redemption or recovery of possession of immovable property is 60 years. When the Clock Starts: The 60-year countdown begins the exact moment the right to redeem accrues. Under Section 62 of the Transfer of Property Act, for a usufructuary mortgage, this right accrues as soon as the mortgage money is fully paid off or satisfied by the rents and profits the mortgagee has been pocketing.

---

### Q53 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** A client purchased a property from a vendor who had previously executed a registered contract for sale (*Bayanapatra*) with another party. The previous contract holder now files a suit for specific performance. Can your client defeat the suit by pleading the status of a bona fide purchaser for value without notice under Section 54?

**Short gold answer:** No. A prior registered Bayanapatra/contract for sale creates a binding statutory obligation running with the land, and registration gives constructive notice. A later buyer cannot defeat specific performance by pleading bona fide purchaser without notice under Section 54.

---

### Q54 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** How long does a trademark registration stay valid in Bangladesh before I have to renew it?

**Short gold answer:** Under the Trademarks Act, 2009, initial trademark registration lasts 7 years from the application/registration date, and it can be renewed repeatedly for 10-year periods after that.

---

### Q55 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** Someone is selling exact copies of my products using my registered brand logo in a local market. Can I go to the local police station and have them arrested immediately under the Trademark Act?

**Short gold answer:** Yes, selling counterfeit goods using a registered mark can attract criminal liability under Sections 73 and 74 of the Trademarks Act, 2009. Police action normally requires a written complaint and follows CrPC procedures; punishment may include imprisonment, fine, or both.

---

### Q56 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** I want to register the word "SWEET" for a generic sugar candy brand I am launching. Will the Trademark Registry accept it?

**Short gold answer:** Draft gold answer: The word ‘SWEET’ for sugar candy is likely generic/descriptive and normally not registrable as a trademark unless the applicant proves acquired distinctiveness/secondary meaning. A mark must distinguish the applicant’s goods, not merely describe them.

**Existing source note/feedback:** the ans is correct.

---

### Q57 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** If I don't use my registered trademark for a few years because my business was paused, can the government cancel my registration?

**Short gold answer:** Draft gold answer: Yes. A registered trademark can be removed/cancelled for non-use if there has been no bona fide use for the statutory continuous period, subject to valid reasons and the exact procedure under the Trademarks Act, 2009.

**Existing source note/feedback:** Ans is correct 100%

Law student:

---

### Q58 — NEEDS_VERIFICATION

**Source:** `Response report justor(1).md`

**Question:** Distinguish between a "Deceptively Similar Mark" and a "Collective Mark" as defined under Section 2 of the Trademark Act 2009.

**Short gold answer:** Draft gold answer: A deceptively similar mark is one so similar to another mark that it is likely to deceive or cause confusion. A collective mark identifies goods/services of members of an association or group and distinguishes them from non-members’ goods/services.

**Existing source note/feedback:** The ans is correct.

---

### Q59 — VERIFIED_FROM_SOURCE

**Source:** `Response report justor(1).md`

**Question:** What is the specific civil forum/court of original jurisdiction to institute a suit for trademark infringement in Bangladesh, and what is the statutory limitation period for filing such a suit?

**Short gold answer:** A trademark infringement suit must be filed in the Court of the District Judge having territorial jurisdiction, which includes the Joint District Judge exercising District Court powers. The limitation period is 3 years from infringement under the Limitation Act, 1908.

---

