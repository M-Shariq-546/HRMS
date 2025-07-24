from helpdesk.models import DepartmentManager
from notifications.signals import notify
from django.urls import reverse
from employee.models import EmployeeWorkInformation
from base.models import *
from django.db import transaction
from employee.models import Employee
from django.contrib.auth.models import User


def is_department_manager(request, ticket):
    """
    Method used to find the user is a department manger of given ticket
    """
    user_emp = request.user.employee_get
    if ticket.assigning_type == "job_position":
        job_position = ticket.get_raised_on_object()
        department = job_position.department_id
    elif ticket.assigning_type == "department":
        department = ticket.get_raised_on_object()
    else:
        return False
    return DepartmentManager.objects.filter(
        manager=user_emp, department=department
    ).exists()


def notification_to_request_user(user, assignees, ticket):
    notify.send(
        user.employee_get,
        recipient=user,
        verb = "Your Ticket has been created successfully",
        verb_ar = "تم إنشاء تذكرتك بنجاح",
        verb_de = "Ihr Ticket wurde erfolgreich erstellt",
        verb_es = "Tu ticket ha sido creado con éxito",
        verb_fr = "Votre ticket a été créé avec succès",
        icon="infinite",
        redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
    )

def notification_to_managers_users(user, department_managers, ticket, type, instance):
    for departmen_manager in department_managers:
        notify.send(
            user.employee_get,
            recipient=departmen_manager.manager.employee_user_id,
            verb = f"A New ticket is added for {type} {instance}",
            verb_ar = f"تمت إضافة تذكرة جديدة لـ {type} {instance}",
            verb_de = f"Ein neues Ticket wurde für {type} {instance} hinzugefügt",
            verb_es = f"Se ha añadido un nuevo ticket para {type} {instance}",
            verb_fr = f"Un nouveau ticket a été ajouté pour {type} {instance}",
            icon="infinite",
            redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
        )

def notification_to_individual_user(user, assignees, ticket, type, instance):
    notify.send(
        user.employee_get,
        recipient=instance.employee_user_id,
        verb = "A New Ticket has been forwarded to you",
        verb_ar = "تم تحويل تذكرة جديدة إليك.",
        verb_de = "Ein neues Ticket wurde an Sie weitergeleitet.",
        verb_es = "Se te ha reenviado un nuevo ticket.",
        verb_fr = "Un nouveau ticket vous a été transféré.",
        icon="infinite",
        redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
    )

def Department_job_user_query(data):
    if data.get('assigning_type') == 'department':
        department = Department.objects.get(id=data.get('raised_on'))
        department_managers = department.dept_manager.all()
        return department , None, None, department_managers
    if data.get('assigning_type') == 'job_position':
        job_position = JobPosition.objects.get(id=data.get('raised_on'))
        department_managers = job_position.department_id.dept_manager.all()
        return None, job_position , None, department_managers
    if data.get('assigning_type') == 'individual':
        employee = Employee.objects.get(id=data.get('raised_on'))
        return None, None, employee, None
    

def send_assigning_ticket_notification(request ,assignees, ticket):
    for assignee in assignees:
        notify.send(
            request.user.employee_get,
            recipient=assignee.employee_user_id,
            verb = "You have been assigned a new ticket.",
            verb_ar = "تم تعيين تذكرة جديدة لك.",
            verb_de = "Ihnen wurde ein neues Ticket zugewiesen.",
            verb_es = "Se te ha asignado un nuevo ticket.",
            verb_fr = "Un nouveau ticket vous a été attribué.",
            icon="infinite",
            redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
        )

def send_removing_ticket_notification(request ,removals, ticket):
    for remove in removals:
        notify.send(
            request.user.employee_get,
            recipient=remove.employee_user_id,
            verb =f"You have been removed from ticket {ticket.title[:15]}",
            verb_ar = f"تم إزالتك من التذكرة {ticket.title[:15]}",
            verb_de = f"Sie wurden aus dem Ticket {ticket.title[:15]} entfernt", 
            verb_es = f"Se te ha eliminado del ticket {ticket.title[:15]}", 
            verb_fr = f"Vous avez été retiré du ticket {ticket.title[:15]}",
            icon="infinite",
            redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
        )


