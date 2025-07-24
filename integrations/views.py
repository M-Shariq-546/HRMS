import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from employee.models import EmployeeWorkInformation
from base.models import Company
from integrations.models import CompanyIntegration, AvailableIntegration, DocumensoFieldsData
from django.urls import reverse
from django.utils import timezone
import os
from employee.models import Employee
from django.db import transaction
import json
from django.views.decorators.csrf import csrf_exempt
from horilla.utils.logger import HorillaLogger
from django.contrib import messages
from integrations.forms.forms import CompanyIntegrationUpdateForm, DocumensoConnectionForm, WiseConnectionForm
from django.core.signing import Signer, BadSignature
from base.services.image_service import FileStorageService
from base.services.slack_service import SlackService
from base.services.documenso_service import DocumensoService
from base.services.wise_service import WiseService
from django.middleware.csrf import get_token

logger = HorillaLogger("recruitment.views")

signer = Signer()


# Service-specific OAuth details
OAUTH_PROVIDERS = {
    "slack": {
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access"
    },
    # Add more services here...
}

def start_oauth(request, service):
    """
    Start the OAuth flow for any service.
    """
    service = service.lower()
    provider = None
    company = request.session.get('selected_company')
    try:
        provider = CompanyIntegration.objects.get(service_name=service, company=company)
    except CompanyIntegration.DoesNotExist:
        return JsonResponse({"error": "Service not supported."}, status=400)
    employee = None
    if not request.user.is_superuser:
        employee = EmployeeWorkInformation.objects.filter(employee_id=request.user.employee_get).first()
        if not employee:
            return JsonResponse({"error": "Employee information not found."}, status=404)
        company_id = str(employee.company_id.id)
        signed_state = signer.sign(company_id)  # Ensures integrity
    else:
        company_id = request.session.get('selected_company')
        if company_id == 'all' or company_id == None:
            messages.error(request, f"Please Select Company of which you want to connect the integration")
            return redirect('integrations:integration_list')
        signed_state = signer.sign(company_id)
    logger.info(f"========= service in start_oauth {service} ==========")
    auth_uri = OAUTH_PROVIDERS.get(service, {}).get("auth_url", "")
    logger.info(f"========= auth_uri in start_oauth {auth_uri} ==========")
    
    # Build the OAuth authorization URL dynamically based on the service
    authorization_url = f"{auth_uri}?client_id={provider.client_id}&redirect_uri={provider.redirect_uri}&scope={provider.scopes}&response_type=code&state={signed_state}"

    return redirect(authorization_url)

def oauth_callback(request, service):
    """
    Handle the OAuth callback and save the integration using DB-stored provider config.
    """
    service = service.lower()

    # Get provider from DB
    try:
        provider = CompanyIntegration.objects.get(service__iexact=service)
    except CompanyIntegration.DoesNotExist:
        return JsonResponse({"error": "Service not supported."}, status=400)

    # Authorization code from provider
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Authorization code missing."}, status=400)

    # Decode and validate state to get company_id
    state = request.GET.get("state")
    try:
        company_id = signer.unsign(state)
    except BadSignature:
        return JsonResponse({"error": "Invalid state parameter."}, status=400)

    company = Company.objects.filter(id=company_id).first()
    if not company:
        return JsonResponse({"error": "Company not found."}, status=404)

    # Check if already connected
    if CompanyIntegration.objects.filter(company=company, service=service).exists():
        return JsonResponse({"message": f"{service} is already connected."}, status=200)


    oauth_callback_status = SlackService.OauthCallback(code, company, provider, service)
    if oauth_callback_status:
        return JsonResponse({"message": f"{service} connected successfully."}, status=200)

    return JsonResponse({"message": f"{service} didn't connected ."}, status=400)
    



