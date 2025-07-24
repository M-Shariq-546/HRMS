import os
from apscheduler.schedulers.background import BackgroundScheduler
from attendance.models import Attendance
from employee.models import EmployeeWorkInformation
from base.models import Company
from horilla.utils.logger import HorillaLogger
from django.urls import reverse
from django.contrib.auth.models import User
from notifications.signals import notify
from leave.leaves_time_method import str_to_seconds
from horilla.utils.logger import HorillaLogger


logger = HorillaLogger('attendance.scheduler')

def Minimum_hours_notification():
    """
    Check for employees who haven't met their minimum working hours requirement
    and send them notifications.
    
    This function:
    1. Filters companies that have notification access enabled
    2. For each company, gets all employees
    3. For each employee, compares total worked hours with required hours
    4. Sends a notification if worked hours are less than required
    """
    companies = Company.objects.filter(is_notified_access=True)
    total_hours = None
    total_worked_hours = None    
    bot = User.objects.filter(username="Horilla Bot").first()
    if not bot:
        logger.error("Horilla Bot user not found. Cannot send notifications.")
        return
    for company in companies:    
        employees = EmployeeWorkInformation.objects.filter(company_id=company)
        for employee in employees:
            try:
                all_attendances = Attendance.objects.filter(employee_id=employee.employee_id)
                total_hours = sum(str_to_seconds(attendance.minimum_hour) for attendance in all_attendances)
                total_worked_hours = sum(str_to_seconds(attendance.attendance_worked_hour) for attendance in all_attendances)        
                if total_worked_hours < total_hours:
                    notify.send(
                    bot,
                    recipient=employee.employee_id.employee_user_id,
                    verb = "Your attendance is short. Please work harder and put in extra time to complete your weekly target.",
                    verb_ar = "حضورك غير كافٍ، يُرجى العمل بجهد إضافي لإكمال هدفك الأسبوعي.",
                    verb_de = "Ihre Anwesenheit ist unzureichend. Bitte arbeiten Sie härter und leisten Sie Überstunden, um Ihr Wochenziel zu erreichen.",
                    verb_es = "Su asistencia es insuficiente. Por favor, trabaje más duro y dedique tiempo extra para cumplir su objetivo semanal.",
                    verb_fr = "Votre présence est insuffisante. Veuillez travailler davantage et faire des heures supplémentaires pour atteindre votre objectif hebdomadaire.",
                    redirect=reverse("view-my-attendance"),
                    icon="info",
                )
            except Exception as e:
                logger.error(f"Error processing attendance for employee {employee.employee_id}: {e}")
    logger.info('running the script of timing for the notification of minimum hours ')


def start():
    """
    Initializes and starts background tasks using APScheduler when the server is running.
    """
    if os.environ.get("RUN_MAIN") != "true":
        return 
    
    logger.info("Initializing Attendance scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(Minimum_hours_notification, "interval", minutes=1)
    logger.info("Added Minimum_hours_notification job to scheduler")
    
    scheduler.start()
    logger.info("Attendance scheduler started successfully")
