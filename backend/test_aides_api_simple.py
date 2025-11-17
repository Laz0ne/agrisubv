"""
Test simple de l'API Aides-Territoires
Pour comprendre sa structure réelle
"""

import httpx
import asyncio
import json

API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"

async def test_api():
    headers = {
        "X-AUTH-TOKEN": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 80)
        print("TEST 1 : Root endpoint")
        print("=" * 80)
        response = await client.get(API_BASE_URL + "/", headers=headers)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 80)
        print("TEST 2 : Recherche aides avec mot-clé 'agricole'")
        print("=" * 80)
        response = await client.get(
            API_BASE_URL + "/aids/",
            headers=headers,
            params={"text": "agricole", "page_size": 3}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Count: {data.get('count', 0)}")
        print(f"Results: {len(data.get('results', []))}")
        if data.get("results"):
            print("\nPremière aide:")
            print(json.dumps(data["results"][0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_api())
