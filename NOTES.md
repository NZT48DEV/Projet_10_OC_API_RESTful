# ✅ Progression - Projet Django (LITRevu)

## 🔧 Déjà fait
- [x] Création du projet Django `django-rest-api`.
- [x] Création de l'app `Users`.
- [x] Création du model `User` avec ses fonction `__str__` et une surcharge de la fonction `save`.
- [x] Dans `models.py`, création de la fonction `validate_age` pour vérifier l'âge de l'utilisateur (règles RGPD).
- [x] Ajout de `AUTH_USER_MODEL = "users.User"`dans `config/settings.py`.
- [x] Création du serializer `UserSerializer` avec sa fonction `create` pour une création sécurisée.
- [x] Création de `views.py` avec la classe `UserViewSet` et sa fonction `get_permissions` pour gérer les permissions.
- [x] Création du router et Ajout des routes dans `users/urls.py`.
- [x] Ajout de la route `api/users/` dans `config/urls.py`.
- [x] Tests dans le SHELL pour créer/supprimer/accéder aux `users` + vérification gestion de l'âge et retour erreur.
- [X] Tests des requêtes API via POSTMAN (POST, GET) sur le endpoint `api/users/`.
- [X] Installation et configuration de `djangorestframework-simplejwt` (configuration `REST_FRAMEWORK` dans `config/settings.py`).
- [X] Ajout des routes `api/token/`et `api/token/refresh/` dans `config/urls.py`.
- [X] Tests des requêtes pour récupérer les TOKENS via `api/token/`
- [X] Ajout d'une variable dans POSTMAN pour le TOKEN
- [X] Tests des requêtes pour récupérer les utilisateurs (AVEC et SANS Token) -> OK fonctionne comme prévu.


## 🚧 En cours


## 🎯 Pour demain


## 🚀 Pour semaine prochaine


## 💡 Améliorations possibles (idées)
