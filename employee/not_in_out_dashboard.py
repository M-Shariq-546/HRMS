"""
employee/context_processors.py

This module is used to write context processor methods
"""

import json
from datetime import date
from .validations import *
import os
from django import template
from django.apps import apps
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from horilla.utils.logger import HorillaLogger
from base.backends import ConfiguredEmailBackend
from base.forms import MailTemplateForm
from base.methods import export_data, generate_pdf
from base.models import HorillaMailTemplate
from employee.filters import EmployeeFilter
from employee.models import Employee
from horilla import settings
from horilla.decorators import login_required, manager_can_enter
from base.services.email_service import email_service

logger = HorillaLogger("horilla.not_in_out_dashboard")

def paginator_qry(qryset, page_number):
    """
    This method is used to paginate query set
    """
    paginator = Paginator(qryset, 20)
    qryset = paginator.get_page(page_number)
    return qryset


@login_required
@manager_can_enter("employee.view_employee")
def not_in_yet(request):
    """
    This context processor wil return the employees, if they not marked the attendance
    for the day
    """
    page_number = request.GET.get("page")
    previous_data = request.GET.urlencode()
    emps = (
        EmployeeFilter({"not_in_yet": date.today()})
        .qs.exclude(employee_work_info__isnull=True)
        .filter(is_active=True)
    )

    return render(
        request,
        "dashboard/not_in_yet.html",
        {
            "employees": paginator_qry(emps, page_number),
            "pd": previous_data,
        },
    )


@login_required
@manager_can_enter("employee.view_employee")
def not_out_yet(request):
    """
    This context processor wil return the employees, if they not marked the attendance
    for the day
    """
    emps = (
        EmployeeFilter({"not_out_yet": date.today()})
        .qs.exclude(employee_work_info__isnull=True)
        .filter(is_active=True)
    )
    return render(request, "dashboard/not_out_yet.html", {"employees": emps})


@login_required
@manager_can_enter("employee.change_employee")
def send_mail(request, emp_id=None):
    """
    This method used send mail to the employees
    """
    employee = None
    if emp_id:
        employee = Employee.objects.get(id=emp_id)
    employees = Employee.objects.all()

    templates = HorillaMailTemplate.objects.all()
    return render(
        request,
        "employee/send_mail.html",
        {"employee": employee, "templates": templates, "employees": employees},
    )


@login_required
@manager_can_enter("employee.change_employee")
def employee_data_export(request, emp_id=None):
    """
    This method used send mail to the employees
    """

    resolver_match = request.resolver_match
    if (
        resolver_match
        and resolver_match.url_name
        and resolver_match.url_name == "export-data-employee"
    ):
        employee = None
        if emp_id:
            employee = Employee.objects.get(id=emp_id)

        context = {"employee": employee}

        # IF LEAVE IS INSTALLED
        if apps.is_installed("leave"):
            from leave.filters import LeaveRequestFilter
            from leave.forms import LeaveRequestExportForm

            excel_column = LeaveRequestExportForm()
            export_filter = LeaveRequestFilter()
            context.update(
                {
                    "leave_excel_column": excel_column,
                    "leave_export_filter": export_filter.form,
                }
            )

        # IF ATTENDANCE IS INSTALLED
        if apps.is_installed("attendance"):
            from attendance.filters import AttendanceFilters
            from attendance.forms import AttendanceExportForm
            from attendance.models import Attendance

            excel_column = AttendanceExportForm()
            export_filter = AttendanceFilters()
            context.update(
                {
                    "attendance_excel_column": excel_column,
                    "attendance_export_filter": export_filter.form,
                }
            )

        # IF PAYROLL IS INSTALLED
        if apps.is_installed("payroll"):
            from payroll.filters import PayslipFilter
            from payroll.forms.component_forms import PayslipExportColumnForm

            context.update(
                {
                    "payroll_export_column": PayslipExportColumnForm(),
                    "payroll_export_filter": PayslipFilter(request.GET),
                }
            )

        return render(request, "employee/export_data_employee.html", context=context)
    return export_data(
        request=request,
        model=Attendance,
        filter_class=AttendanceFilters,
        form_class=AttendanceExportForm,
        file_name="Attendance_export",
    )


@login_required
def get_template(request, emp_id):
    """
    This method is used to return the mail template
    """
    body = HorillaMailTemplate.objects.get(id=emp_id).body
    return JsonResponse({"body": body})


