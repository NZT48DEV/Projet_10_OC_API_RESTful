import uuid

from django.conf import settings
from django.db import models


class Project(models.Model):
    TYPE_CHOICES = [
        ("BACK_END", "Back-end"),
        ("FRONT_END", "Front-end"),
        ("iOS", "iOS"),
        ("ANDROID", "Android"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_authored",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("title", "author_user")
        ordering = ["-created_time"]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return f"{self.title} ({self.type})"


class Contributor(models.Model):
    PERMISSION_CHOICES = [
        ("AUTHOR", "Author"),
        ("CONTRIBUTOR", "Contributor"),
    ]

    ROLE_CHOICES = [
        (
            "Auteur et Contributeur du projet",
            "Auteur et Contributeur du projet",
        ),
        ("Contributeur", "Contributeur"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_contributed",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="contributors",
    )
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        verbose_name = "Contributeur"
        verbose_name_plural = "Contributeurs"
        ordering = ["project", "user"]

    def __str__(self):
        return f"{self.user.username} ({self.role} - {self.project.title})"


class Issue(models.Model):
    TAG_CHOICES = [
        ("BUG", "Bug"),
        ("FEATURE", "Feature"),
        ("TASK", "Task"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("FINISHED", "Finished"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="TODO"
    )
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues",
    )
    assignee_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="assigned_issues",
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="issues"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("title", "project", "assignee_user")
        ordering = ["-created_time"]
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self):
        return f"[{self.project.title}] {self.title} ({self.tag})"


class Comment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    issue = models.ForeignKey(
        "projects.Issue",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("description", "issue", "author_user")
        ordering = ["-created_time"]
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        return (
            f"Comment {self.uuid} by {self.author_user.username} "
            f"on {self.issue.title}"
        )
