# 🌾 AgriSubv

**Plateforme de correspondance des aides agricoles françaises**

AgriSubv aide les agriculteurs à identifier les subventions et aides auxquelles ils sont éligibles grâce à un questionnaire adaptatif intelligent. La plateforme croise le profil de l'exploitant (localisation, productions, statut, surfaces…) avec les aides disponibles issues d'Aides-Territoires et du programme PAC.

---

## 📋 Sommaire

- [Architecture](#-architecture)
- [Stack technique](#-stack-technique)
- [Installation rapide](#-installation-rapide)
- [Variables d'environnement](#-variables-denvironnement)
- [Endpoints API](#-endpoints-api)
- [Déploiement sur Render](#-déploiement-sur-render)
- [Structure du projet](#-structure-du-projet)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Utilisateur                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Frontend React / Vite (Render Static Site)       │
│  • Questionnaire adaptatif                                  │
│  • Affichage des résultats (éligibles / presque éligibles)  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST (VITE_API_URL)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Backend FastAPI / Python (Render Web Service)    │
│  • Moteur de matching (score + critères bloquants)          │
│  • Questionnaire adaptatif                                  │
│  • Endpoints de synchronisation                             │
└──────────┬────────────────────────┬────────────────────────-┘
           │                        │
           ▼                        ▼
┌──────────────────┐   ┌────────────────────────────────────┐
│     MongoDB      │   │         Scripts de sync            │
│  (Motor async)   │◄──│  • sync_aides_territoires_v2.py    │
│                  │   │    (API Aides-Territoires)          │
│  Collections :   │   │  • sync_datagouv_pac.py            │
│  • aides_v2      │   │    (DataGouv — PAC / DPB / MAEC…)  │
│  • sessions      │   └────────────────────────────────────┘
└──────────────────┘
```

---

## 🛠 Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18, Vite 5, Tailwind CSS, React Router 6 |
| Backend | FastAPI 0.115, Python 3.11, Uvicorn |
| Base de données | MongoDB (Motor async) |
| Sync données | aiohttp, Aides-Territoires API, DataGouv |
| Déploiement | Render (Web Service + Static Site) |

---

## ⚡ Installation rapide

### Prérequis

- Node.js ≥ 18
- Python ≥ 3.11
- Une instance MongoDB accessible (ex : MongoDB Atlas)

### 1. Cloner le dépôt

```bash
git clone https://github.com/Laz0ne/agrisubv.git
cd agrisubv
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt

# Copier et renseigner les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (voir section ci-dessous)

uvicorn server:app --reload --port 8000
```

L'API sera disponible sur `http://localhost:8000`.  
La documentation interactive Swagger est accessible sur `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install

# Créer le fichier .env local
echo "VITE_API_URL=http://localhost:8000" > .env

npm run dev
```

L'application sera disponible sur `http://localhost:8080`.

---

## 🔐 Variables d'environnement

### Backend (`backend/.env`)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `MONGO_URL` | Chaîne de connexion MongoDB | `mongodb+srv://user:pwd@cluster.mongodb.net/` |
| `DB_NAME` | Nom de la base de données | `agrisubv_db` |
| `AIDES_TERRITOIRES_API_TOKEN` | Token API Aides-Territoires | `votre_token_ici` |
| `CORS_ORIGINS` | Origines autorisées pour CORS | `https://votre-frontend.onrender.com` |

> Le fichier `backend/.env.example` contient un template prêt à l'emploi.

### Frontend (`frontend/.env`)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `VITE_API_URL` | URL de base de l'API backend | `https://votre-backend.onrender.com` |

---

## 📡 Endpoints API

Base URL : `/api`

### Santé & informations

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/health` | Vérification de santé du service |
| `GET` | `/api/stats/aides` | Statistiques de la base d'aides |

### Matching & éligibilité

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/matching` | Soumettre un profil agriculteur, obtenir les aides correspondantes |
| `POST` | `/api/eligibilite` | Vérifier l'éligibilité à une aide spécifique |

### Questionnaire adaptatif

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/questionnaire/config` | Récupérer la configuration du questionnaire (adaptatif ou statique) |
| `POST` | `/api/questionnaire/start` | Démarrer une session de questionnaire adaptatif |
| `POST` | `/api/questionnaire/answer` | Soumettre une réponse en mode adaptatif |
| `POST` | `/api/questionnaire/next` | Obtenir la prochaine question adaptative |
| `POST` | `/api/questionnaire/results` | Obtenir les résultats finaux du questionnaire adaptatif |

### Synchronisation des données

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/sync/aides-territoires` | Déclencher la synchronisation Aides-Territoires |
| `POST` | `/api/sync/datagouv-pac` | Déclencher la synchronisation des données PAC (DataGouv) |
| `POST` | `/api/sync/aides-territoires-v2` | Synchronisation Aides-Territoires v2 (avec authentification Bearer) |

### Administration & exploration

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/explore-aides-territoires` | Explorer les données brutes Aides-Territoires |
| `GET` | `/api/admin/export-aides-agricoles` | Exporter les données d'aides |
| `POST` | `/api/admin/analyze-criteria` | Analyser les critères d'une aide |

---

## 🚀 Déploiement sur Render

### Backend (Web Service)

1. Créer un **Web Service** sur [render.com](https://render.com)
2. Connecter le dépôt GitHub et sélectionner le dossier `backend/`
3. Configurer :
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Ajouter les variables d'environnement : `MONGO_URL`, `DB_NAME`, `AIDES_TERRITOIRES_API_TOKEN`, `CORS_ORIGINS`

### Frontend (Static Site)

1. Créer un **Static Site** sur Render
2. Connecter le dépôt GitHub et sélectionner le dossier `frontend/`
3. Configurer :
   - **Build Command** : `npm install && npm run build`
   - **Publish Directory** : `dist`
4. Ajouter la variable d'environnement : `VITE_API_URL` (URL du backend Render)

---

## 📁 Structure du projet

```
agrisubv/
├── backend/
│   ├── server.py                    # Application FastAPI principale
│   ├── matching_engine.py           # Moteur de matching agriculteur ↔ aides
│   ├── questionnaire_engine.py      # Logique du questionnaire adaptatif
│   ├── questionnaire_endpoint.py    # Routes questionnaire
│   ├── questionnaire_config.json    # Configuration des questions
│   ├── sync_aides_territoires_v2.py # Sync Aides-Territoires (v2, Bearer auth)
│   ├── sync_datagouv_pac.py         # Sync aides PAC depuis DataGouv
│   ├── models_v2.py                 # Modèles Pydantic
│   ├── explore_aides_endpoint.py    # Endpoint d'exploration
│   ├── export_aides_endpoint.py     # Endpoint d'export
│   ├── analyze_criteria_endpoint.py # Endpoint d'analyse des critères
│   ├── tests/                       # Tests automatisés
│   │   └── test_questionnaire_engine.py
│   ├── requirements.txt             # Dépendances Python
│   ├── Procfile                     # Commande de démarrage Render
│   ├── runtime.txt                  # Version Python (3.11)
│   └── .env.example                 # Template de configuration
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Application principale & routing
│   │   ├── icons.jsx                # Icônes SVG partagées
│   │   ├── components/
│   │   │   ├── DynamicQuestionnaire.jsx  # Questionnaire adaptatif
│   │   │   ├── ResultsPage.jsx           # Affichage des résultats
│   │   │   ├── ErrorBoundary.jsx         # Gestion des erreurs React
│   │   │   ├── home/                     # Page d'accueil
│   │   │   ├── results/                  # Composants résultats
│   │   │   └── layout/                   # Composants de mise en page
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── README.md
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. **Forker** le dépôt
2. Créer une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Effectuer vos modifications en respectant les conventions du projet (French UI strings, commentaires en français)
4. **Tester** vos changements :
   ```bash
   # Backend
   cd backend && python -m pytest tests/
   ```
5. Soumettre une **Pull Request** avec une description claire des changements

### Conventions

- Les chaînes de caractères de l'interface utilisateur sont en **français**
- Le backend suit les conventions **PEP 8**
- Le frontend utilise les conventions **React / ESLint** du projet
- Pas de breaking change sur le contrat API sans discussion préalable

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

*Développé avec ❤️ pour accompagner les agriculteurs français dans leurs démarches de financement.*
