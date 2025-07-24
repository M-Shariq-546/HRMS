from base.models import Company
from django.contrib import messages
from django.shortcuts import redirect

def update_company_notification_access(request):
    """
    Retrieves a list of companies that have the 'is_notified_access' flag set to True.
    """
    if not request.user.has_perm('base.change_company'):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('general-settings')
    company_id = request.POST.get('company_id')
    access_status = request.POST.get('access_status') == 'on'
    if not company_id:
        messages.error(request, "Company ID is required.")
        return redirect('general-settings')

    try:
        company = Company.objects.get(id=company_id)
        company.is_notified_access = access_status
        company.save()
        messages.success(request, "Company notification access updated successfully.")
    except Company.DoesNotExist:
        messages.error(request, "Company not found.")
    return redirect('general-settings')