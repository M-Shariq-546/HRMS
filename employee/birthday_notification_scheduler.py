from datetime import datetime
from employee.models import EmployeeWorkInformation
from django.utils import timezone
from slack_sdk import WebClient
from integrations.models import CompanyIntegration
import os
from base.services.slack_service import SlackService
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from horilla.utils.logger import HorillaLogger, log_execution
from base.messages import MESSAGES
# Initialize logger
logger = HorillaLogger("horilla.birthday_scheduler")

@log_execution("horilla.birthday_scheduler")
def birthday_notification_scheduler():
    """
    This function is used to send birthday notifications to employees.
    It retrieves all employees whose birthday is today and sends them a notification.
    """
    try:
        # Get today's date
        server_timezone = timezone.now()

        # Get all employees whose birthday is today
        employees = EmployeeWorkInformation.objects.select_related('employee_id').filter(
            employee_id__dob__isnull=False, 
            employee_id__timezone__isnull=False
        )
        logger.info(f"Found {employees.count()} employees with birthday information")

        birthday_employees_list = []    
        
        for emp in employees:
            employee_timezone = emp.employee_id.timezone
            employee_dob = emp.employee_id.dob
            
            try:
                emp_tz = pytz.timezone(employee_timezone)
                employee_local_time = timezone.localtime(server_timezone, emp_tz)
                employee_today = employee_local_time.date()
                
                if employee_today.day == employee_dob.day and employee_today.month == employee_dob.month:
                    birthday_employees_list.append(emp)
                    logger.info(f"Employee {emp.employee_id} has birthday today")
            except pytz.exceptions.UnknownTimeZoneError:
                logger.error(f"Invalid timezone '{employee_timezone}' for employee {emp.employee_id}")
            except Exception as e:
                logger.log_error(e, {"employee": emp.employee_id, "timezone": employee_timezone})
        
        for employee in birthday_employees_list:
            try:
                company = employee.company_id
                logger.info(f"Processing birthday notification for company: {company}")
                
                company_integration = CompanyIntegration.objects.filter(
                    company_id=company, 
                    is_connected=True,
                    send_birthday_notifications=True
                ).first()
                
                if company_integration is None:
                    logger.warning(f"No active integration found for company {company}")
                    continue
                    
                logger.info(f"Sending birthday message to {employee} in channel {company_integration.channel_id}")
                datetime_now = datetime.now()
                birthday_message_send = SlackService.SendMessage(company_integration, employee.employee_id, datetime_now, MESSAGES['SLACK_BIRTHDAY_NOTIFICATION']['message'])
                    
            except Exception as e:
                logger.log_error(e, {
                    "employee": employee,
                    "company": company,
                    "integration": company_integration
                })
                
    except Exception as e:
        logger.log_error(e, {"function": "birthday_notification_scheduler"})
            
@log_execution("horilla.birthday_scheduler")
def start():
    """
    This function is used to start the birthday notification scheduler.
    It can be called from a management command or a cron job.
    """
    try:
        scheduler = BackgroundScheduler()
        
        if os.environ.get('RUN_MAIN', None) != 'true':
            scheduler.add_job(
                birthday_notification_scheduler,
                trigger="cron",
                hour=0,
                minute=5,
                id="birthday_notification_job",
                replace_existing=True,
            )
            logger.info("Birthday notification job scheduled successfully")
            
        scheduler.start()
        logger.info("Birthday notification scheduler started successfully")
        
    except Exception as e:
        logger.log_error(e, {"function": "start"})