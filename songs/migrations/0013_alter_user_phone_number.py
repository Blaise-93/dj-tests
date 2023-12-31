# Generated by Django 4.2 on 2023-12-20 02:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0012_alter_user_is_organizer_alter_user_is_pharmacist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, validators=[django.core.validators.MinValueValidator('010100000'), django.core.validators.MaxValueValidator('099910000')]),
        ),
    ]
