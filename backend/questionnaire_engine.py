"""
Moteur de questionnaire adaptatif pour AgriSubv.
Génère dynamiquement les questions les plus discriminantes
à partir des critères réels des aides en base MongoDB.
"""

import math
import uuid
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from models_v2 import (
    AideAgricoleV2,
    CriteresEligibilite,
    ProfilAgriculteur,
    StatutJuridique,
    TypeProduction,
    TypeProjet,
    StatutMatching,
)
from matching_engine import MatchingEngine

logger = logging.getLogger(__name__)


# ============ MODÈLES DE DONNÉES ============

class CriterionDefinition(BaseModel):
    """Définit un critère pouvant être transformé en question"""
    criterion_id: str
    label: str
    question_type: str  # "select", "multiselect", "number", "boolean"
    options: Optional[List[dict]] = None
    field_mapping: str  # champ correspondant dans ProfilAgriculteur
    weight: float = 10.0
    is_blocking: bool = False
    coverage_count: int = 0


class QuestionnaireState(BaseModel):
    """Suit l'état courant du questionnaire adaptatif"""
    session_id: str
    answers: Dict[str, Any] = {}
    remaining_aids_count: int = 0
    total_aids_count: int = 0
    questions_asked: List[str] = []
    is_complete: bool = False


# ============ MOTEUR DE QUESTIONNAIRE ============

