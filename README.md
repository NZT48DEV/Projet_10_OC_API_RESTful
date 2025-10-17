# 🛡️ SoftDesk – API REST sécurisée

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django)
![Tests](https://img.shields.io/badge/tests-automatisés-success?logo=githubactions)
![Dependabot](https://img.shields.io/badge/Dependabot-active-brightgreen?logo=dependabot)

---

## 📖 Présentation du projet

**SoftDesk** est une API RESTful développée avec **Django REST Framework**.  
Elle permet de gérer des **projets collaboratifs** en ligne, avec la possibilité de créer des projets, d’ajouter des contributeurs, de signaler des issues (tickets) et d’y associer des commentaires.

L’objectif du projet est de proposer une API **sécurisée**, **maintenable** et **conforme aux standards RGPD**.  
Elle met en œuvre une **authentification JWT**, un **système de permissions personnalisé**, et une **architecture modulaire** pensée pour la scalabilité.

---

## 🚀 Fonctionnalités principales

- Gestion complète des **utilisateurs** et de leurs données (RGPD-friendly).
- Création et gestion de **projets collaboratifs**.
- Système de **tickets (issues)** avec priorités, statuts et assignation.
- Gestion des **commentaires** liés aux issues.
- Permissions personnalisées selon le rôle : auteur, contributeur, ou utilisateur anonyme.
- Sécurité renforcée via **JWT (JSON Web Token)**.
- **Tests unitaires automatisés** (Pytest + GitHub Actions CI).
- Suivi des mises à jour et vulnérabilités via **Dependabot**.

---

## 🧱 Technologies utilisées

- **Python 3.12**
- **Django 5.2**
- **Django REST Framework (DRF)**
- **djangorestframework-simplejwt**
- **Pytest**
- **Pre-commit** (Black, Isort, Flake8)
- **GitHub Actions** (tests automatiques)
- **Dependabot** (sécurité des dépendances)

---

## 🧩 Structure du projet

```
📦 10 Projet - Créez une API sécurisée RESTful
├── .github/                  # CI/CD & surveillance (Dependabot, GitHub Actions)
│   ├── workflows/
│   │   └── tests.yml
│   └── dependabot.yml
│
├── django-rest-api/                    # Code source principal de l'API
│   ├── manage.py
│   ├── config/                         # Configuration principale Django
│   ├── users/                          # Gestion des utilisateurs & RGPD
│   ├── projects/                       # Projets, contributeurs, issues, commentaires
│   ├── pytest.ini                      # Configuration des tests
│   ├── requirements.txt                # Dépendances Python du projet
│   └── SoftDesk_Progress_Report.md     # Journal d'avancement
│
├── .gitignore                # Exclusions Git (env, cache, migrations...)
├── README.md                 # Présentation du projet
├── requirements.txt          # Copie pour CI/CD (GitHub Actions)
└── .env/                     # Environnement virtuel local (non versionné)
```

---

## 🔐 Authentification

L’API utilise **JSON Web Token (JWT)** pour gérer l’authentification et la sécurité des endpoints.  
Chaque utilisateur peut obtenir un token via les endpoints `/api/token/` et `/api/token/refresh/` pour accéder aux routes protégées.

---

## 🧪 Qualité & Sécurité

- Pipeline **Pre-commit** : formatage, linting et tests avant chaque commit.
- **CI/CD** automatisé via GitHub Actions.
- Surveillance des dépendances avec **Dependabot**.
- Conformité **RGPD** : gestion de l’âge, droit à l’oubli, et consentement explicite.

---

## ⚙️ Installation rapide

```bash
git clone https://github.com/NZT48DEV/Projet_10_OC_API_RESTful.git
cd django-rest-api
python -m venv .env
source .env/bin/activate   # ou .env\Scripts\activate sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🧠 Auteur

👤 **NZT48DEV**  
🎓 Projet n°10 - Créez une API sécurisée RESTful en utilisant Django REST – Parcours Développeur d'application Python – *OpenClassrooms*

📧 Contact : [nzt48.dev@gmail.com](mailto:nzt48.dev@gmail.com)

---

## 🏁 Statut du projet

✅ Authentification et permissions implémentées  
✅ Tests unitaires automatisés  
✅ CI/CD GitHub Actions opérationnelle  
✅ Surveillance de sécurité active  
🕒 Pagination et documentation technique à venir
