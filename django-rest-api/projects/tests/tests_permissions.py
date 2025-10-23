import pytest
from django.urls import reverse
from projects.models import Comment, Contributor, Issue, Project
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestAPIBehavior:
    """Tests essentiels sur les permissions principales de l’API SoftDesk."""

    def setup_method(self):
        """Initialisation par test (DB disponible)."""
        self.client = APIClient()

        # Utilisateurs
        self.author = User.objects.create_user(
            username="author",
            password="pass1234",
            age=30,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        self.contributor = User.objects.create_user(
            username="contrib",
            password="pass1234",
            age=28,
            can_be_contacted=False,
            can_data_be_shared=True,
        )
        self.stranger = User.objects.create_user(
            username="stranger",
            password="pass1234",
            age=25,
            can_be_contacted=False,
            can_data_be_shared=False,
        )

        # Projet
        self.project = Project.objects.create(
            title="Projet Test",
            description="Projet de test",
            type="BACK_END",
            author_user=self.author,
        )

        Contributor.objects.create(
            user=self.author,
            project=self.project,
            permission="AUTHOR",
            role="Auteur",
        )
        Contributor.objects.create(
            user=self.contributor,
            project=self.project,
            permission="CONTRIBUTOR",
            role="Contributeur",
        )

        # Issue + Commentaire
        self.issue = Issue.objects.create(
            title="Bug critique",
            description="Un bug à corriger",
            tag="BUG",
            priority="HIGH",
            project=self.project,
            author_user=self.author,
            assignee_user=self.contributor,
        )
        self.comment = Comment.objects.create(
            description="Je vais corriger ce bug.",
            issue=self.issue,
            author_user=self.contributor,
        )

    # -------------------- PROJETS --------------------
    def test_anonymous_cannot_access_projects(self):
        """Les utilisateurs non connectés n’ont aucun accès."""
        res = self.client.get(reverse("project-list"))
        assert res.status_code in [401, 403]

    def test_author_and_contributor_project_rights(self):
        """Auteur peut créer/modifier/supprimer — contributeur lecture seule."""
        url = reverse("project-detail", args=[self.project.id])

        # Auteur : mise à jour autorisée
        self.client.force_authenticate(user=self.author)
        res = self.client.patch(url, {"title": "Projet Modifié"})
        assert res.status_code == 200

        # Contributeur : modification refusée
        self.client.force_authenticate(user=self.contributor)
        res = self.client.patch(url, {"title": "Hack Projet"})
        assert res.status_code == 403

    # -------------------- CONTRIBUTEURS --------------------
    def test_author_can_add_and_remove_contributor(self):
        """L’auteur peut ajouter ou supprimer un contributeur."""
        self.client.force_authenticate(user=self.author)

        add_url = reverse("contributor-list")
        res = self.client.post(
            add_url, {"user": self.stranger.id, "project": self.project.id}
        )
        assert res.status_code == 201
        assert Contributor.objects.filter(user=self.stranger).exists()

        # Suppression du contributeur
        contrib = Contributor.objects.get(user=self.stranger)
        del_url = reverse("contributor-detail", args=[contrib.id])
        res = self.client.delete(del_url)
        assert res.status_code in [200, 204]
        assert not Contributor.objects.filter(id=contrib.id).exists()

    # -------------------- ISSUES --------------------
    def test_contributor_can_create_issue_but_not_stranger(self):
        """Un contributeur peut créer une issue, un étranger non."""
        url = reverse("issue-list")

        # Création valide
        self.client.force_authenticate(user=self.contributor)
        res = self.client.post(
            url,
            {
                "title": "Nouvelle tâche",
                "description": "Test issue création",
                "tag": "TASK",
                "priority": "LOW",
                "project": self.project.id,
                "assignee_user": self.author.id,
            },
        )
        assert res.status_code == 201
        assert Issue.objects.filter(title="Nouvelle tâche").exists()

        # Utilisateur externe
        self.client.force_authenticate(user=self.stranger)
        res = self.client.post(
            url,
            {
                "title": "Non autorisé",
                "description": "Tentative d’accès",
                "tag": "BUG",
                "priority": "HIGH",
                "project": self.project.id,
            },
        )
        assert res.status_code in [400, 403]

    def test_only_assignee_can_update_issue_status(self):
        """Seul l’utilisateur assigné peut changer le statut."""
        url = reverse("issue-detail", args=[self.issue.id])

        # L’assigné
        self.client.force_authenticate(user=self.contributor)
        res = self.client.patch(url, {"status": "IN_PROGRESS"})
        assert res.status_code == 200

        # Un autre contributeur
        other = User.objects.create_user(
            username="other",
            password="pass123",
            age=27,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        Contributor.objects.create(
            user=other,
            project=self.project,
            permission="CONTRIBUTOR",
            role="Autre contrib",
        )
        self.client.force_authenticate(user=other)
        res = self.client.patch(url, {"status": "FINISHED"})
        assert res.status_code == 403

    # -------------------- COMMENTAIRES --------------------
    def test_comment_permissions(self):
        """Contributeur peut commenter/modifier/supprimer, pas un étranger."""
        list_url = reverse("comment-list")
        detail_url = reverse("comment-detail", args=[self.comment.id])

        # Création par un contributeur
        self.client.force_authenticate(user=self.contributor)
        res = self.client.post(
            list_url,
            {"description": "Nouveau commentaire", "issue": self.issue.id},
        )
        assert res.status_code == 201

        # Modification par l’auteur du commentaire
        res = self.client.patch(
            detail_url, {"description": "Correction faite."}
        )
        assert res.status_code == 200

        # Un utilisateur externe ne peut pas modifier ni commenter
        self.client.force_authenticate(user=self.stranger)
        res = self.client.post(
            list_url,
            {"description": "Commentaire interdit", "issue": self.issue.id},
        )
        assert res.status_code in [400, 403]
        res = self.client.patch(detail_url, {"description": "Hack"})
        assert res.status_code in [403, 404]

        # Suppression par le propriétaire
        self.client.force_authenticate(user=self.contributor)
        res = self.client.delete(detail_url)
        assert res.status_code in [200, 204]
        assert not Comment.objects.filter(id=self.comment.id).exists()