def disconnect_integration(request, service):
    """
    Disconnects a service (integration) for a company.
    """
    logger.info(f"Disconnect request for service: {service}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Accept header: {request.headers.get('Accept')}")
    
    try:
        company = None
        company = request.session.get('selected_company')
        logger.info(f"Selected company: {company}")
        
        if company == 'all':
            if request.headers.get('Accept') == 'application/json':
                logger.info("Returning JSON error for company selection")
                return JsonResponse({
                    'error': 'Please Select Company of which you want to disconnect the integration'
                }, status=400)
            messages.error(request, f"Please Select Company of which you want to disconnect the integration")
            return redirect('integrations:integration_list_react')
            
        service_obj = CompanyIntegration.objects.get(service_name=service, company=company)
        logger.info(f"Found service object: {service_obj}")
        
        if DocumensoService.IsDocumensoService(service):
            logger.info("Disconnecting Documenso service")
            logger.info(f"service_obj: {service_obj.service_name}")
            DocumensoService.DisconnectDocumenso(service_obj, company)
            if request.headers.get('Accept') == 'application/json':
                logger.info("Returning JSON success for Documenso")
                return JsonResponse({
                    'success': True,
                    'message': f"{service.capitalize()} integration has been disconnected."
                })
            messages.success(request, f"{service.capitalize()} integration has been disconnected.")
            return redirect('integrations:integration_list_react')
            
        elif WiseService.IsWiseService(service):
            logger.info("Disconnecting Wise service")
            WiseService.DisconnectWise(service_obj, company)
            if request.headers.get('Accept') == 'application/json':
                logger.info("Returning JSON success for Wise")
                return JsonResponse({
                    'success': True,
                    'message': f"{service.capitalize()} integration has been disconnected."
                })
            messages.success(request, f"{service.capitalize()} integration has been disconnected.")
            return redirect('integrations:integration_list_react')
            
        logger.info("Disconnecting Slack service")
        disconnected = SlackService.DisconnectSlack(service_obj, request.user, company)
        if disconnected:
            if request.headers.get('Accept') == 'application/json':
                logger.info("Returning JSON success for Slack")
                return JsonResponse({
                    'success': True,
                    'message': f"{service_obj.service_name.capitalize()} integration has been disconnected."
                })
            messages.success(request, f"{service_obj.service_name.capitalize()} integration has been disconnected.")
            return redirect('integrations:integration_list_react')
        else:
            if request.headers.get('Accept') == 'application/json':
                logger.info("Returning JSON error for Slack disconnect failure")
                return JsonResponse({
                    'error': f"Failed to disconnect {service} integration."
                }, status=400)
            messages.error(request, f"Failed to disconnect {service} integration.")
            return redirect('integrations:integration_list_react')
            
    except CompanyIntegration.DoesNotExist:
        logger.error(f"CompanyIntegration not found for service: {service}, company: {company}")
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'error': f"{service} integration not found for this company."
            }, status=404)
        messages.error(request, f"{service} integration not found for this company.")
        return redirect('integrations:integration_list_react')
    except Exception as e:
        logger.error(f"Exception in disconnect_integration: {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'error': 'An error occurred while disconnecting the integration.'
            }, status=500)
        messages.error(request, "An error occurred while disconnecting the integration.")
        logger.error(f"Error disconnecting {service} integration: {str(e)}")
        return redirect('integrations:integration_list_react')


