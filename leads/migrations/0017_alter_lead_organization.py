# Generated by Django 4.2 on 2023-11-04 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0016_alter_lead_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='organization',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='leads.userprofile'),
            preserve_default=False,
        ),
    ]
