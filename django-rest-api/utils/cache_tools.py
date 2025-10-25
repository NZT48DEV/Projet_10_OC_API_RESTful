"""
Outils utilitaires liés à la gestion du cache.
Permet la suppression sécurisée de clés ou de motifs
dans tous les backends compatibles (FileBased, LocMem, Redis...).
"""

from django.core.cache import cache


def safe_delete_pattern(pattern: str) -> None:
    """
    Supprime en toute sécurité les entrées du cache correspondant à un motif.

    - Compatible avec tous les backends (FileBased, LocMem, Redis…)
    - Si le backend ne supporte pas `delete_pattern`, un fallback
      interne est utilisé pour supprimer manuellement les clés.
    - Si aucune suppression ciblée n’est possible, un clear global
      est effectué en dernier recours.

    Args:
        pattern (str): motif de clé (ex: "user_projects_*")
    """
    deleted_any = False

    # 🔹 Cas 1 — Backend avec support natif de delete_pattern (ex: Redis)
    try:
        cache.delete_pattern(pattern)
        deleted_any = True
    except AttributeError:
        # 🔹 Cas 2 — Backend sans delete_pattern (ex: FileBased / LocMem)
        base = pattern.replace("*", "")
        try:
            local_cache = getattr(cache, "_cache", {})
            for key in list(local_cache.keys()):
                if base in str(key):
                    cache.delete(key)
                    deleted_any = True
        except Exception:
            # Évite toute erreur fatale si le backend ne supporte pas l’accès direct
            pass

    # 🔹 Cas 3 — Aucun élément supprimé : fallback global
    if not deleted_any:
        cache.clear()
