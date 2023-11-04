# Generated by Django 4.2 on 2023-11-04 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0014_alter_lead_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default='2023-11-04 14:56:40.263576'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='description',
            field=models.TextField(default='CRM IS GOOD'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='email',
            field=models.EmailField(default='baise@gmail.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='phone_number',
            field=models.CharField(default='987654336', max_length=12),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lead',
            name='social_media_accounts',
            field=models.CharField(blank=True, choices=[('Youtube', 'Youtube'), ('Facebook', 'Facebook'), ('Newsletter', 'Newsletter')], max_length=20, null=True),
        ),
    ]
