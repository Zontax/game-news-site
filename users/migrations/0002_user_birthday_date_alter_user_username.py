# Generated by Django 4.2.11 on 2024-05-14 14:51

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthday_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='День народження'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 40 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=40, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator(), django.core.validators.MinLengthValidator(3)], verbose_name='Username'),
        ),
    ]
