# Generated by Django 4.2 on 2023-12-03 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmcare', '0028_team_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='full_name',
            field=models.CharField(max_length=50, verbose_name='Full name'),
        ),
    ]
