# Generated by Django 4.2 on 2024-01-02 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0082_alter_followupplan_state_of_improvement_by_score'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='patient',
            options={'ordering': ['-id', '-date_created']},
        ),
        migrations.RemoveField(
            model_name='pharmaceuticalcareplan',
            name='patient_full_name',
        ),
    ]
