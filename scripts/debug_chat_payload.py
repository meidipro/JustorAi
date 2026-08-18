import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv('.env')

from backend.backend import chat, ChatRequest
from fastapi import Request

async def debug():
    payload = {
        "message": "What are the steps to file for a divorce in Bangladesh?",
        "user_id": "guest_1786913125877_cq1new6ku6v",
        "role": "General Public",
        "history": [{"role": "assistant", "content": "Peace be upon you! What can I help you with today?"}]
    }
    
    req_model = ChatRequest(**payload)
    
    # Mock Request
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/chat",
        "headers": [],
        "client": ("127.0.0.1", 5000)
    }
    req = Request(scope)
    
    try:
        res = await chat(req_model, req)
        print("SUCCESS! Status Code:", getattr(res, "status_code", 200))
        print("Content:", res.body.decode('utf-8')[:500] if hasattr(res, "body") else res)
    except Exception as e:
        import traceback
        print("CAUGHT EXCEPTION IN CHAT ENDPOINT:")
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(debug())
