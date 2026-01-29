"""
Test pour vérifier les améliorations des labels requis
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from models_v2 import (
    AideAgricoleV2, ProfilAgriculteur, CriteresEligibilite, MontantAide,
    TypeProduction, StatutJuridique, TypeMontant
)
from matching_engine import MatchingEngine


def test_labels_requis_explicites():
    """
    Test que les labels manquants sont explicitement listés
    """
    print("\n🧪 Test: Labels requis manquants doivent être explicites")
    
    # Profil sans les labels requis
    profil = ProfilAgriculteur(
        profil_id="test-labels-1",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.CEREALES],
        labels=["Label Rouge"],  # N'a pas Agriculture Biologique ni HVE
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide qui requiert Agriculture Biologique et HVE
    criteres = CriteresEligibilite(
        regions=["National"],
        labels_requis=["Agriculture Biologique", "HVE"]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-LABELS-001",
        titre="Aide test avec labels requis",
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
    print(f"   Détails critères: {len(resultat.details_criteres)}")
    
    # Trouver le détail des labels requis
    labels_detail = next(
        (d for d in resultat.details_criteres if "Labels requis" in d.nom),
        None
    )
    
    assert labels_detail is not None, "❌ ÉCHEC: Détail des labels requis manquant"
    
    print(f"   📝 Explication: {labels_detail.explication}")
    
    # Vérifier que l'explication contient les labels manquants
    assert "Label(s) manquant(s)" in labels_detail.explication, \
        "❌ ÉCHEC: L'explication devrait mentionner les labels manquants"
    
    # Vérifier que les labels manquants sont listés
    assert "Agriculture Biologique" in labels_detail.explication, \
        "❌ ÉCHEC: Agriculture Biologique devrait être dans la liste des labels manquants"
    
    assert "HVE" in labels_detail.explication, \
        "❌ ÉCHEC: HVE devrait être dans la liste des labels manquants"
    
    # Vérifier que "Cette aide nécessite" est dans l'explication
    assert "Cette aide nécessite" in labels_detail.explication, \
        "❌ ÉCHEC: L'explication devrait mentionner les labels requis par l'aide"
    
    print("   ✅ Les labels manquants sont explicitement listés!")
    print("   ✅ Test réussi!\n")


def test_labels_requis_presents():
    """
    Test que les labels présents sont correctement reconnus
    """
    print("🧪 Test: Labels requis présents doivent donner des points")
    
    # Profil avec les labels requis
    profil = ProfilAgriculteur(
        profil_id="test-labels-2",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.CEREALES],
        labels=["Agriculture Biologique", "HVE", "Label Rouge"],  # A tous les labels requis
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide qui requiert Agriculture Biologique
    criteres = CriteresEligibilite(
        regions=["National"],
        labels_requis=["Agriculture Biologique"]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-LABELS-002",
        titre="Aide test avec labels requis présents",
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
    
    # Trouver le détail des labels requis
    labels_detail = next(
        (d for d in resultat.details_criteres if "Labels requis" in d.nom),
        None
    )
    
    assert labels_detail is not None, "❌ ÉCHEC: Détail des labels requis manquant"
    assert labels_detail.valide, "❌ ÉCHEC: Les labels requis devraient être validés"
    assert labels_detail.points > 0, "❌ ÉCHEC: Devrait avoir des points pour les labels"
    
    print(f"   📝 Explication: {labels_detail.explication}")
    assert "✅" in labels_detail.explication, \
        "❌ ÉCHEC: L'explication devrait indiquer que les labels sont présents"
    
    print("   ✅ Les labels requis sont correctement reconnus!")
    print("   ✅ Test réussi!\n")


def test_labels_bonus():
    """
    Test que les labels bonus fonctionnent correctement
    """
    print("🧪 Test: Labels bonus doivent donner des points supplémentaires")
    
    # Profil avec certains labels bonus
    profil = ProfilAgriculteur(
        profil_id="test-labels-3",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.CEREALES],
        labels=["HVE", "Label Rouge"],  # A 2 des 3 labels bonus
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide avec labels bonus
    criteres = CriteresEligibilite(
        regions=["National"],
        labels_bonus=["HVE", "Label Rouge", "AOC"]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-LABELS-003",
        titre="Aide test avec labels bonus",
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
    
    # Trouver le détail des labels bonus
    labels_bonus_detail = next(
        (d for d in resultat.details_criteres if "Labels bonus" in d.nom),
        None
    )
    
    assert labels_bonus_detail is not None, "❌ ÉCHEC: Détail des labels bonus manquant"
    assert labels_bonus_detail.valide, "❌ ÉCHEC: Les labels bonus devraient être validés"
    assert labels_bonus_detail.points > 0, "❌ ÉCHEC: Devrait avoir des points pour les labels bonus"
    
    print(f"   📝 Explication: {labels_bonus_detail.explication}")
    assert "HVE" in labels_bonus_detail.explication and "Label Rouge" in labels_bonus_detail.explication, \
        "❌ ÉCHEC: Les labels bonus obtenus devraient être listés"
    
    print("   ✅ Les labels bonus fonctionnent correctement!")
    print("   ✅ Test réussi!\n")


def test_labels_bonus_manquants():
    """
    Test que les labels bonus manquants sont suggérés
    """
    print("🧪 Test: Labels bonus manquants doivent être suggérés")
    
    # Profil sans labels bonus
    profil = ProfilAgriculteur(
        profil_id="test-labels-4",
        region="Bretagne",
        departement="35",
        statut_juridique=StatutJuridique.EARL,
        sau_totale=50.0,
        productions=[TypeProduction.CEREALES],
        labels=[],  # Aucun label
        age=35,
        jeune_agriculteur=False
    )
    
    # Aide avec labels bonus
    criteres = CriteresEligibilite(
        regions=["National"],
        labels_bonus=["HVE", "Label Rouge", "AOC"]
    )
    
    montant = MontantAide(
        type_montant=TypeMontant.POURCENTAGE,
        taux_max=40
    )
    
    aide = AideAgricoleV2(
        aid_id="TEST-LABELS-004",
        titre="Aide test sans labels bonus",
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
    
    # Trouver le détail des labels bonus
    labels_bonus_detail = next(
        (d for d in resultat.details_criteres if "Labels bonus" in d.nom),
        None
    )
    
    assert labels_bonus_detail is not None, "❌ ÉCHEC: Détail des labels bonus manquant"
    
    print(f"   📝 Explication: {labels_bonus_detail.explication}")
    
    # Vérifier que les labels bonus possibles sont suggérés
    assert "💡" in labels_bonus_detail.explication, \
        "❌ ÉCHEC: Les labels bonus devraient être suggérés avec 💡"
    
    assert "Labels bonus possibles" in labels_bonus_detail.explication, \
        "❌ ÉCHEC: L'explication devrait mentionner les labels bonus possibles"
    
    print("   ✅ Les labels bonus manquants sont suggérés!")
    print("   ✅ Test réussi!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DES AMÉLIORATIONS DES LABELS")
    print("=" * 60)
    
    try:
        test_labels_requis_explicites()
        test_labels_requis_presents()
        test_labels_bonus()
        test_labels_bonus_manquants()
        
        print("=" * 60)
        print("✅ TOUS LES TESTS DES LABELS SONT PASSÉS!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DES TESTS: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
