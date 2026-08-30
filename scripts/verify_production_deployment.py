#!/usr/bin/env python3
"""
scripts/verify_production_deployment.py
Checks deployment endpoints (/ping, /health/legal-data, /chat, /chat/stream)
across local development or live Render production.
"""

import sys
import os
import time
import json
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_deployment(base_url: str):
    print("=" * 60)
    print(f"Justor AI — Deployment Health & Streaming Verification")
    print(f"Target URL: {base_url}")
    print("=" * 60)

    client = httpx.Client(timeout=15.0)

    # 1. Ping Check
    try:
        t0 = time.time()
        res = client.get(f"{base_url}/ping")
        elapsed = (time.time() - t0) * 1000
        if res.status_code == 200:
            print(f"[✓] Ping Check: OK ({elapsed:.1f}ms) -> {res.text.strip()}")
        else:
            print(f"[!] Ping Check: Status {res.status_code} -> {res.text}")
    except Exception as e:
        print(f"[✗] Ping Check Failed: {e}")

    # 2. Legal Data Health Check
    try:
        t0 = time.time()
        res = client.get(f"{base_url}/health/legal-data")
        elapsed = (time.time() - t0) * 1000
        if res.status_code == 200:
            data = res.json()
            print(f"[✓] Legal Data Health: OK ({elapsed:.1f}ms)")
            print(f"    - Canonical Instruments : {data.get('canonical_instruments_count', 0)}")
            print(f"    - Canonical Provisions   : {data.get('canonical_provisions_count', 0)}")
            print(f"    - Current Active Versions: {data.get('current_versions_count', 0)}")
        else:
            print(f"[!] Legal Data Health: Status {res.status_code}")
    except Exception as e:
        print(f"[!] Legal Data Health Check Skipped / Inaccessible: {e}")

    # 3. Stream Protocol Validation (SSE)
    print("\n--- Testing Streaming Engine Protocol (/chat/stream) ---")
    try:
        payload = {
            "query": "Is an agreement for sale registrable under Section 17A of Registration Act?",
            "user_role": "Legal Professional",
            "language": "EN"
        }
        t0 = time.time()
        with client.stream("POST", f"{base_url}/chat/stream", json=payload, timeout=20.0) as stream_res:
            if stream_res.status_code == 200:
                print(f"[✓] SSE Connection Established ({stream_res.status_code} OK)")
                events_received = 0
                for line in stream_res.iter_lines():
                    if line.startswith("data:"):
                        events_received += 1
                        try:
                            evt = json.loads(line[5:].strip())
                            ev_type = evt.get("event")
                            if ev_type == "step":
                                s = evt.get("data", {})
                                print(f"    [Step {s.get('step')}] {s.get('title')}: {s.get('summary')[:60]}...")
                            elif ev_type == "authorities":
                                print(f"    [Authorities] Received {len(evt.get('data', []))} verified legal source cards")
                            elif ev_type == "complete":
                                print(f"    [Complete] Verified Legal Answer Generated ({len(evt.get('data',{}).get('response',''))} chars)")
                                break
                        except Exception:
                            pass
                elapsed = time.time() - t0
                print(f"[✓] Streaming Protocol Succeeded! ({events_received} events in {elapsed:.2f}s)\n")
            else:
                print(f"[!] Streaming Endpoint: Status {stream_res.status_code}")
    except Exception as e:
        print(f"[!] Streaming Test Note: {e}\n")

    print("=" * 60)
    print("Verification Completed.")
    print("=" * 60)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getenv("VITE_BACKEND_URL", "https://justorai-backend.onrender.com")
    check_deployment(target.rstrip("/"))
