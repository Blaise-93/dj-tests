# Generated by Django 4.2 on 2023-12-09 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0030_alter_lead_agent'),
        ('pharmcare', '0039_patient_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pharmaceuticalcareplan',
            name='pharmacist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.agent', verbose_name='Pharmacist'),
        ),
    ]
