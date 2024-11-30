from django.test import TestCase
import os
import django
from django.urls import reverse


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()


class TestPostViews(TestCase):

    def test_post_list_view(self):
        response = self.client.get(reverse('posts:index'))
        
        self.assertEqual(response.status_code, 200,
                         'Перевірка відповіді 200 "/"')
        self.assertTemplateUsed(response, 'posts/index.html',
                                'Перевірка використання шаблону')
        
    
    def test_post_type_slug_view(self):
        response = self.client.get(reverse('posts:type', kwargs={'type_slug': 'news'}))
        bad_response = self.client.get(reverse('posts:type', kwargs={'type_slug': '2notnews2'}))
        
        self.assertEqual(response.status_code, 200,
                         'Перевірка відповіді 200')
        self.assertEqual(bad_response.status_code, 404,
                         'Перевірка відповіді 404')
        self.assertTemplateUsed(response, 'posts/index.html',
                                'Перевірка використання шаблону')