def integration_list(request):
    """
    Displays the list of integrations for the company.
    """
    company = request.session.get('selected_company')
    logger.info(f"Selected company: {company}")
    if company == 'all' or company is None:
        if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
            return JsonResponse({
                'error': 'Please select a company to view integrations.',
                'integration_status': {},
                'company': None,
                'is_documenso_connected': False
            }, status=400)
        messages.error(request, "Please Select Company of which you want to see the integrations.")
        return redirect('home-page')
    try:
        is_documenso_connected = DocumensoService.IsDocumensoConnected(company)
        integrations = CompanyIntegration.objects.filter(company=company)
        logger.info(f"========= integgrations {company} ==========")
        integration_status = {}
        for integration in integrations:
            if integration.service_name is None and integration.service is not None:
                integration.service_name = integration.service.name.lower()
                integration.save(update_fields=['service_name'])
            
            # Special fix for Documenso integrations that might have service_name as None
            if integration.service_name is None and integration.documenso_api_key is not None:
                integration.service_name = 'documenso'
                integration.save(update_fields=['service_name'])
            
            # Skip integrations with None service_name (should not happen after fixes above)
            if integration.service_name is None:
                logger.warning(f"Skipping integration with None service_name: {integration}")
                continue
            
            integration_status[integration.service_name.lower()] = {
                'is_connected': integration.is_connected,
            }
            logger.info(f"========= integration_status {integration_status} ==========")
            logger.info(f"========= integration {integration.service_name} ==========")
            logger.info(f"========= integration.is_connected {integration.is_connected} ==========")
        
        # Ensure Wise integration status is included even if not in database yet
        if 'wise' not in integration_status:
            integration_status['wise'] = {'is_connected': False}
        
        # Check if request wants JSON (for React app)
        if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
            logger.info(f"Returning JSON response for company {company}")
            logger.info(f"Integration status: {integration_status}")
            return JsonResponse({
                'integration_status': integration_status,
                'company': company,
                'is_documenso_connected': is_documenso_connected
            })
            
        return render(request, 'integrations/integrations.html', {'integration_status': integration_status, 'company':company, 'is_documenso_connected': is_documenso_connected})
    except Exception as e:
        messages.error(request, "An error occurred while fetching integrations.")
        logger.error(f"Error fetching integrations: {str(e)}")
        return redirect('general-settings')


def search_integration(request):
    integrations = None
    company = request.session.get('selected_company')
    if request.method == "GET":
        search_query = request.GET.get("name", "").strip()
        if search_query:
            integrations = AvailableIntegration.objects.filter(name__icontains=search_query) if company != 'all' else AvailableIntegration.objects.filter(name__icontains=search_query)
        else:
            integrations = AvailableIntegration.objects.all()
        
    return render(request, 'integrations/integrations_card.html', {'integrations': integrations})



def slack_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code:
        messages.error(request, "Authorization code not provided.")
        return redirect('integrations:integration_list')

    company = None
    try:
        # Unsigned and validate the company ID from the state
        company_id = signer.unsign(state)
        company = get_object_or_404(Company, id=company_id)
    except BadSignature:
        return HttpResponse("Invalid or tampered state.", status=400)
    except Company.DoesNotExist:
        return HttpResponse("Company not found.", status=404)

    slack = CompanyIntegration.objects.filter(company=company , service_name='slack').first()

    if not slack:
        messages.error(request, "Slack integration not found.")
        return redirect('integrations:integration_list')

    channels = SlackService.ConnectToSlack(slack, company, code)
    
    if channels is None:
        messages.error(request, "Failed to connect to Slack. Please try again.")
        return redirect('integrations:integration_list')
    return render(request, 'integrations/select-channel.html', {'channels': channels, 'company': company})


def connect_documenso(request, company):
    integration, created = CompanyIntegration.objects.get_or_create(company=company, service_name='documenso')
    print('====== request POST in connect_documenso ========= ', request.POST)
    form = DocumensoConnectionForm(instance=integration)
    if request.method == "POST":
        form = DocumensoConnectionForm(request.POST, instance=integration)
        if form.is_valid():
            form.save()
            documenso_service = DocumensoService()
            connected = documenso_service.ConnectDocumenso(integration)
            if connected:
                messages.success(request, "Documenso Connected successfully.")
                return redirect('integrations:integration_list_react')
            else:
                messages.error(request, "Error connecting Documenso. API Key is not valid or expired.")
                return redirect('integrations:integration_list_react')
        else:    
            messages.error(request, "Error updating integration. Please check the form.")
    else:
        form = DocumensoConnectionForm(instance=integration)
    return render(request, 'integrations/update-integration.html', {'update_form': form, 'service': 'documenso', 'company': company})


