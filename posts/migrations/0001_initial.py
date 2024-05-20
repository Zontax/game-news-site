# Generated by Django 4.2.11 on 2024-05-12 20:21

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=130, unique=True, verbose_name='Назва')),
                ('slug', models.SlugField(max_length=150, unique=True, verbose_name='Slug')),
                ('summary', models.CharField(default='', max_length=200, verbose_name='Короткий опис')),
                ('content', django_ckeditor_5.fields.CKEditor5Field(max_length=50000, verbose_name='Текст')),
                ('meta_description', models.CharField(blank=True, max_length=400, null=True, verbose_name='SEO Інформація')),
                ('image', models.ImageField(upload_to='images/posts_title', verbose_name='Зображення')),
                ('detail_image', models.ImageField(blank=True, null=True, upload_to='images/posts_detail_image', verbose_name='Фон')),
                ('is_publicated', models.BooleanField(default=True, verbose_name='Опубліковано')),
                ('is_edited', models.BooleanField(default=False, verbose_name='Змінено')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('edit_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата редагування')),
            ],
            options={
                'verbose_name': 'Публікація',
                'verbose_name_plural': '🟩 Публікації',
                'db_table': 'posts',
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='PostTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Назва')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Опис')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'db_table': 'post_tags',
            },
        ),
        migrations.CreateModel(
            name='PostType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Назва')),
                ('name_plural', models.CharField(max_length=100, verbose_name='Назва (однина)')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Колір')),
                ('description', models.CharField(max_length=300, verbose_name='Опис')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата')),
            ],
            options={
                'verbose_name': 'Тип публікації',
                'verbose_name_plural': 'Типи публікацій',
                'db_table': 'post_types',
                'ordering': ('created_date',),
            },
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', django_ckeditor_5.fields.CKEditor5Field(max_length=1000, verbose_name='Текст')),
                ('is_edited', models.BooleanField(default=False, verbose_name='Змінено')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('edit_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата редагування')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='childrens', to='posts.postcomment', verbose_name='Відповідь на')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post', verbose_name='Пост')),
            ],
            options={
                'verbose_name': 'Коментар',
                'verbose_name_plural': 'Коментарі',
                'db_table': 'comments',
                'ordering': ('-created_date',),
            },
        ),
    ]
