# Generated by Django 4.2 on 2023-12-16 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0042_alter_pharmaceuticalcareplan_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientdetail',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]