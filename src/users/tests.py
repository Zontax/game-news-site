import os
import django
from django.test import TestCase
from users.models import User


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')
django.setup()


class Test_PostsModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    @classmethod
    def setUp(self):
        pass

    # def test_get_user(self):
    #     admin = User.objects.first()
    #     self.assertEqual(admin.username, 'admin', 'Перевірка імені адміністратора')
    #     self.assertTrue(admin.is_superuser, 'Перевірка прав адміністратора')
