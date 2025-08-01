# Generated by Django 4.2.11 on 2025-02-28 13:57

import attendance.methods.utils
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('attendance_date', models.DateField(validators=[attendance.methods.utils.attendance_date_validate], verbose_name='Attendance date')),
                ('attendance_clock_in_date', models.DateField(null=True, verbose_name='Check-In Date')),
                ('attendance_clock_in', models.TimeField(help_text='First Check-In Time', null=True, verbose_name='Check-In')),
                ('attendance_clock_out_date', models.DateField(null=True, verbose_name='Check-Out Date')),
                ('attendance_clock_out', models.TimeField(help_text='Last Check-Out Time', null=True, verbose_name='Check-Out')),
                ('attendance_worked_hour', models.CharField(default='00:00', max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format], verbose_name='Worked Hours')),
                ('minimum_hour', models.CharField(default='00:00', max_length=10, validators=[attendance.methods.utils.validate_time_format], verbose_name='Minimum hour')),
                ('attendance_overtime', models.CharField(default='00:00', max_length=10, validators=[attendance.methods.utils.validate_time_format], verbose_name='Overtime')),
                ('attendance_overtime_approve', models.BooleanField(default=False, verbose_name='Overtime approved')),
                ('attendance_validated', models.BooleanField(default=False, verbose_name='Attendance validated')),
                ('at_work_second', models.IntegerField(blank=True, null=True)),
                ('overtime_second', models.IntegerField(blank=True, null=True, verbose_name='Overtime In Second')),
                ('approved_overtime_second', models.IntegerField(default=0)),
                ('is_validate_request', models.BooleanField(default=False, verbose_name='Is validate request')),
                ('is_bulk_request', models.BooleanField(default=False, editable=False)),
                ('is_validate_request_approved', models.BooleanField(default=False, verbose_name='Is validate request approved')),
                ('request_description', models.TextField(max_length=255, null=True)),
                ('request_type', models.CharField(choices=[('create_request', 'Create Request'), ('update_request', 'Update Request'), ('revalidate_request', 'Re-validate Request')], default='update_request', max_length=18, null=True)),
                ('is_holiday', models.BooleanField(default=False)),
                ('requested_data', models.JSONField(editable=False, null=True)),
            ],
            options={
                'ordering': ['-attendance_date', 'employee_id__employee_first_name', 'attendance_clock_in'],
                'permissions': [('change_validateattendance', 'Validate Attendance'), ('change_approveovertime', 'Change Approve Overtime')],
            },
        ),
        migrations.CreateModel(
            name='AttendanceActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('attendance_date', models.DateField(null=True, validators=[attendance.methods.utils.attendance_date_validate], verbose_name='Attendance Date')),
                ('in_datetime', models.DateTimeField(null=True)),
                ('clock_in_date', models.DateField(null=True, verbose_name='In Date')),
                ('clock_in', models.TimeField(verbose_name='Check In')),
                ('clock_out_date', models.DateField(null=True, verbose_name='Out Date')),
                ('out_datetime', models.DateTimeField(null=True)),
                ('clock_out', models.TimeField(null=True, verbose_name='Check Out')),
            ],
            options={
                'ordering': ['-attendance_date', 'employee_id__employee_first_name', 'clock_in'],
            },
        ),
        migrations.CreateModel(
            name='AttendanceGeneralSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('time_runner', models.BooleanField(default=True)),
                ('enable_check_in', models.BooleanField(default=True, help_text='Enabling this feature allows employees to record their attendance using the Check-In/Check-Out button.', verbose_name='Enable Check in/Check out')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceLateComeEarlyOut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('type', models.CharField(choices=[('late_come', 'Late Come'), ('early_out', 'Early Out')], max_length=20, verbose_name='Type')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'ordering': ['-attendance_id__attendance_date'],
            },
        ),
        migrations.CreateModel(
            name='AttendanceOverTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('month', models.CharField(max_length=10, verbose_name='Month')),
                ('month_sequence', models.PositiveSmallIntegerField(default=0)),
                ('year', models.CharField(default='2025', max_length=10, null=True, verbose_name='Year')),
                ('worked_hours', models.CharField(default='00:00', max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format], verbose_name='Worked Hours')),
                ('pending_hours', models.CharField(default='00:00', max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format], verbose_name='Pending Hours')),
                ('overtime', models.CharField(default='00:00', max_length=20, validators=[attendance.methods.utils.validate_time_format], verbose_name='Overtime Hours')),
                ('hour_account_second', models.IntegerField(default=0, null=True, verbose_name='Worked Seconds')),
                ('hour_pending_second', models.IntegerField(default=0, null=True, verbose_name='Pending Seconds')),
                ('overtime_second', models.IntegerField(default=0, null=True, verbose_name='Overtime Seconds')),
            ],
            options={
                'ordering': ['-year', '-month_sequence'],
            },
        ),
        migrations.CreateModel(
            name='AttendanceRequestComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('comment', models.TextField(max_length=255, null=True, verbose_name='Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceRequestFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('file', models.FileField(upload_to='attendance/request_files')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceValidationCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('validation_at_work', models.CharField(max_length=10, validators=[attendance.methods.utils.validate_time_format], verbose_name='Worked Hours Auto Approve Till')),
                ('minimum_overtime_to_approve', models.CharField(blank=True, max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format])),
                ('overtime_cutoff', models.CharField(blank=True, max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format])),
                ('auto_approve_ot', models.BooleanField(default=False, verbose_name='Auto Approve OT')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BatchAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('title', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GraceTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('allowed_time', models.CharField(default='00:00:00', max_length=10, validators=[attendance.methods.utils.validate_hh_mm_ss_format], verbose_name='Allowed time')),
                ('allowed_time_in_secs', models.IntegerField()),
                ('allowed_clock_in', models.BooleanField(default=True, help_text='Allcocate this grace time for Check-In Attendance')),
                ('allowed_clock_out', models.BooleanField(default=False, help_text='Allcocate this grace time for Check-Out Attendance')),
                ('is_default', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalAttendance',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('history_title', models.CharField(blank=True, max_length=20, null=True)),
                ('history_description', models.TextField(null=True)),
                ('history_highlight', models.BooleanField(default=False, null=True)),
                ('attendance_date', models.DateField(validators=[attendance.methods.utils.attendance_date_validate], verbose_name='Attendance date')),
                ('attendance_clock_in_date', models.DateField(null=True, verbose_name='Check-In Date')),
                ('attendance_clock_in', models.TimeField(help_text='First Check-In Time', null=True, verbose_name='Check-In')),
                ('attendance_clock_out_date', models.DateField(null=True, verbose_name='Check-Out Date')),
                ('attendance_clock_out', models.TimeField(help_text='Last Check-Out Time', null=True, verbose_name='Check-Out')),
                ('attendance_worked_hour', models.CharField(default='00:00', max_length=10, null=True, validators=[attendance.methods.utils.validate_time_format], verbose_name='Worked Hours')),
                ('minimum_hour', models.CharField(default='00:00', max_length=10, validators=[attendance.methods.utils.validate_time_format], verbose_name='Minimum hour')),
                ('attendance_overtime', models.CharField(default='00:00', max_length=10, validators=[attendance.methods.utils.validate_time_format], verbose_name='Overtime')),
                ('attendance_overtime_approve', models.BooleanField(default=False, verbose_name='Overtime approved')),
                ('attendance_validated', models.BooleanField(default=False, verbose_name='Attendance validated')),
                ('at_work_second', models.IntegerField(blank=True, null=True)),
                ('overtime_second', models.IntegerField(blank=True, null=True, verbose_name='Overtime In Second')),
                ('approved_overtime_second', models.IntegerField(default=0)),
                ('is_validate_request', models.BooleanField(default=False, verbose_name='Is validate request')),
                ('is_bulk_request', models.BooleanField(default=False, editable=False)),
                ('is_validate_request_approved', models.BooleanField(default=False, verbose_name='Is validate request approved')),
                ('request_description', models.TextField(max_length=255, null=True)),
                ('request_type', models.CharField(choices=[('create_request', 'Create Request'), ('update_request', 'Update Request'), ('revalidate_request', 'Re-validate Request')], default='update_request', max_length=18, null=True)),
                ('is_holiday', models.BooleanField(default=False)),
                ('requested_data', models.JSONField(editable=False, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical attendance',
                'verbose_name_plural': 'historical attendances',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='PenaltyAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('minus_leaves', models.FloatField(default=0.0, null=True)),
                ('deduct_from_carry_forward', models.BooleanField(default=False)),
                ('penalty_amount', models.FloatField(default=0.0, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_name', models.CharField(blank=True, max_length=250, null=True)),
                ('work_record_type', models.CharField(choices=[('FDP', 'Present'), ('HDP', 'Half Day Present'), ('ABS', 'Absent'), ('HD', 'Holiday/Company Leave'), ('CONF', 'Conflict'), ('DFT', 'Draft')], max_length=5, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('at_work', models.CharField(blank=True, default='00:00', max_length=5, null=True, validators=[attendance.methods.utils.validate_time_format])),
                ('min_hour', models.CharField(blank=True, default='00:00', max_length=5, null=True, validators=[attendance.methods.utils.validate_time_format])),
                ('at_work_second', models.IntegerField(blank=True, default=0, null=True)),
                ('min_hour_second', models.IntegerField(blank=True, default=0, null=True)),
                ('note', models.TextField(max_length=255)),
                ('message', models.CharField(blank=True, max_length=30, null=True)),
                ('is_attendance_record', models.BooleanField(default=False)),
                ('is_leave_record', models.BooleanField(default=False)),
                ('day_percentage', models.FloatField(default=0)),
                ('last_update', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OverrideAttendances',
            fields=[
                ('attendance_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='attendance.attendance')),
            ],
            options={
                'abstract': False,
            },
            bases=('attendance.attendance',),
        ),
    ]
