# Generated by Django 4.2 on 2023-11-02 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0007_lead_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='leads.userprofile'),
        ),
    ]