class QuestionnaireEngine:
    """
    Moteur de questionnaire adaptatif.
    Sélectionne à chaque étape la question la plus discriminante
    en fonction des aides restantes et des réponses déjà fournies.
    """

    # Nombre maximum de questions à poser
    MAX_QUESTIONS = 12

    # Seuil d'aides restantes pour considérer la convergence
    CONVERGENCE_THRESHOLD_COUNT = 5

    # Nombre minimum de questions à poser avant de pouvoir converger sur le seuil d'aides
    MIN_QUESTIONS_BEFORE_CONVERGENCE = 3

    # Valeurs de périmètre signifiant "toute la France" (aide nationale)
    NATIONAL_REGION_IDENTIFIERS = frozenset({"National", "France entière", "France"})

    # Définitions statiques des critères — ordre suggéré si scores égaux
    CRITERION_DEFINITIONS: Dict[str, dict] = {
        "region": {
            "label": "Dans quelle région est située votre exploitation ?",
            "question_type": "select",
            "field_mapping": "region",
            "weight": 25.0,
            "is_blocking": True,
        },
        "departement": {
            "label": "Dans quel département est située votre exploitation ?",
            "question_type": "select",
            "field_mapping": "departement",
            "weight": 20.0,
            "is_blocking": True,
        },
        "types_production": {
            "label": "Quels sont vos types de production ?",
            "question_type": "multiselect",
            "field_mapping": "productions",
            "weight": 20.0,
            "is_blocking": True,
        },
        "types_projets": {
            "label": "Quels projets envisagez-vous ?",
            "question_type": "multiselect",
            "field_mapping": "projets_en_cours",
            "weight": 15.0,
            "is_blocking": False,
        },
        "statuts_juridiques": {
            "label": "Quel est votre statut juridique ?",
            "question_type": "select",
            "field_mapping": "statut_juridique",
            "weight": 10.0,
            "is_blocking": True,
        },
        "age": {
            "label": "Quel est votre âge ?",
            "question_type": "number",
            "field_mapping": "age",
            "weight": 10.0,
            "is_blocking": False,
        },
        "superficie": {
            "label": "Quelle est votre surface agricole utile (SAU) en hectares ?",
            "question_type": "number",
            "field_mapping": "sau_totale",
            "weight": 10.0,
            "is_blocking": False,
        },
        "labels_requis": {
            "label": "Disposez-vous de labels ou certifications ?",
            "question_type": "multiselect",
            "field_mapping": "labels",
            "weight": 10.0,
            "is_blocking": False,
        },
        "jeune_agriculteur": {
            "label": "Êtes-vous un jeune agriculteur (moins de 40 ans, installé récemment) ?",
            "question_type": "boolean",
            "field_mapping": "jeune_agriculteur",
            "weight": 8.0,
            "is_blocking": False,
        },
        "premiere_installation": {
            "label": "S'agit-il de votre première installation ?",
            "question_type": "boolean",
            "field_mapping": "premiere_installation",
            "weight": 8.0,
            "is_blocking": False,
        },
        "en_difficulte": {
            "label": "Votre exploitation est-elle en difficulté financière ?",
            "question_type": "boolean",
            "field_mapping": "en_difficulte",
            "weight": 6.0,
            "is_blocking": False,
        },
        "projets_collectifs": {
            "label": "Votre projet est-il collectif (GAEC, coopérative, groupement…) ?",
            "question_type": "boolean",
            "field_mapping": "projets_collectifs",
            "weight": 6.0,
            "is_blocking": False,
        },
    }

    def __init__(self):
        self._matching_engine = MatchingEngine()

    # ------------------------------------------------------------------ #
    #  API PUBLIQUE                                                        #
    # ------------------------------------------------------------------ #

    async def start_session(self, db) -> QuestionnaireState:
        """Initialise une nouvelle session de questionnaire."""
        total = await db.aides_v2.count_documents({"statut": "active"})
        return QuestionnaireState(
            session_id=str(uuid.uuid4()),
            answers={},
            remaining_aids_count=total,
            total_aids_count=total,
            questions_asked=[],
            is_complete=False,
        )

    async def get_next_question(self, db, state: QuestionnaireState) -> dict:
        """
        Retourne la prochaine question la plus discriminante.
        Inclut les options disponibles extraites des aides restantes.
        """
        if state.is_complete:
            return {"is_complete": True, "remaining_aids_count": state.remaining_aids_count}

        aids = await self._load_filtered_aids(db, state.answers)

        if self._check_convergence(state, len(aids)):
            return {
                "is_complete": True,
                "remaining_aids_count": len(aids),
                "total_aids_count": state.total_aids_count,
            }

        # Critères non encore demandés
        unanswered = [
            cid for cid in self.CRITERION_DEFINITIONS
            if cid not in state.questions_asked
        ]

        if not unanswered:
            return {
                "is_complete": True,
                "remaining_aids_count": len(aids),
                "total_aids_count": state.total_aids_count,
            }

        # Sélectionner le critère le plus discriminant
        best_criterion_id = self._select_best_criterion(aids, unanswered, state.answers)
        criterion_def = self.CRITERION_DEFINITIONS[best_criterion_id]

        # Extraire les options disponibles depuis les aides restantes
        options = self._extract_options(aids, best_criterion_id)

        question = {
            "criterion_id": best_criterion_id,
            "label": criterion_def["label"],
            "question_type": criterion_def["question_type"],
            "field_mapping": criterion_def["field_mapping"],
            "weight": criterion_def["weight"],
            "is_blocking": criterion_def["is_blocking"],
            "options": options,
            "is_complete": False,
            "remaining_aids_count": len(aids),
            "total_aids_count": state.total_aids_count,
            "questions_asked": state.questions_asked,
        }
        return question

    async def submit_answer(
        self, db, state: QuestionnaireState, criterion_id: str, value: Any
    ) -> QuestionnaireState:
        """Enregistre une réponse et met à jour l'état."""
        new_answers = {**state.answers, criterion_id: value}
        new_questions_asked = state.questions_asked + [criterion_id]

        aids = await self._load_filtered_aids(db, new_answers)
        remaining = len(aids)

        is_complete = self._check_convergence(
            QuestionnaireState(
                session_id=state.session_id,
                answers=new_answers,
                remaining_aids_count=remaining,
                total_aids_count=state.total_aids_count,
                questions_asked=new_questions_asked,
            ),
            remaining,
        )

        return QuestionnaireState(
            session_id=state.session_id,
            answers=new_answers,
            remaining_aids_count=remaining,
            total_aids_count=state.total_aids_count,
            questions_asked=new_questions_asked,
            is_complete=is_complete,
        )

    async def get_results(self, db, state: QuestionnaireState) -> dict:
        """
        Retourne les résultats finaux du matching à partir des réponses.
        """
        profil = self._answers_to_profil(state.answers)
        aids_docs = await db.aides_v2.find({"statut": "active"}).to_list(length=None)
        aids = [AideAgricoleV2(**doc) for doc in aids_docs]

        # Build a map for quick lookup
        aids_by_id = {aide.aid_id: aide for aide in aids}

        resultats = self._matching_engine.find_best_matches(aids, profil, top_n=200)

        # Enrich each result with the full aide data (mirrors server.py behaviour)
        resultats_enrichis = []
        for r in resultats:
            r_dict = r.model_dump()
            aide = aids_by_id.get(r.aide_id)
            if aide:
                r_dict['aide'] = {
                    'aid_id': aide.aid_id,
                    'titre': aide.titre,
                    'description': aide.description if aide.description else '',
                    'description_courte': (
                        aide.description[:200] + '...'
                        if aide.description and len(aide.description) > 200
                        else aide.description
                    ),
                    'organisme': aide.organisme,
                    'programme': aide.programme,
                    'source': aide.source,
                    'source_url': aide.source_url,
                    'lien_officiel': aide.lien_officiel,
                    'lien_dossier': aide.lien_dossier,
                    'date_debut': aide.date_debut,
                    'date_fin': aide.date_fin,
                    'date_limite_depot': aide.date_limite_depot,
                    'montant': {
                        'type': aide.montant.type_montant.value if aide.montant and aide.montant.type_montant else None,
                        'min': aide.montant.montant_min if aide.montant else None,
                        'max': aide.montant.montant_max if aide.montant else None,
                        'taux_min': aide.montant.taux_min if aide.montant else None,
                        'taux_max': aide.montant.taux_max if aide.montant else None,
                        'plafond': aide.montant.plafond if aide.montant else None,
                        'description': aide.montant.description if aide.montant else None,
                    },
                    'criteres': {
                        'regions': aide.criteres.regions if aide.criteres else [],
                        'departements': aide.criteres.departements if aide.criteres else [],
                        'types_production': [p.value for p in aide.criteres.types_production] if aide.criteres and aide.criteres.types_production else [],
                        'types_projets': [p.value for p in aide.criteres.types_projets] if aide.criteres and aide.criteres.types_projets else [],
                        'labels_requis': aide.criteres.labels_requis if aide.criteres else [],
                        'jeune_agriculteur': aide.criteres.jeune_agriculteur if aide.criteres else None,
                    },
                    'conditions_eligibilite': aide.conditions_eligibilite if aide.conditions_eligibilite else '',
                    'demarche': aide.demarche if aide.demarche else '',
                    'contact': aide.contact,
                    'tags': aide.tags[:15] if aide.tags else [],
                    'statut': aide.statut,
                }
            resultats_enrichis.append(r_dict)

        classified: Dict[str, list] = {
            StatutMatching.TRES_PROBABLE.value: [],
            StatutMatching.PROBABLE.value: [],
            StatutMatching.A_VERIFIER.value: [],
            StatutMatching.NON_RETENUE.value: [],
        }
        for r in resultats:
            statut = r.statut_matching or StatutMatching.NON_RETENUE.value
            if statut in classified:
                classified[statut].append(r.model_dump())

        return {
            "profil": profil.model_dump(),
            "resultats": resultats_enrichis,
            "classified": classified,
            "stats": {
                "total_evaluated": len(aids),
                "eligible_count": sum(1 for r in resultats if r.eligible),
                "tres_probable": len(classified[StatutMatching.TRES_PROBABLE.value]),
                "probable": len(classified[StatutMatching.PROBABLE.value]),
                "a_verifier": len(classified[StatutMatching.A_VERIFIER.value]),
            },
        }

    # ------------------------------------------------------------------ #
    #  MÉTHODES INTERNES                                                   #
    # ------------------------------------------------------------------ #

    def _calculate_discrimination_score(
        self, aids: list, criterion_id: str, current_answers: dict
    ) -> float:
        """
        Calcule le pouvoir discriminant d'un critère pour l'ensemble d'aides courant.
        Basé sur l'entropie : un bon critère partage les aides en groupes à peu près égaux.
        """
        groups: Dict[str, int] = {}
        aids_with_criterion = 0

        for aide in aids:
            criteres = aide.criteres if hasattr(aide, "criteres") else None
            if criteres is None:
                continue

            values = self._get_criterion_values(criteres, criterion_id)
            # None or empty list means no constraint defined for this criterion
            if values is None:
                continue
            if isinstance(values, list) and not values:
                continue
            if isinstance(values, dict) and not any(v is not None for v in values.values()):
                continue

            aids_with_criterion += 1
            key = str(sorted(values) if isinstance(values, list) else values)
            groups[key] = groups.get(key, 0) + 1

        if aids_with_criterion == 0:
            return 0.0

        # Coverage score — critère plus pertinent s'il couvre plus d'aides
        coverage = aids_with_criterion / max(len(aids), 1)

        # Entropie normalisée — critère plus discriminant si les groupes sont équilibrés
        total = aids_with_criterion
        entropy = 0.0
        for count in groups.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        max_entropy = math.log2(len(groups)) if len(groups) > 1 else 0.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        # Score final = couverture × entropie normalisée × poids configuré
        weight = self.CRITERION_DEFINITIONS.get(criterion_id, {}).get("weight", 10.0)
        return coverage * normalized_entropy * weight

    def _filter_aids_by_answers(self, aids: list, answers: dict) -> list:
        """Filtre les aides selon les réponses déjà données."""
        remaining = []
        for aide in aids:
            criteres = aide.criteres
            if self._aide_matches_answers(criteres, answers):
                remaining.append(aide)
        return remaining

    def _aide_matches_answers(self, criteres: CriteresEligibilite, answers: dict) -> bool:
        """Retourne True si les critères de l'aide sont compatibles avec les réponses."""
        for criterion_id, value in answers.items():
            if value is None:
                continue
            crit_values = self._get_criterion_values(criteres, criterion_id)
            # None means the aide has no constraint for this criterion → compatible
            if crit_values is None:
                continue
            # Empty list means no constraint
            if isinstance(crit_values, list) and not crit_values:
                continue
            # Aide nationale → compatible avec toutes les régions et tous les départements
            if criterion_id in ("region", "departement") and isinstance(crit_values, list):
                if any(v in self.NATIONAL_REGION_IDENTIFIERS for v in crit_values):
                    continue
            if not self._value_matches(criterion_id, crit_values, value):
                return False
        return True

    def _value_matches(self, criterion_id: str, crit_values: Any, user_value: Any) -> bool:
        """Vérifie si la valeur de l'utilisateur est compatible avec les valeurs du critère."""
        q_type = self.CRITERION_DEFINITIONS.get(criterion_id, {}).get("question_type", "select")

        if q_type == "boolean":
            return bool(user_value) == bool(crit_values)

        if q_type == "number":
            # Pour les critères numériques, crit_values est un dict {"min": x, "max": y}
            if isinstance(crit_values, dict):
                v = float(user_value) if user_value is not None else None
                if v is None:
                    return True
                if crit_values.get("min") is not None and v < crit_values["min"]:
                    return False
                if crit_values.get("max") is not None and v > crit_values["max"]:
                    return False
            return True

        # select / multiselect
        if isinstance(user_value, list):
            # Intersection : au moins une valeur en commun
            return bool(set(user_value) & set(crit_values))
        else:
            return str(user_value) in [str(v) for v in crit_values]

    def _get_criterion_values(self, criteres: CriteresEligibilite, criterion_id: str) -> Any:
        """Extrait les valeurs d'un critère depuis CriteresEligibilite."""
        if criterion_id == "region":
            return criteres.regions or []
        if criterion_id == "departement":
            return criteres.departements or []
        if criterion_id == "types_production":
            return [tp.value if hasattr(tp, "value") else tp for tp in criteres.types_production]
        if criterion_id == "types_projets":
            return [tp.value if hasattr(tp, "value") else tp for tp in criteres.types_projets]
        if criterion_id == "statuts_juridiques":
            return [sj.value if hasattr(sj, "value") else sj for sj in criteres.statuts_juridiques]
        if criterion_id == "labels_requis":
            return criteres.labels_requis or []
        if criterion_id == "jeune_agriculteur":
            return criteres.jeune_agriculteur
        if criterion_id == "premiere_installation":
            return criteres.premiere_installation
        if criterion_id == "en_difficulte":
            return criteres.en_difficulte
        if criterion_id == "projets_collectifs":
            return criteres.projets_collectifs
        if criterion_id == "age":
            if criteres.age_min is None and criteres.age_max is None:
                return None
            return {"min": criteres.age_min, "max": criteres.age_max}
        if criterion_id == "superficie":
            if criteres.superficie_min is None and criteres.superficie_max is None:
                return None
            return {"min": criteres.superficie_min, "max": criteres.superficie_max}
        return None

    # ------------------------------------------------------------------ #
    #  LISTES DE RÉFÉRENCE FRANÇAISES (fallback si aucune aide renseignée) #
    # ------------------------------------------------------------------ #

    _FALLBACK_OPTIONS: Dict[str, List[str]] = {
        "region": [
            "Auvergne-Rhône-Alpes",
            "Bourgogne-Franche-Comté",
            "Bretagne",
            "Centre-Val de Loire",
            "Corse",
            "Grand Est",
            "Guadeloupe",
            "Guyane",
            "Hauts-de-France",
            "Île-de-France",
            "La Réunion",
            "Martinique",
            "Mayotte",
            "Normandie",
            "Nouvelle-Aquitaine",
            "Occitanie",
            "Pays de la Loire",
            "Provence-Alpes-Côte d'Azur",
        ],
        "departement": [
            "01", "02", "03", "04", "05", "06", "07", "08", "09",
            "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
            "21", "22", "23", "24", "25", "26", "27", "28", "29",
            "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
            "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
            "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
            "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
            "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
            "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
            "90", "91", "92", "93", "94", "95",
            "971", "972", "973", "974", "976",
        ],
        "statuts_juridiques": [sj.value for sj in StatutJuridique],
        "types_production": [tprod.value for tprod in TypeProduction],
        "types_projets": [tproj.value for tproj in TypeProjet],
        "labels_requis": [
            "Agriculture Biologique (AB)",
            "Haute Valeur Environnementale (HVE)",
            "Label Rouge",
            "AOC/AOP",
            "IGP",
            "STG",
            "Demeter",
            "Nature & Progrès",
            "GlobalGAP",
        ],
    }

    def _extract_options(self, aids: list, criterion_id: str) -> Optional[List[dict]]:
        """
        Extrait les valeurs distinctes pour un critère depuis les aides restantes.
        Si aucune option n'est trouvée dans les aides, utilise les listes de référence
        françaises complètes comme fallback (les deux sont fusionnées et dédupliquées).
        """
        q_type = self.CRITERION_DEFINITIONS.get(criterion_id, {}).get("question_type", "select")
        if q_type in ("number", "boolean"):
            return None

        seen: set = set()
        options: List[dict] = []

        # Reference set for filtering coded values (regions & departements)
        valid_reference: set = set(self._FALLBACK_OPTIONS.get(criterion_id, []))

        # Extraire les options réelles depuis les aides en base
        for aide in aids:
            values = self._get_criterion_values(aide.criteres, criterion_id)
            if not values or not isinstance(values, list):
                continue
            for v in values:
                sv = str(v).strip()
                if not sv or sv in seen:
                    continue
                # For region/departement, skip coded DB values not in the reference list
                if criterion_id in ("region", "departement") and valid_reference and sv not in valid_reference:
                    continue
                seen.add(sv)
                options.append({"value": sv, "label": sv})

        # Fusionner avec les valeurs de référence (fallback)
        fallback_values = self._FALLBACK_OPTIONS.get(criterion_id, [])
        for fv in fallback_values:
            sv = str(fv).strip()
            if sv and sv not in seen:
                seen.add(sv)
                options.append({"value": sv, "label": sv})

        return sorted(options, key=lambda o: o["label"]) if options else None

    def _select_best_criterion(
        self, aids: list, unanswered: List[str], current_answers: dict
    ) -> str:
        """Sélectionne le critère le plus discriminant parmi ceux non encore demandés."""
        best_id = unanswered[0]
        best_score = -1.0

        for cid in unanswered:
            score = self._calculate_discrimination_score(aids, cid, current_answers)
            if score > best_score:
                best_score = score
                best_id = cid

        return best_id

    def _answers_to_profil(self, answers: dict) -> ProfilAgriculteur:
        """Convertit les réponses du questionnaire en ProfilAgriculteur."""

        def _to_statut(val: Any) -> StatutJuridique:
            if not val:
                return StatutJuridique.AUTRE
            if isinstance(val, list):
                val = val[0] if val else ""
            for sj in StatutJuridique:
                if sj.value == str(val) or sj.name == str(val):
                    return sj
            return StatutJuridique.AUTRE

        def _to_productions(val: Any) -> List[TypeProduction]:
            if not val:
                return []
            if not isinstance(val, list):
                val = [val]
            result = []
            for v in val:
                for tp in TypeProduction:
                    if tp.value == str(v) or tp.name == str(v):
                        result.append(tp)
                        break
            return result

        def _to_projets(val: Any) -> List[TypeProjet]:
            if not val:
                return []
            if not isinstance(val, list):
                val = [val]
            result = []
            for v in val:
                for tp in TypeProjet:
                    if tp.value == str(v) or tp.name == str(v):
                        result.append(tp)
                        break
            return result

        region = answers.get("region", "")
        if isinstance(region, list):
            region = region[0] if region else ""

        departement = answers.get("departement", "")
        if isinstance(departement, list):
            departement = departement[0] if departement else ""

        return ProfilAgriculteur(
            region=str(region) if region else "Non précisé",
            departement=str(departement) if departement else "Non précisé",
            statut_juridique=_to_statut(answers.get("statuts_juridiques")),
            sau_totale=float(answers.get("superficie", 0) or 0),
            productions=_to_productions(answers.get("types_production", [])),
            projets_en_cours=_to_projets(answers.get("types_projets", [])),
            age=int(answers.get("age")) if answers.get("age") else None,
            jeune_agriculteur=bool(answers.get("jeune_agriculteur", False)),
            premiere_installation=bool(answers.get("premiere_installation", False)),
            en_difficulte=bool(answers.get("en_difficulte", False)),
            projets_collectifs=bool(answers.get("projets_collectifs", False)),
            labels=answers.get("labels_requis", []) if isinstance(answers.get("labels_requis"), list) else [],
        )

    def _check_convergence(self, state: QuestionnaireState, remaining_aids_count: int) -> bool:
        """Vérifie si on doit arrêter de poser des questions."""
        if len(state.questions_asked) >= self.MAX_QUESTIONS:
            return True
        # Ne pas converger sur le seuil d'aides avant d'avoir posé le minimum de questions
        if len(state.questions_asked) >= self.MIN_QUESTIONS_BEFORE_CONVERGENCE:
            if remaining_aids_count <= self.CONVERGENCE_THRESHOLD_COUNT:
                return True
        unanswered = [
            cid for cid in self.CRITERION_DEFINITIONS
            if cid not in state.questions_asked
        ]
        if not unanswered:
            return True
        return False

    async def _load_filtered_aids(self, db, answers: dict) -> list:
        """Charge les aides actives et les filtre selon les réponses courantes."""
        docs = await db.aides_v2.find({"statut": "active"}).to_list(length=None)
        aids = [AideAgricoleV2(**doc) for doc in docs]
        return self._filter_aids_by_answers(aids, answers)
