# Generated by Django 4.2.11 on 2025-02-28 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('asset_name', models.CharField(max_length=255)),
                ('asset_description', models.TextField(blank=True, max_length=255, null=True)),
                ('asset_tracking_id', models.CharField(max_length=30, unique=True)),
                ('asset_purchase_date', models.DateField()),
                ('asset_purchase_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('asset_status', models.CharField(choices=[('In use', 'In Use'), ('Available', 'Available'), ('Not-Available', 'Not-Available')], default='Available', max_length=40)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('notify_before', models.IntegerField(default=1, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AssetAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('assigned_date', models.DateField(auto_now_add=True)),
                ('return_date', models.DateField(blank=True, null=True)),
                ('return_condition', models.TextField(blank=True, max_length=255, null=True)),
                ('return_status', models.CharField(blank=True, choices=[('Minor damage', 'Minor damage'), ('Major damage', 'Major damage'), ('Healthy', 'Healthy')], max_length=30, null=True)),
                ('return_request', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('asset_category_name', models.CharField(max_length=255, unique=True)),
                ('asset_category_description', models.TextField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssetDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('file', models.FileField(blank=True, null=True, upload_to='asset/asset_report/documents/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssetLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('lot_number', models.CharField(max_length=30, unique=True)),
                ('lot_description', models.TextField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Asset Batch',
                'verbose_name_plural': 'Asset Batches',
            },
        ),
        migrations.CreateModel(
            name='AssetReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReturnImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('image', models.FileField(blank=True, null=True, upload_to='asset/return_images/')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssetRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('asset_request_date', models.DateField(auto_now_add=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('asset_request_status', models.CharField(blank=True, choices=[('Requested', 'Requested'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Requested', max_length=30, null=True)),
                ('asset_category_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='asset.assetcategory', verbose_name='Asset Category')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
