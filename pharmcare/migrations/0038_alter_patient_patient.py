# Generated by Django 4.2 on 2023-12-07 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0037_alter_pharmaceuticalcareplan_total_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pharmcare.patientdetail', verbose_name='Patient-detail'),
        ),
    ]