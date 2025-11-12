"""
Modèles de données V2 pour AgriSubv
Version optimisée pour gérer 1000+ aides avec critères enrichis
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone
from enum import Enum
import uuid


# ============ ENUMS ============

class TypeProduction(str, Enum):
    """Types de production agricole"""
    CEREALES = "Céréales"
    MARAICHAGE = "Maraîchage"
    VITICULTURE = "Viticulture"
    ARBORICULTURE = "Arboriculture"
    ELEVAGE_BOVIN = "Élevage bovin"
    ELEVAGE_OVIN = "Élevage ovin"
    ELEVAGE_CAPRIN = "Élevage caprin"
    ELEVAGE_PORCIN = "Élevage porcin"
    ELEVAGE_AVICOLE = "Élevage avicole"
    ELEVAGE_LAITIER = "Élevage laitier"
    GRANDES_CULTURES = "Grandes cultures"
    HORTICULTURE = "Horticulture"
    APICULTURE = "Apiculture"
    AQUACULTURE = "Aquaculture"


class TypeProjet(str, Enum):
    """Types de projets agricoles"""
    INSTALLATION = "Installation"
    CONVERSION_BIO = "Conversion bio"
    MODERNISATION = "Modernisation"
    DIVERSIFICATION = "Diversification"
    IRRIGATION = "Irrigation"
    BATIMENT = "Bâtiment"
    MATERIEL = "Matériel"
    ENERGIE = "Énergie"
    ENVIRONNEMENT = "Environnement"
    FORMATION = "Formation"
    COMMERCIALISATION = "Commercialisation"
    NUMERIQUE = "Numérique"
    BIEN_ETRE_ANIMAL = "Bien-être animal"


class StatutJuridique(str, Enum):
    """Statuts juridiques des exploitations"""
    INDIVIDUEL = "Exploitation individuelle"
    EARL = "EARL"
    GAEC = "GAEC"
    SCEA = "SCEA"
    SA = "SA"
    CUMA = "CUMA"
    COOPERATIVE = "Coopérative"
    GIE = "GIE"
    AUTRE = "Autre"


class TypeMontant(str, Enum):
    """Types de montant d'aide"""
    FORFAITAIRE = "Forfaitaire"
    POURCENTAGE = "Pourcentage"
    SURFACE = "Surface"
    TETE = "Tête"
    UNITE = "Unité"


# ============ SOUS-MODÈLES ============

class CriteresEligibilite(BaseModel):
    """Critères d'éligibilité détaillés pour une aide"""
    
    regions: List[str] = Field(default_factory=list)
    departements: List[str] = Field(default_factory=list)
    zones_specifiques: List[str] = Field(default_factory=list)
    
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    jeune_agriculteur: Optional[bool] = None
    
    superficie_min: Optional[float] = None
    superficie_max: Optional[float] = None
    cheptel_min: Optional[int] = None
    cheptel_max: Optional[int] = None
    
    ca_min: Optional[float] = None
    ca_max: Optional[float] = None
    
    types_production: List[TypeProduction] = Field(default_factory=list)
    types_projets: List[TypeProjet] = Field(default_factory=list)
    
    statuts_juridiques: List[StatutJuridique] = Field(default_factory=list)
    labels_requis: List[str] = Field(default_factory=list)
    labels_bonus: List[str] = Field(default_factory=list)
    
    premiere_installation: Optional[bool] = None
    en_difficulte: Optional[bool] = None
    projets_collectifs: Optional[bool] = None


class MontantAide(BaseModel):
    """Montant et modalités de l'aide"""
    
    type_montant: TypeMontant = TypeMontant.FORFAITAIRE
    
    montant_min: Optional[float] = None
    montant_max: Optional[float] = None
    montant_fixe: Optional[float] = None
    
    taux_min: Optional[float] = None
    taux_max: Optional[float] = None
    
    plafond: Optional[float] = None
    plancher: Optional[float] = None
    
    montant_par_unite: Optional[float] = None
    unite: Optional[str] = None
    
    description: Optional[str] = None
    conditions_particulieres: Optional[str] = None


