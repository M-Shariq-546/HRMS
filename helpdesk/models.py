import os
from datetime import datetime

from django import apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from base.horilla_company_manager import HorillaCompanyManager
from base.models import Company, Department, JobPosition, Tags
from employee.models import Employee
from horilla.models import HorillaModel
from horilla_audit.methods import get_diff
from horilla_audit.models import HorillaAuditInfo, HorillaAuditLog, HistoricalRecords

PRIORITY = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]
MANAGER_TYPES = [
    ("department", "Department"),
    ("job_position", "Job Position"),
    ("individual", "Individual"),
]

TICKET_TYPES = [
    ("suggestion", "Suggestion"),
    ("complaint", "Complaint"),
    ("service_request", "Service Request"),
    ("meeting_request", "Meeting Request"),
    ("anounymous_complaint", "Anonymous Complaint"),
    ("others", "Others"),
]

TICKET_STATUS = [
    ("new", "New"),
    ('re_open', 'Re-Open'),
    ("in_progress", "In Progress"),
    ("on_hold", "On Hold"),
    ("resolved", "Resolved"),
    ("canceled", "Canceled"),
]


class DepartmentManager(HorillaModel):
    manager = models.ForeignKey(
        Employee,
        verbose_name="Manager",
        related_name="dep_manager",
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        Department,
        verbose_name="Department",
        related_name="dept_manager",
        on_delete=models.CASCADE,
    )
    company_id = models.ForeignKey(
        Company, null=True, editable=False, on_delete=models.PROTECT
    )
    objects = HorillaCompanyManager("manager__employee_work_info__company_id")

    class Meta:
        unique_together = ("department", "manager")

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if not self.manager.get_department() == self.department:
            raise ValidationError(_(f"This employee is not from {self.department} ."))


class TicketType(HorillaModel):
    title = models.CharField(max_length=100)
    type = models.CharField(choices=TICKET_TYPES, max_length=50)
    prefix = models.CharField(max_length=3)
    company_id = models.ForeignKey(
        Company, null=True, on_delete=models.PROTECT
    )
    objects = HorillaCompanyManager(related_company_field="company_id")

    def __str__(self):
        return self.title

TICKET_FREQUENCY = [
    ("select", "Select Frequency"),
    ("daily", "Daily"),
    ("weekly", "Weekly"),
    ("monthly", "Monthly"),
    ("custom", "Custom CRON"),
]

class Ticket(HorillaModel):

    title = models.CharField(max_length=50)
    employee_id = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="ticket", verbose_name="Owner"
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        verbose_name="Ticket Type",
    )
    description = models.TextField(max_length=255)
    priority = models.CharField(choices=PRIORITY, max_length=100, default="low")
    created_date = models.DateField(auto_now_add=True)
    resolved_date = models.DateField(blank=True, null=True)
    assigning_type = models.CharField(choices=MANAGER_TYPES, max_length=100)
    raised_on = models.CharField(max_length=100, verbose_name="Forward To")
    assigned_to = models.ManyToManyField(
        Employee, blank=True, related_name="ticket_assigned_to"
    )
    deadline = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tags, blank=True, related_name="ticket_tags")
    status = models.CharField(choices=TICKET_STATUS, default="new", max_length=50)
    frequency = models.CharField(choices=TICKET_FREQUENCY, default="select", max_length=50)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    next_execution_at = models.DateTimeField(null=True, blank=True)
    cron_expression = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        help_text="CRON expression (e.g. '0 9 * * 1-5' for 9 AM on weekdays) without parenthesis"
    )
    history = HorillaAuditLog(
        related_name="history_set",
        bases=[
            HorillaAuditInfo,
        ],
    )
    objects = HorillaCompanyManager(
        related_company_field="employee_id__employee_work_info__company_id"
    )

    class Meta:
        ordering = ["-created_date"]

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        deadline = self.deadline
        today = datetime.today().date()
        if deadline < today:
            raise ValidationError(_("Deadline should be greater than today"))

    def get_raised_on(self):
        obj_id = self.raised_on
        if self.assigning_type == "department":
            raised_on = Department.objects.get(id=obj_id).department
        elif self.assigning_type == "job_position":
            raised_on = JobPosition.objects.get(id=obj_id).job_position
        elif self.assigning_type == "individual":
            raised_on = Employee.objects.get(id=obj_id).get_full_name()
        return raised_on

    def get_raised_on_object(self):
        obj_id = self.raised_on
        if self.assigning_type == "department":
            raised_on = Department.objects.get(id=obj_id)
        elif self.assigning_type == "job_position":
            raised_on = JobPosition.objects.get(id=obj_id)
        elif self.assigning_type == "individual":
            raised_on = Employee.objects.get(id=obj_id)
        return raised_on

    def __str__(self):
        return self.title

    def tracking(self):
        """
        This method is used to return the tracked history of the instance
        """
        return get_diff(self)
    
    def get_ticket_history(self, previous_raised_on=None, new_raised_on=None, updated_by=None, previous_assigning_type=None, new_assigning_type=None):
        from helpdesk.methods import tracking_history_list
        return tracking_history_list(self, previous_raised_on, new_raised_on, updated_by, previous_assigning_type, new_assigning_type)
    
    def get_all_history(self):
        from helpdesk.methods import history_fetched
        return history_fetched(self)
    
    @staticmethod
    def get_status_display_with_key(key):
        return dict(TICKET_STATUS).get(key, key)

