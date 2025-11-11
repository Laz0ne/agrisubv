"""
Script de synchronisation avec l'API Aides-Territoires
Récupère les aides agricoles et les normalise pour MongoDB
"""

import requests
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration API Aides-Territoires
AIDES_TERRITOIRES_API_URL = "https://aides-territoires.beta.gouv.fr/api/aids/"
AIDES_TERRITOIRES_BASE_URL = "https://aides-territoires.beta.gouv.fr"

class AidesTerritoiresSyncer:
    """Classe pour synchroniser les aides depuis Aides-Territoires"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        })
    
    def fetch_aides_agricoles(self, page_size: int = 50) -> List[Dict[str, Any]]:
        """Récupère toutes les aides agricoles depuis l'API"""
        
        all_aides = []
        page = 1
        
        params = {
    'categories': 'agriculture',  # Chercher par catégorie au lieu de audience
    'is_charged': 'false',
    'page_size': page_size,
    'page': page
}
        
        logger.info("🔄 Début de la récupération des aides agricoles...")
        
        while True:
            try:
                response = self.session.get(AIDES_TERRITOIRES_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('results', [])
                if not results:
                    break
                
                all_aides.extend(results)
                logger.info(f"✅ Page {page} : {len(results)} aides récupérées (Total: {len(all_aides)})")
                
                if not data.get('next'):
                    break
                
                page += 1
                params['page'] = page
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la récupération page {page}: {e}")
                break
        
        logger.info(f"✅ Total aides récupérées : {len(all_aides)}")
        return all_aides
    
    def normalize_aide(self, aide_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise une aide Aides-Territoires vers le format AgriSubv"""
        
        aid_id = f"AT-{aide_data.get('id', 'unknown')}"
        titre = aide_data.get('name', 'Aide sans titre')
        
        financers = aide_data.get('financers', [])
        organisme = ', '.join([f.get('name', '') for f in financers]) if financers else 'Non spécifié'
        
        niveau = self._detect_niveau(aide_data)
        regions, departements = self._extract_perimeter(aide_data)
        type_aide = self._extract_type_aide(aide_data)
        montant_min, montant_max, taux_min, taux_max = self._extract_montants(aide_data)
        
        date_limite = aide_data.get('submission_deadline', None)
        date_ouverture = aide_data.get('start_date', None)
        expiree = self._is_expired(date_limite)
        
        criteres_eligibilite = aide_data.get('eligibility', '')
        criteres_durs_expr = self._build_criteres_durs(aide_data, criteres_eligibilite)
        criteres_mous_tags = self._extract_keywords(aide_data)
        
        lien_officiel = aide_data.get('url', '')
        if lien_officiel and not lien_officiel.startswith('http'):
            lien_officiel = f"{AIDES_TERRITOIRES_BASE_URL}{lien_officiel}"
        
        normalized_aide = {
            "aid_id": aid_id,
            "titre": titre,
            "organisme": organisme,
            "programme": aide_data.get('programs', [''])[0] if aide_data.get('programs') else '',
            "source_url": lien_officiel,
            "derniere_maj": datetime.now(timezone.utc).isoformat(),
            "niveau": niveau,
            "regions": regions,
            "departements": departements,
            "type_aide": type_aide,
            "productions": [],
            "statuts": [],
            "labels": [],
            "montant_min_eur": montant_min,
            "montant_max_eur": montant_max,
            "taux_min_pct": taux_min,
            "taux_max_pct": taux_max,
            "plafond_eur": montant_max,
            "date_ouverture": date_ouverture,
            "date_limite": date_limite,
            "criteres_durs_expr": criteres_durs_expr,
            "criteres_mous_tags": criteres_mous_tags,
            "conditions_clefs": criteres_eligibilite[:500] if criteres_eligibilite else '',
            "lien_officiel": lien_officiel,
            "confiance": 0.8,
            "expiree": expiree,
            "source": "aides-territoires",
            "raw_data": aide_data
        }
        
        return normalized_aide
    
    def _detect_niveau(self, aide_data: Dict[str, Any]) -> str:
        perimeter = aide_data.get('perimeter', {})
        if not perimeter:
            return "National"
        
        scale = perimeter.get('scale', '').lower()
        
        if 'europe' in scale or 'european' in scale:
            return "Européen"
        elif 'region' in scale or 'régional' in scale:
            return "Régional"
        elif 'department' in scale or 'département' in scale:
            return "Départemental"
        elif 'commune' in scale or 'local' in scale:
            return "Local"
        else:
            return "National"
    
    def _extract_perimeter(self, aide_data: Dict[str, Any]) -> tuple:
        regions = []
        departements = []
        
        perimeter = aide_data.get('perimeter', {})
        if not perimeter:
            return ["National"], []
        
        perimeter_name = perimeter.get('name', '')
        scale = perimeter.get('scale', '').lower()
        
        if 'region' in scale:
            regions.append(perimeter_name)
        elif 'department' in scale:
            match = re.search(r'\b(\d{2,3})\b', perimeter_name)
            if match:
                departements.append(match.group(1))
        elif 'france' in perimeter_name.lower() or 'national' in scale:
            regions.append("National")
        
        return regions if regions else ["National"], departements
    
    def _extract_type_aide(self, aide_data: Dict[str, Any]) -> str:
        categories = aide_data.get('categories', [])
        
        if any('bio' in cat.lower() or 'conversion' in cat.lower() for cat in categories):
            return "Conversion Bio"
        elif any('installation' in cat.lower() or 'jeune' in cat.lower() for cat in categories):
            return "Installation"
        elif any('investissement' in cat.lower() or 'équipement' in cat.lower() for cat in categories):
            return "Investissement"
        elif any('innovation' in cat.lower() or 'numérique' in cat.lower() for cat in categories):
            return "Innovation"
        elif any('environnement' in cat.lower() or 'transition' in cat.lower() for cat in categories):
            return "Transition écologique"
        else:
            return "Autre"
    
    def _extract_montants(self, aide_data: Dict[str, Any]) -> tuple:
        montant_str = aide_data.get('subvention_rate', '') or aide_data.get('aid_amount', '')
        
        montant_min = None
        montant_max = None
        taux_min = None
        taux_max = None
        
        if not montant_str:
            return None, None, None, None
        
        montants_euros = re.findall(r'(\d+[\s\u202f]?\d*)\s*€', montant_str)
        if montants_euros:
            montants = [int(m.replace(' ', '').replace('\u202f', '')) for m in montants_euros]
            if len(montants) == 1:
                montant_max = montants[0]
            elif len(montants) >= 2:
                montant_min = min(montants)
                montant_max = max(montants)
        
        taux = re.findall(r'(\d+)\s*%', montant_str)
        if taux:
            taux_values = [int(t) for t in taux]
            if len(taux_values) == 1:
                taux_max = taux_values[0]
            elif len(taux_values) >= 2:
                taux_min = min(taux_values)
                taux_max = max(taux_values)
        
        return montant_min, montant_max, taux_min, taux_max
    
    def _build_criteres_durs(self, aide_data: Dict[str, Any], eligibility_text: str) -> Dict[str, Any]:
        return {}
    
    def _extract_keywords(self, aide_data: Dict[str, Any]) -> List[str]:
        keywords = []
        
        categories = aide_data.get('categories', [])
        keywords.extend([cat.lower() for cat in categories])
        
        titre = aide_data.get('name', '').lower()
        important_words = ['bio', 'installation', 'jeune', 'irrigation', 'énergie', 
                          'robot', 'numérique', 'environnement', 'transition']
        for word in important_words:
            if word in titre:
                keywords.append(word)
        
        return list(set(keywords))
    
    def _is_expired(self, date_limite: Optional[str]) -> bool:
        if not date_limite:
            return False
        
        try:
            deadline = datetime.fromisoformat(date_limite.replace('Z', '+00:00'))
            return deadline < datetime.now(timezone.utc)
        except:
            return False


async def sync_aides_to_db(db, limit: Optional[int] = None) -> Dict[str, Any]:
    """Synchronise les aides depuis Aides-Territoires vers MongoDB"""
    
    syncer = AidesTerritoiresSyncer()
    
    logger.info("🔄 Récupération des aides depuis Aides-Territoires...")
    aides_brutes = syncer.fetch_aides_agricoles()
    
    if limit:
        aides_brutes = aides_brutes[:limit]
    
    logger.info(f"🔄 Normalisation de {len(aides_brutes)} aides...")
    aides_normalized = []
    for aide_brute in aides_brutes:
        try:
            aide_norm = syncer.normalize_aide(aide_brute)
            aides_normalized.append(aide_norm)
        except Exception as e:
            logger.error(f"❌ Erreur normalisation aide {aide_brute.get('id')}: {e}")
    
    logger.info(f"💾 Insertion de {len(aides_normalized)} aides dans MongoDB...")
    
    inserted_count = 0
    updated_count = 0
    errors_count = 0
    
    for aide in aides_normalized:
        try:
            existing = await db.aides.find_one({"aid_id": aide['aid_id']})
            
            if existing:
                await db.aides.update_one(
                    {"aid_id": aide['aid_id']},
                    {"$set": aide}
                )
                updated_count += 1
            else:
                await db.aides.insert_one(aide)
                inserted_count += 1
        except Exception as e:
            logger.error(f"❌ Erreur insertion aide {aide['aid_id']}: {e}")
            errors_count += 1
    
    logger.info(f"✅ Synchronisation terminée !")
    logger.info(f"   - Nouvelles aides : {inserted_count}")
    logger.info(f"   - Aides mises à jour : {updated_count}")
    logger.info(f"   - Erreurs : {errors_count}")
    
    return {
        "success": True,
        "total_fetched": len(aides_brutes),
        "total_normalized": len(aides_normalized),
        "inserted": inserted_count,
        "updated": updated_count,
        "errors": errors_count
    }


if __name__ == "__main__":
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'agrisubv_db')]
    
    result = asyncio.run(sync_aides_to_db(db, limit=100))
    print(f"\n📊 Résultat : {result}")
