from rest_framework import viewsets, permissions
from projects.models import Project, Contributor, Issue, Comment
from projects.serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer

class ProjectViewSet(viewsets.ModelViewSet):
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
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.filter(project__contributors__user=self.request.user)
    
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Issue.objects.filter(project__contributors__user=self.request.user).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(issue__project__contributors__user=self.request.user).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)