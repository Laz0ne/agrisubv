from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

# Imports pour matching V2
from matching_engine import MatchingEngine
from models_v2 import ProfilAgriculteur as ProfilAgriculteurV2, ResultatMatching, AideAgricoleV2

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'agrisubv_db')]

# Create the main app
app = FastAPI(title="AgriSubv API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# ============ MODELS ============ 

class AideAgricole(BaseModel):
    aid_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titre: str
    organisme: str
    programme: str
    source_url: str
    derniere_maj: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    regions: List[str] = Field(default_factory=list)
    departements: List[str] = Field(default_factory=list)
    productions: List[str] = Field(default_factory=list)
    statuts: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    montant_min_eur: Optional[float] = None
    montant_max_eur: Optional[float] = None
    taux_min_pct: Optional[float] = None
    taux_max_pct: Optional[float] = None
    plafond_eur: Optional[float] = None
    date_ouverture: Optional[str] = None
    date_limite: Optional[str] = None
    criteres_durs_expr: Dict[str, Any] = Field(default_factory=dict)
    criteres_mous_tags: List[str] = Field(default_factory=list)
    conditions_clefs: str = ""
    lien_officiel: str = ""
    confiance: float = 1.0
    expiree: bool = False

class ProfilAgriculteur(BaseModel):
    profil_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region: str
    departement: Optional[str] = None
    statut_juridique: str
    superficie_ha: float
    productions: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    age_exploitant: Optional[int] = None
    jeune_agriculteur: bool = False
    projets: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EligibiliteResult(BaseModel):
    aide: AideAgricole
    eligible: bool
    raisons: List[str] = Field(default_factory=list)
    score_pertinence: float = 0.0
    resume_ia: str = ""

class EligibiliteResponse(BaseModel):
    profil: ProfilAgriculteur
    aides_eligibles: List[EligibiliteResult]
    total_aides: int
    total_eligibles: int

class AssistantRequest(BaseModel):
    question: str
    profil: Optional[ProfilAgriculteur] = None

# ============ LOGIQUE ELIGIBILITE ============ 

def evaluate_criteres_durs(criteres: Dict[str, Any], profil: ProfilAgriculteur) -> tuple:
    raisons = []
    
    def get_profil_value(key: str):
        mapping = {
            "$region": profil.region,
            "$departement": profil.departement,
            "$statut": profil.statut_juridique,
            "$superficie_ha": profil.superficie_ha,
            "$productions": profil.productions,
            "$labels": profil.labels,
            "$age": profil.age_exploitant,
            "$jeune_agriculteur": profil.jeune_agriculteur,
            "$projets": profil.projets,
        }
        return mapping.get(key)

    def eval_expr(expr):
        if not expr:
            return True
        
        if "and" in expr:
            results = [eval_expr(sub) for sub in expr["and"]]
            return all(results)
        
        if "or" in expr:
            results = [eval_expr(sub) for sub in expr["or"]]
            return any(results)
        
        if "in" in expr:
            field, values = expr["in"]
            profil_val = get_profil_value(field)
            
            if isinstance(profil_val, list):
                result = any(item in values for item in profil_val)
                if not result:
                    raisons.append(f"❌ {field.replace('$', '').capitalize()} : aucune correspondance")
                else:
                    matched = [item for item in profil_val if item in values]
                    raisons.append(f"✅ {field.replace('$', '').capitalize()} : {matched}")
            else:
                result = profil_val in values
                if not result:
                    raisons.append(f"❌ {field.replace('$', '').capitalize()} : non éligible")
                else:
                    raisons.append(f"✅ {field.replace('$', '').capitalize()} : {profil_val}")
            return result
        
        if ">=" in expr:
            field, value = expr[">="]
            profil_val = get_profil_value(field)
            result = profil_val is not None and profil_val >= value
            if not result:
                raisons.append(f"❌ {field.replace('$', '').capitalize()} : {profil_val} < {value} requis")
            else:
                raisons.append(f"✅ {field.replace('$', '').capitalize()} : {profil_val} >= {value}")
            return result
        
        if "<=" in expr:
            field, value = expr["<="]
            profil_val = get_profil_value(field)
            result = profil_val is not None and profil_val <= value
            if not result:
                raisons.append(f"❌ {field.replace('$', '').capitalize()} : {profil_val} > {value}")
            else:
                raisons.append(f"✅ {field.replace('$', '').capitalize()} : {profil_val} <= {value}")
            return result
        
        if "==" in expr:
            field, value = expr["=="]
            profil_val = get_profil_value(field)
            result = profil_val == value
            if not result:
                raisons.append(f"❌ {field.replace('$', '').capitalize()} : {profil_val} ≠ {value}")
            else:
                raisons.append(f"✅ {field.replace('$', '').capitalize()} : {profil_val} = {value}")
            return result
        
        return True
    
    eligible = eval_expr(criteres)
    return eligible, raisons

def calculate_score_pertinence(aide: AideAgricole, profil: ProfilAgriculteur) -> float:
    score = 0.0
    max_score = 0.0
    
    for tag in aide.criteres_mous_tags:
        max_score += 1.0
        if tag.lower() in [p.lower() for p in profil.projets]:
            score += 1.0
        elif tag.lower() in [l.lower() for l in profil.labels]:
            score += 0.8
        elif tag.lower() in [p.lower() for p in profil.productions]:
            score += 0.6
    
    if max_score > 0:
        return round((score / max_score) * 100, 1)
    return 0.0

async def generate_ia_summary(aide: AideAgricole, profil: ProfilAgriculteur, eligible: bool, raisons: List[str]) -> str:
    if eligible:
        return f"✅ Vous êtes éligible à cette aide. Votre profil correspond aux critères requis."
    else:
        return f"❌ Non éligible pour le moment. Vérifiez les critères manquants."

# ============ ENDPOINTS ============ 

@api_router.get("/")
async def root():
    return {"message": "AgriSubv API - Bienvenue sur l'API d'intelligence agricole"}

@api_router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@api_router.get("/aides", response_model=List[AideAgricole])
async def get_aides(
    region: Optional[str] = None,
    departement: Optional[str] = None,
    production: Optional[str] = None,
    projet: Optional[str] = None,
    statut: Optional[str] = None,
    label: Optional[str] = None,
    montant_min: Optional[float] = None,
    source: Optional[str] = None,
    q: Optional[str] = None,
    include_expired: bool = False,
    skip: int = 0,
    limit: int = 100
):
    """
    Récupère les aides avec filtres avancés
    
    Paramètres:
    - region: Filtrer par région
    - departement: Filtrer par département
    - production: Filtrer par type de production
    - projet: Filtrer par type de projet
    - statut: Filtrer par statut juridique
    - label: Filtrer par label
    - montant_min: Montant minimum de l'aide
    - source: Filtrer par source (manual, aides_territoires, datagouv_pac)
    - q: Recherche textuelle dans titre et description
    - include_expired: Inclure les aides expirées
    - skip: Nombre d'aides à sauter (pagination)
    - limit: Nombre maximum d'aides à retourner
    """
    query = {}
    
    # Filtrer les aides expirées sauf si demandé explicitement
    if not include_expired:
        query["expiree"] = False
    
    # Filtres géographiques
    if region:
        query["regions"] = {"$in": [region, "National"]}
    if departement:
        query["departements"] = departement
    
    # Filtres de production et projets
    if production:
        query["productions"] = production
    if projet:
        query["criteres_mous_tags"] = {"$regex": projet, "$options": "i"}
    
    # Filtres statut et labels
    if statut:
        query["statuts"] = statut
    if label:
        query["labels"] = label
    
    # Filtre montant minimum
    if montant_min is not None:
        query["$or"] = [
            {"montant_max_eur": {"$gte": montant_min}},
            {"montant_min_eur": {"$gte": montant_min}}
        ]
    
    # Filtre source
    if source:
        query["source"] = source
    
    # Recherche textuelle
    if q:
        query["$or"] = [
            {"titre": {"$regex": q, "$options": "i"}},
            {"conditions_clefs": {"$regex": q, "$options": "i"}},
            {"programme": {"$regex": q, "$options": "i"}}
        ]
    
    # Comptage total pour pagination
    total = await db.aides.count_documents(query)
    
    # Récupération avec pagination
    aides_cursor = db.aides.find(query).skip(skip).limit(limit)
    aides = await aides_cursor.to_list(length=limit)
    
    return [AideAgricole(**aide) for aide in aides]

@api_router.post("/eligibilite", response_model=EligibiliteResponse)
async def check_eligibilite(profil: ProfilAgriculteur):
    aides_cursor = db.aides.find({"expiree": False})
    aides = await aides_cursor.to_list(length=500)
    
    resultats = []
    
    for aide_data in aides:
        aide = AideAgricole(**aide_data)
        eligible, raisons = evaluate_criteres_durs(aide.criteres_durs_expr, profil)
        score = calculate_score_pertinence(aide, profil)
        resume_ia = await generate_ia_summary(aide, profil, eligible, raisons)
        
        resultats.append(EligibiliteResult(
            aide=aide,
            eligible=eligible,
            raisons=raisons,
            score_pertinence=score,
            resume_ia=resume_ia
        ))
    
    resultats.sort(key=lambda x: (not x.eligible, -x.score_pertinence))
    eligibles = [r for r in resultats if r.eligible]
    
    return EligibiliteResponse(
        profil=profil,
        aides_eligibles=resultats,
        total_aides=len(resultats),
        total_eligibles=len(eligibles)
    )

# ============ MATCHING V2 INTELLIGENT ============

@api_router.post("/matching")
async def calculate_matching_v2(profil: ProfilAgriculteurV2):
    """
    Matching intelligent V2 entre un profil agriculteur et toutes les aides V2
    
    Utilise le matching engine pour calculer un score de correspondance (0-100%)
    pour chaque aide en fonction de critères pondérés :
    - Localisation : 25%
    - Production : 20%
    - Projet : 15%
    - Statut juridique : 10%
    - Âge : 10%
    - Surface/Cheptel : 10%
    - Labels : 10%
    
    Args:
        profil: Profil complet de l'agriculteur (ProfilAgriculteurV2)
    
    Returns:
        {
            "profil_id": str,
            "total_aides": int,
            "aides_eligibles": int,
            "aides_quasi_eligibles": int,
            "aides_non_eligibles": int,
            "montant_total_estime_min": float,
            "montant_total_estime_max": float,
            "resultats": [ResultatMatching]
        }
    """
    try:
        logger.info(f"🎯 Matching V2 pour profil: {profil.region}, {profil.statut_juridique.value}")
        
        # Récupérer toutes les aides V2 actives
        aides_cursor = db.aides_v2.find({"statut": "active"})
        aides = await aides_cursor.to_list(length=5000)
        
        if not aides:
            logger.warning("⚠️  Aucune aide V2 trouvée dans la base")
            return {
                "profil_id": profil.profil_id,
                "total_aides": 0,
                "aides_eligibles": 0,
                "aides_quasi_eligibles": 0,
                "aides_non_eligibles": 0,
                "montant_total_estime_min": 0,
                "montant_total_estime_max": 0,
                "resultats": []
            }
        
        logger.info(f"   📊 {len(aides)} aides V2 trouvées")
        
        # Créer le matching engine
        engine = MatchingEngine()
        
        # Calculer le matching pour chaque aide
        resultats = []
        for aide_data in aides:
            try:
                # Convertir en objet AideAgricoleV2
                aide = AideAgricoleV2(**aide_data)
                
                # Calculer le matching
                resultat = engine.calculate_match(aide, profil)
                resultats.append(resultat)
                
            except Exception as e:
                logger.error(f"   ❌ Erreur matching aide {aide_data.get('aid_id')}: {e}")
                continue
        
        # Trier par score décroissant (aides les plus pertinentes en premier)
        resultats.sort(key=lambda x: (-x.eligible, -x.score))
        
        # Statistiques globales
        aides_eligibles = [r for r in resultats if r.eligible]
        aides_quasi_eligibles = [r for r in resultats if not r.eligible and r.score >= 40]
        aides_non_eligibles = [r for r in resultats if r.score < 40]
        
        # Calcul du montant total estimé (uniquement aides éligibles)
        montant_total_min = sum(
            r.montant_estime_min or 0 
            for r in aides_eligibles 
            if r.montant_estime_min
        )
        montant_total_max = sum(
            r.montant_estime_max or 0 
            for r in aides_eligibles 
            if r.montant_estime_max
        )
        
        logger.info(f"   ✅ Matching terminé:")
        logger.info(f"      - Éligibles: {len(aides_eligibles)}")
        logger.info(f"      - Quasi-éligibles: {len(aides_quasi_eligibles)}")
        logger.info(f"      - Non éligibles: {len(aides_non_eligibles)}")
        if montant_total_min > 0 or montant_total_max > 0:
            logger.info(f"      - Montant estimé: {montant_total_min:,.0f}€ - {montant_total_max:,.0f}€")
        
        return {
            "profil_id": profil.profil_id,
            "total_aides": len(resultats),
            "aides_eligibles": len(aides_eligibles),
            "aides_quasi_eligibles": len(aides_quasi_eligibles),
            "aides_non_eligibles": len(aides_non_eligibles),
            "montant_total_estime_min": round(montant_total_min, 2),
            "montant_total_estime_max": round(montant_total_max, 2),
            "resultats": [r.model_dump() for r in resultats]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du matching V2: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du calcul du matching: {str(e)}"
        )


@api_router.get("/matching/test")
async def test_matching_endpoint():
    """
    Endpoint de test pour vérifier que le matching engine fonctionne
    
    Returns:
        {
            "status": "ok" | "error",
            "matching_engine": "loaded" | "error",
            "aides_v2_count": int,
            "message": str
        }
    """
    try:
        # Vérifier que le matching engine peut être importé
        engine = MatchingEngine()
        
        # Compter les aides V2
        count_v2 = await db.aides_v2.count_documents({})
        count_active = await db.aides_v2.count_documents({"statut": "active"})
        
        return {
            "status": "ok",
            "matching_engine": "loaded",
            "aides_v2_count": count_v2,
            "aides_v2_active": count_active,
            "message": "✅ Endpoint de matching V2 opérationnel"
        }
    except ImportError as e:
        logger.error(f"Erreur import matching engine: {e}")
        return {
            "status": "error",
            "matching_engine": "import_error",
            "error": str(e),
            "message": "❌ Erreur lors du chargement du matching engine"
        }
    except Exception as e:
        logger.error(f"Erreur test matching: {e}")
        return {
            "status": "error",
            "matching_engine": "error",
            "error": str(e),
            "message": "❌ Erreur lors du test du matching engine"
        }

@api_router.post("/aides")
async def create_or_update_aide(aide: AideAgricole):
    aide_dict = aide.dict()
    existing = await db.aides.find_one({"aid_id": aide.aid_id})
    
    if existing:
        await db.aides.update_one({"aid_id": aide.aid_id}, {"$set": aide_dict})
        return {"message": "Aide mise à jour", "aid_id": aide.aid_id}
    else:
        await db.aides.insert_one(aide_dict)
        return {"message": "Aide créée", "aid_id": aide.aid_id}

@api_router.post("/seed")
async def seed_database():
    """Initialize database with sample agricultural aids"""
    
    # Check if already seeded
    existing_count = await db.aides.count_documents({})
    if existing_count > 0:
        return {
            "message": "Database already contains aids",
            "existing_aids": existing_count,
            "action": "skipped"
        }
    
    # Sample aids data
    sample_aids = [
        {
            "aid_id": "aide-001",
            "titre": "Aide à la Conversion Bio",
            "organisme": "Agence Bio",
            "programme": "Conversion Agriculture Biologique 2024",
            "source_url": "https://www.agencebio.org/aides",
            "regions": ["National"],
            "departements": [],
            "productions": ["Céréales", "Maraîchage", "Viticulture", "Élevage"],
            "statuts": ["EARL", "SCEA", "Exploitation individuelle"],
            "labels": ["Agriculture Biologique"],
            "montant_min_eur": 3500,
            "montant_max_eur": 12000,
            "date_ouverture": "2024-01-15",
            "date_limite": "2024-12-31",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$productions", ["Céréales", "Maraîchage", "Viticulture", "Élevage"]]},
                    {">=": ["$superficie_ha", 5]}
                ]
            },
            "criteres_mous_tags": ["bio", "conversion", "agriculture durable"],
            "conditions_clefs": "Engagement conversion bio sur 5 ans minimum",
            "lien_officiel": "https://www.agencebio.org/conversion",
            "confiance": 0.95,
            "expiree": False
        },
        {
            "aid_id": "aide-002",
            "titre": "Dotation Jeunes Agriculteurs (DJA)",
            "organisme": "Ministère Agriculture",
            "programme": "Installation Jeunes Agriculteurs 2024",
            "source_url": "https://agriculture.gouv.fr/dja",
            "regions": ["National"],
            "departements": [],
            "productions": ["Tous types"],
            "statuts": ["Exploitation individuelle", "EARL", "GAEC"],
            "labels": [],
            "montant_min_eur": 8000,
            "montant_max_eur": 36000,
            "date_ouverture": "2024-01-01",
            "date_limite": "2024-12-31",
            "criteres_durs_expr": {
                "and": [
                    {"<=": ["$age", 40]},
                    {"==": ["$jeune_agriculteur", True]}
                ]
            },
            "criteres_mous_tags": ["installation", "jeune", "reprise exploitation"],
            "conditions_clefs": "Moins de 40 ans, diplôme agricole requis",
            "lien_officiel": "https://agriculture.gouv.fr/jeunes-agriculteurs",
            "confiance": 1.0,
            "expiree": False
        },
        {
            "aid_id": "aide-003",
            "titre": "Aide à l'Irrigation Économe en Eau",
            "organisme": "Agence de l'Eau",
            "programme": "Gestion Durable de l'Eau Agricole",
            "source_url": "https://www.lesagencesdeleau.fr",
            "regions": ["Nouvelle-Aquitaine", "Occitanie", "PACA"],
            "departements": [],
            "productions": ["Maraîchage", "Arboriculture"],
            "statuts": ["EARL", "SCEA", "Exploitation individuelle"],
            "labels": [],
            "taux_min_pct": 30,
            "taux_max_pct": 50,
            "plafond_eur": 30000,
            "date_ouverture": "2024-03-01",
            "date_limite": "2024-09-30",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$region", ["Nouvelle-Aquitaine", "Occitanie", "PACA"]]},
                    {"in": ["$productions", ["Maraîchage", "Arboriculture"]]}
                ]
            },
            "criteres_mous_tags": ["irrigation", "économie eau", "goutte-à-goutte"],
            "conditions_clefs": "Installation système irrigation goutte-à-goutte",
            "lien_officiel": "https://www.lesagencesdeleau.fr/irrigation",
            "confiance": 0.88,
            "expiree": False
        },
        {
            "aid_id": "aide-004",
            "titre": "Certification HVE (Haute Valeur Environnementale)",
            "organisme": "Ministère Agriculture",
            "programme": "Transition Agroécologique",
            "source_url": "https://agriculture.gouv.fr/hve",
            "regions": ["National"],
            "departements": [],
            "productions": ["Viticulture", "Grandes cultures", "Arboriculture"],
            "statuts": ["EARL", "SCEA", "Exploitation individuelle", "GAEC"],
            "labels": ["HVE"],
            "montant_min_eur": 2500,
            "montant_max_eur": 8000,
            "date_ouverture": "2024-01-01",
            "date_limite": "2024-11-30",
            "criteres_durs_expr": {
                "in": ["$productions", ["Viticulture", "Grandes cultures", "Arboriculture"]]
            },
            "criteres_mous_tags": ["environnement", "biodiversité", "certification"],
            "conditions_clefs": "Audit environnemental et plan d'amélioration requis",
            "lien_officiel": "https://agriculture.gouv.fr/certification-hve",
            "confiance": 0.92,
            "expiree": False
        },
        {
            "aid_id": "aide-005",
            "titre": "Aide Robotisation et Numérique Agricole",
            "organisme": "FranceAgriMer",
            "programme": "Agriculture 4.0",
            "source_url": "https://www.franceagrimer.fr",
            "regions": ["National"],
            "departements": [],
            "productions": ["Élevage laitier", "Grandes cultures"],
            "statuts": ["EARL", "GAEC", "SCEA"],
            "labels": [],
            "taux_min_pct": 20,
            "taux_max_pct": 40,
            "plafond_eur": 50000,
            "date_ouverture": "2024-02-01",
            "date_limite": "2024-10-31",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$productions", ["Élevage laitier", "Grandes cultures"]]},
                    {">=": ["$superficie_ha", 30]}
                ]
            },
            "criteres_mous_tags": ["robot", "numérique", "automatisation", "précision"],
            "conditions_clefs": "Investissement dans robots de traite ou outils de précision",
            "lien_officiel": "https://www.franceagrimer.fr/robotique",
            "confiance": 0.85,
            "expiree": False
        },
        {
            "aid_id": "aide-006",
            "titre": "Aide au Bien-être Animal",
            "organisme": "Région Bretagne",
            "programme": "Élevage Responsable 2024",
            "source_url": "https://www.bretagne.bzh/agriculture",
            "regions": ["Bretagne"],
            "departements": ["22", "29", "35", "56"],
            "productions": ["Élevage porcin", "Élevage bovin", "Élevage avicole"],
            "statuts": ["EARL", "GAEC", "SCEA"],
            "labels": [],
            "taux_min_pct": 25,
            "taux_max_pct": 40,
            "plafond_eur": 20000,
            "date_ouverture": "2024-01-15",
            "date_limite": "2024-06-30",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$region", ["Bretagne"]]},
                    {"in": ["$productions", ["Élevage porcin", "Élevage bovin", "Élevage avicole"]]}
                ]
            },
            "criteres_mous_tags": ["bien-être animal", "bâtiment", "aménagement"],
            "conditions_clefs": "Aménagement bâtiments d'élevage pour bien-être animal",
            "lien_officiel": "https://www.bretagne.bzh/bien-etre-animal",
            "confiance": 0.90,
            "expiree": False
        },
        {
            "aid_id": "aide-007",
            "titre": "Aide à l'Agroforesterie",
            "organisme": "Région Nouvelle-Aquitaine",
            "programme": "Plantation Agroforesterie 2024",
            "source_url": "https://les-aides.nouvelle-aquitaine.fr",
            "regions": ["Nouvelle-Aquitaine"],
            "departements": [],
            "productions": ["Grandes cultures", "Élevage", "Viticulture"],
            "statuts": ["Exploitation individuelle", "EARL", "GAEC", "SCEA"],
            "labels": [],
            "montant_min_eur": 5000,
            "montant_max_eur": 15000,
            "date_ouverture": "2024-02-01",
            "date_limite": "2024-05-31",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$region", ["Nouvelle-Aquitaine"]]},
                    {">=": ["$superficie_ha", 10]}
                ]
            },
            "criteres_mous_tags": ["agroforesterie", "arbre", "haie", "biodiversité"],
            "conditions_clefs": "Plantation minimum 100 arbres/ha",
            "lien_officiel": "https://les-aides.nouvelle-aquitaine.fr/agroforesterie",
            "confiance": 0.87,
            "expiree": False
        },
        {
            "aid_id": "aide-008",
            "titre": "Aide Méthanisation Collective",
            "organisme": "ADEME",
            "programme": "Énergie Renouvelable Agricole",
            "source_url": "https://www.ademe.fr",
            "regions": ["National"],
            "departements": [],
            "productions": ["Élevage"],
            "statuts": ["GAEC", "CUMA", "Coopérative"],
            "labels": [],
            "taux_min_pct": 30,
            "taux_max_pct": 55,
            "plafond_eur": 200000,
            "date_ouverture": "2024-01-01",
            "date_limite": "2024-12-31",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$productions", ["Élevage"]]},
                    {"in": ["$statut", ["GAEC", "CUMA", "Coopérative"]]}
                ]
            },
            "criteres_mous_tags": ["méthanisation", "énergie", "biogaz", "collectif"],
            "conditions_clefs": "Projet collectif minimum 3 exploitations",
            "lien_officiel": "https://www.ademe.fr/methanisation",
            "confiance": 0.83,
            "expiree": False
        },
        {
            "aid_id": "aide-009",
            "titre": "Aide Développement Circuits Courts",
            "organisme": "Chambre d'Agriculture",
            "programme": "Vente Directe 2024",
            "source_url": "https://chambres-agriculture.fr",
            "regions": ["National"],
            "departements": [],
            "productions": ["Maraîchage", "Élevage", "Viticulture", "Arboriculture"],
            "statuts": ["Exploitation individuelle", "EARL", "GAEC"],
            "labels": [],
            "montant_min_eur": 3000,
            "montant_max_eur": 10000,
            "date_ouverture": "2024-01-15",
            "date_limite": "2024-08-31",
            "criteres_durs_expr": {
                "in": ["$productions", ["Maraîchage", "Élevage", "Viticulture", "Arboriculture"]]
            },
            "criteres_mous_tags": ["circuit court", "vente directe", "magasin", "marché"],
            "conditions_clefs": "Création point de vente ou aménagement pour circuits courts",
            "lien_officiel": "https://chambres-agriculture.fr/circuits-courts",
            "confiance": 0.91,
            "expiree": False
        },
        {
            "aid_id": "aide-010",
            "titre": "Aide Modernisation des Serres",
            "organisme": "FranceAgriMer",
            "programme": "Horticulture Durable",
            "source_url": "https://www.franceagrimer.fr",
            "regions": ["National"],
            "departements": [],
            "productions": ["Maraîchage", "Horticulture"],
            "statuts": ["EARL", "SCEA", "Exploitation individuelle"],
            "labels": [],
            "taux_min_pct": 25,
            "taux_max_pct": 40,
            "plafond_eur": 40000,
            "date_ouverture": "2024-03-01",
            "date_limite": "2024-09-30",
            "criteres_durs_expr": {
                "and": [
                    {"in": ["$productions", ["Maraîchage", "Horticulture"]]},
                    {">=": ["$superficie_ha", 0.5]}
                ]
            },
            "criteres_mous_tags": ["serre", "économie énergie", "isolation", "chauffage"],
            "conditions_clefs": "Travaux isolation ou système chauffage économe",
            "lien_officiel": "https://www.franceagrimer.fr/serres",
            "confiance": 0.86,
            "expiree": False
        },
        {
            "aid_id": "aide-011",
            "titre": "Aide à la Diversification Agricole",
            "organisme": "Région Auvergne-Rhône-Alpes",
            "programme": "Diversification Activités 2024",
            "source_url": "https://www.auvergnerhonealpes.fr",
            "regions": ["Auvergne-Rhône-Alpes"],
            "departements": [],
            "productions": ["Tous types"],
            "statuts": ["Exploitation individuelle", "EARL", "GAEC"],
            "labels": [],
            "taux_min_pct": 30,
            "taux_max_pct": 50,
            "plafond_eur": 25000,
            "date_ouverture": "2024-02-01",
            "date_limite": "2024-11-30",
            "criteres_durs_expr": {
                "in": ["$region", ["Auvergne-Rhône-Alpes"]]
            },
            "criteres_mous_tags": ["diversification", "agrotourisme", "transformation", "vente"],
            "conditions_clefs": "Création activité complémentaire (agrotourisme, transformation...)",
            "lien_officiel": "https://www.auvergnerhonealpes.fr/diversification",
            "confiance": 0.84,
            "expiree": False
        }
    ]
    
    # Insert aids
    result = await db.aides.insert_many(sample_aids)
    
    return {
        "message": "Database seeded successfully with agricultural aids",
        "aids_created": len(result.inserted_ids),
        "aids": sample_aids
    }
