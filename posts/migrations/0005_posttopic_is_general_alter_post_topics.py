# Generated by Django 4.2.11 on 2024-05-16 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_post_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='posttopic',
            name='is_general',
            field=models.BooleanField(default=False, verbose_name='Головна'),
        ),
        migrations.AlterField(
            model_name='post',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='posts', to='posts.posttopic', verbose_name='Рубрики'),
        ),
    ]
