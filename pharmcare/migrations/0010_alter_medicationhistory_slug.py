# Generated by Django 4.2 on 2023-11-23 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0009_alter_analysisofclinicalproblem_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicationhistory',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
