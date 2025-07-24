# models.py
from django.db import models
from datetime import datetime
from base.models import HorillaModel, Company
from base.services.image_service import FileStorageService
from employee.models import Employee
from payroll.models.models import Payslip
import os 
# Enum for supported integration services
class IntegrationService(models.TextChoices):
    SLACK = "slack"
    # GMAIL = "gmail"
    # GOOGLE_CALENDAR = "google_calendar"
    # GOOGLE_MEET = "google_meet"
    # CUSTOM_EMAIL = "custom_email"
    # ZAPIER = "zapier"

ESSENTIAL_SCOPES = {
    "slack": "channels:read,chat:write",
    "gmail": "https://www.googleapis.com/auth/gmail.readonly",
    # Add more service: scopes as needed
}

# CompanyIntegration Model
class CompanyIntegration(HorillaModel):
    company = models.ForeignKey(Company, related_name='integrations', on_delete=models.CASCADE, null=True,  blank=True)
    service = models.ForeignKey('AvailableIntegration', related_name='available_integration', on_delete=models.CASCADE, null=True,  blank=True)
    service_name = models.CharField(max_length=255, null=True, blank=True)
    is_connected = models.BooleanField(default=False)
    images = models.ImageField(upload_to='integration_images/', null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    config = models.JSONField(null=True, blank=True) 
    documenso_api_key = models.CharField(max_length=255, null=True, blank=True, verbose_name='Documenso API Key')
    documenso_notification_message = models.TextField(null=True, blank=True, verbose_name='Documenso Document Notification Message')
    documenso_processing_hours = models.CharField(max_length=255, null=True, blank=True, verbose_name='Documenso Processing Hours')
    client_id = models.CharField(max_length=255, null=True, blank=True)
    auth_uri = models.CharField(max_length=255, null=True, blank=True)
    client_secret = models.CharField(max_length=255, null=True, blank=True)
    wise_api_key = models.CharField(max_length=255, null=True, blank=True, verbose_name='Wise API Key')
    scopes = models.CharField(max_length=500, null=True, blank=True)
    redirect_uri = models.CharField(max_length=255, null=True, blank=True)
    channel_id = models.CharField(max_length=255, null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    send_attendance_notifications = models.BooleanField(default=False, verbose_name='Attendance Notifications')
    send_birthday_notifications = models.BooleanField(default=False, verbose_name='Birthday Notifications')

    class Meta:
        permissions = [
            ("can_connect_service", "Can connect to integration services"),
            ("can_disconnect_service", "Can disconnect to integration services"),
            ("can_update_service", "Can update to integration services"),
            ("can_create_service", "Can add to integration services"),
        ]

    def __str__(self):
        return f"{self.company} - {self.service_name}"

    def get_image_url(self):
        file_service = FileStorageService()
        file_url = file_service.GetImageUrl(self.images)
        return file_url


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Step 2: Set scopes only if not already set
        if not self.scopes and self.service_name:
            print('=== inside scope saving method')
            self.scopes = ESSENTIAL_SCOPES.get(self.service_name.lower(), "")
            super().save(update_fields=['scopes'])  # corrected field name
        
class AvailableIntegration(HorillaModel):
    name= models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='integrations/images',max_length=1000)
    
    def __str__(self) -> str:
        return self.name
    
    def get_image_url(self):
        url = FileStorageService.GetImageUrl(self.image)
        return url
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            file_url = FileStorageService.UploadImage(self.image, image_type='integrations')
            self.image = file_url
            super().save(update_fields=['image'])
            
            
class DocumensoFieldsData(HorillaModel):
    template_id = models.CharField(max_length=255, null=True, blank=True)
    fields = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.template_id}"
    
    
    
status_choices = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

class EmployeeWiseRecipient(HorillaModel):
    """
    EmployeeWiseRecipient
    """
    payslip_id = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='wise_recipient_payslip')
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='wise_recipient_employee')
    recipient_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=status_choices)
    transfer_id = models.CharField(max_length=255, null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.employee_id} - {self.payslip_id}"
