'''
Module: Payroll: Scheduler for sending payslip to employee on selected dates on settings if and only if the slips statuses are paid and email is not sent and also can be sent upto the
Timezone selected for companies at the time of scheduler creation

Note: This feature can be managed by admin and settings
'''
from horilla.utils.logger import HorillaLogger
from django.utils import timezone
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from .models.models import Payslip
from payroll.models.synetec_models import PayslipAutomationEmail
from django.test import Client
from django.contrib.auth.models import User
from django_apscheduler.jobstores import register_events
import os


scheduler = BackgroundScheduler()
logger = HorillaLogger("recruitment.views")


def EmailSchedulingJob():
    try:
        configs = PayslipAutomationEmail.objects.filter(scheduler_status=True)
        for config in configs:
            if not config:
                logger.error(f"No valid config found for ID: {config.id}. Exiting.")
                continue

            cofig_company_scheduler_timezone = pytz.timezone(config.company.timezone)
            now = timezone.now().astimezone(cofig_company_scheduler_timezone)
            if int(now.day) != int(config.scheduler_date):
                logger.error(' Not the date on which to run')
                continue
            
            if now.hour != config.scheduler_time.hour or now.minute != config.scheduler_time.minute:
                logger.error('Waiting for time  ')
                continue

            payslips = Payslip.objects.filter(status='paid', sent_to_employee=False, employee_id__employee_work_info__company_id=config.company)
            if not payslips.exists():
                logger.error('No payslips found to process. Exiting scheduler run.')
                continue

            payslip_ids = payslips.values_list('id', flat=True)
            client = Client()
            query_string = '&'.join(f'id={id}' for id in payslip_ids)
            user = User.objects.filter(is_superuser=True).first()
            if user:
                client.force_login(user)
            response = client.get(f'/payroll/send-slip?{query_string}')
        pass
    except Exception as e:
        logger.error(f'The Exception error is {e}')

def start():
    # This is development lock to repeat the scheduler more than once when loaded
    if os.environ.get("RUN_MAIN") != "true":
        return 
    register_events(scheduler)
    scheduler.add_job(EmailSchedulingJob, trigger='interval', minutes=1, id='Email_scheduler')
    
    scheduler.start()  
    for job in scheduler.get_jobs():
        logger.warning(f"Job Scheduled -> ID: {job.id}, Next Run: {job.next_run_time}")