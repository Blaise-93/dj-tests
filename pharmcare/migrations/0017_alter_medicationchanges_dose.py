# Generated by Django 4.2 on 2023-11-29 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0016_alter_medicationchanges_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicationchanges',
            name='dose',
            field=models.CharField(max_length=150),
        ),
    ]
