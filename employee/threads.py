from employee.models import Employee , EmployeeWorkInformation
from horilla.utils.logger import HorillaLogger
from base.services.email_service import email_service
from django.conf import settings
from base.models import Company
from django.template import loader
from django.template.loader import render_to_string
from base.context_processors import white_labelling_company
from base.services.documenso_service import DocumensoService


logger = HorillaLogger('employee.threads')


def send_new_employee_announcement(request,  new_employee, company_instance):
    html_email_template_name='company_welcome_template.html',
    logger.info(' ============= The Welcome email thread started ========== ')
    employees_work_infos = EmployeeWorkInformation.objects.filter(company_id_id=company_instance.id)
    employees_emails_list = [employee.employee_id.email for employee in employees_work_infos if employee.employee_id is not None]
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    context = {
        'new_employee': new_employee,
        'company_name': company_instance,
        'host':host,
        'protocol':protocol,
        'company_icon': company_instance.get_icon_url_for_email() if company_instance.icon else None,
        'white_label_company_name': white_labelling_company(request)['white_label_company_name'],
    }
    
    if not employees_emails_list:
        return
    
    to_email = employees_emails_list[0]
    cc_emails = employees_emails_list[1:] if len(employees_emails_list) > 1 else []
    
    subject = f"Welcome {new_employee.employee_first_name} {new_employee.employee_last_name} to {company_instance}!"
    
    html_body = loader.render_to_string(html_email_template_name, context)
    
    email_service.send_email(
        emails=[to_email],
        subject=subject,
        cc=cc_emails,
        message=html_body,
    )

def send_welcome_email_to_employee(request, new_employee, company_instance):
    html_email_template_name='new_employee_welcome_template.html',
    logger.info(' ====== the welcome email to single employee started ======= ')
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    context = {
        'new_employee': new_employee,
        'host':host,
        'protocol':protocol,
        'company_name': company_instance,
        'company_icon': company_instance.get_icon_url_for_email() if company_instance.icon else None,
        'white_label_company_name': white_labelling_company(request)['white_label_company_name'],
    }
    
    subject = f"Welcome to {company_instance}!"
    
    html_body = loader.render_to_string(html_email_template_name, context)
    
    email_service.send_email(
        emails=[new_employee.email],
        subject=subject,
        message=html_body,
    )


def send_onboarding_email_to_employee(request, new_employee, company_instance):
    documenso_service = DocumensoService()
    if documenso_service.IsDocumensoConnected(company_instance):
        created_documents = documenso_service.CreateDocumentFromTemplate([
            {
                "title": "Onboarding Document",
                'email': new_employee.email,
                'name': f"{new_employee.employee_first_name} {new_employee.employee_last_name}",
            }
        ], company_instance, new_employee)
        documents_list = []
        if created_documents:
            for document in created_documents:
                logger.info(f'document_id for new employee {new_employee.employee_first_name} {new_employee.employee_last_name} =======  : {document}')
                logger.info(f'===== document id {document}')
                documents_list.append(str(document))
            logger.info(f'===== documents final list {documents_list}')
            new_employee.documenso_documents_list = ",".join(documents_list)
            new_employee.save()
    else:
        logger.info(f'Documenso is not connected to the company {company_instance}')

def EmployeeWelcomeMailsThread(request, new_employee, company_instance):
    logger.info(f" The checks of employee {new_employee.send_welcome_email_to_company} && {new_employee.send_welcome_email_to_employee}")
    if new_employee.send_welcome_email_to_company:
        send_new_employee_announcement(request, new_employee, company_instance)
    if new_employee.send_welcome_email_to_employee:
        send_welcome_email_to_employee(request, new_employee, company_instance)
    if new_employee.send_onboarding_email_to_employee:
        send_onboarding_email_to_employee(request, new_employee, company_instance)
    
        
    logger.info('====== The thread ended successfully =====')
