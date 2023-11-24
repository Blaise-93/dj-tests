# Generated by Django 4.2 on 2023-11-21 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0028_alter_contact_email_alter_contact_message_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='full_name',
            field=models.CharField(help_text='Enter your full name', max_length=30),
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject',
            field=models.CharField(help_text='Kindly enter your request subject...', max_length=100),
        ),
    ]
