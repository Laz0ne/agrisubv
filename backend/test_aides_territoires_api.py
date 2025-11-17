"""
Script de test pour l'API Aides-Territoires
Objectif : Explorer l'API et identifier les aides agricoles
"""

import requests
import json
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "https://aides-territoires.beta.gouv.fr/api"
API_TOKEN = "92de4853a490b73a75567d7fb66955d62babdd0c9328f67c12a9f2f4266b8ecb"  # Ta clé API

# Headers pour authentification
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def test_api_connection():
    """Teste la connexion à l'API"""
    print("🔍 Test de connexion à l'API Aides-Territoires...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", headers=HEADERS)
        response.raise_for_status()
        
        endpoints = response.json()
        print("✅ Connexion réussie !")
        print(f"\n📋 Endpoints disponibles : {len(endpoints)}")
        print(json.dumps(endpoints, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def explore_audiences():
    """Liste tous les types de bénéficiaires disponibles"""
    print("\n\n👥 Exploration des audiences (bénéficiaires)...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/aids/audiences/", headers=HEADERS)
        response.raise_for_status()
        
        audiences = response.json()
        print(f"✅ {len(audiences)} types de bénéficiaires trouvés :")
        
        for audience in audiences:
            print(f"  - {audience}")
        
        # Chercher les audiences agricoles
        agri_audiences = [a for a in audiences if any(
            keyword in str(a).lower() 
            for keyword in ["agricul", "farmer", "rural", "exploit"]
        )]
        
        print(f"\n🌾 Audiences agricoles identifiées : {len(agri_audiences)}")
        for audience in agri_audiences:
            print(f"  ✅ {audience}")
        
        return agri_audiences
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

def explore_categories():
    """Liste toutes les catégories d'aides disponibles"""
    print("\n\n📂 Exploration des catégories...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/categories/", headers=HEADERS)
        response.raise_for_status()
        
        categories = response.json()
        print(f"✅ {len(categories)} catégories trouvées")
        
        # Afficher toutes les catégories
        for cat in categories:
            print(f"  - {cat.get('name', cat)}")
        
        # Catégories agricoles
        agri_categories = [c for c in categories if any(
            keyword in str(c).lower() 
            for keyword in ["agricul", "rural", "environment", "bio", "foret", "eau"]
        )]
        
        print(f"\n🌾 Catégories agricoles identifiées : {len(agri_categories)}")
        for cat in agri_categories:
            print(f"  ✅ {cat.get('name', cat)}")
        
        return agri_categories
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

def search_agricultural_aids(limit=10):
    """Recherche des aides agricoles avec filtres"""
    print(f"\n\n🔎 Recherche des {limit} premières aides agricoles...")
    
    # Mots-clés de recherche
    keywords = [
        "agricole", "agriculteur", "exploitation",
        "élevage", "bio", "installation"
    ]
    
    all_aids = []
    
    for keyword in keywords[:3]:  # Tester avec les 3 premiers mots-clés
        print(f"\n🔍 Recherche avec mot-clé : '{keyword}'")
        
        try:
            params = {
                "text": keyword,
                "targeted_audiences": "farmer",  # Filtrer par audience agriculteur
                "perimeter": "france",
                "page_size": limit
            }
            
            response = requests.get(
                f"{API_BASE_URL}/aids/",
                headers=HEADERS,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            print(f"  ✅ {len(results)} aides trouvées")
            
            all_aids.extend(results)
            
        except Exception as e:
            print(f"  ❌ Erreur : {e}")
    
    # Dédupliquer par ID
    unique_aids = {aid['id']: aid for aid in all_aids}.values()
    
    print(f"\n📊 Total : {len(unique_aids)} aides agricoles uniques")
    
    return list(unique_aids)

def analyze_aid_structure(aids: List[Dict]):
    """Analyse la structure des aides pour comprendre les critères d'éligibilité"""
    print("\n\n🔬 Analyse de la structure des aides...")
    
    if not aids:
        print("❌ Aucune aide à analyser")
        return
    
    # Analyser la première aide en détail
    first_aid = aids[0]
    
    print(f"\n📋 Exemple d'aide : {first_aid.get('name', 'N/A')}")
    print(f"ID : {first_aid.get('id', 'N/A')}")
    print(f"URL : {first_aid.get('url', 'N/A')}")
    
    print("\n🔑 Champs disponibles :")
    for key in sorted(first_aid.keys()):
        value = first_aid[key]
        value_type = type(value).__name__
        
        # Afficher un aperçu de la valeur
        if isinstance(value, str) and len(value) > 100:
            preview = value[:100] + "..."
        elif isinstance(value, list) and len(value) > 3:
            preview = f"[{len(value)} éléments]"
        else:
            preview = value
        
        print(f"  - {key} ({value_type}): {preview}")
    
    # Analyser les critères d'éligibilité communs
    print("\n🎯 Critères d'éligibilité détectés :")
    
    eligibility_fields = [
        "eligibility", "targeted_audiences", "mobilization_steps",
        "destinations", "aid_types", "perimeter", "recurrence"
    ]
    
    for field in eligibility_fields:
        if field in first_aid:
            print(f"  ✅ {field}: {first_aid[field]}")
    
    # Statistiques sur tous les champs
    print("\n📊 Statistiques sur tous les champs :")
    field_counts = {}
    for aid in aids:
        for key in aid.keys():
            field_counts[key] = field_counts.get(key, 0) + 1
    
    for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(aids)) * 100
        print(f"  - {field}: {count}/{len(aids)} ({percentage:.1f}%)")
    
    # Sauvegarder un échantillon complet en JSON
    sample_file = "backend/sample_aides_agricoles.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(aids[:5], f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Échantillon sauvegardé dans : {sample_file}")

def main():
    """Fonction principale"""
    print("=" * 80)
    print("🌾 EXPLORATION API AIDES-TERRITOIRES POUR AGRICULTEURS")
    print("=" * 80)
    
    # 1. Test de connexion
    if not test_api_connection():
        return
    
    # 2. Explorer les audiences
    audiences = explore_audiences()
    
    # 3. Explorer les catégories
    categories = explore_categories()
    
    # 4. Rechercher des aides agricoles
    aids = search_agricultural_aids(limit=20)
    
    # 5. Analyser la structure
    if aids:
        analyze_aid_structure(aids)
    
    print("\n" + "=" * 80)
    print("✅ Exploration terminée !")
    print("=" * 80)


if __name__ == "__main__":
    main()