# Generated by Django 4.2.11 on 2025-04-17 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0003_taxbracket_base_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxbracket',
            name='base_amount',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Base Value'),
        ),
    ]
