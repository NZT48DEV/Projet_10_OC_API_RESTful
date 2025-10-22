⚠️ **Note :**
Les informations présentées dans ce rapport sont destinées exclusivement à l’évaluation du projet.  
Elles ne seraient pas rendues publiques dans un contexte professionnel pour préserver la sécurité et la confidentialité.

# SoftDesk – API REST sécurisée

## ✅ Avancement du projet

### 🧱 Refonte et validation des tests
- [x] Création d’un **fichier de tests fonctionnels** complet : `projects/tests/test_functional_api.py`.
- [x] Correction et uniformisation des anciens tests (`projects/tests/tests_permissions.py`, `users/tests/tests_permissions.py`).
- [x] Ajout systématique de l’en-tête `HTTP_ACCEPT="application/json"` pour forcer le retour JSON depuis DRF.
- [x] Gestion des cas HTML avec fallback automatique (`parse_response()`).
- [x] Résolution des erreurs `NoneType.lower()` et `Content-Type: text/html`.
- [x] Vérification du comportement complet des endpoints CRUD (`Projects`, `Contributors`, `Issues`, `Comments`).
- [x] Validation des règles RGPD sur les utilisateurs (`test_authenticated_user_can_list_self` corrigé).

### 🧩 Améliorations techniques
- [x] Refactorisation du code de test pour une **robustesse accrue** et une meilleure lisibilité.
- [x] Utilisation des fixtures Pytest et de `APIClient` pour isoler chaque scénario.
- [x] Tests d’intégration complets validés : `pytest -v` → **100 % passed**.
- [x] Renforcement du typage et des contrôles dans les serializers et views.

### 🧪 Vérification du comportement des ViewSets
- [x] `ProjectViewSet` → création automatique du contributeur auteur ✅
- [x] `ContributorViewSet` → pagination, regroupement par projet ✅
- [x] `IssueViewSet` → permissions cohérentes et messages d’erreur clairs ✅
- [x] `CommentViewSet` → suppression et création conformes ✅

### 🧰 Automatisation et qualité
- [x] Validation complète du pipeline `pre-commit` : `black`, `isort`, `flake8`, `pytest`.
- [x] CI/CD GitHub Actions exécutée automatiquement sur `feature/securite`.
- [x] Rapport de progression mis à jour (`SoftDesk_Progress_Report.md`).
- [x] **README.md** refondu avec badges, structure claire et instructions de test.

---

## 🚀 Résumé global
| Domaine | Statut |
|----------|--------|
| Authentification JWT | ✅ Stable |
| Permissions et sécurité | ✅ Validées |
| Tests unitaires et fonctionnels | ✅ 100 % success |
| RGPD (droits et confidentialité) | ✅ Conforme |
| CI/CD et qualité de code | ✅ Automatisée |
| Pagination et documentation | 🕒 À finaliser |

---

## 🧭 Étapes suivantes
- [ ] Ajouter la **documentation Swagger/OpenAPI** pour les endpoints REST.
- [ ] Mettre en place la **pagination DRF** sur les listes `projects`, `issues` et `comments`.
- [ ] Générer un **rapport HTML pytest** à inclure dans la soutenance.
- [ ] Préparer la **soutenance finale** avec démonstration des tests passés.
