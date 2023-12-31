# Generated by Django 4.2 on 2023-11-06 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0002_user_is_agent_user_is_organizer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('date_subscribed', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