@api_router.post("/assistant")
async def assistant_ia(request: AssistantRequest):
    return {"reponse": "Assistant IA non disponible dans cette version. Utilisez le formulaire pour trouver vos aides."}

@api_router.get("/stats")
async def get_stats():
    total_aides = await db.aides.count_documents({})
    aides_actives = await db.aides.count_documents({"expiree": False})
    
    pipeline = [
        {"$group": {"_id": "$organisme", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    organismes = await db.aides.aggregate(pipeline).to_list(length=20)
    
    return {
        "total_aides": total_aides,
        "aides_actives": aides_actives,
        "par_organisme": organismes
    }
# ============ SYNC AIDES-TERRITOIRES ============

from sync_aides_territoires import sync_aides_to_db

@api_router.post("/sync/aides-territoires")
async def sync_aides_territoires(limit: Optional[int] = None):
    """
    Synchronise les aides depuis l'API Aides-Territoires
    
    Paramètres:
    - limit: Nombre maximum d'aides à synchroniser (optionnel, pour tests)
    """
    try:
        result = await sync_aides_to_db(db, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sync/status")
async def get_sync_status():
    """Retourne le statut de la base de données avec comptage par source et statut"""
    
    try:
        # Comptage total
        total_aides = await db.aides.count_documents({})
        
        # Comptage par source
        aides_manual = await db.aides.count_documents({"source": "manual"})
        aides_at = await db.aides.count_documents({"source": "aides-territoires"})
        aides_pac = await db.aides.count_documents({"source": "datagouv-pac"})
        # Aides sans source définie (anciennes)
        aides_no_source = await db.aides.count_documents({"source": {"$exists": False}})
        
        # Comptage par statut
        aides_actives = await db.aides.count_documents({"expiree": False})
        aides_inactives = await db.aides.count_documents({"expiree": True})
        
        # Dernière synchronisation
        derniere_aide = await db.aides.find_one(
            {"source": {"$in": ["aides-territoires", "datagouv-pac"]}},
            sort=[("derniere_maj", -1)]
        )
        derniere_maj = derniere_aide.get('derniere_maj') if derniere_aide else None
        
        return {
            "total_aides": total_aides,
            "by_source": {
                "manual": aides_manual + aides_no_source,
                "aides_territoires": aides_at,
                "datagouv_pac": aides_pac
            },
            "by_status": {
                "active": aides_actives,
                "inactive": aides_inactives
            },
            "derniere_synchronisation": derniere_maj
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")

# ============ SYNC DATA.GOUV.FR PAC ============

from sync_datagouv_pac import sync_pac_to_db

@api_router.post("/sync/datagouv-pac")
async def sync_datagouv_pac(limit: Optional[int] = None):
    """
    Synchronise les aides PAC depuis Data.gouv.fr
    
    Paramètres:
    - limit: Nombre maximum d'aides à synchroniser (optionnel)
    """
    try:
        result = await sync_pac_to_db(db, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation PAC : {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ SYNC AIDES-TERRITOIRES V2 ============

from sync_aides_territoires_v2 import sync_aides_territoires_v2

@api_router.post("/sync/aides-territoires-v2")
async def sync_aides_territoires_v2_endpoint(
    max_pages: Optional[int] = None,
    background_tasks = None
):
    """
    Synchronise les aides depuis Aides-Territoires vers le modèle V2
    
    Paramètres:
    - max_pages: Nombre maximum de pages à synchroniser (optionnel, pour tests)
    """
    try:
        # Lancer la synchronisation
        result = await sync_aides_territoires_v2(db, max_pages=max_pages)
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation V2 : {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def create_indexes():
    """Crée les index MongoDB optimisés au démarrage"""
    try:
        logger.info("🔧 Création des index MongoDB...")
        
        # Index texte pour recherche full-text sur titre et description
        await db.aides.create_index([
            ("titre", "text"),
            ("conditions_clefs", "text")
        ], name="text_search_index")
        logger.info("   ✅ Index texte créé")
        
        # Index sur les régions
        await db.aides.create_index("regions", name="regions_index")
        logger.info("   ✅ Index régions créé")
        
        # Index sur source et statut
        await db.aides.create_index("source", name="source_index")
        await db.aides.create_index("expiree", name="expiree_index")
        logger.info("   ✅ Index source et statut créés")
        
        # Index sur date_fin pour gérer les expirations
        await db.aides.create_index("date_limite", name="date_limite_index")
        logger.info("   ✅ Index date_limite créé")
        
        # Index sur productions et tags
        await db.aides.create_index("productions", name="productions_index")
        await db.aides.create_index("criteres_mous_tags", name="tags_index")
        logger.info("   ✅ Index productions et tags créés")
        
        # Index pour la collection V2
        await db.aides_v2.create_index([
            ("titre", "text"),
            ("description", "text")
        ], name="v2_text_search_index")
        await db.aides_v2.create_index("criteres.regions", name="v2_regions_index")
        await db.aides_v2.create_index("source", name="v2_source_index")
        await db.aides_v2.create_index("statut", name="v2_statut_index")
        await db.aides_v2.create_index("criteres.types_production", name="v2_productions_index")
        await db.aides_v2.create_index("criteres.types_projets", name="v2_projets_index")
        logger.info("   ✅ Index V2 créés")
        
        logger.info("✅ Tous les index MongoDB ont été créés avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des index: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
