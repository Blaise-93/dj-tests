# Generated by Django 4.2 on 2024-01-01 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0036_alter_managementprofile_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(help_text="Enter the category's name"),
        ),
    ]
