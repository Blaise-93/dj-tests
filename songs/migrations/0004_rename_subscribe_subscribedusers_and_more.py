# Generated by Django 4.2 on 2023-11-12 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0003_subscribe'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscribe',
            new_name='SubscribedUsers',
        ),
        migrations.AlterModelOptions(
            name='subscribedusers',
            options={'verbose_name_plural': 'SubscribedUsers'},
        ),
    ]
