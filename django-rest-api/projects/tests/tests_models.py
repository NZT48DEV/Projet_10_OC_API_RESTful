"""
Tests unitaires des modèles du module projects.
Vérifie la création, la cohérence et la représentation textuelle
des entités principales : Project, Contributor, Issue et Comment.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from projects.models import Comment, Contributor, Issue, Project

User = get_user_model()


class ProjectModelTest(TestCase):
    """Tests des modèles du module projects."""

    @classmethod
    def setUpTestData(cls):
        """Crée les données de base partagées entre tous les tests."""
        cls.user = User.objects.create_user(
            username="testuser",
            password="pass123",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        cls.project = Project.objects.create(
            title="SoftDesk API",
            description="Backend API Test",
            type="BACK_END",
            author_user=cls.user,
        )
        cls.contributor = Contributor.objects.create(
            user=cls.user,
            project=cls.project,
            permission="AUTHOR",
            role="Chef de projet",
        )

    def test_project_str_and_creation(self):
        """Teste la création et la méthode __str__ du modèle Project."""
        self.assertEqual(self.project.title, "SoftDesk API")
        self.assertEqual(str(self.project), "SoftDesk API (BACK_END)")

    def test_contributor_str_and_creation(self):
        """Teste la création et l’affichage d’un contributeur."""
        self.assertEqual(self.contributor.permission, "AUTHOR")
        self.assertIn("Chef de projet", str(self.contributor))

    def test_issue_str_and_creation(self):
        """Teste la création et la méthode __str__ du modèle Issue."""
        issue = Issue.objects.create(
            title="Bug critique",
            description="Erreur de connexion",
            tag="BUG",
            priority="HIGH",
            project=self.project,
            author_user=self.user,
            assignee_contributor=self.contributor,  # ✅ nouveau champ
        )
        self.assertEqual(issue.status, "TODO")
        self.assertIn("Bug critique", str(issue))
        self.assertEqual(issue.assignee_contributor.user.username, "testuser")

    def test_comment_str_and_creation(self):
        """Teste la création et la méthode __str__ du modèle Comment."""
        issue = Issue.objects.create(
            title="Erreur d’affichage",
            description="Dashboard mobile cassé",
            tag="BUG",
            priority="MEDIUM",
            project=self.project,
            author_user=self.user,
            assignee_contributor=self.contributor,
        )
        comment = Comment.objects.create(
            description="Reproduit sur Android.",
            author_user=self.user,
            issue=issue,
        )
        self.assertEqual(comment.author_user.username, "testuser")
        self.assertIn("Reproduit", comment.description)
        self.assertIn("Erreur d’affichage", str(comment))