def connect_wise(request, company):
    integration, created = CompanyIntegration.objects.get_or_create(company=company, service_name='wise')
    form = WiseConnectionForm(instance=integration)
    if request.method == "POST":
        form = WiseConnectionForm(request.POST, instance=integration)
        if form.is_valid():
            try:
                form.save()
                profiles = WiseService.ConnectToWise(integration)
                logger.info(f"========= profiles in wise service {profiles} ==========")
                if profiles:
                    integration.is_connected = True
                    integration.save()
                messages.success(request, "Wise Connected successfully.")
                return redirect('integrations:integration_list_react')
            except ValueError as e:
                messages.error(request, "The token is invalid, please use another token.")
                return redirect('integrations:integration_list_react')
        else:    
            messages.error(request, "Error updating integration. Please check the form.")
    else:
        form = WiseConnectionForm(instance=integration)
    return render(request, 'integrations/update-integration.html', {'update_form': form, 'service': 'wise', 'company': company})


def save_selected_channel(request):
    if request.method == "POST":
        company_id = request.POST.get('company_id')
        channel_id = request.POST.get('channel_id')
        SlackService.ChannelInfoSave(channel_id, company_id)
        messages.success(request, "Slack Connected successfully.")
        return redirect('integrations:integration_list_react')
    
        

    return HttpResponse("Invalid request method.", status=400)

def info_to_connect_integration(request, service):
    """
    Connect the available integration.
    """
    try:
        if request.session.get('selected_company') == 'all':
            messages.error(request, f"Please Select Company of which you want to connect the integration")
            return HttpResponse("<script>window.location.href = '/integrations/integrations_react/';</script>")
        
        logger.info(f"========= service {service} ==========")
        service = service.lower()
        company = Company.objects.get(id=request.session.get('selected_company')) 
        if DocumensoService.IsDocumensoService(service):
            return connect_documenso(request, company)
        elif service == 'wise':
            return connect_wise(request, company)
        integration, created = CompanyIntegration.objects.get_or_create(company=company, service_name=service)
        form = CompanyIntegrationUpdateForm(instance=integration)
        if request.method == "POST":
            form = CompanyIntegrationUpdateForm(request.POST, request.FILES, instance=integration)
            if form.is_valid():
                integration = form.save()
                return redirect('integrations:start_oauth', service=service)
            else:
                messages.error(request, "Error updating integration. Please check the form.")
        else:
            form = CompanyIntegrationUpdateForm(instance=integration)

        return render(request, 'integrations/update-integration.html', {'update_form': form, 'service': service})
    except CompanyIntegration.DoesNotExist:
        messages.error(request, "Integration not found.")
        return redirect('integrations:integration_list_react')
    
    
def documenso_templates_fields(request):
    print('request =================', request)
    company = Company.objects.get(id=request.session.get('selected_company'))
    fields = DocumensoService.GetTemplatesFields(company)  # expected to return a list of templates
    saved_mappings = DocumensoFieldsData.objects.filter(template_id__isnull=False)
    print('saved_mappings =================', saved_mappings)
    mappings_by_template = {}
    for mapping in saved_mappings:
        if mapping.template_id not in mappings_by_template:
            mappings_by_template[mapping.template_id] = {}

        for field in mapping.fields:
            mappings_by_template[mapping.template_id][field.get('id')] = field.get('variable')

    print('mappings_by_template =================', mappings_by_template)

    # Get the notification message from company integration
    documenso_integration = CompanyIntegration.objects.filter(
        company=company, 
        service_name='documenso'
    ).first()
    notification_message = documenso_integration.documenso_notification_message if documenso_integration else ""
    processing_hours = documenso_integration.documenso_processing_hours if documenso_integration else "12"

    return JsonResponse({
        'templates': fields,
        'saved_mappings': mappings_by_template,
        'notification_message': notification_message,
        'processing_hours': processing_hours
    })


