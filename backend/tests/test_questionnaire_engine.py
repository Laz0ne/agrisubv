"""
Tests unitaires pour le moteur de questionnaire adaptatif.
Couvre: session, discrimination, filtrage, convergence, conversion de profil, statuts.
"""

import sys
import os
import pytest

# Ajout du répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models_v2 import (
    AideAgricoleV2,
    CriteresEligibilite,
    ProfilAgriculteur,
    ResultatMatching,
    StatutJuridique,
    StatutMatching,
    TypeProduction,
    TypeProjet,
    ConditionAide,
    MontantAide,
)
from matching_engine import MatchingEngine
from questionnaire_engine import QuestionnaireEngine, QuestionnaireState


# ============ HELPERS ============


def make_aide(
    aid_id: str = "aide_test",
    regions: list = None,
    types_production: list = None,
    statuts_juridiques: list = None,
    jeune_agriculteur: bool = None,
    age_min: int = None,
    age_max: int = None,
    superficie_min: float = None,
    superficie_max: float = None,
    labels_requis: list = None,
) -> AideAgricoleV2:
    criteres = CriteresEligibilite(
        regions=regions or [],
        types_production=types_production or [],
        statuts_juridiques=statuts_juridiques or [],
        jeune_agriculteur=jeune_agriculteur,
        age_min=age_min,
        age_max=age_max,
        superficie_min=superficie_min,
        superficie_max=superficie_max,
        labels_requis=labels_requis or [],
    )
    return AideAgricoleV2(
        aid_id=aid_id,
        titre=f"Aide {aid_id}",
        organisme="Test",
        criteres=criteres,
        statut="active",
    )


def make_profil(**kwargs) -> ProfilAgriculteur:
    defaults = {
        "region": "Occitanie",
        "departement": "31",
        "statut_juridique": StatutJuridique.EARL,
        "sau_totale": 50.0,
        "productions": [TypeProduction.CEREALES],
        "projets_en_cours": [TypeProjet.IRRIGATION],
    }
    defaults.update(kwargs)
    return ProfilAgriculteur(**defaults)


# ============ TESTS MODELS_V2 ============


class TestModels:
    def test_condition_aide_model(self):
        cond = ConditionAide(
            criterion="localisation_region",
            operator="in",
            value=["Occitanie"],
            mandatory=True,
            weight=30.0,
        )
        assert cond.criterion == "localisation_region"
        assert cond.operator == "in"
        assert cond.mandatory is True
        assert cond.weight == 30.0

    def test_statut_matching_enum(self):
        assert StatutMatching.TRES_PROBABLE.value == "tres_probable"
        assert StatutMatching.PROBABLE.value == "probable"
        assert StatutMatching.A_VERIFIER.value == "a_verifier"
        assert StatutMatching.NON_RETENUE.value == "non_retenue"

    def test_resultat_matching_has_statut_matching(self):
        r = ResultatMatching(
            aide_id="a1",
            profil_id="p1",
            score=75.0,
            eligible=True,
            statut_matching=StatutMatching.PROBABLE.value,
        )
        assert r.statut_matching == "probable"

    def test_aide_agricole_v2_has_conditions(self):
        aide = AideAgricoleV2(
            titre="Test aide",
            organisme="Org",
            conditions=[
                ConditionAide(criterion="region", operator="in", value=["Bretagne"])
            ],
        )
        assert len(aide.conditions) == 1
        assert aide.conditions[0].criterion == "region"


# ============ TESTS MATCHING ENGINE — STATUT ============


class TestMatchingEngineStatut:
    def setup_method(self):
        self.engine = MatchingEngine()

    def test_statut_tres_probable(self):
        statut = self.engine._get_statut_matching(85.0, True, [], [])
        assert statut == StatutMatching.TRES_PROBABLE.value

    def test_statut_probable(self):
        statut = self.engine._get_statut_matching(70.0, True, [], [])
        assert statut == StatutMatching.PROBABLE.value

    def test_statut_a_verifier(self):
        statut = self.engine._get_statut_matching(50.0, False, [], [])
        assert statut == StatutMatching.A_VERIFIER.value

    def test_statut_non_retenue_bloquant(self):
        statut = self.engine._get_statut_matching(0.0, False, ["Localisation"], [])
        assert statut == StatutMatching.NON_RETENUE.value

    def test_statut_non_retenue_score_bas(self):
        statut = self.engine._get_statut_matching(30.0, False, [], [])
        assert statut == StatutMatching.NON_RETENUE.value

    def test_calculate_match_populates_statut(self):
        aide = make_aide(
            aid_id="a_statut",
            regions=["Occitanie"],
            types_production=[TypeProduction.CEREALES],
        )
        profil = make_profil()
        result = self.engine.calculate_match(aide, profil)
        assert result.statut_matching is not None
        assert result.statut_matching in [sm.value for sm in StatutMatching]


