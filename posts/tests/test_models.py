import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()
from django.test import TestCase
from posts.models import Post, PostType


class TestPostsModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        # post_types_to_delete = PostType.objects.all()[1:]
        # for t in post_types_to_delete:
        #     t.delete()
        ...

    def setUp(self) -> None:
        ...

    def test_post_type_model_save(self):

        post_type1 = PostType(
            name='Test News',
            name_plural='Test News',
            slug='test-news')
        post_type1.save()

        post_type2 = PostType(
            name='Test Guides',
            name_plural='Test Guides',
            slug='test-guides')
        post_type2.save()

        all = PostType.objects.all()

        self.assertEqual(all.count(), 3, 
                         'Перевірка кількості типів постів у БД')
        self.assertEqual(PostType.objects.all()[0].name, 'Новини',
                         'Назва першого автоматично створеного типу в БД')
        self.assertEqual(PostType.objects.all()[1].name, post_type1.name, 
                         'Назва другого типу в БД')
        self.assertEqual(PostType.objects.all()[2].name, post_type2.name, 
                         'Назва третього типу в БД')

    # def test_post_model_save(self):

    #     post1 = Post(
    #         title='Test News',
    #         type=PostType.objects.first(),
            
    #         )
    #     post1.save()
        
    #     all = Post.objects.all()
        
    #     self.assertEqual(all.count(), 1, 
    #                      'Перевірка кількості постів у БД')