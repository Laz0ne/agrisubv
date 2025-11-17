"""
Endpoint pour analyser les critères d'éligibilité des 507 aides agricoles
Extrait automatiquement tous les critères mentionnés pour créer le questionnaire optimal
"""

import httpx
import re
from collections import defaultdict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def analyze_criteria_handler():
    """
    Analyse les 507 aides agricoles pour extraire tous les critères d'éligibilité
    Retourne une structure complète des critères détectés
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
            
            # Récupération de TOUTES les aides agricoles
            logger.info("📥 Récupération des 507 aides agricoles...")
            all_aids = []
            page = 1
            
            while True:
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
                    break
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                all_aids.extend(results)
                logger.info(f"   ✅ Page {page}: {len(all_aids)} aides récupérées")
                
                if len(results) < 50:
                    break
                
                page += 1
                
                if page > 15:
                    break
            
            logger.info(f"📊 Analyse de {len(all_aids)} aides...")
            
            # Structures pour l'analyse
            analysis = {
                "total_aids": len(all_aids),
                "analysis_date": datetime.now(timezone.utc).isoformat(),
                
                # Compteurs de fréquence
                "criteria_frequency": defaultdict(int),
                
                # Exemples de critères détectés
                "criteria_examples": defaultdict(list),
                
                # Valeurs uniques détectées
                "unique_values": {
                    "productions": set(),
                    "statuts_juridiques": set(),
                    "labels": set(),
                    "types_projets": set(),
                    "regions": set()
                },
                
                # Patterns de montants
                "montant_patterns": {
                    "with_taux": 0,
                    "with_montant_fixe": 0,
                    "with_plafond": 0
                }
            }
            
            # Patterns de détection
            patterns = {
                "sau": r"(?:sau|surface|hectare|ha)\s*(?:minimum|mini|min|>|≥|supérieur|de)\s*(\d+)",
                "age": r"(?:âge|age)\s*(?:maximum|maxi|max|<|≤|inférieur|moins de)\s*(\d+)",
                "age_ja": r"(?:jeune agriculteur|ja|moins de 40 ans|âge.*40)",
                "bio": r"(?:agriculture biologique|bio|ab|conversion bio|label bio)",
                "diplome": r"(?:diplôme|bac pro|bts|capacité professionnelle|niveau)",
                "installation": r"(?:installation|installé|première installation|titre principal)",
                "statut": r"(?:earl|gaec|scea|individuel|société|exploitation)",
                "montant_ha": r"(\d+)\s*€\s*(?:/|par)\s*(?:ha|hectare)",
                "taux_percent": r"(\d+)\s*%",
                "plafond": r"plafond\s*(?:de)?\s*(\d+(?:\s?\d+)*)\s*€"
            }
            
            # Productions types à détecter
            productions_keywords = {
                "cereales": ["céréale", "blé", "orge", "maïs", "colza"],
                "elevage_bovin": ["bovin", "vache", "taureau", "veau"],
                "elevage_ovin": ["ovin", "mouton", "brebis", "agneau"],
                "elevage_porcin": ["porcin", "porc", "cochon"],
                "elevage_volaille": ["volaille", "poulet", "poule"],
                "viticulture": ["viticult", "vin", "vigne", "raisin"],
                "maraichage": ["maraîch", "légume", "légumier"],
                "arboriculture": ["arboricult", "fruitier", "verger"],
                "apiculture": ["apicult", "abeille", "miel"],
                "horticulture": ["horticult", "fleur", "plante"]
            }
            
            # Analyse de chaque aide
            for aid in all_aids:
                eligibility_text = (aid.get("eligibility") or "").lower()
                description_text = (aid.get("description") or "").lower()
                full_text = eligibility_text + " " + description_text
                
                # Détection SAU
                if re.search(patterns["sau"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["sau_mentioned"] += 1
                    matches = re.findall(patterns["sau"], full_text, re.IGNORECASE)
                    if matches and len(analysis["criteria_examples"]["sau"]) < 5:
                        analysis["criteria_examples"]["sau"].append(f"{aid.get('name')}: {matches[0]} ha minimum")
                
                # Détection âge / Jeune Agriculteur
                if re.search(patterns["age"], full_text, re.IGNORECASE) or re.search(patterns["age_ja"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["age_mentioned"] += 1
                    if len(analysis["criteria_examples"]["age"]) < 5:
                        analysis["criteria_examples"]["age"].append(aid.get('name'))
                
                # Détection Bio
                if re.search(patterns["bio"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["bio_mentioned"] += 1
                    if len(analysis["criteria_examples"]["bio"]) < 5:
                        analysis["criteria_examples"]["bio"].append(aid.get('name'))
                
                # Détection diplôme
                if re.search(patterns["diplome"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["diplome_mentioned"] += 1
                    if len(analysis["criteria_examples"]["diplome"]) < 5:
                        analysis["criteria_examples"]["diplome"].append(aid.get('name'))
                
                # Détection installation
                if re.search(patterns["installation"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["installation_mentioned"] += 1
                    if len(analysis["criteria_examples"]["installation"]) < 5:
                        analysis["criteria_examples"]["installation"].append(aid.get('name'))
                
                # Détection statut juridique
                if re.search(patterns["statut"], full_text, re.IGNORECASE):
                    analysis["criteria_frequency"]["statut_juridique_mentioned"] += 1
                
                # Détection productions
                for prod_key, keywords in productions_keywords.items():
                    for keyword in keywords:
                        if keyword in full_text:
                            analysis["unique_values"]["productions"].add(prod_key)
                            break
                
                # Détection montants
                if re.search(patterns["taux_percent"], full_text):
                    analysis["montant_patterns"]["with_taux"] += 1
                
                if re.search(patterns["montant_ha"], full_text):
                    analysis["montant_patterns"]["with_montant_fixe"] += 1
                
                if re.search(patterns["plafond"], full_text):
                    analysis["montant_patterns"]["with_plafond"] += 1
                
                # Régions
                perimeter = aid.get("perimeter", "")
                if perimeter:
                    analysis["unique_values"]["regions"].add(perimeter)
                
                # Catégories
                categories = aid.get("categories", [])
                for cat in categories:
                    if "agriculture" in cat.lower():
                        analysis["criteria_frequency"]["agriculture_category"] += 1
            
            # Convertir les sets en listes
            analysis["unique_values"]["productions"] = sorted(list(analysis["unique_values"]["productions"]))
            analysis["unique_values"]["regions"] = sorted(list(analysis["unique_values"]["regions"]))[:20]  # Top 20
            
            # Ajouter les valeurs communes de statuts juridiques
            analysis["unique_values"]["statuts_juridiques"] = [
                "individuel", "EARL", "GAEC", "SCEA", "SA", "CUMA", "Coopérative"
            ]
            
            # Ajouter les labels communs
            analysis["unique_values"]["labels"] = [
                "Agriculture Biologique (AB)", "HVE (Haute Valeur Environnementale)",
                "Label Rouge", "AOC/AOP", "IGP"
            ]
            
            # Ajouter les types de projets communs
            analysis["unique_values"]["types_projets"] = [
                "installation", "modernisation", "diversification", "conversion_bio",
                "transition_energetique", "agritourisme", "circuit_court",
                "investissement_materiel", "batiment", "irrigation", "bien_etre_animal"
            ]
            
            # Convertir defaultdict en dict normal
            analysis["criteria_frequency"] = dict(analysis["criteria_frequency"])
            analysis["criteria_examples"] = dict(analysis["criteria_examples"])
            
            # Calculer les pourcentages
            total = analysis["total_aids"]
            analysis["criteria_percentage"] = {
                key: round((value / total) * 100, 1)
                for key, value in analysis["criteria_frequency"].items()
            }
            
            logger.info(f"✅ Analyse terminée : {len(analysis['criteria_frequency'])} types de critères détectés")
            
            return {
                "status": "success",
                "analysis": analysis,
                "recommendations": {
                    "questions_essentielles": [
                        "Region/Département",
                        "SAU totale",
                        "Statut juridique",
                        "Productions principales",
                        "Types de projets"
                    ],
                    "questions_frequentes": [
                        "Âge (pour JA)" if analysis["criteria_frequency"].get("age_mentioned", 0) > 50 else None,
                        "Label Bio" if analysis["criteria_frequency"].get("bio_mentioned", 0) > 50 else None,
                        "Diplôme agricole" if analysis["criteria_frequency"].get("diplome_mentioned", 0) > 30 else None,
                        "Installation récente" if analysis["criteria_frequency"].get("installation_mentioned", 0) > 40 else None
                    ],
                    "questions_conditionnelles": [
                        "SAU bio (si label bio)",
                        "Date d'installation (si JA)",
                        "Type d'élevage (si production élevage)"
                    ]
                }
            }
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