# ============ TESTS QUESTIONNAIRE ENGINE ============


class TestQuestionnaireEngine:
    def setup_method(self):
        self.engine = QuestionnaireEngine()

    # --- Discrimination score ---

    def test_discrimination_score_empty_aids(self):
        score = self.engine._calculate_discrimination_score([], "region", {})
        assert score == 0.0

    def test_discrimination_score_with_aids(self):
        aids = [
            make_aide("a1", regions=["Occitanie"]),
            make_aide("a2", regions=["Bretagne"]),
            make_aide("a3", regions=["Occitanie"]),
        ]
        score = self.engine._calculate_discrimination_score(aids, "region", {})
        assert score > 0.0

    def test_discrimination_score_no_criterion(self):
        # Aides sans critère région → score 0
        aids = [make_aide("a1"), make_aide("a2")]
        score = self.engine._calculate_discrimination_score(aids, "region", {})
        assert score == 0.0

    def test_discrimination_score_boolean(self):
        aids = [
            make_aide("a1", jeune_agriculteur=True),
            make_aide("a2", jeune_agriculteur=False),
        ]
        score = self.engine._calculate_discrimination_score(aids, "jeune_agriculteur", {})
        assert score > 0.0

    # --- Filtrage par réponses ---

    def test_filter_aids_no_answers(self):
        aids = [make_aide("a1", regions=["Occitanie"]), make_aide("a2", regions=["Bretagne"])]
        result = self.engine._filter_aids_by_answers(aids, {})
        assert len(result) == 2

    def test_filter_aids_by_region(self):
        aids = [
            make_aide("a1", regions=["Occitanie"]),
            make_aide("a2", regions=["Bretagne"]),
            make_aide("a3"),  # Pas de région → compatible
        ]
        result = self.engine._filter_aids_by_answers(aids, {"region": "Occitanie"})
        assert len(result) == 2  # a1 (Occitanie) + a3 (pas de critère)

    def test_filter_aids_by_multiselect_production(self):
        aids = [
            make_aide("a1", types_production=[TypeProduction.CEREALES]),
            make_aide("a2", types_production=[TypeProduction.VITICULTURE]),
            make_aide("a3"),
        ]
        result = self.engine._filter_aids_by_answers(
            aids, {"types_production": ["Céréales"]}
        )
        assert any(a.aid_id == "a1" for a in result)
        assert not any(a.aid_id == "a2" for a in result)
        assert any(a.aid_id == "a3" for a in result)

    def test_filter_aids_by_boolean(self):
        aids = [
            make_aide("a1", jeune_agriculteur=True),
            make_aide("a2", jeune_agriculteur=False),
            make_aide("a3"),  # Pas de critère JA
        ]
        result = self.engine._filter_aids_by_answers(aids, {"jeune_agriculteur": True})
        assert any(a.aid_id == "a1" for a in result)
        assert not any(a.aid_id == "a2" for a in result)
        assert any(a.aid_id == "a3" for a in result)

    def test_filter_aids_by_age_range(self):
        aids = [
            make_aide("a1", age_min=18, age_max=40),
            make_aide("a2", age_min=41, age_max=65),
            make_aide("a3"),  # Pas de critère âge
        ]
        result = self.engine._filter_aids_by_answers(aids, {"age": 30})
        assert any(a.aid_id == "a1" for a in result)
        assert not any(a.aid_id == "a2" for a in result)
        assert any(a.aid_id == "a3" for a in result)

    # --- Convergence ---

    def test_convergence_max_questions(self):
        state = QuestionnaireState(
            session_id="test",
            questions_asked=[f"q{i}" for i in range(1, QuestionnaireEngine.MAX_QUESTIONS + 1)],
        )
        assert self.engine._check_convergence(state, 100) is True

    def test_convergence_few_aids(self):
        state = QuestionnaireState(session_id="test", questions_asked=["region"])
        assert self.engine._check_convergence(state, 3) is True

    def test_no_convergence_many_aids(self):
        state = QuestionnaireState(session_id="test", questions_asked=["region"])
        assert self.engine._check_convergence(state, 50) is False

    def test_convergence_no_more_questions(self):
        all_criteria = list(self.engine.CRITERION_DEFINITIONS.keys())
        state = QuestionnaireState(session_id="test", questions_asked=all_criteria)
        assert self.engine._check_convergence(state, 50) is True

    # --- Conversion answers → ProfilAgriculteur ---

    def test_answers_to_profil_basic(self):
        answers = {
            "region": "Occitanie",
            "departement": "31",
            "statuts_juridiques": "EARL",
            "superficie": 80.0,
        }
        profil = self.engine._answers_to_profil(answers)
        assert isinstance(profil, ProfilAgriculteur)
        assert profil.region == "Occitanie"
        assert profil.departement == "31"
        assert profil.sau_totale == 80.0

    def test_answers_to_profil_productions(self):
        answers = {
            "region": "Bretagne",
            "departement": "35",
            "types_production": ["Céréales", "Viticulture"],
        }
        profil = self.engine._answers_to_profil(answers)
        assert TypeProduction.CEREALES in profil.productions
        assert TypeProduction.VITICULTURE in profil.productions

    def test_answers_to_profil_projets(self):
        answers = {
            "region": "Bretagne",
            "departement": "35",
            "types_projets": ["Irrigation"],
        }
        profil = self.engine._answers_to_profil(answers)
        assert TypeProjet.IRRIGATION in profil.projets_en_cours

    def test_answers_to_profil_defaults(self):
        answers = {}
        profil = self.engine._answers_to_profil(answers)
        assert profil.region == "Non précisé"
        assert profil.departement == "Non précisé"
        assert profil.sau_totale == 0.0

    def test_answers_to_profil_boolean_flags(self):
        answers = {
            "region": "Normandie",
            "departement": "14",
            "jeune_agriculteur": True,
            "premiere_installation": True,
            "en_difficulte": False,
            "projets_collectifs": True,
        }
        profil = self.engine._answers_to_profil(answers)
        assert profil.jeune_agriculteur is True
        assert profil.premiere_installation is True
        assert profil.en_difficulte is False
        assert profil.projets_collectifs is True

    # --- Extraction d'options ---

    def test_extract_options_region(self):
        aids = [
            make_aide("a1", regions=["Occitanie"]),
            make_aide("a2", regions=["Bretagne"]),
            make_aide("a3", regions=["Occitanie"]),
        ]
        options = self.engine._extract_options(aids, "region")
        assert options is not None
        values = [o["value"] for o in options]
        assert "Occitanie" in values
        assert "Bretagne" in values
        # No duplicates (set size equals list size)
        assert len(set(values)) == len(values)
        # Fallback regions are also included
        assert len(values) >= 2

    def test_extract_options_number_returns_none(self):
        aids = [make_aide("a1", age_min=18, age_max=40)]
        options = self.engine._extract_options(aids, "age")
        assert options is None

    def test_extract_options_boolean_returns_none(self):
        aids = [make_aide("a1", jeune_agriculteur=True)]
        options = self.engine._extract_options(aids, "jeune_agriculteur")
        assert options is None

    # --- Sélection du meilleur critère ---

    def test_select_best_criterion(self):
        # Région très discriminante (50/50), production pas de valeur → région doit gagner
        aids = [
            make_aide("a1", regions=["Occitanie"]),
            make_aide("a2", regions=["Bretagne"]),
            make_aide("a3", regions=["Occitanie"]),
            make_aide("a4", regions=["Bretagne"]),
        ]
        unanswered = list(self.engine.CRITERION_DEFINITIONS.keys())
        best = self.engine._select_best_criterion(aids, unanswered, {})
        # "region" devrait être sélectionné car très discriminant et bien couvert
        assert best == "region"


# ============ TESTS INTÉGRATION MATCHING ============


class TestMatchingIntegration:
    def setup_method(self):
        self.engine = MatchingEngine()

    def test_full_matching_with_statut(self):
        aide = make_aide(
            aid_id="full_test",
            regions=["Occitanie"],
            types_production=[TypeProduction.CEREALES],
            statuts_juridiques=[StatutJuridique.EARL],
        )
        profil = make_profil(
            region="Occitanie",
            departement="31",
            statut_juridique=StatutJuridique.EARL,
            productions=[TypeProduction.CEREALES],
        )
        result = self.engine.calculate_match(aide, profil)
        assert result.statut_matching is not None
        # Profile matches → should be eligible or at least a_verifier
        if result.eligible:
            assert result.statut_matching in [
                StatutMatching.PROBABLE.value,
                StatutMatching.TRES_PROBABLE.value,
            ]

    def test_find_best_matches_with_statuts(self):
        aids = [
            make_aide("b1", regions=["Occitanie"]),
            make_aide("b2", regions=["Bretagne"]),
        ]
        profil = make_profil()
        results = self.engine.find_best_matches(aids, profil, top_n=5)
        assert len(results) > 0
        for r in results:
            assert r.statut_matching is not None