@csrf_exempt
def save_documenso_mappings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mappings = data.get("template_mappings", [])
        company_id = request.session.get('selected_company')
        notification_message = data.get("notification_message")
        processing_hours = data.get("processing_hours")
        print('mappings =================', mappings)
        print('data =================', data)
        print('notification_message =================', notification_message)
        print('processing_hours =================', processing_hours)
        company = Company.objects.get(id=company_id)
        documenso_integration = CompanyIntegration.objects.filter(
            company=company, 
            service_name='documenso'
        ).first()
        if notification_message and notification_message.strip():
            documenso_integration.documenso_notification_message = notification_message
            documenso_integration.documenso_processing_hours = processing_hours
            documenso_integration.save()
        else:
            return JsonResponse({"status": "error", "message": "Notification message is required."}, status=400)

        # Save one entry per template
        grouped = {}
        for mapping in mappings:
            template_id = mapping["template"]
            if template_id not in grouped:
                grouped[template_id] = {
                    "title": template_id,
                    "fields": [],
                }
            grouped[template_id]["fields"].append({
                "id": mapping["fieldId"],
                "label": mapping["fieldLabel"],
                "variable": mapping["variable"],
            })

        with transaction.atomic():
            print('grouped items =================', grouped.items())
            for template_id, group in grouped.items():
                DocumensoFieldsData.objects.update_or_create(
                    template_id=template_id,
                    defaults={"fields": group["fields"]}
                )

            return JsonResponse({"status": "success", "message": "Mappings saved successfully."}, status=200)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def test_api(request):
    company = Company.objects.get(id=request.session.get('selected_company'))
    DocumensoService.CreateDocumentFromTemplate(company)
    return JsonResponse({"status": "success", "message": "Variables set successfully."})

def wise_recipients(request):
    company = Company.objects.get(id=request.session.get('selected_company'))
    wise_integration = CompanyIntegration.objects.filter(company=company, service_name='wise').first()
    if wise_integration:
        recipients = WiseService.GetWiseRecipients(wise_integration)
        return JsonResponse({"status": "success", "message": "Recipients fetched successfully.", "recipients": recipients})
    else:
        return JsonResponse({"status": "error", "message": "Wise integration not found."}, status=404)


def wise_add_recipient(request):
    if request.method == "POST":
        data = json.loads(request.body)
        logger.info(f"========= data in wise add recipient {data} ==========")

        name = data.get("name")
        email = data.get("email")
        iban = data.get("iban")
        country = data.get("country")
        currency = data.get("currency")

        company = Company.objects.get(id=request.session.get('selected_company'))
        wise_integration = CompanyIntegration.objects.filter(company=company, service_name='wise').first()

        if not wise_integration:
            return JsonResponse({"status": "error", "message": "Wise integration not configured."}, status=400)

        # ✅ Check if IBAN already exists
        existing_recipient = WiseService.FindRecipientByIBAN(wise_integration, iban)
        if existing_recipient:
            return JsonResponse({
                "status": "exists",
                "message": "Recipient with this IBAN already exists.",
                "recipient": existing_recipient
            })

        # ✅ Create recipient if not found
        try:
            employee = Employee.objects.get(email=email)
            if employee:
                recipient = WiseService.CreateWiseRecipient(wise_integration, name, email, iban, country, currency)
                employee.wise_recipient_id = recipient['id']
                employee.save()
                return JsonResponse({
                    "status": "success",
                    "message": "Recipient added successfully.",
                    "recipient": recipient
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Employee not found."
                })
        except Exception as e:
            logger.exception("Failed to create Wise recipient.")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


