from drf_spectacular.utils import OpenApiExample, OpenApiResponse

# ---------------------------------------------------------------------
# SCHEMA POUR REGISTER - GET
# ---------------------------------------------------------------------
register_get_schema = {
    "description": "Empêche les requêtes GET sur la route d'inscription.",
    "responses": {
        200: OpenApiResponse(
            description="Réponse informative pour les requêtes GET.",
            response={
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Utilisez POST pour créer un nouveau compte.",
                    }
                },
            },
        ),
        405: OpenApiResponse(
            description="Méthode non autorisée. Seules les requêtes GET et POST sont permises.",
            response={
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Méthode non autorisée.",
                    }
                },
            },
        ),
    },
    "examples": [
        OpenApiExample(
            name="Exemple de réponse 200",
            summary="Réponse standard quand on appelle GET sur /api-auth/register/",
            value={"detail": "Utilisez POST pour créer un nouveau compte."},
            response_only=True,
        ),
        OpenApiExample(
            name="Exemple de réponse 405",
            summary="Quand une méthode non permise est utilisée.",
            value={"detail": "Méthode non autorisée."},
            response_only=True,
        ),
    ],
}


# ---------------------------------------------------------------------
# SCHEMA POUR REGISTER - POST
# ---------------------------------------------------------------------
register_post_schema = {
    "description": "Crée un utilisateur et renvoie un message de confirmation.",
    "responses": {
        201: OpenApiResponse(
            description="Compte créé avec succès.",
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Le compte utilisateur 'alice' a été créé avec succès.",
                    },
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "username": {"type": "string", "example": "alice"},
                            "email": {
                                "type": "string",
                                "example": "alice@example.com",
                            },
                            "age": {"type": "integer", "example": 25},
                            "can_be_contacted": {
                                "type": "boolean",
                                "example": True,
                            },
                            "can_data_be_shared": {
                                "type": "boolean",
                                "example": False,
                            },
                            "created_time": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2025-10-27T12:00:00Z",
                            },
                        },
                    },
                },
            },
        ),
        400: OpenApiResponse(
            description="Erreur de validation : données invalides ou incomplètes.",
            response={
                "type": "object",
                "properties": {
                    "errors": {
                        "type": "object",
                        "example": {
                            "username": ["Ce nom d’utilisateur existe déjà."],
                            "password": ["Ce champ est requis."],
                        },
                    }
                },
            },
        ),
        403: OpenApiResponse(
            description="Accès refusé : seul un utilisateur non authentifié peut s'inscrire.",
            response={
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Accès refusé : vous êtes déjà connecté.",
                    }
                },
            },
        ),
    },
    "examples": [
        OpenApiExample(
            name="Exemple de succès (201)",
            summary="Création réussie d’un compte utilisateur.",
            value={
                "message": "Le compte utilisateur 'alice' a été créé avec succès.",
                "user": {
                    "id": 1,
                    "username": "alice",
                    "email": "alice@example.com",
                    "age": 25,
                    "can_be_contacted": True,
                    "can_data_be_shared": False,
                    "created_time": "2025-10-27T12:00:00Z",
                },
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Exemple d’erreur 400",
            summary="Erreur de validation : données manquantes ou invalides.",
            value={
                "errors": {
                    "username": ["Ce nom d’utilisateur existe déjà."],
                    "password": ["Ce champ est requis."],
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Exemple d’erreur 403",
            summary="Utilisateur déjà connecté tentant de s’inscrire.",
            value={"detail": "Accès refusé : vous êtes déjà connecté."},
            response_only=True,
        ),
    ],
}
