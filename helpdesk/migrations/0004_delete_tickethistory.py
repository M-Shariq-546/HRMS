# Generated by Django 4.2.11 on 2025-04-14 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0003_tickethistory'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TicketHistory',
        ),
    ]
