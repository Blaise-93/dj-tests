# Generated by Django 4.2 on 2023-11-03 00:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0011_alter_category_organization'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id'], 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='lead',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='agent',
            name='category',
        ),
        migrations.AddField(
            model_name='lead',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.category'),
        ),
    ]
