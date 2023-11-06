# Generated by Django 4.2 on 2023-11-04 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0018_alter_lead_social_media_accounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='address',
            field=models.CharField(default='20 Goodwill Estate Ajah, Lagos Nigeria', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lead',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
    ]