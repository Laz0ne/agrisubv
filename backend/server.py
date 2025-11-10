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