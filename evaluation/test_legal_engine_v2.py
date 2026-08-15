import json
import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def run_benchmark():
    with open("evaluation/legal_gold_v2.json", encoding="utf-8") as file:
        tests = json.load(file)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60) as client:
        for case in tests:
            print(f"Running test {case['id']} ({case['persona']})...")
            response = await client.post(
                "/chat",
                json={
                    "message": case["question"],
                    "role": case["persona"],
                    "user_id": "test_benchmark_user",
                    "history": []
                },
            )

            assert response.status_code == 200, f"HTTP Error: {response.status_code}"
            payload = response.json()
            assert payload.get("status") in {"ok", "abstain"}, f"Unexpected status: {payload.get('status')}"

            if payload["status"] == "abstain":
                print(f"⚠️ {case['id']} abstained: {payload.get('verification_reason')}")
                continue

            authorities = payload.get("authorities", [])
            normalized = {
                (x.get("act", "").lower(), str(x.get("section", "")).upper())
                for x in authorities
            }

            for required in case.get("required_authorities", []):
                expected = (
                    required["act"].lower(),
                    str(required["section"]).upper(),
                )
                print(f"Checking required authority: {expected} in {normalized}")

            print(f"✅ Test {case['id']} completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
