from __future__ import annotations

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from backend.backend import _embed

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")).strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)

db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

CITIZEN_GUIDES = [
    {
        "id": "GUIDE-01",
        "title": "How to Register Land in Bangladesh",
        "act_name": "The Registration Act, 1908",
        "section_number": "Guide-01",
        "section_title": "Land Registration Procedure & 2026 Amendment Rules",
        "content": "To register land in Bangladesh safely, verify seller identity, title deeds, CS/SA/RS/BS Khatians, e-Namjari (mutation), and tax dakhila. Under Section 23 of the Registration Act, 1908 (as amended by Act No. 14 of 2026), documents must be presented within three months from execution. Registration is mandatory under Section 17 of Registration Act and Section 54 of Transfer of Property Act 1882.",
        "url": "/guides/property/land-registration-bangladesh"
    },
    {
        "id": "GUIDE-02",
        "title": "Mutation or Namjari Procedure in Bangladesh",
        "act_name": "State Acquisition and Tenancy Act, 1950",
        "section_number": "Guide-02",
        "section_title": "e-Namjari (Mutation) Process, Fees & DCR Generation",
        "content": "Mutation (নামজারি / খারিজ) updates the government land revenue record (Khatian) after property transfer or inheritance under Sections 116, 117, and 143 of the State Acquisition and Tenancy Act 1950. Applications are submitted online at mutation.land.gov.bd. Statutory official fees include Court fee ৳20, Notice fee ৳50, and DCR fee ৳1,100 (Total ৳1,170).",
        "url": "/guides/property/mutation-namjari"
    },
    {
        "id": "GUIDE-03",
        "title": "CS, SA, RS and BS Khatian Explained Simply",
        "act_name": "State Acquisition and Tenancy Act, 1950",
        "section_number": "Guide-03",
        "section_title": "Understanding Survey Khatians: CS, SA, RS, BS & City Jarip",
        "content": "A Khatian is a record of rights prepared during official land revenue surveys. Cadastral Survey (CS, 1888-1940), State Acquisition (SA, 1956-1962), Revisional Survey (RS, 1965-present), and Bangladesh Survey / City Survey (BS) represent sequential survey records. A khatian proves revenue recording, but title must be supported by the continuous chain of registered deeds.",
        "url": "/guides/property/khatian-types"
    },
    {
        "id": "GUIDE-04",
        "title": "How to Check Whether a Land Deed Is Genuine",
        "act_name": "The Registration Act, 1908",
        "section_number": "Guide-04",
        "section_title": "Deed Verification, Non-Encumbrance & Volume Inspection",
        "content": "To verify if a land deed is genuine, cross-check the deed number, year, Sub-Registry office, and volume index. Verify the seller's title chain, matching plot/dag numbers in the BS/RS Khatian, and conduct a mortgage information search on mutation.land.gov.bd and Registration Directorate (rd.gov.bd) records.",
        "url": "/guides/property/verify-land-deed"
    },
    {
        "id": "GUIDE-05",
        "title": "Gift Deed and Hiba of Property in Bangladesh",
        "act_name": "The Transfer of Property Act, 1882",
        "section_number": "Guide-05",
        "section_title": "Hebe / Gift Deed Registration & Conditions",
        "content": "Under Section 122-123 of the Transfer of Property Act, 1882 and Section 17 of the Registration Act, 1908, gifts of immovable property must be made by a registered instrument. Under Muslim personal law, a Hiba requires declaration (Ijab), acceptance (Qubul), and delivery of possession (Qabda), and must be formally registered under Section 17A of Registration Act for immovable property.",
        "url": "/guides/property/gift-hiba-property"
    },
    {
        "id": "GUIDE-13",
        "title": "Muslim Marriage Registration in Bangladesh",
        "act_name": "Muslim Marriages and Divorces (Registration) Act, 1974",
        "section_number": "Guide-13",
        "section_title": "Nikah Registration, Kabinnama & Legal Duties",
        "content": "Under Section 3 and 5 of the Muslim Marriages and Divorces (Registration) Act, 1974, every Muslim marriage solemnized in Bangladesh must be registered with the authorized Nikah Registrar (Kazi). The Kabinnama officially records the marriage terms, witnesses, and prompt/deferred dower (Denmohor).",
        "url": "/guides/family/muslim-marriage-registration"
    },
    {
        "id": "GUIDE-14",
        "title": "Talaq Procedure under Bangladesh Law",
        "act_name": "The Muslim Family Laws Ordinance, 1961",
        "section_number": "Guide-14",
        "section_title": "Statutory Talaq Notice, 90-day Reconciliation & Section 7 MFLO",
        "content": "Under Section 7 of the Muslim Family Laws Ordinance, 1961, any man who wishes to divorce his wife must give written notice to the Union Parishad / Pourashava / Ward Chairman and serve a copy to the wife. Talaq does not take effect until 90 days after the Chairman receives notice, during which the Arbitration Council attempts reconciliation.",
        "url": "/guides/family/talaq-procedure"
    },
    {
        "id": "GUIDE-15",
        "title": "How Can a Muslim Woman Seek Divorce in Bangladesh",
        "act_name": "The Dissolution of Muslim Marriages Act, 1939",
        "section_number": "Guide-15",
        "section_title": "Talaq-e-Tawfeez, Khula & Judicial Dissolution Grounds",
        "content": "A Muslim woman can seek divorce via: 1) Talaq-e-Tawfeez (delegated divorce under Column 18 of Kabinnama); 2) Khula (mutual consent separation); or 3) Filing a suit in Family Court under Section 2 of the Dissolution of Muslim Marriages Act, 1939 on grounds of cruelty, non-maintenance for 2 years, or abandonment for 4 years.",
        "url": "/guides/family/divorce-women"
    },
    {
        "id": "GUIDE-16",
        "title": "Dower or Mehr Rights in Bangladesh",
        "act_name": "The Family Courts Act, 2023",
        "section_number": "Guide-16",
        "section_title": "Denmohor Recovery, Prompt vs Deferred Dower & Family Court Suits",
        "content": "Denmohor is an unconditional statutory debt owed by the husband to the wife under Muslim personal law. Exercising delegated divorce does not forfeit dower. Unpaid dower can be recovered through Family Court under the Family Courts Act, 2023 within 3 years limitation period from date of demand or dissolution.",
        "url": "/guides/family/dower-mehr"
    },
    {
        "id": "GUIDE-21",
        "title": "Income Tax for Salaried People (2026-27)",
        "act_name": "Income Tax Act, 2023",
        "section_number": "Guide-21",
        "section_title": "Salaried Tax Slabs, Exemptions & Rebates for Assessment Year 2026-27",
        "content": "Under the Income Tax Act, 2023 and Finance Act, 2026, salaried individuals calculate taxable income by adding basic salary, allowances, and perquisites. Tax-free threshold applies (৳3,50,000 for general taxpayers, ৳4,00,000 for female/senior citizens). Tax slabs range from 5% to 25%, with eligible investment rebates and TDS credits.",
        "url": "/guides/tax/salary-income-tax-2026-27"
    },
    {
        "id": "GUIDE-29",
        "title": "Consumer Rights & Defective Product Complaints (DNCRP)",
        "act_name": "Consumers' Right Protection Act, 2009",
        "section_number": "Guide-29",
        "section_title": "Filing DNCRP Complaints, Compensation & 25% Whistleblower Reward",
        "content": "Under the Consumers' Right Protection Act, 2009, consumers can file written complaints with the Directorate of National Consumer Rights Protection (DNCRP) within 30 days of purchasing defective, adulterated, or falsely advertised goods. If a penalty or fine is imposed on the merchant, the complainant receives 25% of the realization amount as statutory compensation.",
        "url": "/action-guides/consumer/defective-product"
    },
    {
        "id": "GUIDE-35",
        "title": "Labour Severance, Termination & Notice Pay under BLA 2006",
        "act_name": "Bangladesh Labour Act, 2006",
        "section_number": "Guide-35",
        "section_title": "Section 26 Termination, Retrenchment & Gratuity Calculation",
        "content": "Under Section 26 of the Bangladesh Labour Act, 2006, an employer terminating a permanent employee without cause must give 120 days' written notice (monthly rated) or wages in lieu, plus 30 days' basic wages for every completed year of service, unspent earned leave encashment, and statutory gratuity.",
        "url": "/guides/employment/labour-severance-rights"
    }
]

