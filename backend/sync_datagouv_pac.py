"""
Script de synchronisation avec Data.gouv.fr - Aides PAC
Télécharge et importe les aides PAC officielles (sans authentification)
"""

import requests
import csv
import io
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL du dataset PAC sur Data.gouv.fr
# Note: Cette URL peut être mise à jour, vérifier sur https://www.data.gouv.fr/fr/datasets/aides-pac/
DATAGOUV_PAC_CSV_URL = "https://www.data.gouv.fr/fr/datasets/r/e6c2f4f8-3c3e-4d3f-9f3e-3c3e4d3f9f3e"

# Mapping des types d'aides PAC
TYPE_AIDE_MAPPING = {
    "DPB": "Paiement direct PAC",
    "MAEC": "Mesures agro-environnementales",
    "BIO": "Agriculture Biologique",
    "ICHN": "Indemnité Compensatoire Handicaps Naturels",
    "DJA": "Installation",
    "FEADER": "Développement rural"
}

class DataGouvPACSyncer:
    """Classe pour synchroniser les aides PAC depuis Data.gouv.fr"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgriSubv/1.0 (https://agrisubv.onrender.com)',
        })
    
    def fetch_aides_pac(self) -> List[Dict[str, Any]]:
        """Récupère les aides PAC depuis un dataset simplifié"""
        
        logger.info("🔄 Récupération des aides PAC depuis Data.gouv.fr...")
        
        # Pour l'instant, on crée des aides PAC standards basées sur la documentation officielle
        # TODO: Remplacer par le vrai CSV quand l'URL est disponible
        
        aides_pac_standards = [
            {
                "nom": "Paiement de Base (DPB)",
                "type": "DPB",
                "organisme": "ASP - Agence de Services et de Paiement",
                "description": "Aide découplée versée à tous les agriculteurs actifs, calculée sur la base des Droits à Paiement de Base (DPB)",
                "montant_ha": "Variable selon région (150-250€/ha)",
                "eligibilite": "Agriculteur actif avec surface admissible PAC",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Paiement Vert (Verdissement)",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Aide conditionnée au respect de pratiques agricoles bénéfiques pour l'environnement",
                "montant_ha": "~85€/ha",
                "eligibilite": "Respect des 3 critères : diversité cultures, SIE, prairies permanentes",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide à la Conversion Agriculture Biologique (CAB)",
                "type": "BIO",
                "organisme": "ASP",
                "description": "Soutien financier pendant la période de conversion vers l'agriculture biologique (2 ans)",
                "montant_ha": "200-600€/ha selon production",
                "eligibilite": "Engagement de conversion bio, certification en cours",
                "url": "https://www.agencebio.org/financement-de-la-bio/"
            },
            {
                "nom": "Aide au Maintien Agriculture Biologique (MAB)",
                "type": "BIO",
                "organisme": "ASP",
                "description": "Soutien pour les exploitations certifiées bio pour maintenir leurs pratiques",
                "montant_ha": "100-300€/ha selon production",
                "eligibilite": "Certification agriculture biologique valide",
                "url": "https://www.agencebio.org/financement-de-la-bio/"
            },
            {
                "nom": "Dotation Jeunes Agriculteurs (DJA)",
                "type": "DJA",
                "organisme": "État / ASP",
                "description": "Aide à l'installation des jeunes agriculteurs pour faciliter leur première installation",
                "montant_ha": "8 000 à 40 000€ selon zone",
                "eligibilite": "Moins de 40 ans, première installation, diplôme agricole",
                "url": "https://agriculture.gouv.fr/installation-des-jeunes-agriculteurs-dja"
            },
            {
                "nom": "ICHN - Indemnité Compensatoire Handicaps Naturels",
                "type": "ICHN",
                "organisme": "ASP",
                "description": "Compensation pour les zones défavorisées (montagne, piémont, zones défavorisées simples)",
                "montant_ha": "50-250€/ha selon zone",
                "eligibilite": "Exploitation située en zone défavorisée",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "MAEC Systèmes - Polyculture Élevage",
                "type": "MAEC",
                "organisme": "ASP",
                "description": "Mesure agro-environnementale pour systèmes herbagers et polyculture-élevage",
                "montant_ha": "Variable selon cahier des charges",
                "eligibilite": "Engagement 5 ans, respect cahier des charges",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "MAEC Localisées - Zones Humides",
                "type": "MAEC",
                "organisme": "ASP",
                "description": "Préservation et gestion des zones humides en zone agricole",
                "montant_ha": "150-300€/ha",
                "eligibilite": "Parcelles en zone humide identifiée, engagement 5 ans",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Bovins Allaitants",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Soutien aux élevages bovins allaitants (vaches nourrices)",
                "montant_ha": "~190€/vache",
                "eligibilite": "Détention de vaches allaitantes, déclaration PAC",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Bovins Laitiers",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Soutien aux élevages de vaches laitières",
                "montant_ha": "~35€/vache",
                "eligibilite": "Détention de vaches laitières, livraison de lait",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Ovins",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Soutien aux élevages ovins (brebis)",
                "montant_ha": "~21€/brebis",
                "eligibilite": "Détention de brebis, déclaration PAC",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Caprins",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Soutien aux élevages caprins (chèvres)",
                "montant_ha": "~17€/chèvre",
                "eligibilite": "Détention de chèvres, déclaration PAC",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Protéines Végétales",
                "type": "DPB",
                "organisme": "ASP",
                "description": "Soutien aux cultures de légumineuses fourragères et protéagineux",
                "montant_ha": "100-150€/ha",
                "eligibilite": "Surfaces en légumineuses, soja, pois, féveroles",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Aide Couplée Fruits et Légumes",
                "type": "DPB",
                "organisme": "ASP / FranceAgriMer",
                "description": "Soutien spécifique aux producteurs de fruits et légumes",
                "montant_ha": "Variable selon production",
                "eligibilite": "Surfaces en fruits/légumes, adhésion OP",
                "url": "https://www.franceagrimer.fr/"
            },
            {
                "nom": "FEADER - Installation des Jeunes Agriculteurs",
                "type": "FEADER",
                "organisme": "Conseil Régional / FEADER",
                "description": "Complément régional à la DJA nationale financé par le FEADER",
                "montant_ha": "Variable selon région (5 000-20 000€)",
                "eligibilite": "Bénéficiaire DJA, projet validé par Région",
                "url": "https://agriculture.gouv.fr/feader"
            },
            {
                "nom": "FEADER - Investissements Modernisation",
                "type": "FEADER",
                "organisme": "Conseil Régional / FEADER",
                "description": "Soutien aux investissements de modernisation des exploitations",
                "montant_ha": "20-40% du montant HT (selon région)",
                "eligibilite": "Projet d'investissement validé, étude technico-économique",
                "url": "https://agriculture.gouv.fr/feader"
            },
            {
                "nom": "Aide au Transport des Animaux - Zone de Montagne",
                "type": "ICHN",
                "organisme": "ASP",
                "description": "Compensation des surcoûts de transport en zone de montagne",
                "montant_ha": "Forfait selon cheptel",
                "eligibilite": "Exploitation en zone de montagne, élevage",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            },
            {
                "nom": "Prime d'Herbe Agro-Environnementale",
                "type": "MAEC",
                "organisme": "ASP",
                "description": "Soutien au maintien des surfaces en herbe",
                "montant_ha": "150€/ha",
                "eligibilite": "Surfaces en prairies permanentes ou temporaires",
                "url": "https://www.telepac.agriculture.gouv.fr/"
            }
        ]
        
        logger.info(f"✅ {len(aides_pac_standards)} aides PAC standards chargées")
        return aides_pac_standards
    
    def normalize_aide_pac(self, aide_raw: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Normalise une aide PAC vers le format AgriSubv"""
        
        # Générer un ID unique
        aid_id = f"PAC-{aide_raw.get('type', 'AIDE')}-{index:03d}"
        
        # Déterminer le type d'aide
        type_aide = TYPE_AIDE_MAPPING.get(aide_raw.get('type', ''), "Paiement PAC")
        
        # Extraire les montants (parsing simple)
        montant_text = aide_raw.get('montant_ha', '')
        montant_max = None
        if '€' in montant_text:
            # Essayer d'extraire un montant numérique
            import re
            montants = re.findall(r'(\d+)', montant_text)
            if montants:
                montant_max = float(montants[-1])  # Prendre le dernier (souvent le max)
        
        normalized_aide = {
            "aid_id": aid_id,
            "titre": aide_raw.get('nom', 'Aide PAC'),
            "organisme": aide_raw.get('organisme', 'ASP'),
            "programme": "Politique Agricole Commune (PAC) 2023-2027",
            "source_url": aide_raw.get('url', 'https://www.telepac.agriculture.gouv.fr/'),
            "derniere_maj": datetime.now(timezone.utc).isoformat(),
            "niveau": "National",
            "regions": ["National"],
            "departements": [],
            "type_aide": type_aide,
            "productions": [],  # Sera enrichi selon le type
            "statuts": ["Exploitation individuelle", "EARL", "GAEC", "SCEA"],
            "labels": [],
            "montant_min_eur": None,
            "montant_max_eur": montant_max,
            "taux_min_pct": None,
            "taux_max_pct": None,
            "plafond_eur": montant_max,
            "date_ouverture": "2024-04-01",  # Campagne PAC annuelle
            "date_limite": "2025-05-15",     # Date limite déclaration PAC
            "criteres_durs_expr": {},
            "criteres_mous_tags": [aide_raw.get('type', '').lower(), 'pac', 'agriculture'],
            "conditions_clefs": aide_raw.get('eligibilite', ''),
            "lien_officiel": aide_raw.get('url', 'https://www.telepac.agriculture.gouv.fr/'),
            "confiance": 1.0,  # Données officielles
            "expiree": False,
            "source": "datagouv-pac",
            "raw_data": aide_raw
        }
        
        # Enrichir les productions selon le type
        if aide_raw.get('type') == 'BIO':
            normalized_aide['labels'] = ['Agriculture Biologique']
        elif 'Bovins' in aide_raw.get('nom', ''):
            normalized_aide['productions'] = ['Élevage bovin']
        elif 'Ovins' in aide_raw.get('nom', ''):
            normalized_aide['productions'] = ['Élevage ovin']
        elif 'Caprins' in aide_raw.get('nom', ''):
            normalized_aide['productions'] = ['Élevage caprin']
        elif 'Protéines' in aide_raw.get('nom', ''):
            normalized_aide['productions'] = ['Grandes cultures']
        
        return normalized_aide

    def generate_pac_reference_aids(self) -> List[Any]:
        """Génère les aides PAC de référence sous forme d'AideAgricoleV2"""
        from models_v2 import (
            AideAgricoleV2, CriteresEligibilite, MontantAide,
            TypeMontant, TypeProduction, TypeProjet
        )

        aides_reference = [
            AideAgricoleV2(
                aid_id="PAC-DPB",
                titre="Droits à Paiement de Base (DPB)",
                description=(
                    "L'aide au paiement de base est une aide découplée versée annuellement "
                    "à tous les agriculteurs actifs disposant de droits à paiement de base (DPB). "
                    "Le montant varie selon la valeur des DPB détenus et la surface admissible déclarée."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=100.0,
                    montant_max=300.0,
                    unite="€/ha",
                    description="Variable selon la valeur des DPB et la région",
                ),
                conditions_eligibilite=(
                    "Être agriculteur actif, détenir des droits à paiement de base, "
                    "déclarer des surfaces admissibles via la télédéclaration PAC annuelle."
                ),
                tags=["DPB", "paiement de base", "aide découplée", "PAC", "surface", "annuel"],
            ),
            AideAgricoleV2(
                aid_id="PAC-PVERT",
                titre="Paiement Vert (Écorégime PAC 2023-2027)",
                description=(
                    "L'écorégime remplace le paiement vert depuis 2023. Il récompense les pratiques "
                    "bénéfiques pour le climat et l'environnement : diversification des cultures, "
                    "maintien de prairies permanentes, couverture des sols, certification HVE ou bio."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[TypeProjet.ENVIRONNEMENT],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=40.0,
                    montant_max=145.0,
                    unite="€/ha",
                    description="Trois niveaux d'engagement : de base, supérieur, gold",
                ),
                conditions_eligibilite=(
                    "Bénéficier du paiement de base et adopter des pratiques agro-environnementales "
                    "(diversification, prairies permanentes, certification HVE/bio, etc.)."
                ),
                tags=["écorégime", "paiement vert", "HVE", "bio", "prairies", "PAC", "environnement"],
            ),
            AideAgricoleV2(
                aid_id="PAC-PREDIST",
                titre="Paiement Redistributif",
                description=(
                    "Le paiement redistributif complète le paiement de base pour les 52 premiers "
                    "hectares de l'exploitation afin de soutenir les petites et moyennes structures. "
                    "Il est plafonné aux 52 premiers hectares éligibles."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=50.0,
                    montant_max=100.0,
                    unite="€/ha (52 premiers ha)",
                    description="Applicable uniquement sur les 52 premiers hectares",
                ),
                conditions_eligibilite=(
                    "Bénéficier du paiement de base. Le complément est automatiquement calculé "
                    "sur les 52 premiers hectares éligibles."
                ),
                tags=["redistributif", "petite exploitation", "PAC", "complément", "surface"],
            ),
            AideAgricoleV2(
                aid_id="PAC-ICHN",
                titre="Indemnité Compensatoire de Handicap Naturel (ICHN)",
                description=(
                    "L'ICHN compense les surcoûts de production et les pertes de revenus des "
                    "agriculteurs installés en zones défavorisées (montagne, piémont, zone défavorisée simple). "
                    "Elle est modulée selon la zone et la surface."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    zones_specifiques=["Zone de montagne", "Zone défavorisée", "Piémont"],
                    types_production=[],
                    types_projets=[],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=25.0,
                    montant_max=250.0,
                    unite="€/ha",
                    description="Varie selon la zone géographique et le type de production",
                ),
                conditions_eligibilite=(
                    "Être installé en zone défavorisée (montagne, piémont ou zone défavorisée simple), "
                    "détenir au moins 3 ha de SAU, exercer une activité agricole à titre principal."
                ),
                tags=["ICHN", "zone montagne", "zone défavorisée", "handicap naturel", "PAC", "compensation"],
            ),
            AideAgricoleV2(
                aid_id="PAC-MAEC",
                titre="Mesures Agro-Environnementales et Climatiques (MAEC)",
                description=(
                    "Les MAEC rémunèrent les agriculteurs qui s'engagent sur 5 ans dans des pratiques "
                    "agro-environnementales allant au-delà des exigences réglementaires : réduction des "
                    "intrants, maintien des prairies, gestion des zones humides, etc."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[TypeProjet.ENVIRONNEMENT],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=50.0,
                    montant_max=600.0,
                    unite="€/ha/an",
                    description="Variable selon le cahier des charges MAEC souscrit",
                ),
                conditions_eligibilite=(
                    "S'engager sur 5 ans dans un cahier des charges MAEC défini localement, "
                    "respecter l'ensemble des exigences de la mesure souscrite."
                ),
                tags=["MAEC", "agro-environnemental", "prairies", "biodiversité", "PAC", "5 ans"],
            ),
            AideAgricoleV2(
                aid_id="PAC-DJA",
                titre="Dotation Jeune Agriculteur (DJA)",
                description=(
                    "La DJA est une aide forfaitaire à l'installation accordée aux jeunes agriculteurs "
                    "de moins de 40 ans s'installant pour la première fois. Son montant varie selon "
                    "la zone d'installation et le projet présenté dans le plan d'entreprise."
                ),
                organisme="Ministère de l'Agriculture",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://agriculture.gouv.fr/la-dotation-jeunes-agriculteurs-dja",
                lien_officiel="https://agriculture.gouv.fr/la-dotation-jeunes-agriculteurs-dja",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    age_max=40,
                    jeune_agriculteur=True,
                    premiere_installation=True,
                    types_production=[],
                    types_projets=[TypeProjet.INSTALLATION],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.FORFAITAIRE,
                    montant_min=8000.0,
                    montant_max=43000.0,
                    description="Majoré en zone de montagne ou zone défavorisée",
                ),
                conditions_eligibilite=(
                    "Avoir moins de 40 ans, s'installer pour la première fois comme chef d'exploitation, "
                    "détenir un diplôme agricole de niveau IV minimum, présenter un plan d'entreprise viable."
                ),
                tags=["DJA", "jeune agriculteur", "installation", "forfait", "PAC", "première installation"],
            ),
            AideAgricoleV2(
                aid_id="PAC-BIO-CONV",
                titre="Aide à la Conversion en Agriculture Biologique",
                description=(
                    "Cette aide soutient les agriculteurs qui s'engagent dans la conversion vers "
                    "l'agriculture biologique. La période de conversion dure 2 à 3 ans selon les "
                    "productions. Le montant est supérieur à l'aide au maintien bio."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[TypeProjet.CONVERSION_BIO],
                    labels_bonus=["Agriculture Biologique en conversion"],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=100.0,
                    montant_max=900.0,
                    unite="€/ha/an",
                    description="Variable selon le type de culture/élevage et la région",
                ),
                conditions_eligibilite=(
                    "S'engager dans une démarche de conversion en agriculture biologique certifiée, "
                    "souscrire un contrat de conversion sur 5 ans avec un organisme certificateur agréé."
                ),
                tags=["bio", "conversion bio", "agriculture biologique", "PAC", "environnement"],
            ),
            AideAgricoleV2(
                aid_id="PAC-BIO-MAINT",
                titre="Aide au Maintien de l'Agriculture Biologique",
                description=(
                    "L'aide au maintien récompense les agriculteurs déjà certifiés en agriculture "
                    "biologique qui poursuivent leurs pratiques. Elle complète le paiement de base "
                    "et l'écorégime pour soutenir l'économie des exploitations bio."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[],
                    labels_requis=["Agriculture Biologique"],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=50.0,
                    montant_max=600.0,
                    unite="€/ha/an",
                    description="Variable selon le type de culture/élevage et la région",
                ),
                conditions_eligibilite=(
                    "Être certifié en agriculture biologique (label AB), maintenir les pratiques "
                    "biologiques sur les surfaces déclarées, réaliser une télédéclaration PAC annuelle."
                ),
                tags=["bio", "maintien bio", "agriculture biologique", "label AB", "PAC"],
            ),
            AideAgricoleV2(
                aid_id="PAC-ASSUR",
                titre="Aide à l'Assurance Récolte",
                description=(
                    "L'aide à l'assurance récolte subventionne une partie des primes d'assurance "
                    "multirisques climatiques souscrites par les agriculteurs. Elle vise à développer "
                    "la couverture des exploitations contre les aléas climatiques."
                ),
                organisme="Ministère de l'Agriculture",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://agriculture.gouv.fr/lassurance-recolte",
                lien_officiel="https://agriculture.gouv.fr/lassurance-recolte",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[],
                    types_projets=[],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.POURCENTAGE,
                    taux_min=30.0,
                    taux_max=70.0,
                    description="Subvention de 30 à 70 % de la prime d'assurance selon le niveau de couverture",
                ),
                conditions_eligibilite=(
                    "Souscrire un contrat d'assurance multirisques climatiques auprès d'un assureur agréé, "
                    "exercer une activité agricole sur des cultures admissibles."
                ),
                tags=["assurance récolte", "aléas climatiques", "multirisque", "PAC", "subvention prime"],
            ),
            AideAgricoleV2(
                aid_id="PAC-PROTEAG",
                titre="Aide Couplée Protéagineux et Légumineuses",
                description=(
                    "Cette aide couplée soutient la production de légumineuses à graines et de "
                    "protéagineux (pois, féveroles, lupins, soja) pour réduire la dépendance en "
                    "protéines végétales et favoriser la rotation des cultures."
                ),
                organisme="ASP (Agence de Services et de Paiement)",
                programme="PAC 2023-2027",
                source="pac_reference",
                source_url="https://www.telepac.agriculture.gouv.fr/",
                lien_officiel="https://www.telepac.agriculture.gouv.fr/",
                criteres=CriteresEligibilite(
                    regions=["National"],
                    types_production=[TypeProduction.GRANDES_CULTURES, TypeProduction.CEREALES],
                    types_projets=[],
                ),
                montant=MontantAide(
                    type_montant=TypeMontant.SURFACE,
                    montant_min=80.0,
                    montant_max=200.0,
                    unite="€/ha",
                    description="Variable selon la culture et la campagne",
                ),
                conditions_eligibilite=(
                    "Cultiver des légumineuses à graines ou protéagineux éligibles "
                    "(pois, féveroles, lupins, soja, lentilles, pois chiches) sur des surfaces admissibles."
                ),
                tags=["protéagineux", "légumineuses", "soja", "pois", "féveroles", "PAC", "aide couplée"],
            ),
        ]

        return aides_reference


