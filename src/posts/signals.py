import os
from django.dispatch import receiver
from django.db.models.signals import post_migrate, pre_delete
from core.settings.base import MEDIA_ROOT
from main.services import create_image
from posts.models import Post, PostType, PostTopic, PostTag


@receiver(pre_delete, sender=Post)
def delete_post(sender, instance: Post, **kwargs):
    """Очистити M2M & видалити зображення"""

    instance.tags.clear()
    instance.topics.clear()
    instance.likes.clear()
    instance.dislikes.clear()
    instance.saves.clear()

    if instance.image:
        image_path = MEDIA_ROOT / instance.image.path
        if os.path.exists(image_path):
            os.remove(image_path)

    if instance.detail_image:
        image_path = MEDIA_ROOT / instance.detail_image.path
        if os.path.exists(image_path):
            os.remove(image_path)


@receiver(post_migrate)
def create_default_objects(sender, **kwargs):
    """Створити типові об'єкти для публікацій"""

    if not PostType.objects.exists():
        types = [('Пости', 'Пост', 'posts', '#52CD2CFF'),
                 ('Новини', 'Новина', 'news', '#FFA30EFF'),
                 ('Огляди', 'Огляд', 'reviews', '#FFFD0EFF'),
                 ('Гайди', 'Гайд', 'guides', '#8000FF')]

        for name, name_plural, slug, color in types:
            PostType.objects.create(
                name=name,
                name_plural=name_plural,
                slug=slug,
                color=color)

    if not PostTopic.objects.exists():
        topics = [('Технології', 'tehnologiyi'),
                  ('Ігрова індустрія', 'igrova-industriya'),
                  ('Фільми та серіали', 'filmy-ta-serialy')]

        for name, slug in topics:
            PostTopic.objects.create(
                is_general=True,
                name=name,
                slug=slug)

    if not PostTag.objects.exists():
        tags = [('Розваги', 'fun'),
                ('Програмування', 'programming'),
                ('Думки', 'thinks')]

        for name, slug in tags:
            PostTag.objects.create(
                name=name,
                slug=slug)

    if not Post.objects.exists():
        image_path = f'images/posts/2024/07/26/init.png'
        create_image(MEDIA_ROOT / image_path)

        post = Post.objects.create(
            user=None,
            type=PostType.objects.first(),
            title='First Publication',
            slug='init',
            content='<p style="margin-left:0px;"><strong>От первого шага до Эльфаэля.</strong></p><figure class="image" style="height:auto;"><img style="aspect-ratio:412/875;" src="https://photobooth.cdn.sports.ru/preset/post/9/65/0742a4dd040c8ac3f7fd06a3df381.png" width="412" height="875"></figure>',
            meta_description='Init post, Test post',
            image=image_path)

        topic = PostTopic.objects.first()
        tags = PostTag.objects.all()[:2]

        post.topics.add(topic)
        post.tags.add(*tags)