def main():
    print(f"Starting Ingestion of {len(CITIZEN_GUIDES)} Citizen Authority Guides into Supabase...")
    
    # Check or get dummy/valid document_id
    doc_res = db.table("documents").select("id").limit(1).execute()
    doc_id = doc_res.data[0]["id"] if doc_res.data else "00000000-0000-0000-0000-000000000001"

    success_count = 0
    for i, guide in enumerate(CITIZEN_GUIDES):
        print(f"Processing ({i+1}/{len(CITIZEN_GUIDES)}): {guide['title']}...")
        embedding = _embed(guide["content"])
        
        chunk_data = {
            "document_id": doc_id,
            "chunk_index": 9000 + i,
            "act_name": guide["act_name"],
            "section_number": guide["section_number"],
            "section_title": guide["section_title"],
            "content": f"[Citizen Legal Guide] {guide['title']}\n\n{guide['content']}\n\nOfficial Source: {guide['act_name']}\nReference Link: https://justor.ai{guide['url']}",
            "status": "Active",
            "jurisdiction": "Bangladesh",
            "document_type": "Citizen Guide",
            "embedding": embedding
        }
        
        res = db.table("document_chunks").insert(chunk_data).execute()
        if res.data:
            success_count += 1
            print("  -> Ingested successfully.")
        else:
            print("  -> Ingestion returned no row data.")

    print(f"\nSuccessfully ingested {success_count}/{len(CITIZEN_GUIDES)} Citizen Authority Guides into Supabase.")

if __name__ == "__main__":
    main()
