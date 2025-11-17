"""
Endpoint admin pour explorer l'API Aides-Territoires
Avec authentification en 2 étapes (connexion puis Bearer Token)
"""

import httpx
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Explore l'API Aides-Territoires avec authentification correcte
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "authentication": None,
            "search_results": []
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # ÉTAPE 1 : Obtenir le Bearer Token
            logger.info("🔐 Étape 1: Obtention du Bearer Token...")
            try:
                response = await client.post(
                    API_BASE_URL + "/connexion/",
                    headers={
                        "X-AUTH-TOKEN": API_TOKEN,
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    auth_data = response.json()
                    bearer_token = auth_data.get("token")
                    
                    results["authentication"] = {
                        "success": True,
                        "status_code": 200,
                        "bearer_token_obtained": bool(bearer_token)
                    }
                    
                    logger.info(f"✅ Bearer Token obtenu: {bearer_token[:50]}...")
                    
                    # ÉTAPE 2 : Utiliser le Bearer Token pour rechercher des aides
                    auth_headers = {
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # TEST 1 : Recherche sans filtre
                    logger.info("🔍 Test 1: Recherche sans filtre...")
                    try:
                        response = await client.get(
                            API_BASE_URL + "/aids/",
                            headers=auth_headers,
                            params={"page_size": 5}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            results["search_results"].append({
                                "test": "Sans filtre",
                                "status_code": 200,
                                "total_count": data.get("count", 0),
                                "results_returned": len(data.get("results", [])),
                                "sample_aids": [
                                    {
                                        "id": aid.get("id"),
                                        "name": aid.get("name"),
                                        "targeted_audiences": aid.get("targeted_audiences", [])
                                    }
                                    for aid in data.get("results", [])[:3]
                                ]
                            })
                            
                            # Analyser la structure complète
                            if data.get("results"):
                                first_aid = data["results"][0]
                                results["first_aid_full_structure"] = {
                                    "all_fields": sorted(list(first_aid.keys())),
                                    "sample_data": {
                                        "id": first_aid.get("id"),
                                        "name": first_aid.get("name"),
                                        "targeted_audiences": first_aid.get("targeted_audiences"),
                                        "aid_types": first_aid.get("aid_types"),
                                        "eligibility": str(first_aid.get("eligibility", ""))[:300]
                                    }
                                }
                            
                            logger.info(f"✅ Test 1: {data.get('count', 0)} aides trouvées")
                    except Exception as e:
                        logger.error(f"❌ Test 1 erreur: {e}")
                        results["search_results"].append({"test": "Sans filtre", "error": str(e)})
                    
                    # TEST 2 : Recherche avec text=agricole
                    logger.info("🔍 Test 2: Recherche text=agricole...")
                    try:
                        response = await client.get(
                            API_BASE_URL + "/aids/",
                            headers=auth_headers,
                            params={"text": "agricole", "page_size": 5}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            results["search_results"].append({
                                "test": "text=agricole",
                                "status_code": 200,
                                "total_count": data.get("count", 0),
                                "results_returned": len(data.get("results", [])),
                                "sample_aids": [
                                    {"id": aid.get("id"), "name": aid.get("name")}
                                    for aid in data.get("results", [])[:3]
                                ]
                            })
                            logger.info(f"✅ Test 2: {data.get('count', 0)} aides trouvées")
                    except Exception as e:
                        logger.error(f"❌ Test 2 erreur: {e}")
                        results["search_results"].append({"test": "text=agricole", "error": str(e)})
                    
                    # TEST 3 : Recherche avec targeted_audiences=farmer
                    logger.info("🔍 Test 3: Recherche targeted_audiences=farmer...")
                    try:
                        response = await client.get(
                            API_BASE_URL + "/aids/",
                            headers=auth_headers,
                            params={"targeted_audiences": "farmer", "page_size": 5}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            results["search_results"].append({
                                "test": "targeted_audiences=farmer",
                                "status_code": 200,
                                "total_count": data.get("count", 0),
                                "results_returned": len(data.get("results", [])),
                                "sample_aids": [
                                    {"id": aid.get("id"), "name": aid.get("name")}
                                    for aid in data.get("results", [])[:3]
                                ]
                            })
                            logger.info(f"✅ Test 3: {data.get('count', 0)} aides trouvées")
                    except Exception as e:
                        logger.error(f"❌ Test 3 erreur: {e}")
                        results["search_results"].append({"test": "targeted_audiences=farmer", "error": str(e)})
                    
                else:
                    results["authentication"] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text[:300]
                    }
                    logger.error(f"❌ Échec authentification: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur authentification: {e}")
                results["authentication"] = {"error": str(e)}
        
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
