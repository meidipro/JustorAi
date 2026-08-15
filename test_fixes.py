import asyncio
import sys, os
from dotenv import load_dotenv
load_dotenv('.env')

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from backend import classify_query, _embed_async, retrieve_context

async def main():
    queries = [
        ("Q01", "Can a person apprehending arrest get anticipatory bail under CrPC in Bangladesh?"),
        ("Q13", "I have a property dispute valued at Tk 4.5 Crore. Which court has the original civil jurisdiction?"),
        ("Q29", "When a sharecropper (bargadar) passes away, what happens to the cultivation rights under the Land Reforms Act 2023?"),
        ("Q42", "I am a petitioner in a Section 96 pre-emption case under the State Acquisition and Tenancy Act 1950.")
    ]
    for qid, q in queries:
        intent = classify_query(q)
        vec = await _embed_async(q)
        acts, dlrs = await retrieve_context(vec, intent)
        print(f"=== {qid} ===")
        print("Detected Act:", intent.get("detected_act"))
        for i, a in enumerate(acts[:3]):
            print(f"  [{i+1}] {a.get('act_name')} | Sec {a.get('section_number')}: {a.get('section_title')}")

if __name__ == "__main__":
    asyncio.run(main())
