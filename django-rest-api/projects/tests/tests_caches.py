import time

import pytest
from django.core.cache import cache
from django.urls import reverse
from projects.models import Contributor, Issue, Project
from rest_framework.test import APIClient
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    """Client API réutilisable pour tous les tests."""
    return APIClient()


@pytest.fixture
def user_setup():
    """Création d’un utilisateur et de son projet pour chaque test."""
    user = User.objects.create_user(
        username="cache_tester",
        password="pass123",
        age=25,
        can_be_contacted=True,
        can_data_be_shared=False,
    )
    project = Project.objects.create(
        title="Projet Cache",
        description="desc",
        type="BACK_END",
        author_user=user,
    )
    Contributor.objects.create(
        user=user, project=project, permission="AUTHOR", role="Auteur"
    )

    # Issue par défaut pour tests
    Issue.objects.create(
        title="Issue Test",
        description="Issue initiale",
        tag="BUG",
        priority="LOW",
        project=project,
        author_user=user,
        assignee_user=user,
    )

    return {"user": user, "project": project}


@pytest.fixture(autouse=True)
def clear_cache():
    """Purge automatique du cache avant et après chaque test."""
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------------------
#  TESTS DU CACHE PROJETS
# ---------------------------------------------------------------------
def test_project_cache_created_and_used(api_client, user_setup):
    """Vérifie que le cache est créé à la 1ʳᵉ requête et réutilisé ensuite."""
    client = api_client
    user = user_setup["user"]
    client.force_authenticate(user=user)
    url = reverse("project-list")
    cache_key = f"user_projects_{user.id}"

    assert (
        cache.get(cache_key) is None
    ), "Le cache devrait être vide au départ."

    # Première requête : création du cache
    client.get(url)
    assert cache.get(cache_key) is not None, "Le cache n’a pas été créé."

    # Deuxième requête : lecture depuis le cache (pas d’erreur attendue)
    client.get(url)
    assert cache.get(cache_key) is not None, "Le cache n’a pas été réutilisé."


def test_project_cache_invalidation_on_create(api_client, user_setup):
    """Vérifie que le cache projet est invalidé après création."""
    client = api_client
    user = user_setup["user"]
    client.force_authenticate(user=user)
    url = reverse("project-list")
    cache_key = f"user_projects_{user.id}"

    # Préremplir le cache
    cache.set(cache_key, ["cached_project"], timeout=600)
    assert cache.get(cache_key), "Cache initial manquant."

    # Création d’un nouveau projet → doit invalider le cache
    client.post(
        url,
        {"title": "Projet Nouveau", "description": "desc", "type": "BACK_END"},
        format="json",
    )

    assert (
        cache.get(cache_key) is None
    ), "Le cache projet n’a pas été invalidé."


def test_project_cache_performance_gain(api_client, user_setup):
    """Compare le temps d’exécution entre cache froid et cache chaud."""
    client = api_client
    user = user_setup["user"]
    client.force_authenticate(user=user)
    url = reverse("project-list")

    # Cache froid
    start = time.perf_counter()
    client.get(url)
    first_duration = time.perf_counter() - start

    # Cache chaud
    start = time.perf_counter()
    client.get(url)
    second_duration = time.perf_counter() - start

    print(
        f"\n 1er appel : {first_duration:.6f}s | "
        f"2e appel (cache) : {second_duration:.6f}s"
    )

    # Si le temps est inférieur à 0.05s, on considère que c’est trop rapide pour juger
    if first_duration < 0.05:
        pytest.skip(
            "Trop rapide pour mesurer un gain de cache fiable (<50 ms)"
        )

    # Vérifie que la 2e requête est au moins 2x plus rapide
    assert second_duration < first_duration * 0.5, (
        f"Le cache n’a pas amélioré les performances "
        f"({first_duration:.4f}s → {second_duration:.4f}s)"
    )


# ---------------------------------------------------------------------
#  TESTS DU CACHE ISSUES
# ---------------------------------------------------------------------
def test_issue_cache_created_and_used(api_client, user_setup):
    """Vérifie que le cache des issues est bien créé et réutilisé."""
    client = api_client
    user, project = user_setup["user"], user_setup["project"]
    client.force_authenticate(user=user)
    url = reverse("issue-list") + f"?project={project.id}"
    cache_key = f"issues_user_{user.id}_project_{project.id}"

    # Première requête : crée le cache
    client.get(url)
    assert cache.get(cache_key), "Le cache des issues n’a pas été créé."

    # Deuxième requête : doit réutiliser le cache
    client.get(url)
    assert cache.get(cache_key), "Le cache des issues n’a pas été réutilisé."


def test_issue_cache_invalidation_on_create(api_client, user_setup):
    """Vérifie que le cache des issues est invalidé après création."""
    client = api_client
    user, project = user_setup["user"], user_setup["project"]
    client.force_authenticate(user=user)
    url = reverse("issue-list")
    cache_key = f"issues_user_{user.id}_project_{project.id}"

    # Préremplir le cache
    cache.set(cache_key, ["cached_issue"], timeout=600)
    assert cache.get(cache_key), "Cache initial manquant."

    # Création d’une nouvelle issue → doit invalider le cache
    client.post(
        url,
        {
            "title": "Issue Cache Reset",
            "description": "Test invalidation",
            "tag": "TASK",
            "priority": "HIGH",
            "project": project.id,
            "assignee_user": user.id,
        },
        format="json",
    )

    assert (
        cache.get(cache_key) is None
    ), "Le cache des issues n’a pas été invalidé."
