⚠️ **Note :**  
Les informations présentées dans ce rapport (structure du projet, configuration, détails techniques et processus de développement) sont fournies exclusivement dans le cadre de l’évaluation.  
Dans un environnement de développement professionnel, ces éléments ne seraient pas rendus publics afin de préserver la confidentialité, la sécurité et la maintenabilité du projet.

# SoftDesk – API REST sécurisée

## ✅ Avancement du projet

### ⚙️ Mise en place du socle du projet
- [x] Initialisation du projet **Django** : création du dossier principal `django-rest-api`.
- [x] Création de l’application **`users`** dédiée à la gestion des utilisateurs.
- [x] Définition du modèle personnalisé **`User`** :
  - Champs spécifiques : `age`, `can_be_contacted`, `can_data_be_shared`, `created_time`.
  - Surcharge de la méthode `save()` pour forcer la validation complète des données.
  - Implémentation de la méthode `__str__()` pour un affichage lisible en console et en admin.
- [x] Mise en place de la fonction **`validate_age`** (conformité RGPD) imposant un âge minimal de 15 ans.
- [x] Configuration du modèle utilisateur personnalisé via `AUTH_USER_MODEL = "users.User"` dans `config/settings.py`.

---

### 🧩 Gestion et exposition de l’API utilisateur
- [x] Création du **`UserSerializer`** avec une méthode `create()` assurant une création d’utilisateur sécurisée (hashage du mot de passe).
- [x] Définition du **`UserViewSet`** avec la méthode `get_permissions()` pour gérer dynamiquement les permissions selon le type de requête (lecture/écriture).
- [x] Configuration du **router Django REST Framework** et ajout des routes dans `users/urls.py`.
- [x] Inclusion de la route principale `api/users/` dans `config/urls.py`.

---

### 🔐 Authentification & Sécurité
- [x] Installation et configuration du package **`djangorestframework-simplejwt`**.
- [x] Mise à jour du fichier `config/settings.py` avec la section `REST_FRAMEWORK` et les paramètres JWT.
- [x] Ajout des endpoints :
  - `api/token/` → génération des tokens (access + refresh),
  - `api/token/refresh/` → renouvellement du token d’accès.
- [x] Tests Postman : génération, stockage et utilisation du token d’accès via variable d’environnement.
- [x] Vérification des accès protégés : requêtes `GET` autorisées uniquement avec token valide ✅.

---

### 🧱 Module **Projects / Contributors / Issues / Comments**
- [x] Création de l’application **`projects`**.
- [x] Implémentation et tests des modèles :
  - **`Project`** : ressource principale avec titre, description, type, auteur.
  - **`Contributor`** : lien entre utilisateur et projet, gestion des rôles (`AUTHOR` / `CONTRIBUTOR`).
  - **`Issue`** : gestion des tickets (`BUG` / `FEATURE` / `TASK`) avec priorités, statuts et assignation.
  - **`Comment`** : gestion des discussions liées aux issues.
- [x] Création des **serializers** correspondants (`ProjectSerializer`, `ContributorSerializer`, `IssueSerializer`, `CommentSerializer`).
- [x] Mise en place des **ViewSets** pour chaque ressource, avec filtrage dynamique selon le rôle et le projet.
- [x] Configuration des **routes API** :
  - `/api/projects/`
  - `/api/contributors/`
  - `/api/issues/`
  - `/api/comments/`
- [x] Tests complets dans Postman :
  - Création d’un projet → l’auteur devient automatiquement contributeur.
  - Création et récupération d’issues liées à un projet.
  - Ajout et consultation de commentaires sur une issue.

---

### 🛡️ Permissions personnalisées & conformité RGPD
- [x] Implémentation de la permission **`IsAuthorAndContributor`** :
  - Les contributeurs peuvent lire les projets, issues et commentaires.
  - Seul l’auteur d’une ressource (projet, issue, commentaire) peut la modifier ou la supprimer.
- [x] Mise en place du filtrage dynamique via `get_queryset()` dans les `ViewSets`.
- [x] Vérification de la conformité RGPD :
  - Gestion des droits d’accès, rectification et suppression des données utilisateur.
  - Respect du droit à l’oubli (suppression réelle des données).
- [x] Ajout de **Dependabot** au repository GitHub pour la veille de sécurité et la mise à jour automatique des dépendances.
- [x] Validation complète des **tests unitaires** :
  - Cas anonymes → `401 Unauthorized`
  - Cas contributeur → accès lecture seulement
  - Cas auteur → accès total (modification/suppression)
- [x] Résultat : `pytest -v` → **16 tests réussis sur 16 ✅**

---

### 🧰 Qualité de code & automatisation
- [x] Installation et configuration de **Pre-commit** avec les hooks :
  - **Black** → formatage automatique du code,
  - **Isort** → tri des imports,
  - **Autoflake** → suppression des imports inutiles,
  - **Flake8** → vérification des normes PEP8.
- [x] Réorganisation du fichier `.pre-commit-config.yaml` :
  - Exécution automatique de `autoflake` avant `flake8`,
  - Ajout des arguments `--max-line-length=79` pour harmoniser avec Black.
- [x] Création d’un hook personnalisé `run-django-tests` pour exécuter automatiquement `pytest` avant chaque commit.
- [x] Nettoyage du code (imports, formatage, indentation) effectué automatiquement via Pre-commit.
- [x] Validation complète du pipeline qualité :
  - Tous les hooks passent (`black`, `isort`, `autoflake`, `flake8`),
  - Tous les tests unitaires passent avant le commit ✅.

---

### 🚀 Prochaines étapes
- [ ] Implémenter la **pagination** sur les endpoints `projects`, `issues` et `comments` (optimisation *green code*).
- [ ] Ajouter les **tests d’intégration complets API** (Postman) pour vérifier le comportement JWT + permissions.
- [ ] Rédiger la **documentation finale** du projet :
  - Présentation du workflow utilisateur,
  - Exemple d’utilisation des tokens JWT,
  - Schéma d’architecture de l’API.
- [ ] Préparer le **rapport de soutenance** et le push final sur GitHub.

---

