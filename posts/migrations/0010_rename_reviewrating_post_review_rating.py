# Generated by Django 4.2.11 on 2024-05-21 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_alter_post_slug_alter_postcomment_text'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='ReviewRating',
            new_name='review_rating',
        ),
    ]