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
  - `api-auth/token/` → génération des tokens (access + refresh),
  - `api-auth/token/refresh/` → renouvellement du token d’accès.
- [x] Création d’une vue d’inscription **`RegisterView`** pour permettre l’enregistrement d’un nouvel utilisateur non connecté (`AllowAny`).
- [x] Réorganisation des routes :
  - Regroupement des endpoints d’authentification dans une nouvelle app **`api_auth`**.
  - `api-auth/register/` → inscription utilisateur,
  - `api-auth/login/` → connexion via interface DRF,
  - `api-auth/token/` → obtention du JWT,
  - `api-auth/token/refresh/` → renouvellement du JWT.
- [x] Mise à jour du fichier `config/urls.py` pour inclure ces routes centralisées.
- [x] Configuration d’une page d’accueil `api_auth_home` permettant de rediriger vers la page de connexion/inscription.
- [x] Vérification de la cohérence des permissions :
  - Accès au `register` bloqué pour les utilisateurs déjà connectés (grâce à `IsNotAuthenticated`).
  - Accès libre pour les utilisateurs anonymes.

---

### 🍪 Gestion des sessions et sécurité côté navigateur
- [x] Activation du système d’authentification par **Session ID** dans DRF (`SessionAuthentication`).
- [x] Analyse et validation du comportement des cookies :
  - Génération automatique de `sessionid` et `csrftoken`.
  - Vérification de la validité et de la durée de vie des cookies via l’onglet **Application** du navigateur.
- [x] Sécurisation de la session :
  - Ajout de `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` pour expirer la session à la fermeture du navigateur.
  - Vérification du comportement effectif (session supprimée à la fermeture complète du navigateur).
  - Expiration du cookie `sessionid` à la fin de la session, tandis que `csrftoken` reste valide (comportement standard).

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
  - `/api/projects/contributors/`
  - `/api/projects/issues/`
  - `/api/projects/comments/`
- [x] Tests complets dans Postman :
  - Création d’un projet → l’auteur devient automatiquement contributeur.
  - Création et récupération d’issues liées à un projet.
  - Ajout et consultation de commentaires sur une issue.

---

### 🛡️ Permissions personnalisées & conformité RGPD
- [x] Implémentation de la permission **`IsAuthorAndContributor`** :
  - Les contributeurs peuvent lire les projets, issues et commentaires.
  - Seul l’auteur d’une ressource peut la modifier ou la supprimer.
- [x] Implémentation des permissions **`IsSelfOrReadOnly`** et **`IsNotAuthenticated`** dans `users/permissions.py`.
- [x] Vérification RGPD :
  - Un utilisateur peut consulter, modifier ou supprimer uniquement **son propre compte**.
  - Les données supprimées sont effectivement retirées de la base.
- [x] Ajout des tests unitaires dédiés (`tests_permissions.py`) validant :
  - la suppression, la modification et la création selon le statut de l’utilisateur ;
  - la conformité au RGPD (`401`, `403`, `204`, `200` selon le cas).
- [x] Validation complète : `pytest -v` → **tous les tests passent ✅**

---

### 🧰 Qualité de code & automatisation
- [x] Installation et configuration de **Pre-commit** avec les hooks :
  - **Black**, **Isort**, **Autoflake**, **Flake8**.
- [x] Ajout d’un hook personnalisé pour exécuter automatiquement `pytest` avant commit.
- [x] Tous les tests et hooks passent avant validation (`black`, `isort`, `flake8`, `pytest`) ✅

---

### 🚀 Prochaines étapes
- [ ] Implémenter les **permissions fines sur les Issues et Comments** :
  - Lecture autorisée à tous les contributeurs.
  - Modification/Suppression réservées à l’auteur.
- [ ] Implémenter la **pagination** sur les endpoints `projects`, `issues` et `comments`.
- [ ] Ajouter les **tests d’intégration API** (JWT + permissions).
- [ ] Rédiger la **documentation finale** et le **rapport de soutenance**.

---
