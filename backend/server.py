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

# ============ CONFIGURATION LOGGER (DÉPLACÉ EN PREMIER) ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Imports pour matching V2
from matching_engine import MatchingEngine
from models_v2 import (
    ProfilAgriculteur as ProfilAgriculteurV2, 
    ResultatMatching, 
    AideAgricoleV2,
    StatutJuridique,
    TypeProduction,
    TypeProjet
)

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

# ============ ADAPTATEUR POUR ANCIEN FORMAT ============

class ProfilAgriculteurLegacy(BaseModel):
    """Ancien format de profil (pour compatibilité frontend)"""
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


def convert_legacy_to_v2(legacy: ProfilAgriculteurLegacy) -> ProfilAgriculteurV2:
    """Convertit l'ancien format en V2"""
    
    # Mapping des statuts
    statut_mapping = {
        "Exploitation individuelle": "INDIVIDUEL",
        "EARL": "EARL",
        "GAEC": "GAEC",
        "SCEA": "SCEA",
        "SA": "SA",
        "CUMA": "CUMA",
        "Coopérative": "COOPERATIVE",
        "GIE": "GIE",
        "Autre": "AUTRE"
    }
    
    # Mapping des productions
    production_mapping = {
        "Céréales": "CEREALES",
        "Maraîchage": "MARAICHAGE",
        "Viticulture": "VITICULTURE",
        "Arboriculture": "ARBORICULTURE",
        "Élevage bovin": "ELEVAGE_BOVIN",
        "Élevage ovin": "ELEVAGE_OVIN",
        "Élevage caprin": "ELEVAGE_CAPRIN",
        "Élevage porcin": "ELEVAGE_PORCIN",
        "Élevage avicole": "ELEVAGE_AVICOLE",
        "Élevage laitier": "ELEVAGE_LAITIER",
        "Grandes cultures": "GRANDES_CULTURES",
        "Horticulture": "HORTICULTURE",
        "Apiculture": "APICULTURE",
        "Aquaculture": "AQUACULTURE"
    }
    
    # Mapping des projets
    projet_mapping = {
        "Installation": "INSTALLATION",
        "Conversion bio": "CONVERSION_BIO",
        "Modernisation": "MODERNISATION",
        "Diversification": "DIVERSIFICATION",
        "Irrigation": "IRRIGATION",
        "Bâtiment": "BATIMENT",
        "Matériel": "MATERIEL",
        "Énergie": "ENERGIE",
        "Environnement": "ENVIRONNEMENT",
        "Formation": "FORMATION",
        "Commercialisation": "COMMERCIALISATION",
        "Numérique": "NUMERIQUE",
        "Bien-être animal": "BIEN_ETRE_ANIMAL"
    }
    
    # Convertir statut
    statut_key = statut_mapping.get(legacy.statut_juridique, "AUTRE")
    try:
        statut = StatutJuridique[statut_key]
    except KeyError:
        logger.warning(f"Statut inconnu: {legacy.statut_juridique}, utilisation de AUTRE")
        statut = StatutJuridique.AUTRE
    
    # Convertir productions
    productions_v2 = []
    for prod in legacy.productions:
        prod_key = production_mapping.get(prod)
        if prod_key:
            try:
                productions_v2.append(TypeProduction[prod_key])
            except KeyError:
                logger.warning(f"Production inconnue: {prod}")
    
    # Convertir projets
    projets_v2 = []
    for proj in legacy.projets:
        proj_key = projet_mapping.get(proj)
        if proj_key:
            try:
                projets_v2.append(TypeProjet[proj_key])
            except KeyError:
                logger.warning(f"Projet inconnu: {proj}")
    
    # Créer le profil V2
    return ProfilAgriculteurV2(
        profil_id=legacy.profil_id,
        region=legacy.region,
        departement=legacy.departement or "00",
        statut_juridique=statut,
        sau_totale=legacy.superficie_ha,
        sau_bio=legacy.superficie_ha if "Agriculture Biologique" in legacy.labels or "Bio" in legacy.labels else 0,
        productions=productions_v2,
        production_principale=productions_v2[0] if productions_v2 else None,
        age=legacy.age_exploitant,
        jeune_agriculteur=legacy.jeune_agriculteur,
        labels=legacy.labels,
        label_bio="Agriculture Biologique" in legacy.labels or "Bio" in legacy.labels,
        projets_en_cours=projets_v2,
        created_at=legacy.created_at
    )

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
    """Récupère les aides avec filtres avancés"""
    query = {}
    
    if not include_expired:
        query["expiree"] = False
    
    if region:
        query["regions"] = {"$in": [region, "National"]}
    if departement:
        query["departements"] = departement
    
    if production:
        query["productions"] = production
    if projet:
        query["criteres_mous_tags"] = {"$regex": projet, "$options": "i"}
    
    if statut:
        query["statuts"] = statut
    if label:
        query["labels"] = label
    
    if montant_min is not None:
        query["$or"] = [
            {"montant_max_eur": {"$gte": montant_min}},
            {"montant_min_eur": {"$gte": montant_min}}
        ]
    
    if source:
        query["source"] = source
    
    if q:
        query["$or"] = [
            {"titre": {"$regex": q, "$options": "i"}},
            {"conditions_clefs": {"$regex": q, "$options": "i"}},
            {"programme": {"$regex": q, "$options": "i"}}
        ]
    
    total = await db.aides.count_documents(query)
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
async def calculate_matching_v2(profil_data: Dict[str, Any]):
    """
    Matching intelligent V2 - Accepte ancien et nouveau format
    """
    try:
        # Détecter le format (V2 a "sau_totale", ancien a "superficie_ha")
        if "superficie_ha" in profil_data:
            logger.info("🔄 Conversion ancien format → V2")
            legacy_profil = ProfilAgriculteurLegacy(**profil_data)
            profil = convert_legacy_to_v2(legacy_profil)
        else:
            logger.info("✅ Format V2 détecté")
            profil = ProfilAgriculteurV2(**profil_data)
        
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
                aide = AideAgricoleV2(**aide_data)
                resultat = engine.calculate_match(aide, profil)
                resultats.append(resultat)
                
            except Exception as e:
                logger.error(f"   ❌ Erreur matching aide {aide_data.get('aid_id')}: {e}")
                continue
        
        # Trier par score décroissant
        resultats.sort(key=lambda x: (-x.eligible, -x.score))
        
        # Statistiques globales
        aides_eligibles = [r for r in resultats if r.eligible]
        aides_quasi_eligibles = [r for r in resultats if not r.eligible and r.score >= 40]
        aides_non_eligibles = [r for r in resultats if r.score < 40]
        
        # Calcul du montant total estimé
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
    """Endpoint de test pour vérifier que le matching engine fonctionne"""
    try:
        engine = MatchingEngine()
        
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
            "message": "❌ Erreur lors du chargement du matching engine"
        }
    except Exception as e:
        logger.error(f"Erreur test matching: {e}")
        return {
            "status": "error",
            "matching_engine": "error",
            "message": "❌ Erreur lors du test du matching engine"
        }

