
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

## ⚙️ Installation rapide

```bash
git clone https://github.com/NZT48DEV/Projet_10_OC_API_RESTful.git
cd django-rest-api
python -m venv .env
source .env/bin/activate  # ou .env\Scripts\activate sous Windows
pip install -r requirements.txt
python manage.py migrate
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
