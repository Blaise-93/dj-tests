# Generated by Django 4.2 on 2023-12-07 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0034_alter_pharmaceuticalcareplan_patient_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmaceuticalcareplan',
            name='amount',
            field=models.PositiveBigIntegerField(default=2600),
            preserve_default=False,
        ),
    ]