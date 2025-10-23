from django.core.cache import cache


def safe_delete_pattern(pattern: str):
    """
    Supprime les clés du cache correspondant à un pattern,
    compatible avec tous les backends (LocMem, Redis, etc.).
    """
    deleted_any = False
    try:
        cache.delete_pattern(pattern)
        deleted_any = True
    except AttributeError:
        base = pattern.replace("*", "")
        try:
            local_cache = getattr(cache, "_cache", {})
            for key in list(local_cache.keys()):
                if base in str(key):
                    cache.delete(key)
                    deleted_any = True
        except Exception:
            pass
    if not deleted_any:
        cache.clear()