def comment_sent_notification(sender , ticker_originator, assignees, ticket):
    if sender == ticker_originator:
        for assignee in assignees:
            notify.send(
                sender.employee_get,
                recipient=assignee.employee_user_id,
                verb = "You have received a comment.",
                verb_ar = "لقد تلقيت تعليقًا.",
                verb_de = "Sie haben einen Kommentar erhalten.",
                verb_es = "Has recibido un comentario.",
                verb_fr = "Vous avez reçu un commentaire.",
                icon="infinite",
                redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
            )
    elif sender.employee_get in assignees:
        notify.send(
            sender.employee_get,
            recipient=ticker_originator,
            verb = "You have received a comment.",
            verb_ar = "لقد تلقيت تعليقًا.",
            verb_de = "Sie haben einen Kommentar erhalten.",
            verb_es = "Has recibido un comentario.",
            verb_fr = "Vous avez reçu un commentaire.",
            icon="infinite",
            redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
        )
    else:
        notify.send(
            sender.employee_get,
            recipient=ticker_originator,
            verb = "You have received a comment.",
            verb_ar = "لقد تلقيت تعليقًا.",
            verb_de = "Sie haben einen Kommentar erhalten.",
            verb_es = "Has recibido un comentario.",
            verb_fr = "Vous avez reçu un commentaire.",
            icon="infinite",
            redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
        )

ASSIGNING_TYPE_MODEL_MAP = {
    'department': (Department, 'department'),
    'job_position': (JobPosition, 'job_position'),
    'individual': (Employee, None),
}

def get_instance(assigning_type, obj_id):
    model_class, attr = ASSIGNING_TYPE_MODEL_MAP[assigning_type]
    instance = model_class.objects.get(id=obj_id)
    return getattr(instance, attr) if attr else instance

def tracking_history_list(instance, old_raised_on, new_raised_on, updated_by, previous_assigning_type, new_assigning_type):
    from helpdesk.models import TicketHistory
    previous_instance = get_instance(previous_assigning_type, old_raised_on)
    new_instance = get_instance(new_assigning_type, new_raised_on)

    with transaction.atomic():
        TicketHistory.objects.create(
            ticket=instance,
            previous=previous_instance,
            new=new_instance,
            updated_by=updated_by.employee_get,
        )
    return TicketHistory.objects.filter(ticket=instance)

def status_priority_update_history(ticket, previous_status=None , new_status=None, employee=None):
    from helpdesk.models import TicketHistory
    with transaction.atomic():
        TicketHistory.objects.create(ticket=ticket, previous=previous_status, new=new_status, updated_by=employee)
        
    pass

def history_fetched(instance):
    from helpdesk.models import TicketHistory
    result = TicketHistory.objects.filter(ticket=instance)
    return result

def claim_request_notification_to_self_user(horilla_bot, user):
    notify.send(
        horilla_bot,
        recipient=user,
        verb = "Your claim request has been sent successfully",
        verb_ar = "تم إرسال طلب المطالبة الخاص بك بنجاح.",
        verb_de = "Ihre Anspruchsanfrage wurde erfolgreich gesendet.",
        verb_es = "Tu solicitud de reclamación se ha enviado correctamente.",
        verb_fr = "Votre demande de réclamation a été envoyée avec succès.",
        icon="infinite",
        redirect=reverse("ticket-view"),
        )
    
def claim_request_to_managers(user, ticket):
    work_informations = EmployeeWorkInformation.objects.get(employee_id__employee_user_id=user)
    if work_informations:
        managers = work_informations.department_id.dept_manager.all()
        for manager in managers:
            notify.send(
                    user.employee_get,
                    recipient=manager.manager.employee_user_id,
                    verb = f"You received a claim request for ticket {ticket}",
                    verb_ar = f"لقد تلقيت طلب مطالبة للتذكرة {ticket}.",
                    verb_de = f"Sie haben eine Anspruchsanfrage für Ticket {ticket} erhalten.",
                    verb_es = f"Has recibido una solicitud de reclamación para el ticket {ticket}.",
                    verb_fr = f"Vous avez reçu une demande de réclamation pour le ticket {ticket}.",
                    icon="infinite",
                    redirect=reverse("ticket-detail", kwargs={"ticket_id": ticket.id}),
            )
            
            
def get_company_logo(request):
    company_logo = request.session.get('selected_company')
    company = Company.objects.get(id=company_logo)
    return company.get_icon_url()
    
    