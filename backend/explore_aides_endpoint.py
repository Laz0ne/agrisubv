"""
Comparaison : 507 aides farmer VS 226 aides agriculture
"""

import httpx
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Compare les deux approches de filtrage
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "comparison": {}
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            
            # Authentification
            logger.info("🔐 Authentification...")
            response = await client.post(
                API_BASE_URL + "/connexion/",
                headers={"X-AUTH-TOKEN": API_TOKEN, "Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": "Échec authentification"}
            
            bearer_token = response.json().get("token")
            auth_headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            
            # TEST 1 : 507 aides (targeted_audiences=farmer uniquement)
            logger.info("🔍 Test 1: targeted_audiences=farmer...")
            response = await client.get(
                API_BASE_URL + "/aids/",
                headers=auth_headers,
                params={
                    "targeted_audiences": "farmer",
                    "page_size": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results["comparison"]["farmer_only"] = {
                    "total_count": data.get("count", 0),
                    "description": "Toutes les aides ciblant les agriculteurs (production + diversification + agritourisme)",
                    "sample_titles": [aid.get("name") for aid in data.get("results", [])[:10]],
                    "categories_sample": [
                        {
                            "titre": aid.get("name"),
                            "categories": aid.get("categories", [])
                        }
                        for aid in data.get("results", [])[:5]
                    ]
                }
                logger.info(f"   ✅ {data.get('count', 0)} aides trouvées")
            
            # TEST 2 : 226 aides (targeted_audiences=farmer + categories=agriculture)
            logger.info("🔍 Test 2: targeted_audiences=farmer + categories=agriculture...")
            response = await client.get(
                API_BASE_URL + "/aids/",
                headers=auth_headers,
                params={
                    "targeted_audiences": "farmer",
                    "categories": "agriculture",
                    "page_size": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results["comparison"]["farmer_agriculture"] = {
                    "total_count": data.get("count", 0),
                    "description": "Aides strictement agricoles (production, installation, matériel)",
                    "sample_titles": [aid.get("name") for aid in data.get("results", [])[:10]],
                    "categories_sample": [
                        {
                            "titre": aid.get("name"),
                            "categories": aid.get("categories", [])
                        }
                        for aid in data.get("results", [])[:5]
                    ]
                }
                logger.info(f"   ✅ {data.get('count', 0)} aides trouvées")
            
            # TEST 3 : Toutes les catégories disponibles
            logger.info("🔍 Test 3: Liste des catégories disponibles...")
            response = await client.get(
                API_BASE_URL + "/themes/",
                headers=auth_headers,
                params={"page_size": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                results["comparison"]["available_categories"] = {
                    "total": data.get("count", 0),
                    "list": data.get("results", [])[:20]
                }
            
            # Analyse comparative
            farmer_count = results["comparison"]["farmer_only"]["total_count"]
            agri_count = results["comparison"]["farmer_agriculture"]["total_count"]
            difference = farmer_count - agri_count
            
            results["comparison"]["analysis"] = {
                "total_farmer": farmer_count,
                "total_agriculture": agri_count,
                "difference": difference,
                "difference_percentage": round((difference / farmer_count) * 100, 1),
                "recommendation": f"Les {difference} aides supplémentaires incluent : agritourisme, diversification, circuits courts, tourisme rural",
                "conclusion": "Recommandation : Importer les 507 aides, puis filtrer manuellement les moins pertinentes lors de l'enrichissement"
            }
        
        logger.info("✅ Comparaison terminée")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
