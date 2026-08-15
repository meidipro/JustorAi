import os
import sys
import asyncio
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root_dir, "backend"))

import backend
app = backend.app
client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("JUSTOR AI PASS/FAIL QUALITY GATE VERIFICATION")
    print("=" * 60)

    # 1. Unauthenticated Mutations Check
    print("\n[Gate 1/4] Unauthenticated Mutations Protection...")
    r_upload = client.post("/upload")
    print(f"  POST /upload without JWT: HTTP {r_upload.status_code} (Expected: 401)")
    assert r_upload.status_code == 401, f"Expected 401, got {r_upload.status_code}"

    r_docs = client.get("/documents")
    print(f"  GET /documents without JWT: HTTP {r_docs.status_code} (Expected: 401)")
    assert r_docs.status_code == 401, f"Expected 401, got {r_docs.status_code}"

    r_del = client.delete("/documents/dummy-id")
    print(f"  DELETE /documents/id without JWT: HTTP {r_del.status_code} (Expected: 401)")
    assert r_del.status_code == 401, f"Expected 401, got {r_del.status_code}"
    print("  ✅ PASS: All administrative/mutation endpoints require Bearer JWT token.")

    # 2. Public Guest Chat Access & query_run_id Telemetry
    print("\n[Gate 2/4] Public Guest Chat Access & Telemetry...")
    r_chat = client.post("/chat", json={
        "message": "What is the penalty for defamation under Penal Code?",
        "role": "General Public"
    })
    print(f"  POST /chat as Guest: HTTP {r_chat.status_code} (Expected: 200)")
    assert r_chat.status_code == 200, f"Expected 200, got {r_chat.status_code}"
    chat_data = r_chat.json()
    run_id = chat_data.get("query_run_id")
    print(f"  query_run_id generated: {run_id}")
    assert run_id, "Missing query_run_id in response!"
    
    # Test POST /feedback
    r_fb = client.post("/feedback", json={"query_run_id": run_id, "rating": 1, "comment": "Excellent answer"})
    print(f"  POST /feedback: HTTP {r_fb.status_code} (Expected: 200)")
    assert r_fb.status_code == 200, f"Expected 200, got {r_fb.status_code}"
    print("  ✅ PASS: Guest demo mode works cleanly over /chat with telemetry & feedback.")

    # 3. Hard Abstention — CrPC 438, CPC 100, Income Tax Ordinance 1984
    print("\n[Gate 3/4] Hard Abstention Checks...")
    test_abstain_queries = [
        ("CrPC Section 438 anticipatory bail", "CrPC 438"),
        ("Section 100 of CPC second appeal", "CPC 100"),
        ("Income Tax Ordinance 1984 tax rebate", "Income Tax Ordinance 1984")
    ]
    for query, label in test_abstain_queries:
        res = client.post("/chat", json={"message": query, "role": "General Public"}).json()
        status = res.get("retrieval_status")
        resp_text = res.get("response", "")
        print(f"  {label} -> retrieval_status: '{status}'")
        assert status in {"out_of_scope_or_repealed", "no_results", "section_not_exact"}, f"Failed hard abstention for {label}, got status: {status}"
        print(f"  Response Preview: {resp_text[:120]}...")
    print("  ✅ PASS: Hard abstention engine successfully fired on out-of-scope/repealed provisions.")

    # 4. Section 4 Isolation Test
    print("\n[Gate 4/4] Section 4 Canonical Isolation...")
    res_sec4 = client.post("/chat", json={
        "message": "Section 4 of Muslim Family Laws Ordinance grandson inheritance",
        "role": "General Public",
        "eval_mode": True
    }).json()
    sources = res_sec4.get("retrieved_sources", [])
    secs_retrieved = [str(s.get("section_number")) for s in sources if s.get("section_number")]
    print(f"  Retrieved sections for Section 4 query: {secs_retrieved}")
    bad_matches = [s for s in secs_retrieved if s in {"14", "40", "54", "400"}]
    assert not bad_matches, f"Section 4 matched substring sections: {bad_matches}"
    print("  ✅ PASS: Querying Section 4 isolated exact section (zero 14/40/54 collisions).")

    print("\n" + "=" * 60)
    print("ALL 4 QUALITY GATES PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
