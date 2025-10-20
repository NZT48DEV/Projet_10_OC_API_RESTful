import pytest
from django.urls import reverse
from projects.models import Comment, Contributor, Issue, Project
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestPermissions:
    """
    Tests unitaires pour les permissions personnalisées :
    - IsAuthenticated
    - IsAuthorAndContributor
    """

    def setup_method(self):
        self.client = APIClient()

        # Création de 3 utilisateurs (avec RGPD)
        self.author = User.objects.create_user(
            username="author",
            password="pass1234",
            can_be_contacted=True,
            can_data_be_shared=False,
            age=30,
        )

        self.contributor = User.objects.create_user(
            username="contrib",
            password="pass1234",
            can_be_contacted=False,
            can_data_be_shared=True,
            age=28,
        )

        self.stranger = User.objects.create_user(
            username="stranger",
            password="pass1234",
            can_be_contacted=False,
            can_data_be_shared=False,
            age=25,
        )

        # Création d’un projet
        self.project = Project.objects.create(
            title="Projet Test",
            description="Projet de test",
            type="BACK_END",
            author_user=self.author,
        )

        # Ajout des contributeurs (via le modèle Contributor)
        Contributor.objects.create(
            user=self.author,
            project=self.project,
            permission="AUHTOR",
            role="Auteur du projet",
        )
        Contributor.objects.create(
            user=self.contributor,
            project=self.project,
            permission="CONTRIBUTOR",
            role="Développeur",
        )

        # Création d’une issue et d’un commentaire
        self.issue = Issue.objects.create(
            title="Bug critique",
            description="Un bug à corriger",
            tag="BUG",
            priority="HIGH",
            status="TODO",
            project=self.project,
            author_user=self.author,
            assignee_user=self.contributor,
        )

        self.comment = Comment.objects.create(
            description="Je vais corriger ce bug.",
            issue=self.issue,
            author_user=self.contributor,
        )

    # -------------------------------
    # 🔐 AUTHENTIFICATION
    # -------------------------------
    def test_anonymous_cannot_access_projects(self):
        """Les utilisateurs non connectés ne peuvent rien consulter"""
        url = reverse("project-list")
        response = self.client.get(url)
        assert response.status_code == 401  # Unauthorized

    # -------------------------------
    # 👀 LECTURE
    # -------------------------------
    def test_contributor_can_view_project(self):
        """Un contributeur peut lire le projet"""
        self.client.force_authenticate(user=self.contributor)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)
        assert response.status_code == 200

    def test_stranger_cannot_view_project(self):
        """Un utilisateur non contributeur ne peut pas lire le projet"""
        self.client.force_authenticate(user=self.stranger)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)
        assert response.status_code == 404

    # -------------------------------
    # ✍️ MODIFICATION / SUPPRESSION
    # -------------------------------
    def test_author_can_update_project(self):
        """L’auteur du projet peut le modifier"""
        self.client.force_authenticate(user=self.author)
        url = reverse("project-detail", args=[self.project.id])
        data = {"title": "Projet Modifié"}
        response = self.client.patch(url, data)
        assert response.status_code == 200
        self.project.refresh_from_db()
        assert self.project.title == "Projet Modifié"

    def test_contributor_cannot_update_project(self):
        """Un contributeur (non auteur) ne peut pas modifier le projet"""
        self.client.force_authenticate(user=self.contributor)
        url = reverse("project-detail", args=[self.project.id])
        data = {"title": "Hack Projet"}
        response = self.client.patch(url, data)
        assert response.status_code == 403

    def test_author_can_delete_issue(self):
        """L’auteur d’une issue peut la supprimer"""
        self.client.force_authenticate(user=self.author)
        url = reverse("issue-detail", args=[self.issue.id])
        response = self.client.delete(url)
        assert response.status_code == 204
        assert not Issue.objects.filter(id=self.issue.id).exists()

    def test_contributor_cannot_delete_issue(self):
        """Un contributeur non auteur ne peut pas supprimer une issue"""
        self.client.force_authenticate(user=self.contributor)
        url = reverse("issue-detail", args=[self.issue.id])
        response = self.client.delete(url)
        assert response.status_code == 403

    def test_comment_author_can_edit(self):
        """L’auteur d’un commentaire peut l’éditer"""
        self.client.force_authenticate(user=self.contributor)
        url = reverse("comment-detail", args=[self.comment.id])
        data = {"description": "Correction en cours."}
        response = self.client.patch(url, data)
        assert response.status_code == 200
        self.comment.refresh_from_db()
        assert self.comment.description == "Correction en cours."

    def test_other_user_cannot_edit_comment(self):
        """Un autre utilisateur ne peut pas éditer le commentaire"""
        self.client.force_authenticate(user=self.stranger)
        url = reverse("comment-detail", args=[self.comment.id])
        data = {"description": "Je change le message."}
        response = self.client.patch(url, data)
        assert response.status_code == 404
