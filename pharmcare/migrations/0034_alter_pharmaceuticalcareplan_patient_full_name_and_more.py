# Generated by Django 4.2 on 2023-12-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0033_pharmaceuticalcareplan_patient_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pharmaceuticalcareplan',
            name='patient_full_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='pharmaceuticalcareplan',
            name='patient_unique_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