class ClaimRequest(HorillaModel):
    ticket_id = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    employee_id = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ("ticket_id", "employee_id")

    def __str__(self) -> str:
        return f"{self.ticket_id}|{self.employee_id}"

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if not self.ticket_id:
            raise ValidationError({"ticket_id": _("This field is required.")})
        if not self.employee_id:
            raise ValidationError({"employee_id": _("This field is required.")})


class Comment(HorillaModel):
    comment = models.TextField(null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comment")
    employee_id = models.ForeignKey(
        Employee, on_delete=models.DO_NOTHING, related_name="employee_comment"
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment


class Attachment(HorillaModel):
    file = models.FileField(upload_to="Tickets/Attachment")
    description = models.CharField(max_length=100, blank=True, null=True)
    format = models.CharField(max_length=50, blank=True, null=True)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ticket_attachment",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comment_attachment",
    )
    def get_file_format(self):
        image_format = [".jpg", ".jpeg", ".png", ".svg"]
        audio_format = [".m4a", ".mp3"]
        file_extension = os.path.splitext(self.file.url)[1].lower()
        if file_extension in audio_format:
            self.format = "audio"
        elif file_extension in image_format:
            self.format = "image"
        else:
            self.format = "file"

    def save(self, *args, **kwargs):
        self.get_file_format()
        super().save(*args, **kwargs)

    def __str__(self):
        return os.path.basename(self.file.name)


class FAQCategory(HorillaModel):
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.title


class FAQ(HorillaModel):
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=255)
    tags = models.ManyToManyField(Tags)
    category = models.ForeignKey(FAQCategory, on_delete=models.PROTECT)
    company_id = models.ForeignKey(
        Company, null=True, editable=False, on_delete=models.PROTECT
    )
    objects = HorillaCompanyManager(related_company_field="company_id")

    def __str__(self):
        return self.question


# updating the faq search index when a new faq is created or deleted


def update_index(sender, instance, **kwargs):
    from .search_indexes import FAQIndex

    index = FAQIndex()
    index.update_object(instance)


def remove_from_index(sender, instance, **kwargs):
    from .search_indexes import FAQIndex

    index = FAQIndex()
    index.remove_object(instance)


post_save.connect(update_index, sender=FAQ)
post_delete.connect(remove_from_index, sender=FAQ)
'''
History testing model for Ticket class 
'''
class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticket_history', null=True, blank=True)
    previous = models.CharField(max_length=255, null=True, blank=True)
    new = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='ticket_updated_by', null=True, blank=True)


    def __str__(self):
        return f"{self.ticket} - {self.updated_by}"
