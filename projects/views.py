from rest_framework import viewsets, permissions
from projects.models import Project, Contributor
from projects.serializers import ProjectSerializer, ContributorSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet permettant de lister, créer, modifier et supprimer des projets.
    Seuls les utilisateurs authentifiés peuvent y accéder.
    """
    serializer_class= ProjectSerializer
    permission_classes= [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user).distinct()
    
    def perform_create(self, serializer):
        project = serializer.save(author_user=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            permission='AUTHOR',
            role='Auteur du projet'
        )

class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les contributeurs d'un projet
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.filter(project__contributors__user=self.request.user)