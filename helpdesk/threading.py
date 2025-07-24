"""
threading.py

This module is used handle mail sent in thread
"""

from horilla.utils.logger import HorillaLogger
from threading import Thread

from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from base.backends import ConfiguredEmailBackend
from base.models import Department
from employee.models import EmployeeWorkInformation
from helpdesk.models import Ticket
from base.services.email_service import email_service
from django.conf import settings
from helpdesk.methods import get_company_logo
logger = HorillaLogger("recruitment.views")


class TicketSendThread(Thread):
    """
    MailSend
    """

    def __init__(self, request, ticket, department_managers, type):
        Thread.__init__(self)
        self.ticket = ticket
        self.type = type
        self.department_managers = department_managers if department_managers else []
        self.request = request
        self.assignees = ticket.assigned_to.all()
        self.host = request.get_host()
        self.protocol = "https" if request.is_secure() else "http"
        raised_on = ticket.get_raised_on_object()
        if isinstance(raised_on, Department):
            if raised_on.dept_manager.all():
                self.department_manager = raised_on.dept_manager.all().first().manager
            else:
                self.department_manager = None

    def send_email(self, subject, content, recipients, ticket_id="#"):
        host = self.host
        protocol = self.protocol
        link = "#"
        
        if ticket_id != "#":
            link = f"{protocol}://{host}/helpdesk/ticket-detail/{ticket_id}/"
            
        company_logo = get_company_logo(self.request)   
        logger.info(f"Company logo: {company_logo}")     
        for recipient in recipients:
            html_message = render_to_string(
                "helpdesk/mail_templates/ticket_mail.html",
                {
                    "link": link,
                    "instance": recipient,
                    "host": host,
                    "protocol": protocol,
                    "subject": subject,
                    "content": content,
                    "company_logo": company_logo,
                },
                request=self.request,
            )

            success = email_service.send_email(
                emails=[recipient.email],
                subject=subject,
                message=html_message,
                custom_variables={
                    'link': link,
                    'instance': recipient,
                    'host': host,
                    'protocol': protocol,
                    'subject': subject,
                    'content': content,
                }
            )
            
            if not success:
                messages.error(
                    self.request, f"Mail not sent to {recipient.get_full_name()}"
                )

    def run(self) -> None:
        super().run()

        if self.type == "create":
            owner = self.ticket.employee_id
            managers = self.department_managers

            content_manager = f"This is to inform you that a ticket has been raised on your department. Take the necessary actions to address the issue or request outlined in the ticket. Should you have any additional information or updates, please feel free to communicate directly with the {owner}."
            subject_manager = "Ticket created raised on your department"

            if managers:
                for manager in managers:
                    self.send_email(subject_manager, content_manager, [manager.manager], self.ticket.id)

            content_owner = "This is to inform you that the ticket you created has been successfully logged into our system. The assigned team/individual will now take the necessary actions to address the issue or request outlined in the ticket. Should you have any additional information or updates, please feel free to communicate directly with the Support/Helpdesk team."
            subject_owner = "Ticket created successfully"

            self.send_email(subject_owner, content_owner, [owner], self.ticket.id)

        elif self.type == "status_change":
            assignees = self.assignees
            owner = self.ticket.employee_id
            managers = self.department_managers

            tracking = self.ticket.ticket_history.order_by('-created_at').first()
            updated_by = None
            new_status = None
            old_status = None
            if tracking:
                updated_by = tracking.updated_by
                new_status = tracking.new
                old_status = tracking.previous

            subject = "The Status of the Ticket has been updated"
            content = f"This is to inform you that the status of the following ticket has been updated by {updated_by} from {old_status} to {new_status}. If you have any questions or require further information, feel free to reach out to the Support/Helpdesk team."

            if managers:
                for manager in managers:
                    self.send_email(
                        subject, content, set(assignees) | {owner} | {manager.manager}, self.ticket.id
                    )
            else:
                self.send_email(subject, content, set(assignees) | {owner}, self.ticket.id)

        elif self.type == "delete":
            assignees = self.assignees
            owner = self.ticket.employee_id
            managers = self.department_managers

            subject = "The Ticket has been deleted"
            content = f'This is to inform you that the Ticket "{self.ticket.title}" has been deleted. If you have any questions or require further information, feel free to reach out to the Support/Helpdesk team.'

            if managers:
                for manager in managers:
                    self.send_email(subject, content, set(assignees) | {owner} | {manager.manager}, self.ticket.id)
            else:
                self.send_email(subject, content, set(assignees) | {owner}, self.ticket.id)

        return


class AddAssigneeThread(Thread):
    """
    MailSend
    """

    def __init__(self, request, ticket, recipient):
        Thread.__init__(self)
        self.ticket = ticket
        self.recipients = recipient
        self.request = request
        self.host = request.get_host()
        self.protocol = "https" if request.is_secure() else "http"

    def run(self) -> None:
        super().run()

        content = "Please review the ticket details and take appropriate action accordingly. If you have any questions or require further information, feel free to reach out to the owner or the Support/Helpdesk team."
        subject = "You have been assigned to a Ticket"

        host = self.host
        protocol = self.protocol
        email_backend = ConfiguredEmailBackend()
        display_email_name = email_backend.dynamic_from_email_with_display_name
        if self.request:
            try:
                display_email_name = f"{self.request.user.employee_get.get_full_name()} <{self.request.user.employee_get.email}>"
            except:
                pass
        link = f"{protocol}://{host}/helpdesk/ticket-detail/{self.ticket.id}/"
        for recipient in self.recipients:
            html_message = render_to_string(
                "helpdesk/mail_templates/ticket_mail.html",
                {
                    "link": link,
                    "instance": recipient,
                    "host": host,
                    "protocol": protocol,
                    "subject": subject,
                    "content": content,
                },
                request=self.request,
            )

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=display_email_name,
                to=[recipient.email],
                reply_to=[display_email_name],
            )
            email.content_subtype = "html"
            try:
                email.send()
            except:
                messages.error(
                    self.request, f"Mail not sent to {recipient.get_full_name()}"
                )


class RemoveAssigneeThread(Thread):
    """
    MailSend
    """

    def __init__(self, request, ticket, recipient):
        Thread.__init__(self)
        self.ticket = ticket
        self.recipients = recipient
        self.request = request
        self.host = request.get_host()
        self.protocol = "https" if request.is_secure() else "http"

    def run(self) -> None:
        super().run()

        content = "Please review the ticket details and take appropriate action accordingly. If you have any questions or require further information, feel free to reach out to the owner or the Support/Helpdesk team."
        subject = "You have been removed from a Ticket"
        email_backend = ConfiguredEmailBackend()

        display_email_name = email_backend.dynamic_from_email_with_display_name
        if self.request:
            try:
                display_email_name = f"{self.request.user.employee_get.get_full_name()} <{self.request.user.employee_get.email}>"
            except:
                pass
        host = self.host
        protocol = self.protocol
        link = f"{protocol}://{host}/helpdesk/ticket-detail/{self.ticket.id}/"
        for recipient in self.recipients:
            html_message = render_to_string(
                "helpdesk/mail_templates/ticket_mail.html",
                {
                    "link": link,
                    "instance": recipient,
                    "host": host,
                    "protocol": protocol,
                    "subject": subject,
                    "content": content,
                },
                request=self.request,
            )

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=display_email_name,
                to=[recipient.email],
                reply_to=[display_email_name],
            )
            email.content_subtype = "html"
            try:
                email.send()
            except:
                messages.error(
                    self.request, f"Mail not sent to {recipient.get_full_name()}"
                )
