# Generated by Django 4.2 on 2023-12-25 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0067_alter_patientdetail_options_alter_patient_pharmacist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='patient',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.patientdetail', verbose_name='Patient-detail'),
        ),
    ]
