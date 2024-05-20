# Generated by Django 4.2.11 on 2024-05-16 18:13

from django_ckeditor_5.fields import CKEditor5Field
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Назва')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Опис')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата')),
            ],
            options={
                'verbose_name': 'Рубрика',
                'verbose_name_plural': 'Рубрики',
                'db_table': 'post_topics',
                'ordering': ('name',),
            },
        ),
        migrations.AlterModelOptions(
            name='posttag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=CKEditor5Field(max_length=50000, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='postcomment',
            name='text',
            field=models.TextField(max_length=1000, verbose_name='Текст'),
        ),
    ]
