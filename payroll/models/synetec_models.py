import calendar
from horilla.utils.logger import HorillaLogger
from datetime import date, datetime, timedelta

from django import forms
from django.apps import apps
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.http import QueryDict
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.horilla_company_manager import HorillaCompanyManager
from base.methods import get_next_month_same_date
from base.models import (
    Company,
    Department,
    EmployeeShift,
    JobPosition,
    JobRole,
    WorkType,
    validate_time_format,
)
from employee.methods.duration_methods import strtime_seconds
from employee.models import BonusPoint, Employee, EmployeeWorkInformation
from horilla import horilla_middlewares
from horilla.models import HorillaModel
from horilla_audit.models import HorillaAuditInfo, HorillaAuditLog

logger = HorillaLogger("recruitment.views")


'''
Automation handling model for payslip
'''

DAYS = [
    ("last day", _("Last Day")),
    ("1", "1st"),
    ("2", "2nd"),
    ("3", "3rd"),
    ("4", "4th"),
    ("5", "5th"),
    ("6", "6th"),
    ("7", "7th"),
    ("8", "8th"),
    ("9", "9th"),
    ("10", "10th"),
    ("11", "11th"),
    ("12", "12th"),
    ("13", "13th"),
    ("14", "14th"),
    ("15", "15th"),
    ("16", "16th"),
    ("17", "17th"),
    ("18", "18th"),
    ("19", "19th"),
    ("20", "20th"),
    ("21", "21th"),
    ("22", "22th"),
    ("23", "23th"),
    ("24", "24th"),
    ("25", "25th"),
    ("26", "26th"),
    ("27", "27th"),
    ("28", "28th"),
    ("29", "29th"),
    ("30", "30th"),
    ("31", "31th"),
]



class PayslipAutomationEmail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True , blank=True, related_name='automation_company_instance')
    scheduler_date =  models.CharField(
        max_length=30,
        choices=DAYS,
        default=("1"),
        verbose_name="Email Scheduler Date",
        help_text="On this day of every month,Payslip will automatically sent to employees via emails whose payslips will be paid",
    )
    scheduler_time = models.TimeField(
        default=timezone.now,
        verbose_name="Email Scheduler Time",
        help_text="Time of the day when payslip scheduler should run"
    )
    scheduler_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company} with automation date is {self.scheduler_date} and having active status {self.scheduler_status}"


