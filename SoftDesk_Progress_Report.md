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

#### 🔹 Renforcement des ViewSets
- [x] Refonte complète des **ViewSets** (`Project`, `Contributor`, `Issue`, `Comment`) pour garantir une gestion cohérente des droits d’accès.
- [x] Ajout d’un filtrage dynamique dans chaque `get_queryset()` :
  - Les utilisateurs ne voient **que les objets liés aux projets auxquels ils participent**.
  - Les superutilisateurs conservent un accès global pour la supervision.
- [x] Vérification de la cohérence des liens entre modèles :
  - Une `Issue` ne peut être créée **que si l’utilisateur est contributeur du projet**.
  - Un `Comment` ne peut être ajouté **que sur une issue appartenant à un projet où l’utilisateur est contributeur**.
- [x] L’auteur d’un projet est automatiquement ajouté comme **contributeur** à sa création.

#### 🔹 Sécurisation des actions
- [x] Implémentation stricte des règles d’accès :
  - **Lecture** : autorisée aux contributeurs et à l’auteur du projet.
  - **Création** : réservée aux contributeurs du projet.
  - **Modification / Suppression** : autorisée uniquement à l’auteur de la ressource.
- [x] Vérification de la cohérence entre les permissions et la base de données :
  - Aucun utilisateur non contributeur ne peut interagir avec une ressource externe.
  - Les contributeurs ne peuvent pas modifier les ressources des autres.

#### 🔹 Prévention de l’énumération d’utilisateurs (User Enumeration)
- [x] Modification du `UserViewSet` :
  - Les utilisateurs ne peuvent **voir que leur propre profil**.
  - Toute tentative d’accès à un autre utilisateur renvoie désormais un **HTTP 404 Not Found**  
    (au lieu de 403) pour **masquer l’existence d’autres comptes**.
- [x] Même stratégie appliquée sur les autres ressources sensibles (`Projects`, `Issues`, `Comments`).

#### 🔹 Mise en conformité RGPD
- [x] Vérification du **droit à l’oubli** : suppression réelle des données utilisateur dans la base.
- [x] Renforcement des règles d’accès utilisateur :
  - Un utilisateur connecté ne peut pas créer un autre compte.
  - Un utilisateur ne peut modifier ou supprimer **que son propre compte**.
  - Les administrateurs conservent un accès complet à tous les utilisateurs.

#### 🔹 Tests & validations
- [x] Exécution complète des tests unitaires et de permission (`pytest`).
- [x] Ajustement des assertions suite à l’implémentation du **comportement 404 sécurisé** :
  - Tests mis à jour pour refléter la logique de sécurité renforcée.
- [x] Tous les tests valides : `pytest -v` → **34 tests réussis sur 34 ✅**

---

### 🛡️ Permissions personnalisées
- [x] Mise à jour des permissions :
  - **`IsAuthorAndContributor`** : permet lecture aux contributeurs, écriture à l’auteur.
  - **`IsAuthorOrProjectContributorReadOnly`** : gère les droits précis sur `Issue` et `Comment`.
- [x] Refactor des permissions pour éliminer les redondances et simplifier la maintenance.
- [x] Centralisation de la logique d’accès dans `projects/permissions.py`.

---

### 🍪 Interface DRF & confidentialité
- [x] Suppression de l’affichage automatique des docstrings dans l’interface **Browsable API** (DRF)  
  via surcharge de la méthode `get_view_description()` → empêche toute fuite d’informations sur les endpoints.
- [x] Uniformisation du comportement visuel de l’interface DRF :
  - Formulaires affichés mais protégés côté backend.
  - Retour systématique `403` ou `404` selon le rôle et le contexte.

---

### 🧰 Qualité de code & automatisation
- [x] Validation complète du pipeline qualité :
  - `black`, `isort`, `autoflake`, `flake8`, et `pytest` passent avant chaque commit.
- [x] Vérification automatique des tests unitaires via le hook `run-pytest` avant validation Git.
- [x] Résolution des problèmes liés au hook `pre-commit` (configuration `.yaml` régénérée).
- [x] Formatage et linting systématique avant chaque push ✅

---

### 🚀 Prochaines étapes
- [ ] Ajouter les **tests d’intégration API complets (Postman)** couvrant JWT + permissions.
- [ ] Implémenter la **pagination** pour les endpoints `projects`, `issues`, et `comments`.
- [ ] Finaliser la **documentation technique** (routes, permissions, schéma de base de données).
- [ ] Préparer la **soutenance** et le **rapport de présentation du projet**.
