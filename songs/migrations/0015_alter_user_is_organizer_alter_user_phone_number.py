# Generated by Django 4.2 on 2023-12-30 10:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0014_alter_user_is_organizer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_organizer',
            field=models.BooleanField(default=False, verbose_name='is an organizer?'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1\\d{9,12}$')]),
        ),
    ]