@login_required
def get_mail_preview(request, emp_id=None):
    """
    This method is used to return the mail template
    """
    body = request.GET.get("body")
    template_bdy = template.Template(body)
    # candidate_id = request.GET.get("candidate_id")
    if emp_id:
        employee = Employee.objects.get(id=emp_id)
        context = template.Context(
            {"instance": employee, "self": request.user.employee_get}
        )
        body = template_bdy.render(context) or " "
    return JsonResponse({"body": body})


@login_required
@manager_can_enter(perm="recruitment.change_employee")
def send_mail_to_employee(request):
    """
    This method is used to send acknowledgement mail to the candidate
    """
    employee_id = request.POST["id"]
    subject = request.POST.get("subject")
    bdy = request.POST.get("body")

    employee_ids = request.POST.getlist("employees")
    employees = Employee.objects.filter(id__in=employee_ids)

    other_attachments = request.FILES.getlist("other_attachments")
    attachments = [
        (file.name, file.read(), file.content_type) for file in other_attachments
    ]

    if employee_id:
        employee_obj = Employee.objects.filter(id=employee_id)
    else:
        employee_obj = Employee.objects.none()
    employees = (employees | employee_obj).distinct()

    template_attachment_ids = request.POST.getlist("template_attachments")
    for employee in employees:
        bodys = list(
            HorillaMailTemplate.objects.filter(
                id__in=template_attachment_ids
            ).values_list("body", flat=True)
        )
        for html in bodys:
            # due to not having solid template we first need to pass the context
            template_bdy = template.Template(html)
            context = template.Context(
                {"instance": employee, "self": request.user.employee_get}
            )
            render_bdy = template_bdy.render(context)
            attachments.append(
                (
                    "Document",
                    generate_pdf(render_bdy, {}, path=False, title="Document").content,
                    "application/pdf",
                )
            )

        status, message = required_fields_check(request, employee)

        if not status:
            messages.error(request, f"{message}")
            return HttpResponse("<script>window.location.reload()</script>")

        template_bdy = template.Template(bdy)
        context = template.Context(
            {
                "instance": employee, "self": request.user.employee_get, 
                "Receiver_Full_name": employee.get_full_name(),
                "Sender_Full_name": request.user.employee_get.get_full_name(),
                "Receiver_Company": employee.employee_work_info.company_id if employee.employee_work_info.company_id else messages.error(request, 'Please Add Company to this employee profile'),
                "Sender_Company": request.user.employee_get.employee_work_info.company_id if request.user.employee_get.employee_work_info.company_id else os.environ.get("PRODUCT_EMAIL_SENDER_NAME", 'WAVEBOT'),
                "Receiver_Job_position": employee.employee_work_info.job_position_id if employee.employee_work_info.job_position_id else "New Team Member",
                "Sender_Job_position": request.user.employee_get.employee_work_info.job_position_id if request.user.employee_get.employee_work_info.job_position_id else os.environ.get("PRODUCT_NAME", 'HRMS'),
                "Receiver_Email": employee.get_email() if employee.get_email() else "",
                "Sender_Email": request.user.employee_get.get_email() if request.user.employee_get.get_email() else "info@horilla.synetechq.com",
                "Candidate_Full_name": employee.get_full_name() if employee.get_full_name() else "",
                "Candidate_Company": employee.get_company if employee.get_company else "",
                "Candidate_Job_position": employee.get_job_position if employee.get_job_position else "",
                "Candidate_Email": employee.get_email if employee.get_email else "",
            }
        )

        render_bdy = template_bdy.render(context)
        send_to_mail = (
            employee.email
        )
        logger.info(f"send_to_mail inside send_mail_to_employee functions of service : {send_to_mail}")
        success = email_service.send_email(
            emails=[send_to_mail],
            subject=subject,
            message=render_bdy,
            custom_variables=context,
            attachments=attachments,
            is_template=True,
        )
        logger.info(f"success inside send_mail_to_employee functions of service : {success}")

        if success:
            if employee.email:
                messages.success(request, f"Mail sent to {employee.get_full_name()}")
            else:
                messages.info(request, f"Email not set for {employee.get_full_name()}")
        else:
            messages.error(request, "Something went wrong")
            
    return HttpResponse("<script>window.location.reload()</script>")
