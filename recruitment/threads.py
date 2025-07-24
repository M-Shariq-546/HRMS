from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from base.services.email_service import email_service
from django.conf import settings
from horilla.utils.logger import HorillaLogger

logger = HorillaLogger("recruitment.views")

def send_email_to_candidate_thread(instance, user, is_edited, host, protocol):
    candidate_email = instance.candidate_id.email
    admin_email = user.email  

    if is_edited:
        subject = "Interview Scheduled Updated"
    else:
        subject = "Interview Scheduled" 
    
    context = {
        'instance':instance,
        'candidate_name': instance.candidate_id.name,
        'interview_date': instance.interview_date,
        'interview_time': instance.interview_time,
        'user':user,
        'host':host,
        'protocol':protocol,
        'company_email':instance.candidate_id.recruitment_id.company_id.email,
        'company_phone':instance.candidate_id.recruitment_id.company_id.phone,
        'company_name':instance.candidate_id.recruitment_id.company_id,
        'is_edited': is_edited,
    }

    # Send the email to the candidate
    email_body = render_to_string("candidate/interview-email-update.html", context)

    success = email_service.send_email(
        emails=[candidate_email],
        subject=subject,
        message=email_body,
        custom_variables=context
    )
    
    if not success:
        logger.error(f"Failed to send interview email to {candidate_email}")