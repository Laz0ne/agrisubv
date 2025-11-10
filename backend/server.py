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
    production: Optional[str] = None,
    statut: Optional[str] = None,
    label: Optional[str] = None,
    mot_cle: Optional[str] = None,
    limit: int = 100
):
    query = {"expiree": False}
    
    if region:
        query["regions"] = {"$in": [region, "National"]}
    if production:
        query["productions"] = production
    if statut:
        query["statuts"] = statut
    if label:
        query["labels"] = label
    if mot_cle:
        query["$or"] = [
            {"titre": {"$regex": mot_cle, "$options": "i"}},
            {"conditions_clefs": {"$regex": mot_cle, "$options": "i"}}
        ]
    
    aides_cursor = db.aides.find(query).limit(limit)
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
