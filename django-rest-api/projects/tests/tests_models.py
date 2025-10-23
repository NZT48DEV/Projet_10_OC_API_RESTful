from django.contrib.auth import get_user_model
from django.test import TestCase
from projects.models import Comment, Contributor, Issue, Project

User = get_user_model()


class ProjectModelTest(TestCase):
    """Tests essentiels des modèles du module projects."""

    @classmethod
    def setUpTestData(cls):
        """Création unique des données de base (gros gain de performance)."""
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

    def test_project_str_and_creation(self):
        """Vérifie la création et la représentation textuelle du projet."""
        self.assertEqual(self.project.title, "SoftDesk API")
        self.assertEqual(str(self.project), "SoftDesk API (BACK_END)")

    def test_contributor_str_and_creation(self):
        """Vérifie la création d’un contributeur et son affichage."""
        contributor = Contributor.objects.create(
            user=self.user,
            project=self.project,
            permission="AUTHOR",
            role="Chef de projet",
        )
        self.assertEqual(contributor.permission, "AUTHOR")
        self.assertIn("Chef de projet", str(contributor))

    def test_issue_str_and_creation(self):
        """Vérifie la création et la représentation textuelle d’une issue."""
        issue = Issue.objects.create(
            title="Bug critique",
            description="Erreur de connexion",
            tag="BUG",
            priority="HIGH",
            project=self.project,
            author_user=self.user,
            assignee_user=self.user,
        )
        self.assertEqual(issue.status, "TODO")
        self.assertIn("Bug critique", str(issue))

    def test_comment_str_and_creation(self):
        """Vérifie la création d’un commentaire et sa représentation."""
        issue = Issue.objects.create(
            title="Erreur d’affichage",
            description="Dashboard mobile cassé",
            tag="BUG",
            priority="MEDIUM",
            project=self.project,
            author_user=self.user,
            assignee_user=self.user,
        )
        comment = Comment.objects.create(
            description="Reproduit sur Android.",
            author_user=self.user,
            issue=issue,
        )
        self.assertEqual(comment.author_user.username, "testuser")
        self.assertIn("Reproduit", comment.description)
        self.assertIn("Erreur d’affichage", str(comment))
