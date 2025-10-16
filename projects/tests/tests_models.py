from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import Project, Contributor

User = get_user_model()

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False
            )
    
    def test_project_creation(self):
        project = Project.objects.create(
            title='API SoftDesk',
            description='Project Test',
            type='BACK_END',
            author_user=self.user
        )
        self.assertEqual(project.title, "API SoftDesk")
        self.assertEqual(str(project), "API SoftDesk")
    
    def test_contributor_creation(self):
        project = Project.objects.create(
            title='SoftDesk Backend',
            description='Développement API',
            type='BACK_END',
            author_user=self.user
        )
        contributor = Contributor.objects.create(
            user=self.user,
            project=project,
            permission='AUTHOR',
            role='Chef de projet'
        )
        self.assertEqual(contributor.permission, 'AUTHOR')
        self.assertEqual(str(contributor), 'testuser (Chef de projet - SoftDesk Backend)')