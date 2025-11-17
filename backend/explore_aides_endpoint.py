"""
Investigation approfondie de l'API Aides-Territoires
Recherche de critères d'éligibilité structurés
"""

import httpx
import json
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Investigation complète pour trouver les critères d'éligibilité structurés
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "investigation": {
                "root_endpoints": None,
                "sample_aids_full": [],
                "eligibility_analysis": {},
                "filter_capabilities": {},
                "available_filters": {}
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            
            # ÉTAPE 1 : Authentification
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
            
            # ÉTAPE 2 : Explorer le root endpoint
            logger.info("🔍 Exploration du root endpoint...")
            try:
                response = await client.get(API_BASE_URL + "/", headers=auth_headers)
                if response.status_code == 200:
                    root_data = response.json()
                    results["investigation"]["root_endpoints"] = root_data
                    logger.info(f"   ✅ Endpoints disponibles: {list(root_data.keys())}")
            except Exception as e:
                logger.error(f"   ❌ Erreur root: {e}")
            
            # ÉTAPE 3 : Récupérer 3 aides agricoles différentes COMPLÈTES
            logger.info("🔍 Récupération de 3 aides agricoles complètes...")
            try:
                response = await client.get(
                    API_BASE_URL + "/aids/",
                    headers=auth_headers,
                    params={"targeted_audiences": "farmer", "page_size": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    aids = data.get("results", [])
                    
                    for i, aid_summary in enumerate(aids, 1):
                        slug = aid_summary.get("slug")
                        logger.info(f"   📥 Aide {i}/{len(aids)}: {slug}")
                        
                        # Récupérer l'aide complète
                        response_detail = await client.get(
                            API_BASE_URL + f"/aids/{slug}/",
                            headers=auth_headers
                        )
                        
                        if response_detail.status_code == 200:
                            full_aid = response_detail.json()
                            
                            # Analyser les champs liés à l'éligibilité
                            eligibility_fields = {
                                "id": full_aid.get("id"),
                                "name": full_aid.get("name"),
                                "slug": slug,
                                "all_fields": sorted(list(full_aid.keys())),
                                "eligibility_text": full_aid.get("eligibility", "")[:500],
                                "targeted_audiences": full_aid.get("targeted_audiences"),
                                "perimeter": full_aid.get("perimeter"),
                                "perimeter_scale": full_aid.get("perimeter_scale"),
                                "mobilization_steps": full_aid.get("mobilization_steps"),
                                "destinations": full_aid.get("destinations"),
                                "categories": full_aid.get("categories"),
                                "aid_types": full_aid.get("aid_types"),
                                
                                # Champs suspects qui pourraient contenir des critères
                                "project_examples": full_aid.get("project_examples"),
                                "is_charged": full_aid.get("is_charged"),
                                "european_aid": full_aid.get("european_aid"),
                            }
                            
                            # Chercher des champs custom/metadata
                            potential_criteria_fields = []
                            for key in full_aid.keys():
                                if any(keyword in key.lower() for keyword in 
                                       ["criteria", "condition", "requirement", "eligible", 
                                        "agricul", "farm", "production", "surface", "age"]):
                                    potential_criteria_fields.append({
                                        "field": key,
                                        "value": full_aid.get(key)
                                    })
                            
                            eligibility_fields["potential_criteria_fields"] = potential_criteria_fields
                            
                            results["investigation"]["sample_aids_full"].append(eligibility_fields)
                            
                            logger.info(f"      ✅ Champs potentiels: {len(potential_criteria_fields)}")
            except Exception as e:
                logger.error(f"   ❌ Erreur récupération aides: {e}")
            
            # ÉTAPE 4 : Tester les capacités de filtrage
            logger.info("🔍 Test des capacités de filtrage...")
            filter_tests = [
                {
                    "name": "Filtre par région + agriculteur",
                    "params": {"targeted_audiences": "farmer", "perimeter_scale": "region"}
                },
                {
                    "name": "Recherche avec mots-clés 'élevage'",
                    "params": {"targeted_audiences": "farmer", "text": "élevage"}
                },
                {
                    "name": "Filtre par catégorie",
                    "params": {"targeted_audiences": "farmer", "categories": "agriculture"}
                },
                {
                    "name": "Filtre par type d'aide",
                    "params": {"targeted_audiences": "farmer", "aid_types": "grant"}
                }
            ]
            
            for test in filter_tests:
                try:
                    response = await client.get(
                        API_BASE_URL + "/aids/",
                        headers=auth_headers,
                        params={**test["params"], "page_size": 1}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results["investigation"]["filter_capabilities"][test["name"]] = {
                            "params": test["params"],
                            "total_count": data.get("count", 0),
                            "works": True
                        }
                        logger.info(f"   ✅ {test['name']}: {data.get('count', 0)} résultats")
                    else:
                        results["investigation"]["filter_capabilities"][test["name"]] = {
                            "params": test["params"],
                            "works": False,
                            "status_code": response.status_code
                        }
                except Exception as e:
                    logger.error(f"   ❌ {test['name']}: {e}")
            
            # ÉTAPE 5 : Chercher un endpoint de filtres disponibles
            logger.info("🔍 Recherche d'endpoints de métadonnées...")
            metadata_endpoints = [
                "/aids/audiences/",
                "/aids/categories/",
                "/aids/themes/",
                "/perimeters/",
                "/programs/",
                "/backers/",
                "/aids/filters/"  # Hypothèse
            ]
            
            for endpoint in metadata_endpoints:
                try:
                    response = await client.get(
                        API_BASE_URL + endpoint,
                        headers=auth_headers,
                        params={"page_size": 5}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results["investigation"]["available_filters"][endpoint] = {
                            "exists": True,
                            "sample_data": data if isinstance(data, list) else data.get("results", [])[:3]
                        }
                        logger.info(f"   ✅ {endpoint}: disponible")
                    else:
                        results["investigation"]["available_filters"][endpoint] = {
                            "exists": False,
                            "status_code": response.status_code
                        }
                except Exception as e:
                    results["investigation"]["available_filters"][endpoint] = {
                        "exists": False,
                        "error": str(e)
                    }
            
            # ÉTAPE 6 : Analyse finale
            results["investigation"]["eligibility_analysis"] = {
                "structured_criteria_found": False,
                "text_only_eligibility": True,
                "available_structured_filters": [
                    "targeted_audiences",
                    "perimeter (géographie)",
                    "categories",
                    "aid_types",
                    "text (recherche textuelle)"
                ],
                "conclusion": "L'API ne semble pas exposer de critères d'éligibilité structurés (SAU, productions, statuts juridiques). Les critères sont dans le champ 'eligibility' en texte libre (HTML).",
                "recommendation": "Il faudra soit parser le texte avec NLP/LLM, soit enrichir manuellement les aides importantes."
            }
        
        logger.info("✅ Investigation terminée")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur globale: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
