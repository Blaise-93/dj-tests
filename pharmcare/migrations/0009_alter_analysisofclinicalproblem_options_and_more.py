# Generated by Django 4.2 on 2023-11-23 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0008_alter_patient_medical_history'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysisofclinicalproblem',
            options={'ordering': ['id'], 'verbose_name_plural': 'Analysis of Clinical Problems'},
        ),
        migrations.AlterModelOptions(
            name='followupplan',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='medicationhistory',
            options={'ordering': ['id'], 'verbose_name_plural': 'Medication History'},
        ),
        migrations.AlterModelOptions(
            name='monitoringplan',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='progressnote',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='analysisofclinicalproblem',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='followupplan',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicationchanges',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicationhistory',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='monitoringplan',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='total',
            field=models.PositiveBigIntegerField(default=65432),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='progressnote',
            name='slug',
            field=models.SlugField(default='nbgvcfdsaedrfgh'),
            preserve_default=False,
        ),
    ]