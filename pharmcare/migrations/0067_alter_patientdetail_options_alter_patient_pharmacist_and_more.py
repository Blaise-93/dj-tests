# Generated by Django 4.2 on 2023-12-25 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0066_alter_patientdetail_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='patientdetail',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='patient',
            name='pharmacist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.pharmacist'),
        ),
        migrations.AlterField(
            model_name='patientdetail',
            name='pharmacist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.pharmacist', verbose_name='Pharmacist'),
        ),
        migrations.AlterField(
            model_name='pharmaceuticalcareplan',
            name='pharmacist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.pharmacist'),
        ),
    ]