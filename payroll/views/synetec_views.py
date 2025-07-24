from django.shortcuts import render
from  payroll.forms.synetec_forms import *
from django.http import HttpResponse , JsonResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from horilla.decorators import (
    login_required,
    hx_request_required,
    permission_required
)
from payroll.models.synetec_models import *

@login_required
@permission_required('payroll.view_payslipautomationemail')
def payslipAutomationEmailsView(request):
    payslip_auto_generate = PayslipAutomationEmail.objects.all()
    context = {'payslip_auto_generate':payslip_auto_generate}
    return render(request, "payroll/settings/auto_payslip_emails_settings.html", context)


@login_required
@hx_request_required
def create_or_update_auto_email_payslip(request, id=None):
    if not (
        request.user.has_perm("payroll.change_payslipautomationemail") or
        request.user.has_perm("payroll.add_payslipautomationemail")
    ):
        raise PermissionDenied
    auto_payslip = None
    if id:
        auto_payslip = PayslipAutomationEmail.objects.get(id=id)
    form = PayslipAutoGenerateForm(instance=auto_payslip)
    if request.method == "POST":
        form = PayslipAutoGenerateForm(request.POST, instance=auto_payslip)
        if form.is_valid():
            auto_payslip = form.save()
            company = (
                auto_payslip.company_id if auto_payslip.company_id else "All company"
            )
            messages.success(
                request, _(f"Email Automation generated for {company} created successfully ")
            )
            return HttpResponse("<script>window.location.reload()</script>")
    return render(
        request, "payroll/settings/email_automation.html", {"form": form}
    )


@login_required
@permission_required("payroll.change_payslipautomationemail")
def activate_auto_email_payslip_generate(request):
    """
    ajax function to update is active field in PayslipAutoGenerate.
    Args:
    - isChecked: Boolean value representing the state of PayslipAutoGenerate,
    - autoId: Id of PayslipAutoGenerate object
    """
    isChecked = request.POST.get("isChecked")
    autoId = request.POST.get("autoId")
    payslip_auto = PayslipAutomationEmail.objects.get(id=autoId)
    if isChecked == "true":
        payslip_auto.scheduler_status = True
        response = {
            "type": "success",
            "message": _("Email Scheduler activated successfully."),
        }
    else:
        payslip_auto.scheduler_status = False
        response = {
            "type": "success",
            "message": _("Email Scheduler deactivated successfully."),
        }
    payslip_auto.save()
    return JsonResponse(response)

@login_required
@hx_request_required
@permission_required("payroll.delete_payslipautomationemail")
def delete_auto_email_payslip(request, id):
    """
    Delete a PayslipAutoGenerate object.

    Args:
        auto_id: The ID of PayslipAutoGenerate object to delete.

    Returns:
        Redirects to the contract view after successfully deleting the contract.

    """
    try:
        auto_payslip = PayslipAutomationEmail.objects.get(id=id)
        if not auto_payslip.scheduler_status:
            company = (
                auto_payslip.company if auto_payslip.company else "All company"
            )
            auto_payslip.delete()
            messages.success(
                request, _(f"Email Scheduler for {company} deleted successfully.")
            )
        else:
            messages.info(request, _(f"Active 'Email Scheduler' cannot delete."))
        return HttpResponse("<script>window.location.reload();</script>")
    except PayslipAutomationEmail.DoesNotExist:
        messages.error(request, _("Email Scheduler not found."))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def company_timezone(request):
    selected_company_id = request.session.get("selected_company")
    if selected_company_id == "all" or not selected_company_id:
        companies = Company.objects.all()
    else:
        companies = Company.objects.filter(id=selected_company_id)
    initial_data = {}
    if selected_company_id and selected_company_id != "all":
        selected_company = Company.objects.filter(id=selected_company_id).first()
        if selected_company:
            initial_data = {
                'company': selected_company,
                'timezone': selected_company.timezone or 'UTC'
            }

    form = CompanyTimezoneForm(initial=initial_data)
    if request.method == 'POST':
        form = CompanyTimezoneForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            timezone = form.cleaned_data['timezone']
            company.timezone = timezone
            company.save()
            messages.success(request, f'Timezone of {company} updated successfully')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    
    return render(
        request,
        "payroll/settings/timezone_settings.html",
        {
            "timezone_form": form,
            "companies": companies,
            "selected_company_id": selected_company_id,
        },
    )
