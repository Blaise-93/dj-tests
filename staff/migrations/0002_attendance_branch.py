# Generated by Django 4.2 on 2023-12-11 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='branch',
            field=models.CharField(default='tr1', max_length=30),
            preserve_default=False,
        ),
    ]
