import os
import asyncio
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
import urllib.request
import json

SUPA_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

db = create_client(SUPA_URL, SUPA_KEY)

def embed(text: str):
    url = "https://openrouter.ai/api/v1/embeddings"
    payload = json.dumps({
        "model": "baai/bge-m3",
        "input": [text.replace('\x00', '')]
    }).encode("utf-8")
    headers = {
        'Authorization': f'Bearer {OPENROUTER_KEY}',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["data"][0]["embedding"]

print("1. Testing real BGE-M3 embedding for 'Land registration Section 17'...")
vec = embed("Land registration Section 17")
print(f"Embedding generated: {len(vec)} dimensions.")

print("\n2. Querying match_acts_v2 RPC...")
res = db.rpc("match_acts_v2", {
    "query_embedding": vec,
    "match_count": 4,
    "match_threshold": 0.25,
    "query_section": "17",
    "prefer_dead_law": False,
    "prefer_amended": False,
    "filter_act_name": "Registration"
}).execute()

print(f"Retrieved {len(res.data or [])} matching sections:")
for r in (res.data or []):
    print(f"  - [{r.get('act_name')}] Section {r.get('section_number')}: {r.get('section_title', '')[:50]} (Score: {r.get('similarity', 0):.3f})")
