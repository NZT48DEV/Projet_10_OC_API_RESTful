from rest_framework.routers import DefaultRouter
from projects.views import ProjectViewSet, ContributorViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'contributors', ContributorViewSet, basename='contributors')

urlpatterns = router.urls