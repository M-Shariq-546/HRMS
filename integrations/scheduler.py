import os
from integrations.models import CompanyIntegration
from apscheduler.schedulers.background import BackgroundScheduler
from django.urls import reverse
from horilla.utils.logger import HorillaLogger
from employee.models import Employee
from base.services.documenso_service import DocumensoService
from notifications.signals import notify
from django.contrib.auth.models import User
logger = HorillaLogger('integrations.scheduler')

def unsigned_documents_reminder():
    """
    This scheduled task to trigger the unsigned documents reminder
    """
    logger.info(f"============= unsigned documents reminder started")
    documenso_services = CompanyIntegration.objects.filter(service_name__icontains='documenso', is_connected=True)
    logger.info(f"============= documenso services {documenso_services}")
    bot = User.objects.filter(username="Horilla Bot").first()
    for service in documenso_services:
        employees = Employee.objects.filter(documenso_documents_list__isnull=False, employee_work_info__company_id=service.company.id)
        logger.info(f"============= employees {employees}")
        logger.info(f"============= service {service}")
        documenso_api_key = service.documenso_api_key
        logger.info(f"============= documenso api key {documenso_api_key}")
        if documenso_api_key and employees.exists():
            logger.info(f"============= documenso api key found")
            fetch_unsigned_documents = DocumensoService.GetUnsignedDocuments(documenso_api_key, service.documenso_processing_hours)
            if fetch_unsigned_documents and fetch_unsigned_documents.get('documents'):
                unsigned_docs = fetch_unsigned_documents.get('documents', [])
                logger.info(f"============= found {len(unsigned_docs)} unsigned documents")
                for document in unsigned_docs:
                    '''
                    Map each document to employee of the company to get the employee list
                    '''
                    employee = employees.filter(documenso_documents_list__icontains=document.get('id')).first()
                    # Replace variables in notification message
                    if employee:
                        logger.info(f"============= employee found for processing message {employee}")
                        processed_message = DocumensoService.ReplaceNotificationVariables(
                            service.documenso_notification_message, 
                            employee, 
                            document
                        )
                        
                        # Get admin users (superusers)
                        admin_users = User.objects.filter(is_superuser=True, is_active=True)
                        
                        # Prepare recipients list - start with admin users
                        recipients = list(admin_users)
                        
                        # Add reporting manager if exists
                        if employee.employee_work_info.reporting_manager_id:
                            recipients.append(employee.employee_work_info.reporting_manager_id.employee_user_id)
                        
                        # Send notification to all recipients at once
                        if recipients:
                            notify.send(
                                bot,
                                recipient=recipients,
                                verb=processed_message,
                                verb_ar=processed_message,
                                verb_de=processed_message,
                                verb_es=processed_message,
                                verb_fr=processed_message,
                                redirect=reverse("employee-view-individual", args=[employee.id]),
                                label="BOT",
                                icon="information",
                            )
                            logger.info(f"============= notification sent to admin user for document: {document.get('title')} (ID: {document.get('id')})")
                        
                        logger.info(f"============= unsigned document: {document.get('title')} (ID: {document.get('id')})")
            else:
                logger.info(f"============= no unsigned documents found")
        else:
            logger.info(f"============= documenso api key not found for {service.company.company}")
    pass


def start():
    logger.info(f"============= integrations scheduler started")
    scheduler = BackgroundScheduler()
    if os.environ.get('RUN_MAIN', None) != 'true':
        job = scheduler.add_job(unsigned_documents_reminder, trigger='cron', hour=0, minute=5)
        scheduler.start()
        logger.info(f"============= integrations scheduler started successfully")
        logger.info(f"============= Next execution time: {job.next_run_time}")