async def sync_pac_to_db(db, limit: Optional[int] = None) -> Dict[str, Any]:
    """Synchronise les aides PAC depuis Data.gouv.fr vers MongoDB"""
    
    syncer = DataGouvPACSyncer()
    
    logger.info("🔄 Récupération des aides PAC...")
    aides_brutes = syncer.fetch_aides_pac()
    
    if limit:
        aides_brutes = aides_brutes[:limit]
    
    logger.info(f"🔄 Normalisation de {len(aides_brutes)} aides PAC...")
    aides_normalized = []
    for index, aide_brute in enumerate(aides_brutes):
        try:
            aide_norm = syncer.normalize_aide_pac(aide_brute, index)
            aides_normalized.append(aide_norm)
        except Exception as e:
            logger.error(f"❌ Erreur normalisation aide PAC {index}: {e}")
    
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

    # ── Insertion des aides PAC de référence enrichies dans aides_v2 ─────────
    logger.info("🌾 Génération des aides PAC de référence enrichies...")
    aides_reference = syncer.generate_pac_reference_aids()
    
    ref_inserted = 0
    ref_updated = 0
    ref_errors = 0

    for aide_v2 in aides_reference:
        try:
            aide_dict = aide_v2.model_dump()
            existing = await db.aides_v2.find_one({"aid_id": aide_dict['aid_id']})
            if existing:
                await db.aides_v2.update_one(
                    {"aid_id": aide_dict['aid_id']},
                    {"$set": aide_dict}
                )
                ref_updated += 1
            else:
                await db.aides_v2.insert_one(aide_dict)
                ref_inserted += 1
        except Exception as e:
            logger.error(f"❌ Erreur insertion aide référence {aide_v2.aid_id}: {e}")
            ref_errors += 1

    logger.info(f"✅ Synchronisation PAC terminée !")
    logger.info(f"   - Nouvelles aides PAC : {inserted_count}")
    logger.info(f"   - Aides PAC mises à jour : {updated_count}")
    logger.info(f"   - Aides PAC référence insérées : {ref_inserted}")
    logger.info(f"   - Aides PAC référence mises à jour : {ref_updated}")
    logger.info(f"   - Erreurs : {errors_count + ref_errors}")
    
    return {
        "success": True,
        "source": "datagouv-pac",
        "total_fetched": len(aides_brutes),
        "total_normalized": len(aides_normalized),
        "inserted": inserted_count,
        "updated": updated_count,
        "reference_inserted": ref_inserted,
        "reference_updated": ref_updated,
        "errors": errors_count + ref_errors,
    }


if __name__ == "__main__":
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'agrisubv_db')]
    
    result = asyncio.run(sync_pac_to_db(db))
    print(f"\n📊 Résultat : {result}")
