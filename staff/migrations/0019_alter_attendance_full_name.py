# Generated by Django 4.2 on 2023-12-28 08:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0018_attendance_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='full_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(9)]),
        ),
    ]
