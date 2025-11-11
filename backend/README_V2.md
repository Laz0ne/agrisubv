# AgriSubv V2 - Infrastructure pour Gestion Massive de Données

## Vue d'ensemble

Cette mise à jour V2 de AgriSubv prépare la plateforme pour gérer 1000+ aides agricoles avec des capacités de recherche et de matching avancées.

## Nouveaux Fichiers

### 1. `models_v2.py` (~400 lignes)
Modèles de données enrichis pour gérer des critères d'éligibilité complexes.

**Enums définis:**
- `TypeProduction` - 14 types (Céréales, Maraîchage, Viticulture, etc.)
- `TypeProjet` - 13 types (Installation, Conversion Bio, Modernisation, etc.)
- `StatutJuridique` - 9 types (EARL, GAEC, SCEA, etc.)
- `TypeMontant` - 5 types (Forfaitaire, Pourcentage, Surface, etc.)

**Modèles principaux:**
- `AideAgricoleV2` - Aide complète avec critères et montants structurés
- `CriteresEligibilite` - Critères géographiques, démographiques, économiques
- `MontantAide` - Montants avec différents types de calcul
- `ProfilAgriculteur` - Profil complet avec 30+ champs
- `ResultatMatching` - Résultat détaillé du matching avec explications

### 2. `matching_engine.py` (~300 lignes)
Moteur de matching avec scoring pondéré.

**Fonctionnalités:**
- Scoring sur 7 catégories de critères avec poids différents
- Critères bloquants vs non-bloquants
- Explications détaillées pour chaque critère (✅/❌)
- Seuil d'éligibilité à 60%
- Recommandations personnalisées

**Poids des critères:**
- Localisation: 25%
- Production: 20%
- Projet: 15%
- Statut: 10%
- Âge: 10%
- Surface: 10%
- Labels: 10%

### 3. `migrate_to_v2.py` (~200 lignes)
Script de migration des aides existantes vers V2.

**Fonctionnalités:**
- Mapping intelligent des anciens champs
- Détection automatique des productions/projets depuis les tags
- Validation post-migration
- Statistiques détaillées
- Sauvegarde dans collection `aides_v2`

**Usage:**
```bash
python migrate_to_v2.py
```

### 4. `sync_aides_territoires_v2.py` (~350 lignes)
Synchronisation optimisée avec Aides-Territoires.

**Fonctionnalités:**
- Récupération paginée asynchrone avec `aiohttp`
- Rate limiting (2 requêtes/seconde)
- Import par batch de 50 aides
- Normalisation intelligente vers modèle V2
- Mapping automatique des catégories vers TypeProjet
- Détection des productions par mots-clés
- Upsert pour éviter les doublons

**Usage:**
```bash
# Via l'API
POST /api/sync/aides-territoires-v2?max_pages=5

# Ou directement
python sync_aides_territoires_v2.py
```

## Améliorations du Serveur (`server.py`)

### Endpoint `/api/sync/status` (amélioré)
Retourne maintenant:
```json
{
  "total_aides": 29,
  "by_source": {
    "manual": 11,
    "aides_territoires": 0,
    "datagouv_pac": 18
  },
  "by_status": {
    "active": 29,
    "inactive": 0
  },
  "derniere_synchronisation": "2024-11-11T20:00:00Z"
}
```

### Endpoint `/api/aides` (amélioré)
Nouveaux filtres:
- `departement` - Filtrer par département
- `projet` - Filtrer par type de projet
- `montant_min` - Montant minimum
- `source` - Filtrer par source
- `q` - Recherche textuelle full-text
- `include_expired` - Inclure les aides expirées
- `skip` - Pagination
- `limit` - Limite de résultats

### Index MongoDB Optimisés
Créés automatiquement au démarrage:
- Index texte sur `titre` et `conditions_clefs`
- Index sur `regions`, `source`, `expiree`, `date_limite`
- Index sur `productions` et `criteres_mous_tags`
- Index V2 sur la collection `aides_v2`

## Tests Validés

### Tests de Base
✅ Import de tous les modules V2
✅ Création d'aides et profils
✅ Matching engine fonctionnel

### Tests de Matching Avancés
✅ Profil éligible (score 100/100)
✅ Rejet pour mauvaise région (critère bloquant)
✅ Rejet pour mauvaise production (critère bloquant)
✅ Rejet pour surface insuffisante (critère bloquant)

## Migration des Données Existantes

Pour migrer les 29 aides existantes vers V2:

```bash
cd backend
python migrate_to_v2.py
```

Cela va:
1. Récupérer les aides de la collection `aides`
2. Les normaliser vers le modèle V2
3. Détecter automatiquement les productions et projets
4. Sauvegarder dans la collection `aides_v2`
5. Afficher des statistiques détaillées

## Compatibilité

✅ **Rétrocompatibilité:** Les anciens endpoints continuent de fonctionner
✅ **Collections séparées:** `aides` et `aides_v2` coexistent
✅ **Migration sans interruption:** Aucun impact sur le service existant

## Prochaines Étapes

1. Migrer les données existantes vers V2
2. Importer des aides depuis Aides-Territoires
3. Tester le matching engine avec des profils réels
4. Créer des endpoints V2 pour l'utilisation du matching
5. Migrer progressivement le frontend vers V2

## Performance et Scalabilité

- ✅ Index MongoDB optimisés pour recherche rapide
- ✅ Rate limiting pour respecter les limites d'API externes
- ✅ Import par batch pour gérer de gros volumes
- ✅ Validation Pydantic pour assurer la qualité des données
- ✅ Support asynchrone pour les opérations I/O

## Sécurité

- Validation stricte des données avec Pydantic
- Gestion des erreurs robuste
- Rate limiting pour éviter les abus
- Pas de données sensibles exposées
