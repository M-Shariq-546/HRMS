"""
mail.py

This module is used handle mail sent in thread
"""

from horilla.utils.logger import HorillaLogger
from threading import Thread
import base64

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from base.backends import ConfiguredEmailBackend
from employee.models import EmployeeWorkInformation
from payroll.models.models import Payslip
from payroll.views.views import payslip_pdf
from base.services.email_service import email_service

logger = HorillaLogger("recruitment.views")


class MailSendThread(Thread):
    """
    MailSend
    """

    def __init__(self, request, result_dict, ids):
        Thread.__init__(self)
        self.result_dict = result_dict
        self.ids = ids
        self.request = request
        self.host = request.get_host()
        self.protocol = "https" if request.is_secure() else "http"

    def run(self) -> None:
        super().run()
        try:
            for record in list(self.result_dict.values()):
                html_message = render_to_string(
                    "payroll/mail_templates/default.html",
                    {
                        "record": record,
                        "host": self.host,
                        "protocol": self.protocol,
                        "company_logo": record["instances"][0].employee_id.employee_work_info.company_id.get_icon_url_for_email(),
                    },
                    request=self.request,
                )
                attachments = []
                for instance in record["instances"]:
                    response = payslip_pdf(self.request, instance.id)
                    
                    # Check if response has content before encoding
                    if response and hasattr(response, 'content') and response.content:
                        try:
                            attachments.append(
                                {
                                    "fileName": f"{instance.get_payslip_title()}.pdf",
                                    "file": response.content
                                }
                            )
                        except Exception as encoding_error:
                            logger.error(f"Error encoding PDF for payslip {instance.id}: {encoding_error}")
                            continue
                    else:
                        logger.error(f"No content in response for payslip {instance.id}")
                        continue
                employee = record["instances"][0].employee_id
                logger.info(f'the attachments are : {attachments}')
                
                # Prepare payload exactly as expected by the service
                payload = {
                    "emails": [employee.get_mail()],
                    "subject": f"Hello, {record['instances'][0].get_name()} Your Payslips is Ready!",
                    "message": html_message,
                    "sender": settings.DEFAULT_FROM_EMAIL,
                    "cc": [],
                    "attachments": attachments,
                    "custom_variables": {
                        'record': record,
                        'host': self.host,
                        'protocol': self.protocol,
                    },
                }
                logger.info(f"payload inside send_mail_to_employee functions of service : {payload}")
                success = email_service.send_email(**payload)
                logger.info(f"success inside send_mail_to_employee functions of service : {success}")
                if success:
                    Payslip.objects.filter(id__in=self.ids).update(sent_to_employee=True)
                else:
                        logger.error(f"Failed to send payslip email to {employee.get_mail()}")
        except Exception as e:
            logger.error(f"Error in send_mail_to_employee functions of service : {e}")
        return

