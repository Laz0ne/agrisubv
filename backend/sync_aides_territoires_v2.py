"""
Script de synchronisation optimisé Aides-Territoires V2
Récupération paginée avec rate limiting et normalisation vers modèle V2
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import re
import os
from dotenv import load_dotenv

from models_v2 import (
    AideAgricoleV2, CriteresEligibilite, MontantAide,
    TypeProduction, TypeProjet, StatutJuridique, TypeMontant
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Token (X-AUTH-TOKEN)
API_TOKEN = os.environ.get('AIDES_TERRITOIRES_API_TOKEN', '')

# Configuration API
AIDES_TERRITOIRES_API_URL = "https://aides-territoires.beta.gouv.fr/api/aids/"
AIDES_TERRITOIRES_BASE_URL = "https://aides-territoires.beta.gouv.fr"

# Authentication URL
CONNEXION_URL = "https://aides-territoires.beta.gouv.fr/api/connexion/"


class AidesTerritoiresSync:
    """Classe pour la synchronisation asynchrone avec Aides-Territoires"""
    
    # Rate limiting
    REQUESTS_PER_SECOND = 2
    BATCH_SIZE = 50
    
    # Mapping catégories -> TypeProjet
    CATEGORIE_TO_PROJET = {
        "installation": TypeProjet.INSTALLATION,
        "conversion": TypeProjet.CONVERSION_BIO,
        "bio": TypeProjet.CONVERSION_BIO,
        "modernisation": TypeProjet.MODERNISATION,
        "investissement": TypeProjet.MODERNISATION,
        "diversification": TypeProjet.DIVERSIFICATION,
        "irrigation": TypeProjet.IRRIGATION,
        "eau": TypeProjet.IRRIGATION,
        "bâtiment": TypeProjet.BATIMENT,
        "construction": TypeProjet.BATIMENT,
        "équipement": TypeProjet.MATERIEL,
        "matériel": TypeProjet.MATERIEL,
        "énergie": TypeProjet.ENERGIE,
        "méthanisation": TypeProjet.ENERGIE,
        "environnement": TypeProjet.ENVIRONNEMENT,
        "biodiversité": TypeProjet.ENVIRONNEMENT,
        "formation": TypeProjet.FORMATION,
        "conseil": TypeProjet.FORMATION,
        "commercialisation": TypeProjet.COMMERCIALISATION,
        "circuit court": TypeProjet.COMMERCIALISATION,
        "numérique": TypeProjet.NUMERIQUE,
        "digital": TypeProjet.NUMERIQUE,
        "animal": TypeProjet.BIEN_ETRE_ANIMAL,
        "bien-être": TypeProjet.BIEN_ETRE_ANIMAL,
    }
    
    # Mots-clés pour détecter les productions
    PRODUCTION_KEYWORDS = {
        TypeProduction.CEREALES: ["céréale", "blé", "orge", "maïs"],
        TypeProduction.MARAICHAGE: ["maraîchage", "légume", "potager"],
        TypeProduction.VITICULTURE: ["vigne", "viticul", "vin"],
        TypeProduction.ARBORICULTURE: ["arbre", "verger", "fruit"],
        TypeProduction.ELEVAGE_BOVIN: ["bovin", "vache", "bœuf"],
        TypeProduction.ELEVAGE_OVIN: ["ovin", "mouton", "brebis"],
        TypeProduction.ELEVAGE_CAPRIN: ["caprin", "chèvre"],
        TypeProduction.ELEVAGE_PORCIN: ["porcin", "porc"],
        TypeProduction.ELEVAGE_AVICOLE: ["avicole", "volaille", "poulet"],
        TypeProduction.ELEVAGE_LAITIER: ["lait", "laitier", "laitage"],
        TypeProduction.GRANDES_CULTURES: ["grande culture", "polyculture"],
        TypeProduction.HORTICULTURE: ["horticulture", "serre"],
        TypeProduction.APICULTURE: ["apiculture", "abeille", "miel"],
        TypeProduction.AQUACULTURE: ["aquaculture", "pisciculture", "poisson"],
    }
    
    def __init__(self, db):
        """
        Initialise le synchroniseur
        
        Args:
            db: Instance de la base de données MongoDB
        """
        self.db = db
        self.session = None
        self.last_request_time = 0
    
    async def get_bearer_token(self) -> Optional[str]:
        """
        Obtient un Bearer Token en utilisant le X-AUTH-TOKEN
        
        Returns:
            Bearer Token (valable 24h) ou None en cas d'erreur
        """
        if not API_TOKEN:
            logger.error("❌ AIDES_TERRITOIRES_API_TOKEN non configuré")
            return None
        
        headers = {
            'User-Agent': 'AgriSubv/2.0 (https://agrisubv.onrender.com)',
            'X-AUTH-TOKEN': API_TOKEN,
        }
        
        try:
            logger.info("🔐 Authentification auprès d'Aides-Territoires...")
            async with aiohttp.ClientSession() as session:
                async with session.post(CONNEXION_URL, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        bearer_token = data.get('token')
                        if bearer_token:
                            logger.info("✅ Bearer Token obtenu avec succès")
                            return bearer_token
                        else:
                            logger.error("❌ Token non trouvé dans la réponse")
                            return None
                    else:
                        logger.error(f"❌ Erreur authentification: HTTP {response.status}")
                        error_text = await response.text()
                        logger.error(f"   Détails: {error_text[:200]}")
                        return None
        except Exception as e:
            logger.error(f"❌ Exception lors de l'authentification: {e}")
            return None
    
    async def _rate_limit(self):
        """Applique le rate limiting"""
        elapsed = time.time() - self.last_request_time
        wait_time = 1.0 / self.REQUESTS_PER_SECOND
        if elapsed < wait_time:
            await asyncio.sleep(wait_time - elapsed)
        self.last_request_time = time.time()
    
    async def fetch_aides_paginated(
        self, 
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les aides de manière paginée avec authentification Bearer
        
        Args:
            max_pages: Nombre maximum de pages à récupérer (None = toutes)
            
        Returns:
            Liste des aides brutes
        """
        # Obtenir le Bearer Token
        bearer_token = await self.get_bearer_token()
        if not bearer_token:
            logger.error("❌ Impossible de continuer sans Bearer Token")
            return []
        
        all_aides = []
        page = 1
        
        headers = {
            'User-Agent': 'AgriSubv/2.0 (https://agrisubv.onrender.com)',
            'Accept': 'application/json',
            'Authorization': f'Bearer {bearer_token}',
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            self.session = session
            
            while True:
                if max_pages and page > max_pages:
                    break
                
                # Rate limiting
                await self._rate_limit()
                
                params = {
                    'categories': 'agriculture',
                    'is_charged': 'false',
                    'page_size': self.BATCH_SIZE,
                    'page': page
                }
                
                try:
                    logger.info(f"🔄 Récupération page {page}...")
                    async with session.get(AIDES_TERRITOIRES_API_URL, params=params) as response:
                        if response.status == 401:
                            logger.error(f"❌ Token expiré ou invalide (401)")
                            # Réessayer avec un nouveau token
                            bearer_token = await self.get_bearer_token()
                            if not bearer_token:
                                break
                            headers['Authorization'] = f'Bearer {bearer_token}'
                            continue
                        
                        if response.status != 200:
                            logger.error(f"❌ Erreur HTTP {response.status} page {page}")
                            error_text = await response.text()
                            logger.error(f"   Détails: {error_text[:200]}")
                            break
                        
                        data = await response.json()
                        results = data.get('results', [])
                        
                        if not results:
                            logger.info(f"✅ Fin de pagination (page {page})")
                            break
                        
                        all_aides.extend(results)
                        logger.info(f"   ✅ {len(results)} aides récupérées (Total: {len(all_aides)})")
                        
                        if not data.get('next'):
                            break
                        
                        page += 1
                        
                except asyncio.TimeoutError:
                    logger.error(f"❌ Timeout page {page}")
                    break
                except Exception as e:
                    logger.error(f"❌ Erreur page {page}: {e}")
                    break
        
        logger.info(f"✅ Total récupéré: {len(all_aides)} aides")
        return all_aides
    
    def detect_productions(self, aide_data: Dict[str, Any]) -> List[TypeProduction]:
        """
        Détecte les types de production depuis les mots-clés
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Liste des types de production détectés
        """
        productions = []
        
        # Texte à analyser (gestion robuste des None et non-strings)
        name = aide_data.get('name')
        titre = str(name).lower() if name is not None else ''
        
        desc = aide_data.get('description')
        description = str(desc).lower() if desc is not None else ''
        
        categories = ' '.join(aide_data.get('categories', [])).lower()
        
        all_text = f"{titre} {description} {categories}"
        
        # Détection par mots-clés
        for type_prod, keywords in self.PRODUCTION_KEYWORDS.items():
            if any(kw in all_text for kw in keywords):
                if type_prod not in productions:
                    productions.append(type_prod)
        
        return productions
    
    def detect_projets(self, aide_data: Dict[str, Any]) -> List[TypeProjet]:
        """
        Détecte les types de projets depuis les catégories et le texte
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Liste des types de projet détectés
        """
        projets = []
        
        # Texte à analyser (gestion robuste des None et non-strings)
        name = aide_data.get('name')
        titre = str(name).lower() if name is not None else ''
        
        categories = aide_data.get('categories', [])
        aid_types = aide_data.get('aid_types', [])
        
        all_text = f"{titre} {' '.join(categories)} {' '.join(aid_types)}".lower()
        
        # Détection par mapping
        for keyword, type_projet in self.CATEGORIE_TO_PROJET.items():
            if keyword in all_text:
                if type_projet not in projets:
                    projets.append(type_projet)
        
        return projets
    
    def extract_perimeter(self, aide_data: Dict[str, Any]) -> tuple:
        """
        Extrait les informations géographiques
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Tuple (régions, départements)
        """
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
            # Extraire le numéro de département
            match = re.search(r'\b(\d{2,3})\b', perimeter_name)
            if match:
                departements.append(match.group(1))
        elif 'france' in perimeter_name.lower() or 'national' in scale:
            regions.append("National")
        
        return regions if regions else ["National"], departements
    
    def extract_montants(self, aide_data: Dict[str, Any]) -> tuple:
        """
        Extrait les informations de montant
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Tuple (type_montant, montant_min, montant_max, taux_min, taux_max)
        """
        montant_raw = aide_data.get('subvention_rate') or aide_data.get('aid_amount') or ''
        montant_str = str(montant_raw) if montant_raw else ''
        
        type_montant = TypeMontant.FORFAITAIRE
        montant_min = None
        montant_max = None
        taux_min = None
        taux_max = None
        
        if not montant_str:
            return type_montant, None, None, None, None
        
        # Recherche de montants en euros
        montants_euros = re.findall(r'(\d+[\s\u202f]?\d*)\s*€', montant_str)
        if montants_euros:
            montants = [int(m.replace(' ', '').replace('\u202f', '')) for m in montants_euros]
            if len(montants) == 1:
                montant_max = montants[0]
            elif len(montants) >= 2:
                montant_min = min(montants)
                montant_max = max(montants)
        
        # Recherche de taux en pourcentage
        taux = re.findall(r'(\d+)\s*%', montant_str)
        if taux:
            type_montant = TypeMontant.POURCENTAGE
            taux_values = [int(t) for t in taux]
            if len(taux_values) == 1:
                taux_max = taux_values[0]
            elif len(taux_values) >= 2:
                taux_min = min(taux_values)
                taux_max = max(taux_values)
        
        # Détection du type selon le texte
        if '/ha' in montant_str.lower() or 'hectare' in montant_str.lower():
            type_montant = TypeMontant.SURFACE
        elif '/tête' in montant_str.lower() or 'animal' in montant_str.lower():
            type_montant = TypeMontant.TETE
        
        return type_montant, montant_min, montant_max, taux_min, taux_max
    
    def extract_eligibility_criteria(self, aide_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les critères d'éligibilité depuis la description
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Dictionnaire avec les critères extraits
        """
        eligibility = aide_data.get('eligibility')
        eligibility_text = str(eligibility).lower() if eligibility is not None else ''
        
        criteria = {
            'jeune_agriculteur': None,
            'labels_requis': []
        }
        
        # Détection jeune agriculteur
        if 'jeune agriculteur' in eligibility_text or '40 ans' in eligibility_text:
            criteria['jeune_agriculteur'] = True
        
        # Détection labels
        if 'bio' in eligibility_text or 'agriculture biologique' in eligibility_text:
            criteria['labels_requis'].append('Agriculture Biologique')
        if 'hve' in eligibility_text or 'haute valeur environnementale' in eligibility_text:
            criteria['labels_requis'].append('HVE')
        
        return criteria
    
    def normalize_aide(self, aide_data: Dict[str, Any]) -> AideAgricoleV2:
        """
        Normalise une aide brute vers le modèle V2
        
        Args:
            aide_data: Données brutes de l'aide
            
        Returns:
            Instance d'AideAgricoleV2
        """
        # ID
        id_externe = str(aide_data.get('id', ''))
        aid_id = f"AT-{id_externe}"
        
        # Informations de base
        titre = aide_data.get('name') or 'Aide sans titre'
        if not isinstance(titre, str):
            titre = str(titre)
            
        description = aide_data.get('description') or ''
        if not isinstance(description, str):
            description = str(description)

        # Organisme (gestion robuste)
        financers = aide_data.get('financers', [])
        if financers and isinstance(financers, list):
            organisme_parts = []
            for f in financers:
                if isinstance(f, dict):
                    name = f.get('name', '')
                    if name:
                        organisme_parts.append(name)
                elif isinstance(f, str):
                    organisme_parts.append(f)
            organisme = ', '.join(organisme_parts) if organisme_parts else 'Non spécifié'
        else:
            organisme = 'Non spécifié'
        
        # Programme (gestion robuste)
        programmes = aide_data.get('programs', [])
        if programmes and isinstance(programmes, list):
            # Peut être une liste de strings ou de dicts
            if programmes and isinstance(programmes[0], dict):
                programme = programmes[0].get('name', '') or programmes[0].get('slug', '')
            elif programmes and isinstance(programmes[0], str):
                programme = programmes[0]
            else:
                programme = ''
        else:
            programme = ''
        
        # URL
        url = aide_data.get('url', '')
        if url and not url.startswith('http'):
            url = f"{AIDES_TERRITOIRES_BASE_URL}{url}"
        
        # Dates
        date_debut = aide_data.get('start_date')
        date_fin = aide_data.get('recurrence', {}).get('end_date') if aide_data.get('recurrence') else None
        date_limite = aide_data.get('submission_deadline')
        
        # Statut
        statut = 'active'
        if date_limite:
            try:
                deadline = datetime.fromisoformat(date_limite.replace('Z', '+00:00'))
                if deadline < datetime.now(timezone.utc):
                    statut = 'expiree'
            except:
                pass
        
        # Détections intelligentes
        productions = self.detect_productions(aide_data)
        projets = self.detect_projets(aide_data)
        regions, departements = self.extract_perimeter(aide_data)
        
        # Critères extraits
        extra_criteria = self.extract_eligibility_criteria(aide_data)
        
        # Construction des critères
        criteres = CriteresEligibilite(
            regions=regions,
            departements=departements,
            types_production=productions,
            types_projets=projets,
            jeune_agriculteur=extra_criteria['jeune_agriculteur'],
            labels_requis=extra_criteria['labels_requis']
        )
        
        # Montant
        type_montant, montant_min, montant_max, taux_min, taux_max = self.extract_montants(aide_data)
        montant = MontantAide(
            type_montant=type_montant,
            montant_min=montant_min,
            montant_max=montant_max,
            taux_min=taux_min,
            taux_max=taux_max,
            plafond=montant_max
        )
        
        # Tags
        tags = aide_data.get('categories', []) + aide_data.get('aid_types', [])
        
        # Construction de l'aide V2
        aide_v2 = AideAgricoleV2(
            aid_id=aid_id,
            id_externe=id_externe,
            titre=titre,
            description=description,
            organisme=organisme,
            programme=programme,
            source='aides_territoires',
            source_url=url,
            date_debut=date_debut,
            date_fin=date_fin,
            date_limite_depot=date_limite,
            statut=statut,
            criteres=criteres,
            montant=montant,
            conditions_eligibilite=aide_data.get('eligibility', ''),
            demarche=aide_data.get('application_url', ''),
            lien_officiel=url,
            confiance=0.8,
            tags=tags,
            raw_data=aide_data
        )
        
        return aide_v2
    
    async def import_batch(self, aides_v2: List[AideAgricoleV2]) -> Dict[str, int]:
        """
        Importe un batch d'aides avec upsert
        
        Args:
            aides_v2: Liste des aides à importer
            
        Returns:
            Dictionnaire avec les compteurs
        """
        inserted = 0
        updated = 0
        errors = 0
        
        for aide in aides_v2:
            try:
                aide_dict = aide.model_dump()
                
                # Upsert (insert ou update)
                result = await self.db.aides_v2.update_one(
                    {'aid_id': aide.aid_id},
                    {'$set': aide_dict},
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted += 1
                elif result.modified_count > 0:
                    updated += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur import {aide.aid_id}: {e}")
                errors += 1
        
        return {'inserted': inserted, 'updated': updated, 'errors': errors}
    
    async def sync(self, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """
        Synchronisation complète
        
        Args:
            max_pages: Nombre maximum de pages à récupérer
            
        Returns:
            Dictionnaire avec les statistiques
        """
        logger.info("=" * 60)
        logger.info("SYNCHRONISATION AIDES-TERRITOIRES V2")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 1. Récupération paginée
        logger.info("\n📥 Phase 1: Récupération des aides...")
        aides_brutes = await self.fetch_aides_paginated(max_pages)
        
        if not aides_brutes:
            logger.warning("⚠️  Aucune aide récupérée")
            return {'success': False, 'message': 'Aucune aide récupérée'}
        
        # 2. Normalisation
        logger.info(f"\n🔄 Phase 2: Normalisation de {len(aides_brutes)} aides...")
        aides_v2 = []
        erreurs_normalisation = 0
        
        for i, aide_brute in enumerate(aides_brutes, 1):
            try:
                aide_v2 = self.normalize_aide(aide_brute)
                aides_v2.append(aide_v2)
                if i % 50 == 0:
                    logger.info(f"   ✅ {i}/{len(aides_brutes)} normalisées")
            except Exception as e:
                # Logs détaillés pour les 5 premières erreurs
                if erreurs_normalisation < 5:
                    import traceback
                    logger.error(f"\n❌ ERREUR DÉTAILLÉE #{erreurs_normalisation + 1}:")
                    logger.error(f"   Aide ID: {aide_brute.get('id')}")
                    logger.error(f"   Aide Name: {aide_brute.get('name', 'N/A')}")
                    logger.error(f"   Type erreur: {type(e).__name__}")
                    logger.error(f"   Message: {e}")
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                elif erreurs_normalisation == 5:
                    logger.error(f"   ... (logs détaillés désactivés après 5 erreurs)")
                
                erreurs_normalisation += 1
        
        logger.info(f"   ✅ {len(aides_v2)} aides normalisées")
        
        # 3. Import par batch
        logger.info(f"\n💾 Phase 3: Import par batch (taille: {self.BATCH_SIZE})...")
        total_inserted = 0
        total_updated = 0
        total_errors = 0
        
        for i in range(0, len(aides_v2), self.BATCH_SIZE):
            batch = aides_v2[i:i + self.BATCH_SIZE]
            logger.info(f"   🔄 Batch {i//self.BATCH_SIZE + 1}: {len(batch)} aides...")
            
            stats = await self.import_batch(batch)
            total_inserted += stats['inserted']
            total_updated += stats['updated']
            total_errors += stats['errors']
            
            logger.info(f"      ✅ Insérées: {stats['inserted']}, Mises à jour: {stats['updated']}, Erreurs: {stats['errors']}")
        
        # 4. Statistiques finales
        elapsed = time.time() - start_time
        
        logger.info(f"\n" + "=" * 60)
        logger.info(f"SYNCHRONISATION TERMINÉE")
        logger.info(f"=" * 60)
        logger.info(f"⏱️  Durée: {elapsed:.1f}s")
        logger.info(f"📥 Aides récupérées: {len(aides_brutes)}")
        logger.info(f"✅ Aides normalisées: {len(aides_v2)}")
        logger.info(f"➕ Nouvelles aides: {total_inserted}")
        logger.info(f"🔄 Mises à jour: {total_updated}")
        logger.info(f"❌ Erreurs: {erreurs_normalisation + total_errors}")
        logger.info(f"=" * 60)
        
        return {
            'success': True,
            'total_fetched': len(aides_brutes),
            'total_normalized': len(aides_v2),
            'inserted': total_inserted,
            'updated': total_updated,
            'errors': erreurs_normalisation + total_errors,
            'duration_seconds': elapsed
        }


async def sync_aides_territoires_v2(db, max_pages: Optional[int] = None) -> Dict[str, Any]:
    """
    Fonction helper pour la synchronisation
    
    Args:
        db: Instance MongoDB
        max_pages: Nombre maximum de pages
        
    Returns:
        Résultat de la synchronisation
    """
    syncer = AidesTerritoiresSync(db)
    return await syncer.sync(max_pages)


async def debug_first_aide(db) -> Dict[str, Any]:
    """
    Récupère et analyse la première aide pour debug
    
    Returns:
        Informations détaillées sur la première aide
    """
    syncer = AidesTerritoiresSync(db)
    
    # Récupérer seulement la première page (50 aides max)
    logger.info("🔍 Mode DEBUG: Récupération de la première page...")
    aides_brutes = await syncer.fetch_aides_paginated(max_pages=1)
    
    if not aides_brutes:
        return {
            'success': False,
            'message': 'Aucune aide récupérée'
        }
    
    # Analyser la première aide
    premiere_aide = aides_brutes[0]
    
    logger.info(f"\n📋 STRUCTURE DE LA PREMIÈRE AIDE:")
    logger.info(f"   Clés présentes: {list(premiere_aide.keys())}")
    logger.info(f"   ID: {premiere_aide.get('id')}")
    logger.info(f"   Name: {premiere_aide.get('name')}")
    logger.info(f"   Financers type: {type(premiere_aide.get('financers'))}")
    logger.info(f"   Financers: {premiere_aide.get('financers')}")
    logger.info(f"   Programs type: {type(premiere_aide.get('programs'))}")
    logger.info(f"   Programs: {premiere_aide.get('programs')}")
    logger.info(f"   Perimeter type: {type(premiere_aide.get('perimeter'))}")
    logger.info(f"   Perimeter: {premiere_aide.get('perimeter')}")
    
    # Tenter la normalisation avec logs détaillés
    logger.info(f"\n🔄 TENTATIVE DE NORMALISATION...")
    try:
        aide_v2 = syncer.normalize_aide(premiere_aide)
        logger.info(f"   ✅ SUCCÈS: {aide_v2.titre}")
        return {
            'success': True,
            'aide_brute': premiere_aide,
            'aide_normalisee': aide_v2.model_dump(),
            'message': 'Normalisation réussie'
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"   ❌ ÉCHEC: {e}")
        logger.error(f"   Traceback complet:\n{error_trace}")
        
        return {
            'success': False,
            'aide_brute': premiere_aide,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': error_trace,
            'message': f'Erreur de normalisation: {e}'
        }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from motor.motor_asyncio import AsyncIOMotorClient
    from pathlib import Path
    
    ROOT_DIR = Path(__file__).parent
    load_dotenv(ROOT_DIR / '.env')
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'agrisubv_db')]
    
    # Synchronisation (limité à 5 pages pour test)
    result = asyncio.run(sync_aides_territoires_v2(db, max_pages=5))
    
    print(f"\n📊 Résultat final: {result}")
    
    client.close()