def wise_recent_transfers(request):
    """
    Returns the latest 20 Wise transfers for the current company, including status, transfer ID, recipient, date/time, amount, errors, and payroll reference if available.
    """
    company_id = request.session.get('selected_company')
    if not company_id or company_id == 'all':
        return JsonResponse({"status": "error", "message": "Please select a company."}, status=400)
    try:
        company = Company.objects.get(id=company_id)
        wise_integration = CompanyIntegration.objects.filter(company=company, service_name='wise').first()
        if not wise_integration:
            return JsonResponse({"status": "error", "message": "Wise integration not found."}, status=404)
        dashboard_data = WiseService.GetWiseDashboardData(wise_integration)
        transfers = dashboard_data.get('transfers', [])[:20]
        # Sort transfers by created date descending
        transfers = sorted(transfers, key=lambda t: t.get('created') or '', reverse=True)
        # Map fields for frontend
        transfer_list = []
        for t in transfers:
            transfer_list.append({
                "id": t.get("id"),
                "status": t.get("status"),
                "reference": t.get("details", {}).get("reference"),
                "targetAccount": t.get("targetAccount"),
                "created": t.get("created"),
                "amount": t.get("sourceValue"),
                "currency": t.get("sourceCurrency"),
                "error": t.get("failureReason") or t.get("errorCode") or t.get("errorMessage"),
                "recipient": t.get("targetAccount"),
                "payroll_reference": t.get("customerTransactionId"),
            })
        return JsonResponse({"status": "success", "transfers": transfer_list})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def integration_list_react(request):
    """
    Displays the React version of integrations list for the company.
    """
    logger.info(f"========= integration_list_react ==========")
    company = request.session.get('selected_company')
    if company == 'all':
        messages.error(request, "Please Select Company of which you want to see the integrations.")
        return redirect('home-page')
    
    return render(request, 'integrations/integrations_react.html', {'company': company})

def integration_list_react_dev(request):
    """
    Displays the development version of integrations list for the company.
    This version doesn't require webpack and loads React components directly.
    """
    logger.info(f"========= integration_list_react_dev ==========")
    company = request.session.get('selected_company')
    if company == 'all':
        messages.error(request, "Please Select Company of which you want to see the integrations.")
        return redirect('home-page')
    
    return render(request, 'integrations/integrations_react_dev.html', {'company': company})

def test_disconnect_api(request, service):
    """
    Test endpoint to verify the disconnect API is working
    """
    logger.info(f"Test disconnect API called for service: {service}")
    return JsonResponse({
        'success': True,
        'message': f'Test disconnect API working for {service}',
        'service': service,
        'headers': dict(request.headers)
    })

def get_csrf_token(request):
    """
    Simple view to get CSRF token for testing
    """
    token = get_token(request)
    return JsonResponse({
        'csrf_token': token,
        'message': 'CSRF token generated successfully'
    })

def slack_connect_api(request):
    """
    API endpoint for Slack integration - returns JSON instead of HTML form
    """
    try:
        if request.session.get('selected_company') == 'all':
            return JsonResponse({
                'error': 'Please Select Company of which you want to connect the integration'
            }, status=400)
        
        company = Company.objects.get(id=request.session.get('selected_company'))
        integration, created = CompanyIntegration.objects.get_or_create(
            company=company, 
            service_name='slack'
        )
        
        if request.method == "POST":
            form = CompanyIntegrationUpdateForm(request.POST, request.FILES, instance=integration)
            if form.is_valid():
                integration = form.save()
                # Return the OAuth URL for Slack
                oauth_url = reverse('integrations:start_oauth', kwargs={'service': 'slack'})
                return JsonResponse({
                    'success': True,
                    'oauth_url': oauth_url,
                    'message': 'Slack configuration saved. Redirecting to OAuth...'
                })
            else:
                return JsonResponse({
                    'error': 'Invalid form data',
                    'form_errors': form.errors
                }, status=400)
        
        # For GET requests, return the form data as JSON
        form = CompanyIntegrationUpdateForm(instance=integration)
        return JsonResponse({
            'success': True,
            'form_data': {
                'client_id': integration.client_id or '',
                'client_secret': '*****' if integration.client_secret else '',
                'redirect_uri': integration.redirect_uri or '',
                'scopes': integration.scopes or 'channels:read,chat:write'
            },
            'message': 'Slack configuration loaded'
        })
        
    except Exception as e:
        logger.error(f"Error in slack_connect_api: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while processing the request'
        }, status=500)
