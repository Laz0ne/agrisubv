"""
Modèles de données V2 pour AgriSubv
Version optimisée pour gérer 1000+ aides avec critères enrichis
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
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
    
    # Critères géographiques
    regions: List[str] = Field(default_factory=list, description="Régions éligibles")
    departements: List[str] = Field(default_factory=list, description="Départements éligibles")
    zones_specifiques: List[str] = Field(default_factory=list, description="Zones spécifiques (montagne, défavorisée, etc.)")
    
    # Critères démographiques
    age_min: Optional[int] = Field(None, description="Âge minimum de l'exploitant")
    age_max: Optional[int] = Field(None, description="Âge maximum de l'exploitant")
    jeune_agriculteur: Optional[bool] = Field(None, description="Réservé aux jeunes agriculteurs")
    
    # Critères d'exploitation
    superficie_min: Optional[float] = Field(None, description="Superficie minimum en hectares")
    superficie_max: Optional[float] = Field(None, description="Superficie maximum en hectares")
    cheptel_min: Optional[int] = Field(None, description="Nombre minimum d'animaux")
    cheptel_max: Optional[int] = Field(None, description="Nombre maximum d'animaux")
    
    # Critères économiques
    ca_min: Optional[float] = Field(None, description="Chiffre d'affaires minimum")
    ca_max: Optional[float] = Field(None, description="Chiffre d'affaires maximum")
    
    # Critères de production et projet
    types_production: List[TypeProduction] = Field(default_factory=list, description="Types de production éligibles")
    types_projets: List[TypeProjet] = Field(default_factory=list, description="Types de projets éligibles")
    
    # Critères de statut et labels
    statuts_juridiques: List[StatutJuridique] = Field(default_factory=list, description="Statuts juridiques acceptés")
    labels_requis: List[str] = Field(default_factory=list, description="Labels requis (Bio, HVE, etc.)")
    labels_bonus: List[str] = Field(default_factory=list, description="Labels donnant des points bonus")
    
    # Critères additionnels
    premiere_installation: Optional[bool] = Field(None, description="Première installation requise")
    en_difficulte: Optional[bool] = Field(None, description="Exploitation en difficulté")
    projets_collectifs: Optional[bool] = Field(None, description="Projets collectifs uniquement")


class MontantAide(BaseModel):
    """Montant et modalités de l'aide"""
    
    type_montant: TypeMontant = Field(TypeMontant.FORFAITAIRE, description="Type de montant")
    
    # Montants forfaitaires
    montant_min: Optional[float] = Field(None, description="Montant minimum en euros")
    montant_max: Optional[float] = Field(None, description="Montant maximum en euros")
    montant_fixe: Optional[float] = Field(None, description="Montant fixe en euros")
    
    # Pourcentages
    taux_min: Optional[float] = Field(None, description="Taux minimum en pourcentage")
    taux_max: Optional[float] = Field(None, description="Taux maximum en pourcentage")
    
    # Plafonds
    plafond: Optional[float] = Field(None, description="Plafond en euros")
    plancher: Optional[float] = Field(None, description="Plancher en euros")
    
    # Par unité (surface, tête, etc.)
    montant_par_unite: Optional[float] = Field(None, description="Montant par unité (ha, tête, etc.)")
    unite: Optional[str] = Field(None, description="Unité de mesure (ha, tête, kW, etc.)")
    
    # Informations complémentaires
    description: Optional[str] = Field(None, description="Description du calcul du montant")
    conditions_particulieres: Optional[str] = Field(None, description="Conditions particulières")


# ============ MODÈLE PRINCIPAL ============

class AideAgricoleV2(BaseModel):
    """Modèle V2 optimisé pour les aides agricoles"""
    
    # Identifiants
    aid_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique")
    id_externe: Optional[str] = Field(None, description="ID dans la source externe")
    
    # Informations de base
    titre: str = Field(..., description="Titre de l'aide")
    description: str = Field("", description="Description détaillée")
    organisme: str = Field(..., description="Organisme porteur")
    programme: str = Field("", description="Programme rattaché")
    
    # Source et métadonnées
    source: str = Field("manual", description="Source de l'aide (manual, aides_territoires, datagouv_pac)")
    source_url: str = Field("", description="URL de la source")
    derniere_maj: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Dates importantes
    date_debut: Optional[str] = Field(None, description="Date de début de validité")
    date_fin: Optional[str] = Field(None, description="Date de fin de validité")
    date_limite_depot: Optional[str] = Field(None, description="Date limite de dépôt")
    
    # Statut
    statut: str = Field("active", description="Statut de l'aide (active, inactive, expiree)")
    
    # Critères et montant
    criteres: CriteresEligibilite = Field(default_factory=CriteresEligibilite)
    montant: MontantAide = Field(default_factory=MontantAide)
    
    # Conditions et informations complémentaires
    conditions_eligibilite: str = Field("", description="Conditions d'éligibilité en texte")
    demarche: str = Field("", description="Démarche à suivre")
    contact: Optional[str] = Field(None, description="Contact pour l'aide")
    
    # Liens
    lien_officiel: str = Field("", description="Lien vers la page officielle")
    lien_dossier: Optional[str] = Field(None, description="Lien vers le dossier de demande")
    
    # Métadonnées de qualité
    confiance: float = Field(1.0, ge=0.0, le=1.0, description="Niveau de confiance dans les données")
    tags: List[str] = Field(default_factory=list, description="Tags pour recherche et matching")
    
    # Données brutes (pour debug)
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Données brutes de la source")
    
    @field_validator('titre')
    @classmethod
    def titre_non_vide(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le titre ne peut pas être vide")
        return v.strip()
    
    @field_validator('statut')
    @classmethod
    def statut_valide(cls, v: str) -> str:
        statuts_valides = ['active', 'inactive', 'expiree']
        if v not in statuts_valides:
            raise ValueError(f"Statut doit être parmi: {statuts_valides}")
        return v
    
    @field_validator('confiance')
    @classmethod
    def confiance_entre_0_et_1(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("La confiance doit être entre 0.0 et 1.0")
        return v


# ============ MODÈLE PROFIL AGRICULTEUR ============

class ProfilAgriculteur(BaseModel):
    """Profil complet d'un agriculteur pour le matching"""
    
    # Identifiant
    profil_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Informations géographiques
    region: str = Field(..., description="Région de l'exploitation")
    departement: str = Field(..., description="Département")
    commune: Optional[str] = Field(None, description="Commune")
    code_postal: Optional[str] = Field(None, description="Code postal")
    zone_montagne: bool = Field(False, description="Située en zone de montagne")
    zone_defavorisee: bool = Field(False, description="Située en zone défavorisée")
    
    # Informations exploitant
    age: Optional[int] = Field(None, description="Âge de l'exploitant")
    jeune_agriculteur: bool = Field(False, description="Jeune agriculteur (< 40 ans)")
    premiere_installation: bool = Field(False, description="Première installation")
    niveau_formation: Optional[str] = Field(None, description="Niveau de formation agricole")
    
    # Informations exploitation
    statut_juridique: StatutJuridique = Field(..., description="Statut juridique")
    annee_installation: Optional[int] = Field(None, description="Année d'installation")
    
    # Surfaces et production
    sau_totale: float = Field(..., ge=0, description="Surface agricole utile totale (ha)")
    sau_bio: float = Field(0, ge=0, description="Surface en agriculture biologique (ha)")
    sau_en_conversion: float = Field(0, ge=0, description="Surface en conversion bio (ha)")
    
    # Productions
    productions: List[TypeProduction] = Field(default_factory=list, description="Types de production")
    production_principale: Optional[TypeProduction] = Field(None, description="Production principale")
    cultures_details: Optional[Dict[str, float]] = Field(None, description="Détail des surfaces par culture")
    
    # Élevage
    a_elevage: bool = Field(False, description="Possède un élevage")
    nb_bovins: int = Field(0, ge=0, description="Nombre de bovins")
    nb_ovins: int = Field(0, ge=0, description="Nombre d'ovins")
    nb_caprins: int = Field(0, ge=0, description="Nombre de caprins")
    nb_porcins: int = Field(0, ge=0, description="Nombre de porcins")
    nb_volailles: int = Field(0, ge=0, description="Nombre de volailles")
    
    # Labels et certifications
    labels: List[str] = Field(default_factory=list, description="Labels et certifications")
    label_bio: bool = Field(False, description="Certifié Agriculture Biologique")
    label_hve: bool = Field(False, description="Certifié Haute Valeur Environnementale")
    
    # Économie
    chiffre_affaires: Optional[float] = Field(None, ge=0, description="Chiffre d'affaires annuel")
    en_difficulte: bool = Field(False, description="Exploitation en difficulté")
    
    # Projets et investissements
    projets_en_cours: List[TypeProjet] = Field(default_factory=list, description="Projets en cours ou envisagés")
    projets_collectifs: bool = Field(False, description="Participe à des projets collectifs")
    budget_projet: Optional[float] = Field(None, description="Budget du projet envisagé")
    
    # Métadonnées
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @field_validator('sau_bio', 'sau_en_conversion')
    @classmethod
    def surface_bio_coherente(cls, v: float, info) -> float:
        if 'sau_totale' in info.data and v > info.data['sau_totale']:
            raise ValueError("La surface bio/conversion ne peut pas dépasser la SAU totale")
        return v


# ============ MODÈLE RÉSULTAT MATCHING ============

class DetailCritere(BaseModel):
    """Détail d'un critère de matching"""
    nom: str = Field(..., description="Nom du critère")
    valide: bool = Field(..., description="Critère validé ou non")
    bloquant: bool = Field(False, description="Critère bloquant")
    points: float = Field(0.0, description="Points obtenus")
    points_max: float = Field(0.0, description="Points maximum")
    explication: str = Field("", description="Explication détaillée")


class ResultatMatching(BaseModel):
    """Résultat du matching entre un profil et une aide"""
    
    # Identifiants
    aide_id: str = Field(..., description="ID de l'aide")
    profil_id: str = Field(..., description="ID du profil")
    
    # Score global
    score: float = Field(..., ge=0.0, le=100.0, description="Score global de matching (0-100)")
    eligible: bool = Field(..., description="Éligible ou non (score >= seuil)")
    
    # Détails par catégorie de critères
    details_criteres: List[DetailCritere] = Field(default_factory=list)
    
    # Catégorisation
    criteres_valides: int = Field(0, description="Nombre de critères validés")
    criteres_total: int = Field(0, description="Nombre total de critères")
    criteres_bloquants_ko: List[str] = Field(default_factory=list, description="Critères bloquants non validés")
    
    # Montant estimé
    montant_estime_min: Optional[float] = Field(None, description="Montant minimum estimé")
    montant_estime_max: Optional[float] = Field(None, description="Montant maximum estimé")
    
    # Résumé et recommandations
    resume: str = Field("", description="Résumé du matching")
    recommandations: List[str] = Field(default_factory=list, description="Recommandations pour améliorer l'éligibilité")
    
    # Métadonnées
    date_matching: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @field_validator('score')
    @classmethod
    def score_valide(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError("Le score doit être entre 0 et 100")
        return round(v, 2)