# ============ ADMIN ENDPOINTS ============

@api_router.post("/admin/run-migration")
async def run_migration_via_http():
    """Endpoint admin pour exécuter la migration V2"""
    try:
        logger.info("🚀 Démarrage de la migration V2 via HTTP...")
        
        from migrate_to_v2 import MigrationV2
        
        migration = MigrationV2(db)
        
        logger.info("⚠️  Mode: Suppression des aides factices ACTIVÉ")
        result = await migration.migrate_all(clean_fake_aids=True)
        
        if result['success']:
            logger.info("✅ Migration terminée avec succès via HTTP")
            
            total_old = int(result.get('total_old', 0))
            total_fake = int(result.get('total_fake', 0))
            fake_deleted = int(result.get('fake_deleted', 0))
            total_real = int(result.get('total_real', 0))
            total_migrated = int(result.get('total_migrated', 0))
            errors_count = int(result.get('errors', 0))
            
            safe_stats = result.get('stats', {})
            by_source = {}
            for k, v in safe_stats.get('by_source', {}).items():
                by_source[str(k)] = int(v) if isinstance(v, (int, float)) else 0
            
            productions = {}
            for k, v in safe_stats.get('productions', {}).items():
                productions[str(k)] = int(v) if isinstance(v, (int, float)) else 0
            
            projets = {}
            for k, v in safe_stats.get('projets', {}).items():
                projets[str(k)] = int(v) if isinstance(v, (int, float)) else 0
            
            return {
                "status": "success",
                "message": "Migration V2 terminée avec succès",
                "migration_results": {
                    "total_old": total_old,
                    "total_fake": total_fake,
                    "fake_deleted": fake_deleted,
                    "total_real": total_real,
                    "total_migrated": total_migrated,
                    "errors": errors_count,
                    "stats": {
                        "by_source": by_source,
                        "productions": productions,
                        "projets": projets
                    }
                },
                "summary": {
                    "aides_before": total_old,
                    "aides_after": total_real,
                    "aides_v2_created": total_migrated,
                    "fake_aids_removed": fake_deleted
                }
            }
        else:
            logger.error("❌ La migration a échoué")
            if result.get('errors_details'):
                logger.error(f"Détails des erreurs: {result.get('errors_details')}")
            return {
                "status": "error",
                "message": "La migration a échoué. Consultez les logs du serveur.",
                "errors_count": int(result.get('errors', 0))
            }
            
    except ImportError as e:
        logger.error(f"❌ Erreur import MigrationV2: {e}")
        return {
            "status": "error",
            "message": "Erreur lors de l'import du module de migration.",
            "error_type": "import_error"
        }
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration via HTTP: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": "Erreur lors de l'exécution de la migration.",
            "error_type": "execution_error"
        }


