# Generated by Django 4.2.11 on 2025-02-28 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('horilla_audit', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('status', models.CharField(choices=[('todo', 'Todo'), ('in_progress', 'In progress'), ('stuck', 'Stuck'), ('completed', 'Completed')], default='todo', max_length=20)),
                ('description', models.TextField(editable=False, max_length=255, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
        ),
        migrations.CreateModel(
            name='Offboarding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=20)),
                ('description', models.TextField(max_length=255)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')], default='ongoing', max_length=10)),
                ('company_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.company', verbose_name='Company')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('managers', models.ManyToManyField(to='employee.employee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OffboardingEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('notice_period', models.IntegerField(null=True)),
                ('unit', models.CharField(choices=[('day', 'days'), ('month', 'Month')], default='month', max_length=10, null=True)),
                ('notice_period_starts', models.DateField(null=True)),
                ('notice_period_ends', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('employee_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employee.employee', verbose_name='Employee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OffboardingStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('notice_period', 'Notice period'), ('fnf', 'FnF Settlement'), ('other', 'Other'), ('interview', 'Interview'), ('handover', 'Work handover'), ('archived', 'Archived')], max_length=13)),
                ('sequence', models.IntegerField(default=0, editable=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('managers', models.ManyToManyField(to='employee.employee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('offboarding_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offboarding.offboarding')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResignationLetter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(max_length=255, null=True)),
                ('planned_to_leave_on', models.DateField()),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='requested', max_length=10)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee', verbose_name='Employee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('offboarding_employee_id', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='offboarding.offboardingemployee')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OffboardingTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=30)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('managers', models.ManyToManyField(to='employee.employee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('stage_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='offboarding.offboardingstage', verbose_name='Stage')),
            ],
            options={
                'unique_together': {('title', 'stage_id')},
            },
        ),
        migrations.CreateModel(
            name='OffboardingStageMultipleFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('attachment', models.FileField(upload_to='offboarding/attachments')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OffboardingNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('attachments', models.ManyToManyField(blank=True, editable=False, to='offboarding.offboardingstagemultiplefile')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('employee_id', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='offboarding.offboardingemployee')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('note_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employee')),
                ('stage_id', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='offboarding.offboardingstage')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OffboardingGeneralSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('resignation_request', models.BooleanField(default=False)),
                ('company_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.company')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='offboardingemployee',
            name='stage_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='offboarding.offboardingstage', verbose_name='Stage'),
        ),
        migrations.CreateModel(
            name='HistoricalEmployeeTask',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('history_title', models.CharField(blank=True, max_length=20, null=True)),
                ('history_description', models.TextField(null=True)),
                ('history_highlight', models.BooleanField(default=False, null=True)),
                ('status', models.CharField(choices=[('todo', 'Todo'), ('in_progress', 'In progress'), ('stuck', 'Stuck'), ('completed', 'Completed')], default='todo', max_length=20)),
                ('description', models.TextField(editable=False, max_length=255, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('employee_id', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='offboarding.offboardingemployee', verbose_name='Employee')),
                ('history_relation', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='history_set', to='offboarding.employeetask')),
                ('history_tags', models.ManyToManyField(to='horilla_audit.audittag')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('task_id', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='offboarding.offboardingtask')),
            ],
            options={
                'verbose_name': 'historical employee task',
                'verbose_name_plural': 'historical employee tasks',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ExitReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=255)),
                ('attachments', models.ManyToManyField(to='offboarding.offboardingstagemultiplefile')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By')),
                ('offboarding_employee_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='offboarding.offboardingemployee')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='employeetask',
            name='employee_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='offboarding.offboardingemployee', verbose_name='Employee'),
        ),
        migrations.AddField(
            model_name='employeetask',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='Modified By'),
        ),
        migrations.AddField(
            model_name='employeetask',
            name='task_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offboarding.offboardingtask'),
        ),
        migrations.AlterUniqueTogether(
            name='employeetask',
            unique_together={('employee_id', 'task_id')},
        ),
    ]
