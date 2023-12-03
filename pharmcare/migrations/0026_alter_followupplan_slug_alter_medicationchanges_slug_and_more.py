# Generated by Django 4.2 on 2023-12-03 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pharmcare', '0025_alter_analysisofclinicalproblem_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followupplan',
            name='slug',
            field=models.SlugField(default='2345678ghhgfcd'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='medicationchanges',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='monitoringplan',
            name='slug',
            field=models.SlugField(default=65432),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pharmaceuticalcareplan',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='progressnote',
            name='slug',
            field=models.SlugField(default=12345676543),
            preserve_default=False,
        ),
    ]