@api_router.get("/admin/migration-status")
async def get_migration_status():
    """Vérifie l'état des collections"""
    try:
        aides_count = await db.aides.count_documents({})
        aides_v2_count = await db.aides_v2.count_documents({})
        
        aides_active = await db.aides.count_documents({"expiree": False})
        aides_v2_active = await db.aides_v2.count_documents({"statut": "active"})
        
        migration_done = aides_v2_count > 0
        
        sources_v1 = {}
        async for aide in db.aides.find({}, {"source": 1}):
            source = aide.get("source", "manual")
            sources_v1[source] = sources_v1.get(source, 0) + 1
        
        sources_v2 = {}
        async for aide in db.aides_v2.find({}, {"source": 1}):
            source = aide.get("source", "manual")
            sources_v2[source] = sources_v2.get(source, 0) + 1
        
        return {
            "aides_collection": {
                "total": aides_count,
                "active": aides_active,
                "by_source": sources_v1
            },
            "aides_v2_collection": {
                "total": aides_v2_count,
                "active": aides_v2_active,
                "by_source": sources_v2
            },
            "migration_done": migration_done,
            "message": "✅ Migration effectuée" if migration_done else "⚠️ Migration non effectuée",
            "recommendations": [
                "Lancer POST /api/admin/run-migration"
            ] if not migration_done else [
                "Migration OK",
                "Testez POST /api/matching"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur statut: {e}")
        return {
            "status": "error",
            "message": "Erreur vérification statut"
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

@api_router.post("/assistant")
async def assistant_ia(request: AssistantRequest):
    return {"reponse": "Assistant IA non disponible."}

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

# ============ SYNC ENDPOINTS ============

from sync_aides_territoires import sync_aides_to_db

@api_router.post("/sync/aides-territoires")
async def sync_aides_territoires(limit: Optional[int] = None):
    try:
        result = await sync_aides_to_db(db, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Erreur sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sync/status")
async def get_sync_status():
    try:
        total_aides = await db.aides.count_documents({})
        
        aides_manual = await db.aides.count_documents({"source": "manual"})
        aides_at = await db.aides.count_documents({"source": "aides-territoires"})
        aides_pac = await db.aides.count_documents({"source": "datagouv-pac"})
        aides_no_source = await db.aides.count_documents({"source": {"$exists": False}})
        
        aides_actives = await db.aides.count_documents({"expiree": False})
        aides_inactives = await db.aides.count_documents({"expiree": True})
        
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
        logger.error(f"Erreur statut sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from sync_datagouv_pac import sync_pac_to_db

@api_router.post("/sync/datagouv-pac")
async def sync_datagouv_pac(limit: Optional[int] = None):
    try:
        result = await sync_pac_to_db(db, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Erreur sync PAC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from sync_aides_territoires_v2 import sync_aides_territoires_v2

@api_router.post("/sync/aides-territoires-v2")
async def sync_aides_territoires_v2_endpoint(
    max_pages: Optional[int] = None,
    background_tasks = None
):
    try:
        result = await sync_aides_territoires_v2(db, max_pages=max_pages)
        return result
    except Exception as e:
        logger.error(f"Erreur sync V2: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ APP CONFIGURATION ============

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def create_indexes():
    """Crée les index MongoDB"""
    try:
        logger.info("🔧 Création index MongoDB...")
        
        await db.aides.create_index([
            ("titre", "text"),
            ("conditions_clefs", "text")
        ], name="text_search_index")
        
        await db.aides.create_index("regions", name="regions_index")
        await db.aides.create_index("source", name="source_index")
        await db.aides.create_index("expiree", name="expiree_index")
        await db.aides.create_index("date_limite", name="date_limite_index")
        await db.aides.create_index("productions", name="productions_index")
        await db.aides.create_index("criteres_mous_tags", name="tags_index")
        
        await db.aides_v2.create_index([
            ("titre", "text"),
            ("description", "text")
        ], name="v2_text_search_index")
        await db.aides_v2.create_index("criteres.regions", name="v2_regions_index")
        await db.aides_v2.create_index("source", name="v2_source_index")
        await db.aides_v2.create_index("statut", name="v2_statut_index")
        await db.aides_v2.create_index("criteres.types_production", name="v2_productions_index")
        await db.aides_v2.create_index("criteres.types_projets", name="v2_projets_index")
        
        logger.info("✅ Index créés")
    except Exception as e:
        logger.error(f"❌ Erreur index: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
