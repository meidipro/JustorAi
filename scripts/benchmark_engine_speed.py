import asyncio
import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv('.env')
from backend.backend import legal_engine_v2

async def benchmark():
    query = 'Explain the 2026 amendment deadline for land registration under Section 23 of the Registration Act.'
    t0 = time.perf_counter()
    res = await legal_engine_v2.answer(query, 'General Public')
    elapsed = time.perf_counter() - t0
    
    print(f'ELAPSED TIME: {elapsed:.2f}s')
    print('STATUS:', res.get('status'))
    print('REASONING STEPS:')
    for step in res.get('reasoning_steps', []):
        print(f"  [{step['step']}] {step['title']}: {step['summary']}")
    print('\nANSWER PREVIEW:')
    print(res.get('answer', '')[:500].encode('ascii', 'replace').decode('ascii'))

if __name__ == '__main__':
    asyncio.run(benchmark())
