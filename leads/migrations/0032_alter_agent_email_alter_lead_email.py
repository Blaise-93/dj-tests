# Generated by Django 4.2 on 2023-12-18 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0031_alter_lead_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='email',
            field=models.EmailField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
