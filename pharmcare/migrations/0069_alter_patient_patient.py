# Generated by Django 4.2 on 2023-12-25 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0068_alter_patient_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='patient',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='pharmcare.patientdetail', verbose_name='Patient-detail'),
            preserve_default=False,
        ),
    ]