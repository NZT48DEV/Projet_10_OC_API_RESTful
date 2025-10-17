from django.contrib.auth import get_user_model
from django.test import TestCase
from projects.models import Comment, Contributor, Issue, Project

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass123",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False,
        )

    def test_project_creation(self):
        project = Project.objects.create(
            title="API SoftDesk",
            description="Project Test",
            type="BACK_END",
            author_user=self.user,
        )
        self.assertEqual(project.title, "API SoftDesk")
        self.assertEqual(str(project), "API SoftDesk")

    def test_contributor_creation(self):
        project = Project.objects.create(
            title="SoftDesk Backend",
            description="Développement API",
            type="BACK_END",
            author_user=self.user,
        )
        contributor = Contributor.objects.create(
            user=self.user,
            project=project,
            permission="AUTHOR",
            role="Chef de projet",
        )
        self.assertEqual(contributor.permission, "AUTHOR")
        self.assertEqual(
            str(contributor), "testuser (Chef de projet - SoftDesk Backend)"
        )

    def test_issue_creation(self):
        project = Project.objects.create(
            title="SoftDesk API",
            description="Test API Project",
            type="BACK_END",
            author_user=self.user,
        )
        issue = Issue.objects.create(
            title="Bug login",
            description="Erreur lors de la connexion",
            tag="BUG",
            priority="HIGH",
            project=project,
            author_user=self.user,
            assignee_user=self.user,
        )
        self.assertEqual(issue.status, "TODO")
        self.assertEqual(str(issue), "[SoftDesk API] Bug login (BUG)")

    def test_comment_creation(self):
        project = Project.objects.create(
            title="SoftDesk API",
            description="Test projet pour commentaires",
            type="BACK_END",
            author_user=self.user,
        )
        issue = Issue.objects.create(
            title="Erreur d’affichage",
            description="Le dashboard plante sur mobile",
            tag="BUG",
            priority="MEDIUM",
            project=project,
            author_user=self.user,
            assignee_user=self.user,
        )
        comment = Comment.objects.create(
            description="Oui, j’ai aussi rencontré ce bug.",
            author_user=self.user,
            issue=issue,
        )
        self.assertEqual(comment.author_user.username, "testuser")
        self.assertEqual(comment.issue.title, "Erreur d’affichage")
        self.assertTrue(comment.uuid)  # Vérifie qu’un UUID est bien généré
        self.assertEqual(
            str(comment),
            f"Comment {comment.uuid} by testuser on Erreur d’affichage",
        )
