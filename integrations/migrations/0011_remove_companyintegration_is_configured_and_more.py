# Generated by Django 4.2.11 on 2025-05-16 08:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0010_companyintegration_is_configured_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyintegration',
            name='is_configured',
        ),
        migrations.RemoveField(
            model_name='companyintegration',
            name='selected_bot_user',
        ),
        migrations.RemoveField(
            model_name='companyintegration',
            name='selected_team',
        ),
    ]
