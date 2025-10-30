"""
Tests du système de cache de l'API SoftDesk.
Couvre la mise en cache, l'invalidation et les gains de performance
pour les projets et les issues.
"""

import time

import pytest
from django.core.cache import cache
from django.urls import reverse
from projects.models import Contributor, Issue, Project
from rest_framework.test import APIClient
from users.models import User

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------
@pytest.fixture
def api_client():
    """Crée un client API réutilisable pour les tests."""
    return APIClient()


@pytest.fixture
def user_setup():
    """Crée un utilisateur, un projet, un contributeur et une issue pour les tests."""
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

    # Création d’un contributeur (l'auteur du projet)
    contributor = Contributor.objects.create(
        user=user, project=project, permission="AUTHOR", role="Auteur"
    )

    # Création d’une issue assignée à ce contributeur
    Issue.objects.create(
        title="Issue Test",
        description="Issue initiale",
        tag="BUG",
        priority="LOW",
        project=project,
        author_user=user,
        assignee_contributor=contributor,
    )

    return {"user": user, "project": project, "contributor": contributor}


@pytest.fixture(autouse=True)
def clear_cache():
    """Vide le cache avant et après chaque test."""
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------------------
# TESTS DU CACHE PROJETS
# ---------------------------------------------------------------------
def test_project_cache_created_and_used(api_client, user_setup):
    """Vérifie la création et la réutilisation du cache projet."""
    client = api_client
    user = user_setup["user"]
    client.force_authenticate(user=user)
    url = reverse("project-list")
    cache_key = f"user_projects_{user.id}"

    assert cache.get(cache_key) is None, "Le cache doit être vide au départ."

    # Première requête : création du cache
    client.get(url)
    assert cache.get(cache_key) is not None, "Le cache n’a pas été créé."

    # Deuxième requête : doit réutiliser le cache
    client.get(url)
    assert cache.get(cache_key) is not None, "Le cache n’a pas été réutilisé."


def test_project_cache_invalidation_on_create(api_client, user_setup):
    """Vérifie que le cache projet est supprimé après création d’un projet."""
    client = api_client
    user = user_setup["user"]
    client.force_authenticate(user=user)
    url = reverse("project-list")
    cache_key = f"user_projects_{user.id}"

    cache.set(cache_key, ["cached_project"], timeout=600)
    assert cache.get(cache_key), "Le cache initial est manquant."

    # Création d’un projet : doit invalider le cache
    client.post(
        url,
        {"title": "Projet Nouveau", "description": "desc", "type": "BACK_END"},
        format="json",
    )

    assert cache.get(cache_key) is None, "Le cache projet n’a pas été vidé."


def test_project_cache_performance_gain(api_client, user_setup):
    """Compare les temps d’accès avec et sans cache."""
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
        f"\nPremière requête : {first_duration:.6f}s | "
        f"Seconde (cache) : {second_duration:.6f}s"
    )

    if first_duration < 0.05:
        pytest.skip("Durée trop courte pour mesurer un gain significatif.")

    assert (
        second_duration < first_duration * 0.5
    ), f"Aucun gain notable : {first_duration:.4f}s → {second_duration:.4f}s"


# ---------------------------------------------------------------------
# TESTS DU CACHE ISSUES
# ---------------------------------------------------------------------
def test_issue_cache_created_and_used(api_client, user_setup):
    """Vérifie la création et la réutilisation du cache des issues."""
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
    """Vérifie la suppression du cache des issues après création."""
    client = api_client
    user, project, contributor = (
        user_setup["user"],
        user_setup["project"],
        user_setup["contributor"],
    )
    client.force_authenticate(user=user)
    url = reverse("issue-list")
    cache_key = f"issues_user_{user.id}_project_{project.id}"

    cache.set(cache_key, ["cached_issue"], timeout=600)
    assert cache.get(cache_key), "Le cache initial est manquant."

    # Création d’une issue : doit invalider le cache
    client.post(
        url,
        {
            "title": "Issue Cache Reset",
            "description": "Test invalidation",
            "tag": "TASK",
            "priority": "HIGH",
            "project": project.id,
            "assignee_contributor": contributor.id,
        },
        format="json",
    )

    assert (
        cache.get(cache_key) is None
    ), "Le cache des issues n’a pas été vidé."
