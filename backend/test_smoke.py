import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add root and backend folders to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))

try:
    import backend
    app = backend.app
except ImportError:
    from backend import app

client = TestClient(app)

tests = [
    {
        "message": "Section 7 NAT Act — tenant holding after lease expiry",
        "role": "Law Student"
    },
    {
        "message": "Inherited 70 bighas under Land Reforms Act 2023",
        "role": "General Public"
    },
    {
        "message": "Section 26A NAT Act sub-letting",
        "role": "Legal Professional"
    },
    {
        "message": "Section 438 anticipatory bail",
        "role": "Legal Professional"
    },
    {
        "message": "Penal Code Section 302",
        "role": "General Public"
    }
]

async def main():
    print("="*60)
    print("JUSTOR AI RAG SYSTEM SMOKE TEST")
    print("="*60)
    
    for i, t in enumerate(tests, 1):
        print(f"\n[Test {i}/5] '{t['message']}' (Persona: {t['role']})")
        print("-" * 50)
        try:
            # TestClient request
            response = client.post("/chat", json={
                "message": t["message"],
                "role": t["role"],
                "history": [],
                "user_id": "smoke-test-agent"
            })
            
            print(f"HTTP Status: {response.status_code}")
            if response.status_code == 200:
                res_data = response.json()
                print(f"Retrieval Status: {res_data.get('retrieval_status')}")
                print(f"Model Used:       {res_data.get('model_used')}")
                print(f"Sources Used:     {res_data.get('sources_used')}")
                print(f"Response Preview:\n{res_data.get('response')[:400]}...")
            else:
                print(f"Error Response: {response.text}")
        except Exception as e:
            print(f"Failed to execute request: {e}")

if __name__ == "__main__":
    # Run the async main loop using asyncio
    asyncio.run(main())
