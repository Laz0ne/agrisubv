"""
Endpoint pour exporter toutes les aides agricoles en JSON
Export des 507 aides ciblant les agriculteurs pour enrichissement manuel
"""

import httpx
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def export_aides_handler():
    """
    Exporte toutes les 507 aides agricoles (targeted_audiences=farmer) en JSON
    Format facilement éditable pour enrichissement manuel
    """
    try:
        API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
        API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            
            # Authentification
            logger.info("🔐 Authentification API Aides-Territoires...")
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
            
            # Récupération de TOUTES les aides agricoles (507 aides)
            logger.info("📥 Récupération des 507 aides agricoles...")
            all_aids = []
            page = 1
            
            while True:
                logger.info(f"   📄 Page {page}...")
                response = await client.get(
                    API_BASE_URL + "/aids/",
                    headers=auth_headers,
                    params={
                        "targeted_audiences": "farmer",
                        "page": page,
                        "page_size": 50
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Erreur page {page}: {response.status_code}")
                    break
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                all_aids.extend(results)
                logger.info(f"      ✅ {len(results)} aides récupérées (total: {len(all_aids)}/{data.get('count', '?')})")
                
                if len(results) < 50:
                    break
                
                page += 1
                
                if page > 15:  # Sécurité (507/50 = ~11 pages)
                    break
            
            # Formater les aides pour export
            logger.info("📝 Formatage des aides pour export...")
            
            exported_aids = []
            
            for aid in all_aids:
                # Nettoyer le HTML
                soup_desc = BeautifulSoup(aid.get("description", ""), 'html.parser')
                soup_elig = BeautifulSoup(aid.get("eligibility", ""), 'html.parser')
                soup_contact = BeautifulSoup(aid.get("contact", ""), 'html.parser')
                
                # Extraire le premier financeur
                financeurs = aid.get("financers", [])
                premier_financeur = financeurs[0] if financeurs else "Non spécifié"
                
                exported_aid = {
                    # ========== IDENTIFIANTS ========== 
                    "aid_id": aid.get("slug"),
                    "source_id": aid.get("id"),
                    "source": "aides-territoires",
                    
                    # ========== INFORMATIONS DE BASE ========== 
                    "titre": aid.get("name", ""),
                    "description": soup_desc.get_text(separator='\n', strip=True),
                    "eligibilite_texte": soup_elig.get_text(separator='\n', strip=True),
                    
                    # ========== ORGANISMES ========== 
                    "financeurs": financeurs,
                    "organisme_principal": premier_financeur,
                    
                    # ========== TYPE ET CATÉGORIE ========== 
                    "type_aide": aid.get("aid_types", []),
                    "categories": aid.get("categories", []),
                    "beneficiaires": aid.get("targeted_audiences", []),
                    "destinations": aid.get("destinations", []),
                    
                    # ========== GÉOGRAPHIE ========== 
                    "zone_geo": aid.get("perimeter", ""),
                    "echelle_geo": aid.get("perimeter_scale", ""),
                    
                    # ========== MONTANTS ========== 
                    "taux_subvention_min": aid.get("subvention_rate_lower_bound"),
                    "taux_subvention_max": aid.get("subvention_rate_upper_bound"),
                    "commentaire_montant": aid.get("subvention_comment", ""),
                    "montant_pret": aid.get("loan_amount"),
                    "avance_recuperable": aid.get("recoverable_advance_amount"),
                    
                    # ========== DATES ========== 
                    "date_ouverture": aid.get("start_date"),
                    "date_cloture": aid.get("submission_deadline"),
                    "date_predeposit": aid.get("predeposit_date"),
                    "recurrence": aid.get("recurrence", ""),
                    "appel_a_projet": aid.get("is_call_for_project", False),
                    
                    # ========== URLS ET CONTACT ========== 
                    "url_origine": aid.get("origin_url", ""),
                    "url_candidature": aid.get("application_url"),
                    "contact": soup_contact.get_text(strip=True),
                    
                    # ========== MÉTADONNÉES ========== 
                    "date_creation": aid.get("date_created"),
                    "date_maj": aid.get("date_updated"),
                    
                    # ========== SECTION À ENRICHIR MANUELLEMENT ========== 
                    "pertinent": None,  # À remplir : true (à importer) / false (exclure) / null (non traité)
                    "priorite": 0,  # À remplir : 0 (non traité), 1 (basse) à 5 (très haute)
                    
                    "criteres_enrichis": {
                        # Critères agriculteur
                        "sau_min": None,
                        "sau_max": None,
                        "age_min": None,
                        "age_max": None,
                        "jeune_agriculteur_requis": False,
                        "installation_titre_principal": False,
                        
                        # Labels et certifications
                        "label_bio_requis": False,
                        "label_bio_ou_conversion": False,
                        "autre_label_requis": None,
                        
                        # Diplômes et formation
                        "diplome_requis": None,  # "BAC_PRO", "BTS", "LICENCE", etc.
                        
                        # Productions
                        "productions_eligibles": [],  # ["cereales", "elevage_bovin", "viticulture", "maraichage", "arboriculture", "toutes"]
                        
                        # Statuts juridiques
                        "statuts_juridiques": [],  # ["individuel", "EARL", "GAEC", "SCEA", "tous"]
                        
                        # Types de projets
                        "types_projets": [],  # ["installation", "modernisation", "diversification", "conversion_bio", "transition_energetique", "agritourisme"]
                        
                        # Montants projet
                        "montant_projet_min": None,
                        "montant_projet_max": None,
                        
                        # Montants aide (si non remplis automatiquement)
                        "montant_aide_min": None,
                        "montant_aide_max": None,
                        
                        # Autres critères
                        "autre_criteres": ""
                    },
                    
                    # Flags de traitement
                    "criteres_enrichis_manuellement": False,
                    "notes": ""  # Notes libres pour enrichissement
                }
                
                exported_aids.append(exported_aid)
            
            # Créer le fichier d'export
            export_data = {
                "metadata": {
                    "export_date": datetime.now(timezone.utc).isoformat(),
                    "export_by": "Laz0ne",
                    "total_aids": len(exported_aids),
                    "source": "aides-territoires",
                    "version": "1.0"
                },
                
                "instructions": {
                    "etape_1_trier": [
                        "Pour chaque aide, définis 'pertinent' :",
                        "  - true : aide pertinente pour les agriculteurs (à importer)",
                        "  - false : aide non pertinente (exclure)",
                        "  - null : non traité encore"
                    ],
                    "etape_2_prioriser": [
                        "Définis 'priorite' pour les aides pertinentes :",
                        "  - 5 : Très importante (DJA, PAC, aides bio, etc.)",
                        "  - 4 : Importante",
                        "  - 3 : Moyenne",
                        "  - 2 : Secondaire",
                        "  - 1 : Faible priorité",
                        "  - 0 : Non traité"
                    ],
                    "etape_3_enrichir": [
                        "Pour les aides priorité 4-5, enrichis 'criteres_enrichis' :",
                        "  - Remplis tous les critères applicables",
                        "  - Laisse null les critères non applicables",
                        "  - Mets 'criteres_enrichis_manuellement' à true quand terminé"
                    ],
                    "valeurs_possibles": {
                        "productions_eligibles": ["cereales", "oleagineux", "proteagineux", "elevage_bovin", "elevage_ovin", "elevage_porcin", "elevage_volaille", "viticulture", "maraichage", "arboriculture", "horticulture", "apiculture", "toutes"],
                        "statuts_juridiques": ["individuel", "EARL", "GAEC", "SCEA", "SCA", "tous"],
                        "types_projets": ["installation", "modernisation", "diversification", "conversion_bio", "transition_energetique", "agritourisme", "circuit_court", "investissement_materiel"],
                        "diplome_requis": ["CAP_AGRICOLE", "BAC_PRO", "BTS", "LICENCE", "INGENIEUR", null]
                    }
                },
                
                "aids": exported_aids
            }
            
            logger.info(f"✅ Export terminé : {len(exported_aids)} aides formatées")
            
            return export_data
        
    except Exception as e:
        logger.error(f"❌ Erreur export: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }