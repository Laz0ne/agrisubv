"""
Endpoint admin pour explorer l'API Aides-Territoires
À ajouter dans server.py
"""

import httpx
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Explore l'API Aides-Territoires pour identifier les aides agricoles
    Retourne les audiences, catégories et échantillons d'aides
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_connection": None,
            "audiences": [],
            "categories": [],
            "sample_aids": [],
            "agricultural_keywords": []
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test connexion API
            logger.info("🔍 Test de connexion API Aides-Territoires...")
            try:
                response = await client.get(API_BASE_URL + "/", headers=headers)
                results["api_connection"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "endpoints": response.json() if response.status_code == 200 else {}
                }
                logger.info(f"✅ Connexion réussie: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Erreur connexion: {e}")
                results["api_connection"] = {"error": str(e)}
            
            # Explorer les audiences
            logger.info("👥 Exploration des audiences...")
            try:
                response = await client.get(API_BASE_URL + "/aids/audiences/", headers=headers)
                if response.status_code == 200:
                    audiences = response.json()
                    results["audiences"] = audiences
                    
                    # Identifier audiences agricoles
                    agri_audiences = [a for a in audiences if any(
                        keyword in str(a).lower() 
                        for keyword in ["agricul", "farmer", "rural", "exploit", "elevage"]
                    )]
                    results["agricultural_audiences"] = agri_audiences
                    logger.info(f"✅ {len(audiences)} audiences trouvées, {len(agri_audiences)} agricoles")
            except Exception as e:
                logger.error(f"❌ Erreur audiences: {e}")
                results["audiences_error"] = str(e)
            
            # Explorer les catégories
            logger.info("📂 Exploration des catégories...")
            try:
                response = await client.get(API_BASE_URL + "/categories/", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    categories = data.get("results", []) if isinstance(data, dict) else data
                    results["categories"] = [
                        {
                            "id": c.get("id"), 
                            "name": c.get("name"), 
                            "slug": c.get("slug")
                        }
                        for c in categories
                    ]
                    
                    # Catégories agricoles
                    agri_categories = [c for c in categories if any(
                        keyword in str(c).lower()
                        for keyword in ["agricul", "rural", "environment", "bio", "elevage"]
                    )]
                    results["agricultural_categories"] = [
                        {"name": c.get("name"), "slug": c.get("slug")}
                        for c in agri_categories
                    ]
                    logger.info(f"✅ {len(categories)} catégories trouvées, {len(agri_categories)} agricoles")
            except Exception as e:
                logger.error(f"❌ Erreur catégories: {e}")
                results["categories_error"] = str(e)
            
            # Rechercher aides agricoles
            logger.info("🔍 Recherche d'aides agricoles...")
            try:
                params = {
                    "text": "agricole",
                    "page_size": 10
                }
                response = await client.get(API_BASE_URL + "/aids/", headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results["total_aids_found"] = data.get("count", 0)
                    
                    aids = data.get("results", [])
                    results["sample_aids"] = [
                        {
                            "id": aid.get("id"),
                            "name": aid.get("name"),
                            "slug": aid.get("slug"),
                            "targeted_audiences": aid.get("targeted_audiences", []),
                            "aid_types": aid.get("aid_types", []),
                            "perimeter": aid.get("perimeter"),
                            "eligibility": aid.get("eligibility"),
                            "url": aid.get("url")
                        }
                        for aid in aids[:5]
                    ]
                    
                    # Analyser la structure d'une aide complète
                    if aids:
                        first_aid = aids[0]
                        results["aid_structure_fields"] = sorted(list(first_aid.keys()))
                        results["sample_full_aid"] = first_aid
                    
                    logger.info(f"✅ {len(aids)} aides trouvées")
            except Exception as e:
                logger.error(f"❌ Erreur recherche aides: {e}")
                results["aids_search_error"] = str(e)
        
        logger.info("✅ Exploration terminée avec succès")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur exploration: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }