# Generated by Django 4.2.11 on 2025-07-11 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_rename_onboarding_email_to_employee_employee_send_onboarding_email_to_employee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='documenso_documents_list',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
