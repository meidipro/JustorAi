#!/usr/bin/env python3
"""
scripts/seed_core_provisions.py
Seeds mandatory and foundational legal provisions into legal_provisions and provision_versions.
"""

import os
import sys
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

db = create_client(SUPABASE_URL, SUPABASE_KEY)

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

PROVISIONS = [
    # ── CPC ──
    {
        "act": "The Code of Civil Procedure, 1908",
        "section": "Order XXXIX Rule 1",
        "heading": "Cases in which temporary injunction may be granted",
        "valid_from": "1909-01-01",
        "text": """Where in any suit it is proved by affidavit or otherwise—
(a) that any property in dispute in a suit is in danger of being wasted, damaged, or alienated by any party to the suit, or wrongfully sold in execution of a decree, or
(b) that the defendant threatens, or intends, to remove or dispose of his property with a view to defrauding his creditors,
the Court may by order grant a temporary injunction to restrain such act, or make such other order for the purpose of staying and preventing the wasting, damaging, alienation, sale, removal, or disposition of the property as the Court thinks fit, until the disposal of the suit or until further orders."""
    },
    {
        "act": "The Code of Civil Procedure, 1908",
        "section": "Order XXXIX Rule 2",
        "heading": "Injunction to restrain repetition or continuance of breach",
        "valid_from": "1909-01-01",
        "text": """(1) In any suit for restraining the defendant from committing a breach of contract or other injury of any kind, whether compensation is claimed in the suit or not, the plaintiff may, at any time after the commencement of the suit, and either before or after judgment, apply to the Court for a temporary injunction to restrain the defendant from committing the breach of contract or injury complained of, or any breach of contract or injury of a like kind arising out of the same contract or relating to the same property or right.
(2) The Court may by order grant such injunction, on such terms as to the duration of the injunction, keeping an account, giving security, or otherwise, as the Court thinks fit."""
    },
    {
        "act": "The Code of Civil Procedure, 1908",
        "section": "Order VII Rule 11",
        "heading": "Rejection of plaint",
        "valid_from": "1909-01-01",
        "text": """The plaint shall be rejected in the following cases:—
(a) where it does not disclose a cause of action;
(b) where the relief claimed is undervalued, and the plaintiff, on being required by the Court to correct the valuation within a time to be fixed by the Court, fails to do so;
(c) where the relief claimed is properly valued, but the plaint is written upon paper insufficiently stamped, and the plaintiff, on being required by the Court to supply the requisite stamp-paper within a time to be fixed by the Court, fails to do so;
(d) where the suit appears from the statement in the plaint to be barred by any law."""
    },
    {
        "act": "The Code of Civil Procedure, 1908",
        "section": "Order IX Rule 13",
        "heading": "Setting aside decree ex parte against defendant",
        "valid_from": "1909-01-01",
        "text": """In any case in which a decree is passed ex parte against a defendant, he may apply to the Court by which the decree was passed for an order to set it aside; and if he satisfies the Court that the summons was not duly served, or that he was prevented by any sufficient cause from appearing when the suit was called on for hearing, the Court shall make an order setting aside the decree as against him upon such terms as to costs, payment into Court or otherwise as it thinks fit, and shall appoint a day for proceeding with the suit."""
    },
    {
        "act": "The Code of Civil Procedure, 1908",
        "section": "Section 9",
        "heading": "Courts to try all civil suits unless barred",
        "valid_from": "1909-01-01",
        "text": """The Courts shall (subject to the provisions herein contained) have jurisdiction to try all suits of a civil nature excepting suits of which their cognizance is either expressly or impliedly barred."""
    },

    # ── NI Act ──
    {
        "act": "The Negotiable Instruments Act, 1881",
        "section": "Section 138",
        "heading": "Dishonour of cheque for insufficiency, etc., of funds in the account",
        "valid_from": "2006-01-01",
        "text": """(1) Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for a term which may extend to one year, or with fine which may extend to thrice the amount of the cheque, or with both:
Provided that nothing contained in this section shall apply unless—
(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;
(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice, in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and
(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within thirty days of the receipt of the said notice.
(2) The notice under clause (b) of sub-section (1) shall be served in any of the following manners—
(a) by delivering it to the person on whom it is to be served; or
(b) by sending it by registered post with acknowledgement due to his usual place of residence or business in Bangladesh; or
(c) by publication in a widely circulated daily Bengali national newspaper."""
    },
    {
        "act": "The Negotiable Instruments Act, 1881",
        "section": "Section 141",
        "heading": "Cognizance of offences and jurisdiction threshold",
        "valid_from": "2026-01-01",
        "text": """Notwithstanding anything contained in the Code of Criminal Procedure, 1898—
(a) no Court shall take cognizance of any offence punishable under section 138 except upon a complaint, in writing, made by the payee or, as the case may be, the holder in due course of the cheque;
(b) such complaint is made within one month of the date on which the cause of action arises under clause (c) of the proviso to section 138;
(c) no Court inferior to that of a Court of Sessions shall try any offence punishable under section 138:
Provided that under the Negotiable Instruments (Amendment) Act, 2026, monetary jurisdiction thresholds and fast-track procedure apply where the cheque amount exceeds Taka 5,00,000."""
    },

    # ── Specific Relief Act ──
    {
        "act": "The Specific Relief Act, 1877",
        "section": "Section 21A",
        "heading": "Unregistered contract for sale not specifically enforceable",
        "valid_from": "2004-07-01",
        "text": """Notwithstanding anything to the contrary contained in this Act or any other law for the time being in force, no contract for sale of any immovable property shall be specifically enforced unless—
(a) the contract is in writing and registered under the Registration Act, 1908, and
(b) the balance consideration, if any, is deposited in the Court at the time of filing of the plaint:
Provided that where the seller has received the full consideration, the suit may be filed with a specific statement to that effect supported by registered deed evidence."""
    },
    {
        "act": "The Specific Relief Act, 1877",
        "section": "Section 9",
        "heading": "Suit by person dispossessed of immovable property",
        "valid_from": "1877-05-01",
        "text": """If any person is dispossessed without his consent of immovable property otherwise than in due course of law, he or any person claiming through him may, by suit, recover possession thereof, notwithstanding any other title that may be set up in such suit.
Nothing in this section shall bar any person from suing to establish his title to such property and to recover possession thereof.
No suit under this section shall be brought against the Government.
No appeal shall lie from any order or decree passed in any suit instituted under this section, nor shall any review of any such order or decree be allowed."""
    },

    # ── Registration Act ──
    {
        "act": "The Registration Act, 1908",
        "section": "Section 17A",
        "heading": "Contract for sale, etc. to be registered",
        "valid_from": "2004-07-01",
        "text": """(1) Notwithstanding anything contained in this Act or any other law for the time being in force, a contract for sale of any immovable property shall be in writing, executed by the parties and registered within thirty days from the date of execution.
(2) No contract for sale shall be received in evidence of any transaction affecting such property unless it has been registered.
(3) The application for registration shall be made in the Sub-Registry office within whose sub-district the whole or some portion of the property is situated."""
    },
    {
        "act": "The Registration Act, 1908",
        "section": "Section 49",
        "heading": "Effect of non-registration of documents required to be registered",
        "valid_from": "1909-01-01",
        "text": """No document required by section 17 or by any provision of the Transfer of Property Act, 1882 to be registered shall—
(a) affect any immovable property comprised therein, or
(b) confer any power to adopt, or
(c) be received as evidence of any transaction affecting such property or conferring such power,
unless it has been registered."""
    },

    # ── Transfer of Property Act ──
    {
        "act": "The Transfer of Property Act, 1882",
        "section": "Section 54",
        "heading": "Sale defined and sale how made",
        "valid_from": "1882-07-01",
        "text": """"Sale" is a transfer of ownership in exchange for a price paid or promised or part-paid and part-promised.
Such transfer, in the case of tangible immovable property of the value of one hundred Taka and upwards, or in the case of a reversion or other intangible thing, can be made only by a registered instrument.
A contract for the sale of immovable property is a contract that a sale of such property shall take place on terms settled between the parties. It does not, of itself, create any interest in or charge on such property."""
    },
    {
        "act": "The Transfer of Property Act, 1882",
        "section": "Section 54A",
        "heading": "Contracts for sale of immovable property to be registered",
        "valid_from": "2004-07-01",
        "text": """Notwithstanding anything contained in this Act or any other law for the time being in force, a contract for sale of immovable property shall be in writing and registered under the Registration Act, 1908, and if not so registered, shall not be valid or enforceable in any court of law."""
    },
    {
        "act": "The Transfer of Property Act, 1882",
        "section": "Section 53A",
        "heading": "Part performance",
        "valid_from": "1929-01-01",
        "text": """Where any person contracts to transfer for consideration any immovable property by writing signed by him or on his behalf from which the terms necessary to constitute the transfer can be ascertained with reasonable certainty, and the transferee has, in part performance of the contract, taken possession of the property or any part thereof, the transferor or any person claiming under him shall be debarred from enforcing against the transferee any right in respect of the property."""
    },

    # ── CrPC ──
    {
        "act": "The Code of Criminal Procedure, 1898",
        "section": "Section 54",
        "heading": "When police may arrest without warrant",
        "valid_from": "1898-07-01",
        "text": """Any police-officer may, without an order from a Magistrate and without a warrant, arrest—
first, any person who has been concerned in any cognizable offence, or against whom a reasonable complaint has been made, or credible information has been received, or a reasonable suspicion exists, of his having been so concerned;
secondly, any person having in his possession without lawful excuse, the burden of proving which excuse shall lie on such person, any implement of house-breaking;
thirdly, any person who has been proclaimed as an offender either under this Code or by order of the Government;
fourthly, any person in whose possession anything is found which may reasonably be suspected to be stolen property;
fifthly, any person who obstructs a police-officer while in the execution of his duty, or who has escaped, or attempts to escape, from lawful custody;
sixthly, any person reasonably suspected of being a deserter from the armed forces of Bangladesh;
seventhly, any person who has been concerned in, or against whom a reasonable complaint has been made of having committed an act outside Bangladesh which would have been punishable as an offence in Bangladesh."""
    },
    {
        "act": "The Code of Criminal Procedure, 1898",
        "section": "Section 61",
        "heading": "Person arrested not to be detained more than twenty-four hours",
        "valid_from": "1898-07-01",
        "text": """No police-officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not, in the absence of a special order of a Magistrate under section 167, exceed twenty-four hours, exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court."""
    },
    {
        "act": "The Code of Criminal Procedure, 1898",
        "section": "Section 167",
        "heading": "Procedure when investigation cannot be completed in twenty-four hours",
        "valid_from": "1898-07-01",
        "text": """(1) Whenever any person is arrested and detained in custody, and it appears that the investigation cannot be completed within the period of twenty-four hours fixed by section 61, the officer in charge of the police-station shall forthwith transmit to the nearest Judicial Magistrate a copy of the entries in the diary and shall at the same time forward the accused to such Magistrate.
(2) The Magistrate may authorize the detention of the accused in such custody as such Magistrate thinks fit, for a term not exceeding fifteen days in the whole.
(3) A Magistrate authorizing under this section detention in the custody of the police shall record his reasons for so doing."""
    },
    {
        "act": "The Code of Criminal Procedure, 1898",
        "section": "Section 497",
        "heading": "When bail may be taken in case of non-bailable offence",
        "valid_from": "1898-07-01",
        "text": """(1) When any person accused of any non-bailable offence is arrested or detained without warrant by an officer in charge of a police-station, or appears or is brought before a Court, he may be released on bail, but he shall not be so released if there appear reasonable grounds for believing that he has been guilty of an offence punishable with death or with imprisonment for life:
Provided that the Court may direct that any person under the age of sixteen years or any woman or any sick or infirm person accused of such an offence be released on bail:
Provided further that under the Children Act, 2013, mandatory child bail considerations apply to any person under the age of eighteen years."""
    },
    {
        "act": "The Code of Criminal Procedure, 1898",
        "section": "Section 561A",
        "heading": "Saving of inherent power of High Court Division",
        "valid_from": "1923-01-01",
        "text": """Nothing in this Code shall be deemed to limit or affect the inherent power of the High Court Division to make such orders as may be necessary to give effect to any order under this Code, or to prevent abuse of the process of any Court or otherwise to secure the ends of justice."""
    },

    # ── Constitution ──
    {
        "act": "The Constitution of the People's Republic of Bangladesh",
        "section": "Article 111",
        "heading": "Binding effect of Supreme Court judgments",
        "valid_from": "1972-12-16",
        "text": """The law declared by the Appellate Division shall be binding on the High Court Division and the law declared by either division of the Supreme Court shall be binding on all courts subordinate thereto."""
    },
    {
        "act": "The Constitution of the People's Republic of Bangladesh",
        "section": "Article 102",
        "heading": "Powers of High Court Division to issue certain orders and directions, etc.",
        "valid_from": "1972-12-16",
        "text": """(1) The High Court Division on the application of any person aggrieved may give such directions or orders to any person or authority, including any person performing any function in connection with the affairs of the Republic, as may be appropriate for the enforcement of any of the fundamental rights conferred by Part III of this Constitution.
(2) The High Court Division may, if satisfied that no other equally efficacious remedy is provided by law—
(a) make an order directing a person performing functions to refrain from doing that which he is not permitted by law to do, or declaring that any act done has been done without lawful authority;
(b) make an order directing that a person in custody be brought before it so that it may satisfy itself that he is not being held in custody without lawful authority (Habeas Corpus), or requiring a person holding or purporting to hold a public office to show under what authority he claims to hold that office (Quo Warranto)."""
    },
    {
        "act": "The Constitution of the People's Republic of Bangladesh",
        "section": "Article 33",
        "heading": "Safeguards as to arrest and detention",
        "valid_from": "1972-12-16",
        "text": """(1) No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice.
(2) Every person who is arrested and detained in custody shall be produced before the nearest magistrate within a period of twenty-four hours of such arrest, excluding the time necessary for the journey from the place of arrest to the court of the magistrate, and no such person shall be detained in custody beyond the said period without the authority of a magistrate."""
    },

    # ── Family Courts Act 2023 ──
    {
        "act": "Family Courts Act, 2023",
        "section": "Section 5",
        "heading": "Jurisdiction of Family Courts",
        "valid_from": "2023-09-01",
        "text": """Subject to the provisions of this Act, a Family Court shall have exclusive jurisdiction to entertain, try and dispose of any suit relating to or arising out of all or any of the following matters, namely:—
(a) dissolution of marriage;
(b) restitution of conjugal rights;
(c) dower (denmohor);
(d) maintenance (khurposh);
(e) guardianship and custody of children."""
    },

    # ── Muslim Family Laws Ordinance 1961 ──
    {
        "act": "The Muslim Family Laws Ordinance, 1961",
        "section": "Section 7",
        "heading": "Talaq procedure and notice",
        "valid_from": "1961-07-15",
        "text": """(1) Any man who wishes to divorce his wife shall, as soon as may be after the pronouncement of talaq in any form whatsoever, give the Chairman notice in writing of his having done so, and shall supply a copy thereof to the wife.
(2) Whoever contravenes the provisions of sub-section (1) shall be punishable with simple imprisonment for a term which may extend to one year or with fine which may extend to ten thousand taka or with both.
(3) Save as provided in sub-section (5), a talaq unless revoked earlier, expressly or otherwise, shall not be effective until the expiration of ninety days from the day on which notice under sub-section (1) is delivered to the Chairman.
(4) Within thirty days of the receipt of notice under sub-section (1), the Chairman shall constitute an Arbitration Council for the purpose of bringing about a reconciliation between the parties."""
    }
]

