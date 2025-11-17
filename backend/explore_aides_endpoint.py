"""
Endpoint admin pour explorer l'API Aides-Territoires
Récupère un exemple complet d'aide agricole
"""

import httpx
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def explore_aides_territoires_handler():
    """
    Explore l'API Aides-Territoires et récupère un exemple complet d'aide agricole
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        results = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "authentication": None,
            "agricultural_aids_summary": None,
            "full_example_aid": None,
            "mapping_analysis": None
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # ÉTAPE 1 : Obtenir le Bearer Token
            logger.info("🔐 Obtention du Bearer Token...")
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
                        "status_code": 200
                    }
                    
                    logger.info(f"✅ Bearer Token obtenu")
                    
                    auth_headers = {
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # ÉTAPE 2 : Récupérer les aides agricoles
                    logger.info("🔍 Récupération des aides agricoles...")
                    response = await client.get(
                        API_BASE_URL + "/aids/",
                        headers=auth_headers,
                        params={"targeted_audiences": "farmer", "page_size": 10}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        results["agricultural_aids_summary"] = {
                            "total_count": data.get("count", 0),
                            "results_returned": len(data.get("results", [])),
                            "sample_titles": [
                                aid.get("name")
                                for aid in data.get("results", [])[:5]
                            ]
                        }
                        
                        # ÉTAPE 3 : Récupérer UNE aide complète en détail
                        if data.get("results"):
                            first_aid = data["results"][0]
                            aid_slug = first_aid.get("slug")
                            
                            logger.info(f"🔍 Récupération détaillée de l'aide: {aid_slug}")
                            
                            # Récupérer l'aide complète via son slug
                            response_detail = await client.get(
                                API_BASE_URL + f"/aids/{aid_slug}/",
                                headers=auth_headers
                            )
                            
                            if response_detail.status_code == 200:
                                full_aid = response_detail.json()
                                
                                results["full_example_aid"] = {
                                    "id": full_aid.get("id"),
                                    "name": full_aid.get("name"),
                                    "slug": full_aid.get("slug"),
                                    "description": full_aid.get("description", "")[:500] + "...",
                                    "eligibility": full_aid.get("eligibility", "")[:500] + "...",
                                    "targeted_audiences": full_aid.get("targeted_audiences"),
                                    "aid_types": full_aid.get("aid_types"),
                                    "aid_types_full": full_aid.get("aid_types_full"),
                                    "financers": full_aid.get("financers"),
                                    "financers_full": full_aid.get("financers_full"),
                                    "categories": full_aid.get("categories"),
                                    "perimeter": full_aid.get("perimeter"),
                                    "perimeter_scale": full_aid.get("perimeter_scale"),
                                    "mobilization_steps": full_aid.get("mobilization_steps"),
                                    "destinations": full_aid.get("destinations"),
                                    "origin_url": full_aid.get("origin_url"),
                                    "application_url": full_aid.get("application_url"),
                                    "start_date": full_aid.get("start_date"),
                                    "submission_deadline": full_aid.get("submission_deadline"),
                                    "subvention_rate_lower_bound": full_aid.get("subvention_rate_lower_bound"),
                                    "subvention_rate_upper_bound": full_aid.get("subvention_rate_upper_bound"),
                                    "subvention_comment": full_aid.get("subvention_comment"),
                                    "loan_amount": full_aid.get("loan_amount"),
                                    "recoverable_advance_amount": full_aid.get("recoverable_advance_amount"),
                                    "contact": full_aid.get("contact"),
                                    "recurrence": full_aid.get("recurrence"),
                                    "programs": full_aid.get("programs"),
                                    "is_call_for_project": full_aid.get("is_call_for_project"),
                                    "date_created": full_aid.get("date_created"),
                                    "date_updated": full_aid.get("date_updated"),
                                    "all_available_fields": sorted(list(full_aid.keys()))
                                }
                                
                                # ÉTAPE 4 : Analyse du mapping vers AideAgricoleV2
                                results["mapping_analysis"] = {
                                    "notre_modele_v2": {
                                        "champs_requis": [
                                            "aid_id", "titre", "description", "organisme",
                                            "source", "url_externe", "date_publication",
                                            "statut", "zone_geo", "beneficiaires",
                                            "type_aide", "montant_min", "montant_max",
                                            "taux_subvention_min", "taux_subvention_max",
                                            "eligibilite_raw", "contact_info"
                                        ]
                                    },
                                    "mapping_propose": {
                                        "aid_id": f"slug: {full_aid.get('slug')}",
                                        "titre": f"name: {full_aid.get('name')[:50]}...",
                                        "description": "description (texte complet)",
                                        "organisme": f"financers_full: {full_aid.get('financers_full')}",
                                        "source": "'aides-territoires'",
                                        "url_externe": f"origin_url: {full_aid.get('origin_url')}",
                                        "date_publication": f"date_created: {full_aid.get('date_created')}",
                                        "statut": "'active' si is_live",
                                        "zone_geo": {
                                            "perimeter": full_aid.get("perimeter"),
                                            "perimeter_scale": full_aid.get("perimeter_scale")
                                        },
                                        "beneficiaires": f"targeted_audiences: {full_aid.get('targeted_audiences')}",
                                        "type_aide": f"aid_types: {full_aid.get('aid_types')}",
                                        "montant_min": "À extraire de subvention_comment",
                                        "montant_max": "À extraire de subvention_comment",
                                        "taux_subvention_min": f"subvention_rate_lower_bound: {full_aid.get('subvention_rate_lower_bound')}",
                                        "taux_subvention_max": f"subvention_rate_upper_bound: {full_aid.get('subvention_rate_upper_bound')}",
                                        "eligibilite_raw": f"eligibility: {full_aid.get('eligibility', '')[:100]}...",
                                        "contact_info": f"contact: {full_aid.get('contact')}"
                                    }
                                }
                                
                                logger.info(f"✅ Aide complète récupérée: {full_aid.get('name')}")
                            else:
                                results["full_example_aid_error"] = f"HTTP {response_detail.status_code}"
                    else:
                        results["agricultural_aids_error"] = f"HTTP {response.status_code}"
                        
                else:
                    results["authentication"] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text[:300]
                    }
                    
            except Exception as e:
                logger.error(f"❌ Erreur: {e}")
                results["error"] = str(e)
        
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
