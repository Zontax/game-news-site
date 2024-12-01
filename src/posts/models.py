from django.db.models import Model, Manager, Index, PositiveSmallIntegerField, CharField, SlugField, BooleanField, TextField, ImageField, DateTimeField, ForeignKey, ManyToManyField, SET_NULL, CASCADE
from django.urls import reverse
from django.contrib import admin
from django.utils.timezone import now
from django_ckeditor_5.fields import CKEditor5Field
from colorfield.fields import ColorField
from users.models import User


class PostType(Model):
    """
    Модель типів для публікацій.
    """
    name = CharField('Назва', max_length=100, unique=True)
    name_plural = CharField('Назва (однина)', max_length=100)
    slug = SlugField('Slug', max_length=200, unique=True)
    color = ColorField('Колір', format="hexa", default='#FF0000')
    description = CharField('Опис', max_length=300)
    created_date = DateTimeField('Дата', default=now)

    class Meta():
        db_table = 'post_types'
        verbose_name = 'Тип публікації'
        verbose_name_plural = 'Типи публікацій'
        ordering = ['created_date']

    def __str__(self):
        return self.name_plural

    def get_absolute_url(self):
        return reverse('posts:index', kwargs={'type_slug': self.slug})


class PostTopic(Model):
    """
    Модель рубрик для публікацій.
    """
    name = CharField('Назва', max_length=150, unique=True)
    slug = SlugField('Slug', max_length=200, unique=True)
    description = TextField('Опис', max_length=1000, blank=True, null=True)
    is_general = BooleanField('Головна', default=False)
    created_date = DateTimeField('Дата', default=now)

    class Meta():
        db_table = 'post_topics'
        verbose_name = 'Рубрика'
        verbose_name_plural = 'Рубрики'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('posts:topic', args=[self.slug])


class PostTag(Model):
    """
    Модель тегів для публікацій.
    """
    name = CharField('Назва', max_length=150, unique=True)
    slug = SlugField('Slug', max_length=200, unique=True)
    description = TextField('Опис', max_length=1000, blank=True, null=True)
    created_date = DateTimeField('Дата', default=now)

    class Meta():
        db_table = 'post_tags'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class PostPublishedManager(Manager):
    """Усі опубліковані публікації."""

    def get_queryset(self):
        return (super().get_queryset()
                .filter(is_publicated=True)
                .order_by('-created_date'))


class Post(Model):
    """
    Базова модель публікації.
    """
    PUBLISH_STATUS = [
        (False, 'Чернетка'),
        (True, 'Опубліковано'),
    ]
    user = ForeignKey(User, SET_NULL, related_name='posts', null=True,
                      blank=True, verbose_name='Автор')
    type = ForeignKey(PostType, SET_NULL, related_name='posts',
                      null=True, verbose_name='Тип')
    title = CharField('Назва', max_length=130, unique=True)
    slug = SlugField('Slug', max_length=150, unique=True,
                     unique_for_date='created_date')
    summary = CharField('Короткий опис', max_length=200, default='')
    content = CKEditor5Field('Текст', config_name='extends', max_length=50000)
    meta_description = CharField('SEO Інформація', max_length=400,
                                 blank=True, null=True)
    image = ImageField('Зображення', upload_to='images/posts/%Y/%m/%d/')
    detail_image = ImageField('Фон', upload_to='images/posts/%Y/%m/%d/detail/',
                              blank=True, null=True)
    topics = ManyToManyField(PostTopic, related_name='posts',
                             blank=True, verbose_name='Рубрики')
    tags = ManyToManyField(PostTag, related_name='posts',
                           blank=True, verbose_name='Теги')
    is_publicated = BooleanField('Опубліковано', choices=PUBLISH_STATUS,
                                 default=True)
    is_edited = BooleanField('Змінено', default=False)
    created_date = DateTimeField('Дата', auto_now_add=True)
    edit_date = DateTimeField('Дата редагування', auto_now=True,
                              blank=True, null=True)
    likes = ManyToManyField(User, related_name='liked_posts',
                            blank=True, verbose_name='Плюси')
    dislikes = ManyToManyField(User, related_name='disliked_posts',
                               blank=True, verbose_name='Мінуси')
    saves = ManyToManyField(User, related_name='saved_posts',
                            blank=True, verbose_name='В збережених')
    review_pluses = CharField('Плюси (Огляд)', max_length=1000,
                              blank=True, null=True)
    review_minuses = CharField('Мінуси (Огляд)', max_length=1000,
                               blank=True, null=True)
    review_rating = PositiveSmallIntegerField('Рейтинг (Огляд)',
                                              blank=True, null=True)

    objects = Manager()
    published = PostPublishedManager()

    class Meta():
        db_table = 'posts'
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'
        ordering = ['-created_date']
        indexes = [Index(fields=['-created_date', 'slug'])]

    def __str__(self):
        return self.title[:30]

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.slug])

    @admin.display(description='Плюси')
    def total_likes(self):
        return self.likes.count()

    @admin.display(description='Мінуси')
    def total_dislikes(self):
        return self.dislikes.count()

    @admin.display(description='В збережених')
    def total_saves(self):
        return self.saves.count()


class PostCommentActiveManager(Manager):
    """Усі активні коментарі."""

    def get_queryset(self):
        return (super().get_queryset()
                .filter(is_active=True)
                .order_by('-created_date'))


class PostComment(Model):
    """Модель коментарів до публікацій."""

    post = ForeignKey(Post, CASCADE, related_name='comments',
                      null=True, blank=True, verbose_name='Пост')
    user = ForeignKey(User, CASCADE, related_name='comments',
                      verbose_name='Автор')
    parent = ForeignKey('self', SET_NULL, related_name='childrens',
                        blank=True, null=True, verbose_name="Відповідь на")
    text = CKEditor5Field('Текст', config_name='comments', max_length=1000)
    is_edited = BooleanField('Змінено', default=False)
    created_date = DateTimeField('Дата', auto_now_add=True)
    edit_date = DateTimeField('Дата редагування', auto_now=True,
                              blank=True, null=True)
    likes = ManyToManyField(User, related_name='liked_comments',
                            blank=True, verbose_name='Плюси')
    dislikes = ManyToManyField(User, related_name='disliked_comments',
                               blank=True, verbose_name='Мінуси')
    is_active = BooleanField('Активний', default=True)

    objects = Manager()
    active = PostCommentActiveManager()

    class Meta():
        db_table = 'comments'
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['-created_date']
        indexes = [Index(fields=['-created_date'])]

    def __str__(self):
        return f'({self.user.username}) {self.text[0:22]}'

    def get_absolute_url(self):
        return f"{reverse('posts:detail', args=[self.post.slug])}#comment-{self.id}"

    @admin.display(description='Плюси')
    def total_likes(self):
        return self.likes.count()

    @admin.display(description='Мінуси')
    def total_dislikes(self):
        return self.dislikes.count()
