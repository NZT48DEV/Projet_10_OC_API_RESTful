from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur les utilisateurs
    - Inscription ouverte (AllowAny)
    - Consultation/Modification réservées aux utilisateurs connectés
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]