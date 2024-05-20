import django
from django.test import TestCase

from users.models import User
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()


# class Test_PostsModels(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         pass

#     @classmethod
#     def setUp(self):
#         pass

#     def test_get_user(self):
#         admin = User.objects.first()
#         self.assertEqual(admin.username, 'zontax', 'Перевірка імені адміністратора')
#         self.assertTrue(admin.is_superuser, 'Перевірка пров адміна')
