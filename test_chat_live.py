import os
import sys
import asyncio
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env')
import backend.backend as b
from fastapi import Request

async def run_test():
    req = b.ChatRequest(
        message="Can an agreement for sale of land be specifically enforced if it is not registered in Bangladesh?",
        role="Legal Professional",
        history=[]
    )
    print("Testing /chat pipeline with Legal Professional role...")
    
    # Mock FastAPI request
    class MockClient:
        host = "127.0.0.1"
    class MockRequest:
        client = MockClient()
        headers = {}
    
    raw_response = await b.chat(req, MockRequest())
    import json
    response = json.loads(raw_response.body.decode('utf-8'))
    print("\n=== RESPONSE RECEIVED ===")
    print("Model used:", response.get("model_used"))
    print("Sources used:", response.get("sources_used"))
    print("Intent detected:", response.get("intent", {}).get("detected_act"))
    print("\n=== FULL ANSWER WITH VERIFIED BADGES & FOOTER ===")
    print(response.get("response", ""))

if __name__ == "__main__":
    asyncio.run(run_test())
