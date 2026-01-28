"""
Test pour vérifier les améliorations du matching engine
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from models_v2 import (
    AideAgricoleV2, ProfilAgriculteur, CriteresEligibilite, MontantAide,
    TypeProduction, TypeProjet, StatutJuridique, TypeMontant
)
from matching_engine import MatchingEngine


def test_production_non_bloquante():
    """
    Test que la production n'est plus bloquante si non renseignée
    """
    print("\n🧪 Test 1: Production non renseignée ne doit pas bloquer")
    
    # Profil sans production renseignée
    profil = ProfilAgriculteur(
        profil_id="test-1",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[],  # ⚠️ Aucune production renseignée
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide avec restriction de production
    criteres = CriteresEligibilite(
        regions=["National"],
        types_production=[TypeProduction.CEREALES]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-001",
        titre="Aide test avec restriction production",
        organisme="Test Organisme",
        source="test",
        criteres=criteres,
        montant=montant,
        statut="active"
    )
    
    engine = MatchingEngine()
    resultat = engine.calculate_match(aide, profil)
    
    # Vérifications
    print(f"   Score: {resultat.score}")
    print(f"   Éligible: {resultat.eligible}")
    print(f"   Critères bloquants KO: {resultat.criteres_bloquants_ko}")
    
    # La production ne doit PAS être dans les critères bloquants
    assert "Production" not in resultat.criteres_bloquants_ko, \
        "❌ ÉCHEC: La production ne devrait pas être bloquante si non renseignée"
    
    print("   ✅ SUCCÈS: La production n'est pas bloquante")
    
    # Vérifier qu'il y a bien un détail avec l'explication
    production_detail = next(
        (d for d in resultat.details_criteres if "production" in d.nom.lower()),
        None
    )
    
    if production_detail:
        print(f"   📝 Explication: {production_detail.explication}")
        assert "non renseignées" in production_detail.explication.lower(), \
            "❌ ÉCHEC: L'explication devrait mentionner que les productions ne sont pas renseignées"
    
    print("   ✅ Test 1 réussi!\n")


def test_production_avec_match():
    """
    Test que la production fonctionne toujours correctement quand elle matche
    """
    print("🧪 Test 2: Production avec correspondance doit donner des points")
    
    # Profil avec production
    profil = ProfilAgriculteur(
        profil_id="test-2",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.CEREALES],  # ✅ Production renseignée
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide avec même restriction de production
    criteres = CriteresEligibilite(
        regions=["National"],
        types_production=[TypeProduction.CEREALES]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-002",
        titre="Aide test avec correspondance production",
        organisme="Test Organisme",
        source="test",
        criteres=criteres,
        montant=montant,
        statut="active"
    )
    
    engine = MatchingEngine()
    resultat = engine.calculate_match(aide, profil)
    
    # Vérifications
    print(f"   Score: {resultat.score}")
    print(f"   Éligible: {resultat.eligible}")
    print(f"   Critères bloquants KO: {resultat.criteres_bloquants_ko}")
    
    # Doit être éligible
    assert resultat.eligible, "❌ ÉCHEC: Devrait être éligible"
    assert "Production" not in resultat.criteres_bloquants_ko, \
        "❌ ÉCHEC: La production ne devrait pas être bloquante"
    
    # Le score doit inclure les points de production
    production_detail = next(
        (d for d in resultat.details_criteres if "production" in d.nom.lower()),
        None
    )
    
    if production_detail:
        print(f"   📝 Points production: {production_detail.points}/{production_detail.points_max}")
        assert production_detail.valide, "❌ ÉCHEC: La production devrait être validée"
        assert production_detail.points > 0, "❌ ÉCHEC: Devrait avoir des points"
    
    print("   ✅ Test 2 réussi!\n")


def test_production_sans_match():
    """
    Test que la production bloque toujours si elle ne correspond pas
    """
    print("🧪 Test 3: Production sans correspondance doit bloquer")
    
    # Profil avec une production différente
    profil = ProfilAgriculteur(
        profil_id="test-3",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.MARAICHAGE],  # ❌ Production différente
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide avec restriction de production
    criteres = CriteresEligibilite(
        regions=["National"],
        types_production=[TypeProduction.CEREALES]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-003",
        titre="Aide test sans correspondance production",
        organisme="Test Organisme",
        source="test",
        criteres=criteres,
        montant=montant,
        statut="active"
    )
    
    engine = MatchingEngine()
    resultat = engine.calculate_match(aide, profil)
    
    # Vérifications
    print(f"   Score: {resultat.score}")
    print(f"   Éligible: {resultat.eligible}")
    print(f"   Critères bloquants KO: {resultat.criteres_bloquants_ko}")
    
    # Ne doit PAS être éligible
    assert not resultat.eligible, "❌ ÉCHEC: Ne devrait pas être éligible"
    assert "Production" in resultat.criteres_bloquants_ko, \
        "❌ ÉCHEC: La production devrait être bloquante"
    
    print("   ✅ Test 3 réussi!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DES AMÉLIORATIONS DU MATCHING ENGINE")
    print("=" * 60)
    
    try:
        test_production_non_bloquante()
        test_production_avec_match()
        test_production_sans_match()
        
        print("=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DES TESTS: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
