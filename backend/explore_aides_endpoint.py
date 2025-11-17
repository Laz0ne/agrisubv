"""
Endpoint admin pour explorer l'API Aides-Territoires
"""

import httpx
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Explore l'API Aides-Territoires avec debug détaillé
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        headers = {
            "X-AUTH-TOKEN": API_TOKEN,
            "Content-Type": "application/json"
        }
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_connection": None,
            "root_endpoint_response": None,
            "aids_search_response": None
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1 : Root endpoint
            logger.info("🔍 Test root endpoint...")
            try:
                response = await client.get(API_BASE_URL + "/", headers=headers)
                results["api_connection"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    root_data = response.json()
                    results["root_endpoint_response"] = root_data
                    logger.info(f"✅ Root endpoint OK, keys: {list(root_data.keys())}")
                else:
                    results["root_endpoint_error"] = response.text[:500]
            except Exception as e:
                logger.error(f"❌ Erreur root: {e}")
                results["root_endpoint_error"] = str(e)
            
            # Test 2 : Recherche d'aides agricoles
            logger.info("🔍 Recherche aides agricoles...")
            try:
                params = {
                    "text": "agricole",
                    "page_size": 5
                }
                response = await client.get(
                    API_BASE_URL + "/aids/",
                    headers=headers,
                    params=params
                )
                
                logger.info(f"Aids search status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    results["aids_search_response"] = {
                        "status_code": 200,
                        "total_count": data.get("count", 0),
                        "results_returned": len(data.get("results", [])),
                        "sample_aids": [
                            {
                                "id": aid.get("id"),
                                "name": aid.get("name"),
                                "slug": aid.get("slug"),
                                "url": aid.get("url"),
                                "targeted_audiences": aid.get("targeted_audiences", []),
                                "aid_types": aid.get("aid_types", []),
                                "available_fields": list(aid.keys())
                            }
                            for aid in data.get("results", [])[:3]
                        ]
                    }
                    
                    # Analyser première aide en détail
                    if data.get("results"):
                        first_aid = data["results"][0]
                        results["first_aid_full_structure"] = {
                            "fields": sorted(list(first_aid.keys())),
                            "targeted_audiences": first_aid.get("targeted_audiences"),
                            "aid_types": first_aid.get("aid_types"),
                            "eligibility_preview": str(first_aid.get("eligibility", ""))[:200]
                        }
                    
                    logger.info(f"✅ {data.get('count', 0)} aides trouvées")
                else:
                    results["aids_search_error"] = {
                        "status_code": response.status_code,
                        "error": response.text[:500]
                    }
            except Exception as e:
                logger.error(f"❌ Erreur search: {e}")
                results["aids_search_error"] = str(e)
        
        logger.info("✅ Exploration terminée")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur globale: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
