from datetime import timedelta
from employee.models import Employee, EmployeeWorkInformation
from django import template
from datetime import datetime

register = template.Library()


register = template.Library()


@register.filter(name="add_days")
def add_days(value, days):
    # Check if value is not None before adding days
    if value is not None:
        return value + timedelta(days=days)
    else:
        return None

@register.filter
def first_item(value):
    try:
        return value[0]
    except (IndexError, TypeError):
        return ''
    

@register.filter
def iso_to_datetime(value, fmt="%Y-%m-%d %H:%M"):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except Exception:
        return value
    
@register.filter(name="is_reportingmanager")
def is_reportingmanager(user):
    """{% load employee_filter %}

    This method will return true if the user employee profile is reporting manager to any employee
    """
    employee = Employee.objects.filter(employee_user_id=user).first()
    return EmployeeWorkInformation.objects.filter(
        reporting_manager_id=employee
    ).exists()