from horilla.utils.logger import HorillaLogger
from datetime import datetime
from notifications.signals import notify
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

def str_to_seconds(time_str):
    """Convert HH:MM string to total seconds."""
    try:
        if not isinstance(time_str, str):
            raise ValueError(f"Expected string input, got {type(time_str)}")
        parts = time_str.strip().split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid time format '{time_str}', expected 'HH:MM' or similar.")

        hours_str, minutes_str = parts
        try:
            hours = int(hours_str)
            minutes = int(minutes_str)
        except ValueError as e:
            logging.error(f"Non-integer values in time string: {time_str}", exc_info=True)
            raise ValueError(f"Cannot convert '{time_str}' to seconds: non-integer parts") from e

        if minutes < 0 or minutes >= 60:
            raise ValueError(f"Minute value out of range in '{time_str}' (0-59)")
        return hours * 3600 + minutes * 60
    except Exception as e:
        logging.error(f"Invalid time format: {time_str}. Error: {str(e)}", exc_info=True)
        raise ValueError(f"Cannot convert '{time_str}' to seconds: {str(e)}") from e


def compensation_leaves_notification_request_user(user, status="created"):
    """
    Send notification to the user who created a compensatory leave request.
    
    Args:
        user: The user who created the request
        status: Status of the request ("created", "reviewed", or "approved")
    """
    try:
        verb_mapping = {
            "created": {
                "en": "Your Compensatory leave request created successfully",
                "ar": "تم إنشاء طلب الإجازة التعويضية بنجاح",
                "de": "Ihr Antrag auf Ausgleichsurlaub wurde erfolgreich erstellt",
                "es": "Su solicitud de permiso compensatorio se ha creado con éxito",
                "fr": "Votre demande de congé compensatoire a été créée avec succès"
            },
            "reviewed": {
                "en": "Your Compensatory leave request has been reviewed",
                "ar": "تمت مراجعة طلب الإجازة التعويضية الخاص بك",
                "de": "Ihr Antrag auf Ausgleichsurlaub wurde überprüft",
                "es": "Su solicitud de permiso compensatorio ha sido revisada",
                "fr": "Votre demande de congé compensatoire a été examinée"
            },
            "approved": {
                "en": "Your Compensatory leave request has been approved",
                "ar": "تمت الموافقة على طلب الإجازة التعويضية الخاص بك",
                "de": "Ihr Antrag auf Ausgleichsurlaub wurde genehmigt",
                "es": "Su solicitud de permiso compensatorio ha sido aprobada",
                "fr": "Votre demande de congé compensatoire a été approuvée"
            }
        }
        notify.send(
            user.employee_get,
            recipient=user,
            verb=verb_mapping.get(status, verb_mapping["created"])["en"],
            verb_ar=verb_mapping.get(status, verb_mapping["created"])["ar"],
            verb_de=verb_mapping.get(status, verb_mapping["created"])["de"],
            verb_es=verb_mapping.get(status, verb_mapping["created"])["es"],
            verb_fr=verb_mapping.get(status, verb_mapping["created"])["fr"],
            icon="infinite",
            redirect=reverse("view-compensatory-leave"),
        )
        return True
    except Exception as e:
        logging.error(f"Failed to send notification to user {user.id}: {str(e)}", exc_info=True)
        return False

def compensation_leaves_notification_department_managers_or_admin(employee):
    """
    Send notification to department managers or admins about a compensatory leave request.
    
    Args:
        employee: The employee who created the request
        
    Returns:
        bool: True if notifications were sent successfully, False otherwise
    """
    try:
        User = get_user_model()
        content_type = ContentType.objects.get(app_label='leave', model='compensatoryleaverequest')

        admin_users = User.objects.filter(
            user_permissions__in=Permission.objects.filter(codename__in=['change_compensatoryleaverequest', 'view_compensatoryleaverequest', 'add_compensatoryleaverequest', 'delete_compensatoryleaverequest'], content_type=content_type)
        ).distinct().union(
            User.objects.filter(
                groups__permissions__in=Permission.objects.filter(codename__in=['change_compensatoryleaverequest', 'view_compensatoryleaverequest', 'add_compensatoryleaverequest', 'delete_compensatoryleaverequest'], content_type=content_type)
            ).distinct()
        )
        recipients = list(admin_users)
        if hasattr(employee, 'employee_work_info') and employee.employee_work_info:
            manager = employee.employee_work_info.reporting_manager_id
            if manager and manager.employee_user_id not in recipients:
                recipients.append(manager.employee_user_id)
        notify.send(
            employee,
            recipient=recipients,
            verb="You have received a compensatory leave request to review",
            verb_ar = "لقد تلقيت طلب إجازة تعويضية للمراجعة",
            verb_de = "Sie haben einen Antrag auf Ausgleichsurlaub zur Überprüfung erhalten",
            verb_es = "Ha recibido una solicitud de permiso compensatorio para revisar",
            verb_fr = "Vous avez reçu une demande de congé compensatoire à examiner",
            icon="infinite",
            redirect=reverse("view-compensatory-leave"),
        )
        return True
    except Exception as e:
        logging.error(f"Failed to send notifications for employee {employee.id}: {str(e)}", exc_info=True)
        return False