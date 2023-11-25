# Generated by Django 4.2 on 2023-11-23 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0012_alter_progressnote_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoringplan',
            name='has_improved',
            field=models.BooleanField(default=False, verbose_name="has improved (tick good, if yes, otherwise don't.)"),
        ),
        migrations.AlterField(
            model_name='patient',
            name='medical_charge',
            field=models.PositiveBigIntegerField(blank=True, null=True, verbose_name='amount paid (medical charge if any)'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='total',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
