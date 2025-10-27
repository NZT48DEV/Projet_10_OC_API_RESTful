"""
Hooks personnalisés pour drf-spectacular.
Permet de modifier dynamiquement le schéma OpenAPI après génération.
"""


def rename_auth_tag(result, generator, request, public):
    """
    Renomme uniquement le tag '-auth' en 'api-auth' pour plus de cohérence.
    """
    for path, path_item in result.get("paths", {}).items():
        for operation in path_item.values():
            tags = operation.get("tags", [])
            operation["tags"] = [
                "api-auth" if t == "-auth" else t for t in tags
            ]
    return result
