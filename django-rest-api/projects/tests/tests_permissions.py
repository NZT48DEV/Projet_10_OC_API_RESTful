import json

import pytest
from django.urls import reverse
from projects.models import Comment, Contributor, Issue, Project
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestAPIBehavior:
    """Tests complets sur les permissions et comportements de l’API."""

    def setup_method(self):
        self.client = APIClient()

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
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin1234", age=40
        )

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
            role="Auteur et Contributeur du projet",
        )
        Contributor.objects.create(
            user=self.contributor,
            project=self.project,
            permission="CONTRIBUTOR",
            role="Contributeur du projet",
        )

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

    # ------------------------------------------------------------------
    #  UTILITAIRE ROBUSTE POUR LIRE LE JSON MÊME SI LE CONTENT-TYPE EST HTML
    # ------------------------------------------------------------------
    def parse_json(self, response):
        try:
            return response.json()
        except Exception:
            try:
                content = response.content.decode().strip()
                if content.startswith("{") and content.endswith("}"):
                    return json.loads(content)
                return {"raw": content}
            except Exception:
                return {}

    # ------------------------------------------------------------------
    #  TESTS
    # ------------------------------------------------------------------

    def test_anonymous_cannot_access_projects(self):
        url = reverse("project-list")
        response = self.client.get(url)
        assert response.status_code in [401, 403]

    def test_contributor_can_view_project(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("project-detail", args=[self.project.id])
        assert self.client.get(url).status_code == 200

    def test_stranger_cannot_view_project(self):
        self.client.force_authenticate(user=self.stranger)
        url = reverse("project-detail", args=[self.project.id])
        assert self.client.get(url).status_code == 404

    # --- PROJETS ---
    def test_author_can_create_project(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("project-list")
        data = {
            "title": "Création d’un nouveau projet",
            "description": "Test de création depuis le test",
            "type": "BACK_END",
        }

        # 👇 Ajout de l’en-tête explicite pour forcer la réponse JSON
        response = self.client.post(
            url, data, format="json", HTTP_ACCEPT="application/json"
        )

        assert (
            response.status_code == 201
        ), f"Réponse inattendue : {response.content.decode()}"

        # Décodage JSON robuste
        try:
            result = response.json()
        except Exception:
            result = {"raw": response.content.decode(errors="ignore")}

        assert isinstance(result, dict), f"Réponse non dict : {result}"
        assert "message" in result, f"Clés présentes : {list(result.keys())}"
        assert "projet" in result["message"].lower()
        assert "créé" in result["message"].lower()

        project = Project.objects.get(title="Création d’un nouveau projet")
        assert project.author_user == self.author

        contributor = project.contributors.get(user=self.author)
        assert contributor.permission == "AUTHOR"
        assert "Auteur" in contributor.role

    def test_author_can_update_project(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, {"title": "Projet Modifié"})
        assert response.status_code == 200
        self.project.refresh_from_db()
        assert self.project.title == "Projet Modifié"

    def test_contributor_cannot_update_project(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, {"title": "Hack Projet"})
        assert response.status_code == 403

    def test_author_can_delete_project(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        assert response.status_code in [200, 204]
        assert not Project.objects.filter(id=self.project.id).exists()

    def test_contributor_cannot_delete_project(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        assert response.status_code == 403

    # --- CONTRIBUTEURS ---
    def test_author_can_add_contributor(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("contributor-list")
        response = self.client.post(
            url, {"user": self.stranger.id, "project": self.project.id}
        )
        assert response.status_code == 201
        assert Contributor.objects.filter(user=self.stranger).exists()

    def test_author_cannot_add_duplicate_contributor(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("contributor-list")
        data = {"user": self.contributor.id, "project": self.project.id}
        response = self.client.post(url, data)
        assert response.status_code == 400
        assert "déjà contributeur" in str(response.data).lower()

    def test_author_cannot_add_superuser(self):
        self.client.force_authenticate(user=self.author)
        url = reverse("contributor-list")
        response = self.client.post(
            url, {"user": self.superuser.id, "project": self.project.id}
        )
        assert response.status_code in [400, 404]

    def test_only_author_can_delete_contributor(self):
        contrib = Contributor.objects.get(user=self.contributor)
        url = reverse("contributor-detail", args=[contrib.id])
        self.client.force_authenticate(user=self.author)
        assert self.client.delete(url).status_code in [200, 204]
        self.client.force_authenticate(user=self.contributor)
        assert self.client.delete(url).status_code in [403, 404]

    # --- ISSUES ---
    def test_contributor_can_create_issue(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("issue-list")
        data = {
            "title": "Nouvelle tâche",
            "description": "Test issue création",
            "tag": "TASK",
            "priority": "LOW",
            "status": "TODO",
            "project": self.project.id,
            "assignee_user": self.author.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == 201
        assert Issue.objects.filter(title="Nouvelle tâche").exists()

    def test_stranger_cannot_create_issue(self):
        self.client.force_authenticate(user=self.stranger)
        url = reverse("issue-list")
        data = {
            "title": "Tâche non autorisée",
            "description": "Tentative",
            "tag": "TASK",
            "priority": "LOW",
            "project": self.project.id,
        }
        response = self.client.post(url, data)
        assert response.status_code in [400, 403]

    def test_user_without_project_cannot_access_issues(self):
        self.client.force_authenticate(user=self.stranger)
        url = reverse("issue-list")

        # 👇 on force le retour JSON
        response = self.client.get(url, HTTP_ACCEPT="application/json")

        assert (
            response.status_code == 403
        ), f"Statut inattendu : {response.status_code}"

        # Parsing robuste du contenu
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.content.decode(errors="ignore")}

        # Lecture du texte pour vérification
        if isinstance(data, dict):
            text = str(data.get("detail", "")).lower()
        else:
            text = str(data).lower()

        assert (
            "accès refusé" in text or "forbidden" in text or "403" in text
        ), f"Réponse inattendue : {text}"

    def test_only_assignee_can_update_status(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("issue-detail", args=[self.issue.id])
        response = self.client.patch(url, {"status": "IN_PROGRESS"})
        assert response.status_code == 200
        self.issue.refresh_from_db()
        assert self.issue.status == "IN_PROGRESS"

    def test_other_contributor_cannot_update_status(self):
        other = User.objects.create_user(
            username="othercontrib",
            password="pass1234",
            age=27,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        Contributor.objects.create(
            user=other,
            project=self.project,
            permission="CONTRIBUTOR",
            role="Contributeur du projet",
        )
        self.client.force_authenticate(user=other)
        url = reverse("issue-detail", args=[self.issue.id])
        response = self.client.patch(url, {"status": "FINISHED"})
        assert response.status_code == 403

    # --- COMMENTAIRES ---
    def test_contributor_can_comment_issue(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("comment-list")
        data = {"description": "Nouveau commentaire", "issue": self.issue.id}
        response = self.client.post(url, data)
        assert response.status_code == 201
        assert Comment.objects.filter(
            description="Nouveau commentaire"
        ).exists()

    def test_stranger_cannot_comment_issue(self):
        self.client.force_authenticate(user=self.stranger)
        url = reverse("comment-list")
        data = {"description": "Commentaire interdit", "issue": self.issue.id}
        response = self.client.post(url, data)
        assert response.status_code in [400, 403]

    def test_comment_author_can_edit(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("comment-detail", args=[self.comment.id])
        response = self.client.patch(url, {"description": "Correction faite."})
        assert response.status_code == 200
        self.comment.refresh_from_db()
        assert self.comment.description == "Correction faite."

    def test_other_user_cannot_edit_comment(self):
        self.client.force_authenticate(user=self.stranger)
        url = reverse("comment-detail", args=[self.comment.id])
        response = self.client.patch(
            url, {"description": "Hack du commentaire"}
        )
        assert response.status_code == 404

    def test_author_can_delete_comment(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse("comment-detail", args=[self.comment.id])
        response = self.client.delete(url)
        assert response.status_code in [200, 204]
        assert not Comment.objects.filter(id=self.comment.id).exists()
