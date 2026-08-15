import os
import sys
import asyncio
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env')
import backend.backend as b

async def run_tests():
    class MockClient:
        host = "127.0.0.1"
    class MockRequest:
        client = MockClient()
        headers = {}
    
    print("=== TEST 1: Greeting query 'hi' ===")
    req1 = b.ChatRequest(message="hi", user_id="guest_test_123", role="General Public", history=[])
    res1 = await b.chat(req1, MockRequest())
    data1 = json.loads(res1.body.decode('utf-8'))
    print("Status:", data1.get("retrieval_status"))
    print("Model:", data1.get("model_used"))
    print("Response:\n", data1.get("response"), "\n")

    print("=== TEST 2: Legal query 'What are the steps to file for a divorce in Bangladesh?' ===")
    req2 = b.ChatRequest(message="What are the steps to file for a divorce in Bangladesh?", user_id="guest_test_123", role="General Public", history=[])
    res2 = await b.chat(req2, MockRequest())
    data2 = json.loads(res2.body.decode('utf-8'))
    print("Status:", data2.get("retrieval_status"))
    print("Model:", data2.get("model_used"))
    print("Sources used:", data2.get("sources_used"))
    print("Response preview:\n", data2.get("response")[:300], "...\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
