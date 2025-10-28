
# 🛡️ SoftDesk – API REST sécurisée avec OAuth2

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django)
![OAuth2](https://img.shields.io/badge/Auth-OAuth2-orange?logo=security)
![Tests](https://img.shields.io/badge/tests-automatisés-success?logo=pytest)
![Dependabot](https://img.shields.io/badge/Dependabot-active-brightgreen?logo=dependabot)

---

## 📖 Présentation du projet

**SoftDesk** est une **API RESTful sécurisée** basée sur **OAuth2**, développée avec **Django REST Framework** et **Django OAuth Toolkit**.  
Elle permet la gestion de **projets collaboratifs**, **issues**, et **commentaires** avec un contrôle d’accès robuste et conforme aux normes de sécurité modernes.

> 🧠 Ce projet a été réalisé dans le cadre de la formation OpenClassrooms *« Développeur d’application Python »*, projet n°10 :  
> **Créez une API sécurisée RESTful avec Django REST Framework**.

---

## 🚀 Fonctionnalités principales

- 🔐 **Authentification OAuth2 complète** (`/o/token/`, `/o/revoke_token/`, `/o/authorize/`)
- 👥 **Gestion des utilisateurs** et conformité **RGPD**
- 🧱 **Création et gestion de projets collaboratifs**
- 🧩 **Ajout et gestion de contributeurs**
- 🐞 **Système d’issues (tickets)** avec priorité, statut et assignation
- 💬 **Commentaires** associés aux issues
- ⚙️ **Permissions personnalisées** (auteur, contributeur, lecture seule)
- 💾 **Mise en cache granulaire** (par utilisateur et projet)
- 🧪 **Tests unitaires** (Pytest)
- 🧰 **Pipeline Pre-commit** (Black, Flake8, Isort)
- 🧱 **CI/CD GitHub Actions**
- 📘 **Documentation interactive** avec Swagger & ReDoc (via `drf-spectacular`)
- 🔍 **Surveillance sécurité** via **Dependabot**

---

## 🧱 Technologies utilisées

| Catégorie | Technologies |
|------------|---------------|
| Langage | Python 3.12 |
| Framework | Django 5.2 |
| API REST | Django REST Framework |
| Authentification | OAuth2 (Django OAuth Toolkit) |
| Config | python-decouple |
| Tests | Pytest |
| Qualité de code | Black • Isort • Flake8 |
| CI/CD | GitHub Actions |
| Sécurité | Dependabot |

---

## 🧩 Structure du projet

```
📦 10 Projet - Créez une API sécurisée RESTful
├── django-rest-api/
│   ├── api_auth                        # Gestion inscriptions / tokens
│   ├── config/                         # Configuration principale Django
│   ├── projects/                       # Projets, contributeurs, issues, commentaires
│   ├── users/                          # Gestion des utilisateurs & RGPD
│   ├── utils/                          # Outils (cache, fonctions utilitaires)
│   ├── manage.py                       # Point d’entrée Django
│   └── requirements.txt                # Dépendances du projet
│
├── .pre-commit-config.yaml             # Pipeline de qualité (Black, Flake8, Isort)
├── pytest.ini                          # Configuration Pytest
├── pyproject.toml                      # Configuration de formatage
├── .flake8                             # Règles du linter
├── .github/workflows/tests.yml         # Intégration continue
├── README.md                           # Présentation du projet
└── SoftDesk_Progress_Report.md         # Journal d’avancement du projet
```

---

---

## ⚙️ Installation avec Pipenv

```bash
# Cloner le projet
git clone https://github.com/NZT48DEV/Projet_10_OC_API_RESTful.git

# Installer pipenv (si non installé)
pip install pipenv

# Créer et activer l’environnement virtuel
pipenv install -r requirements.txt
pipenv shell

# Appliquer les migrations et lancer le serveur
pipenv run python django-rest-api/manage.py migrate
pipenv run python django-rest-api/manage.py runserver

# Audit de sécurité 
pipenv check

```

---

## 🔐 Configuration de la clé secrète Django

Pour sécuriser l’application, la clé `SECRET_KEY` est stockée dans un fichier `.env` non versionné.

### Étapes de configuration :

1. **Générer une clé secrète :**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Créer le fichier `.env` dans `django-rest-api/` :**
   ```bash
   SECRET_KEY=django-insecure-<votre_cle_secrete>
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

3. **Lancer le serveur :**
   ```bash
   python manage.py runserver
   ```

---

## 🔐 Authentification OAuth2

SoftDesk implémente le **grant type "Resource Owner Password Credentials"**, idéal pour les clients de confiance comme Postman.

### 🔸 Étapes d’authentification

1. **Créer une application OAuth2** dans l’administration Django :  
   - `client_type` : Confidential  
   - `authorization_grant_type` : Password grant  
   - Copier le `client_id` et `client_secret`.

2. **Obtenir un token d’accès :**

   ```bash
   POST /o/token/
   Content-Type: application/x-www-form-urlencoded

   grant_type=password
   username=<nom_utilisateur>
   password=<mot_de_passe>
   client_id=<votre_client_id>
   client_secret=<votre_client_secret>
   ```

   → Réponse :
   ```json
   {
       "access_token": "...",
       "refresh_token": "...",
       "token_type": "Bearer",
       "expires_in": 36000
   }
   ```

3. **Rafraîchir le token :**
   ```bash
   POST /o/token/
   grant_type=refresh_token
   refresh_token=<votre_refresh_token>
   client_id=<client_id>
   client_secret=<client_secret>
   ```

4. **Utiliser le token dans Postman :**
   ```http
   Authorization: Bearer <access_token>
   ```

---

## 📘 Documentation API (Swagger / ReDoc)

La documentation interactive est générée automatiquement par
**drf-spectacular** à partir des vues, serializers et permissions.

### Endpoints disponibles

| Type | URL | Description |
|------|-----|-------------|
| **Swagger UI** | `http://127.0.0.1:8000/api/docs/` | Interface interactive |
| **ReDoc** | `http://127.0.0.1:8000/api/redoc/` | Documentation hiérarchisée |
| **Schéma brut (OpenAPI JSON)** | `http://127.0.0.1:8000/api/schema/` | OpenAPI 3.0 JSON |

> 💡 Astuce :
> - Swagger est idéal pour **tester** les endpoints.
> - ReDoc est idéal pour **lire** et **naviguer** proprement.

---

## 🌐 Endpoints de l’API

### 🔑 Authentification (`/api-auth/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `POST` | `/o/token/` | Obtenir un token d’accès (grant_type=password) |
| `POST` | `/o/token/` | Rafraîchir un token expiré (grant_type=refresh_token) |
| `POST` | `/api-auth/register/` | Créer un compte utilisateur |
| `POST` | `/api-auth/login/` | Connexion via interface HTML |
| `GET` | `/api-auth/logout/` | Déconnexion et redirection |
| `GET` | `/api-auth/` | Page d’accueil de l’API |

---

### 👥 Utilisateurs (`/api/users/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `GET` | `/api/users/` | Liste de tous les utilisateurs |
| `GET` | `/api/users/<id>/` | Détails d’un utilisateur |
| `GET` | `/api/users/me/` | Récupère le profil connecté |
| `DELETE` | `/api/users/<id>/` | Supprimer un utilisateur (admin uniquement) |

---

### 🧱 Projets (`/api/projects/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `GET` | `/api/projects/` | Liste des projets accessibles |
| `POST` | `/api/projects/` | Créer un projet |
| `GET` | `/api/projects/<id>/` | Détails d’un projet |
| `DELETE` | `/api/projects/<id>/` | Supprimer un projet (auteur uniquement) |

---

### 🤝 Contributeurs (`/api/contributors/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `GET` | `/api/contributors/` | Liste des contributeurs groupés par projet |
| `POST` | `/api/contributors/` | Ajouter un contributeur à un projet |
| `DELETE` | `/api/contributors/<id>/` | Supprimer un contributeur du projet |

> Lorsqu’un contributeur est ajouté, son rôle est automatiquement défini :  
> - Auteur : `"Auteur et Contributeur du projet"`  
> - Autre utilisateur : `"Contributeur"`

---

### 🐞 Issues (`/api/issues/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `GET` | `/api/issues/` | Liste des issues (option `?project=<id>` pour filtrer) |
| `POST` | `/api/issues/` | Créer une issue dans un projet |
| `GET` | `/api/issues/<id>/` | Détails d’une issue |
| `DELETE` | `/api/issues/<id>/` | Supprimer une issue |
| `PATCH` | `/api/issues/<id>/` | Modifier une issue |

> ⚙️ Lors de la création, seul un contributeur du projet peut être assigné.

---

### 💬 Commentaires (`/api/comments/`)

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| `GET` | `/api/comments/` | Liste des commentaires accessibles |
| `POST` | `/api/comments/` | Ajouter un commentaire à une issue |
| `GET` | `/api/comments/<id>/` | Détails d’un commentaire |
| `DELETE` | `/api/comments/<id>/` | Supprimer un commentaire |
| `PATCH` | `/api/comments/<id>/` | Modifier un commentaire |

> 🚫 La duplication de commentaires identiques sur la même issue est empêchée.

---

## ⚡ Optimisations techniques

- ⚙️ **select_related / prefetch_related** : requêtes SQL optimisées  
- 💾 **Cache multi-niveaux** : invalidation automatique après création ou suppression  
- 🧩 **Transactions atomiques** : cohérence des écritures simultanées  
- 🔒 **Sécurité avancée** :
  - Authentification OAuth2 (RFC 6749)
  - Permissions hiérarchisées
  - Gestion des sessions et CSRF désactivées sur API pure
- 🧼 **Qualité & CI/CD** :
  - Linting (Black, Flake8, Isort)
  - Tests automatisés (Pytest + OAuth2)
  - Exécution GitHub Actions à chaque push

---

## 🧪 Lancer les tests

```bash
pytest -v
```

Les tests couvrent :
- Authentification OAuth2 (`/o/token/`, `/o/token/refresh/`)
- Inscription / connexion utilisateur
- Gestion des projets / issues / commentaires
- Mise en cache et invalidation automatique

---

## 🧠 Auteur

👤 **NZT48DEV**  
🎓 Projet n°10 – OpenClassrooms – *Développeur d’application Python*  
📧 Contact : [nzt48.dev@gmail.com](mailto:nzt48.dev@gmail.com)

---

> ⚠️ **Note :**  
> Les informations techniques et la configuration OAuth2 présentes ici sont fournies à des fins pédagogiques.  
> En environnement professionnel, elles ne seraient **jamais rendues publiques** afin de préserver la **sécurité des identifiants clients** et des **tokens**.