def main():
    print(f"Seeding {len(PROVISIONS)} verified core provisions into TLRE...")
    inst_cache = {}

    for item in PROVISIONS:
        act_title = item["act"]
        if act_title not in inst_cache:
            r = db.table("legal_instruments").select("id").eq("canonical_title", act_title).execute()
            if not r.data:
                print(f"  ❌ Instrument '{act_title}' not found in legal_instruments!")
                continue
            inst_cache[act_title] = r.data[0]["id"]

        inst_id = inst_cache[act_title]
        sec_num = item["section"]
        canon_key = f"{inst_id}_{sec_num}".replace(" ", "_")

        # 1. Upsert legal_provision
        prov_res = db.table("legal_provisions").upsert(
            {
                "instrument_id": inst_id,
                "section_number": sec_num,
                "heading": item.get("heading"),
                "canonical_key": canon_key
            },
            on_conflict="canonical_key"
        ).execute()
        prov_id = prov_res.data[0]["id"]

        # 2. Upsert provision_version
        txt = item["text"].strip()
        h = sha256_hash(txt)
        db.table("provision_versions").upsert(
            {
                "provision_id": prov_id,
                "version_number": 1,
                "legal_text": txt,
                "valid_from": item["valid_from"],
                "valid_to": None,
                "is_current": True,
                "status": "active",
                "created_by_instrument_id": inst_id,
                "source_hash": h,
                "official_source_verified": True,
                "verified_by": "mehedi@justor.ai",
                "verified_at": datetime.utcnow().isoformat()
            },
            on_conflict="provision_id,version_number"
        ).execute()

        print(f"  ✓ {act_title} — {sec_num} (Verified ✓)")

    print("\n✅ All core provisions seeded into TLRE successfully.")

if __name__ == "__main__":
    main()
