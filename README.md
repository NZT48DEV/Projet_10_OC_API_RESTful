# 🛡️ SoftDesk – API REST sécurisée

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django)
![Tests](https://img.shields.io/badge/tests-automatisés-success?logo=githubactions)
![Dependabot](https://img.shields.io/badge/Dependabot-active-brightgreen?logo=dependabot)

---

## 📖 Présentation du projet

**SoftDesk** est une **API RESTful sécurisée** développée avec **Django REST Framework**.  
Elle permet la gestion de **projets collaboratifs** avec un système de **tickets (issues)** et de **commentaires**, dans une architecture claire et maintenable.

Conçue pour être **robuste**, **performante** et **conforme aux standards de sécurité**, cette API illustre les bonnes pratiques de développement back-end moderne :  
authentification JWT, permissions personnalisées, validations métier, pagination, cache applicatif et tests automatisés.

> 🧠 Ce projet a été réalisé dans le cadre de la formation OpenClassrooms *« Développeur d’application Python »*, projet n°10 :  
> **Créez une API sécurisée RESTful avec Django REST Framework**.

---

## 🚀 Fonctionnalités principales

- 🔐 **Authentification JWT** (connexion, renouvellement, accès sécurisé)
- 👥 **Gestion des utilisateurs** et conformité **RGPD**
- 🧱 **Création et gestion de projets collaboratifs**
- 🧩 **Ajout et gestion de contributeurs**
- 🐞 **Système de tickets (issues)** avec priorité, statut et assignation
- 💬 **Commentaires** associés aux issues
- ⚙️ **Permissions personnalisées** (auteur, contributeur, lecture seule)
- 🧪 **Tests unitaires automatisés** (Pytest + GitHub Actions)
- 🧰 **Pipeline Pre-commit** (Black, Flake8, Isort)
- 📦 **Mise en cache** des requêtes fréquentes pour gain de performance
- 🔍 **Surveillance de sécurité** via **Dependabot**

---

## 🧱 Technologies utilisées

| Catégorie | Technologies |
|------------|---------------|
| Langage | Python 3.12 |
| Framework | Django 5.2 |
| API REST | Django REST Framework (DRF) |
| Authentification | djangorestframework-simplejwt |
| Configuration | python-decouple |
| Tests | Pytest |
| Qualité de code | Black • Isort • Flake8 • Autopep8 |
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

## 🔒 Authentification JWT

L’API utilise le système **JSON Web Token (JWT)** pour gérer les connexions sécurisées.

Endpoints disponibles :
- `POST /api/token/` → obtention du token
- `POST /api/token/refresh/` → renouvellement
- `GET /api/users/<id_user>/` → accès aux informations personnelles (token requis)

---

## 🧪 Qualité et sécurité du code

### 🔹 Pipeline Pre-commit
Avant chaque commit :
- **Black** reformate le code (PEP8)
- **Isort** trie les imports
- **Flake8** vérifie les erreurs et la complexité
- **Pytest** exécute les tests automatisés

### 🔹 Intégration continue
- **GitHub Actions** exécute automatiquement la suite de tests à chaque push.
- **Dependabot** surveille les dépendances et alerte sur les vulnérabilités.

---

## ⚡ Optimisations techniques

SoftDesk a été pensé pour offrir des **performances élevées** et une **gestion efficace des ressources** :

### 🧩 Optimisation des requêtes SQL
- Utilisation de **`select_related`** et **`prefetch_related`** pour précharger les relations et éviter le problème des *N+1 queries*.
- Application de **`distinct()`** sur les requêtes combinant plusieurs jointures.
- Réduction du nombre de hits base de données grâce à une structure de queryset optimisée.

### 💾 Mise en cache intelligente
- Mise en place d’un cache **granulaire par utilisateur et par projet** (via `django.core.cache`).
- **Invalidation automatique** du cache lors de la création ou suppression d’un élément (projet, issue, commentaire).
- **Backend file-based** en environnement de développement, facilement remplaçable par **Redis** en production.

### 🔄 Transactions et intégrité
- Usage de **`transaction.atomic()`** pour garantir la cohérence des écritures simultanées.
- Gestion explicite des erreurs `IntegrityError` et `ValidationError`.

### 🧼 Optimisation du code source
- Code uniformisé et formaté automatiquement (Black, Isort, Flake8).
- Découpage logique des viewsets, sérializers et permissions pour respecter le **principe de responsabilité unique (SRP)**.
- Suppression des doublons et simplification des conditions redondantes.

---

## 🧠 Auteur

👤 **NZT48DEV**  
🎓 Projet n°10 - Créez une API sécurisée RESTful en utilisant Django REST Framework  
📚 Parcours : *Développeur d’application Python – OpenClassrooms*  
📧 Contact : [nzt48.dev@gmail.com](mailto:nzt48.dev@gmail.com)

---

## 🏁 Statut du projet

✅ Authentification et permissions terminées  
✅ Tests unitaires complets  
✅ CI/CD GitHub Actions fonctionnelle  
✅ Mise en cache et optimisation SQL opérationnelles  
🕒 Documentation complémentaire à venir

---

> ⚠️ **Note :**  
> Les informations techniques détaillées dans ce projet (structure, configuration, tests, cache, etc.) sont fournies **uniquement à des fins pédagogiques** dans le cadre de l’évaluation.  
> Dans un environnement professionnel, ces éléments ne seraient pas rendus publics afin de préserver la **sécurité** et la **confidentialité** du code source.