class AideAgricoleV2(BaseModel):
    """Modèle V2 optimisé pour les aides agricoles"""
    
    aid_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    id_externe: Optional[str] = None
    
    titre: str
    description: str = ""
    organisme: str
    programme: str = ""
    
    source: str = "manual"
    source_url: str = ""
    derniere_maj: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    date_limite_depot: Optional[str] = None
    
    statut: str = "active"
    
    criteres: CriteresEligibilite = Field(default_factory=CriteresEligibilite)
    montant: MontantAide = Field(default_factory=MontantAide)
    
    conditions_eligibilite: str = ""
    demarche: str = ""
    contact: Optional[str] = None
    
    lien_officiel: str = ""
    lien_dossier: Optional[str] = None
    
    confiance: float = 1.0
    tags: List[str] = Field(default_factory=list)
    
    raw_data: Optional[Dict[str, Any]] = None


# ============ MODÈLE PROFIL AGRICULTEUR AVEC VALIDATEURS ============

class ProfilAgriculteur(BaseModel):
    """Profil complet d'un agriculteur pour le matching"""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False
    )
    
    profil_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    region: str
    departement: str
    commune: Optional[str] = None
    code_postal: Optional[str] = None
    zone_montagne: bool = False
    zone_defavorisee: bool = False
    
    age: Optional[int] = None
    jeune_agriculteur: bool = False
    premiere_installation: bool = False
    niveau_formation: Optional[str] = None
    
    statut_juridique: StatutJuridique
    annee_installation: Optional[int] = None
    
    sau_totale: float = Field(ge=0)
    sau_bio: float = Field(default=0, ge=0)
    sau_en_conversion: float = Field(default=0, ge=0)
    
    # ✅ AVEC VALIDATEUR PERSONNALISÉ
    productions: List[TypeProduction] = Field(default_factory=list)
    production_principale: Optional[TypeProduction] = None
    cultures_details: Optional[Dict[str, float]] = None
    
    a_elevage: bool = False
    nb_bovins: int = Field(default=0, ge=0)
    nb_ovins: int = Field(default=0, ge=0)
    nb_caprins: int = Field(default=0, ge=0)
    nb_porcins: int = Field(default=0, ge=0)
    nb_volailles: int = Field(default=0, ge=0)
    
    labels: List[str] = Field(default_factory=list)
    label_bio: bool = False
    label_hve: bool = False
    
    chiffre_affaires: Optional[float] = Field(default=None, ge=0)
    en_difficulte: bool = False
    
    # ✅ AVEC VALIDATEUR PERSONNALISÉ
    projets_en_cours: List[TypeProjet] = Field(default_factory=list)
    projets_collectifs: bool = False
    budget_projet: Optional[float] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # ✅ VALIDATEUR POUR PRODUCTIONS
    @field_validator('productions', mode='before')
    @classmethod
    def validate_productions(cls, v):
        """Accepte les Enums TypeProduction déjà créés OU les strings"""
        if not v:
            return []
        
        result = []
        for item in v:
            if isinstance(item, TypeProduction):
                # Déjà un Enum, on garde tel quel
                result.append(item)
            elif isinstance(item, str):
                # String, on cherche l'Enum correspondant
                for prod_enum in TypeProduction:
                    if prod_enum.value == item:
                        result.append(prod_enum)
                        break
        
        return result
    
    # ✅ VALIDATEUR POUR PROJETS
    @field_validator('projets_en_cours', mode='before')
    @classmethod
    def validate_projets(cls, v):
        """Accepte les Enums TypeProjet déjà créés OU les strings"""
        if not v:
            return []
        
        result = []
        for item in v:
            if isinstance(item, TypeProjet):
                # Déjà un Enum, on garde tel quel
                result.append(item)
            elif isinstance(item, str):
                # String, on cherche l'Enum correspondant
                for proj_enum in TypeProjet:
                    if proj_enum.value == item:
                        result.append(proj_enum)
                        break
        
        return result


class DetailCritere(BaseModel):
    """Détail d'un critère de matching"""
    nom: str
    valide: bool
    bloquant: bool = False
    points: float = 0.0
    points_max: float = 0.0
    explication: str = ""


class ResultatMatching(BaseModel):
    """Résultat du matching entre un profil et une aide"""
    
    aide_id: str
    profil_id: str
    
    score: float = Field(ge=0.0, le=100.0)
    eligible: bool
    
    details_criteres: List[DetailCritere] = Field(default_factory=list)
    
    criteres_valides: int = 0
    criteres_total: int = 0
    criteres_bloquants_ko: List[str] = Field(default_factory=list)
    
    montant_estime_min: Optional[float] = None
    montant_estime_max: Optional[float] = None
    
    resume: str = ""
    recommandations: List[str] = Field(default_factory=list)
    
    date_matching: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @field_validator('score')
    @classmethod
    def score_valide(cls, v: float) -> float:
        return round(v, 2)
