import os
import requests
from datetime import datetime, timedelta
from horilla.utils.logger import HorillaLogger
from integrations.models import AvailableIntegration, CompanyIntegration, DocumensoFieldsData
from base.models import Company
from base.services.http import unsafe_get, unsafe_post, unsafe_delete

logger = HorillaLogger('base.services.documeso_service')

class DocumensoService:
    BASE_URL = os.environ.get('DOCUMENSO_BASE_URL')
    def __init__(self):
        if not self.BASE_URL:
            logger.error('Documenso base URL is not set')
            raise ValueError('Documenso base URL is not set')

    @classmethod
    def extract_field_key(cls , field):
        field_meta = field.get("fieldMeta")
        if not field_meta:
            return ""
        
        placeholder = field_meta.get("placeholder", "").lower()
        print('======= placeholder =======  : ', placeholder)
        label = field_meta.get("label", "").lower()
        print('======= label =======  : ', label)
        custom_text = field.get("customText", "").lower()
        print('======= custom_text =======  : ', custom_text)
        return placeholder or label or custom_text or ""

    
    @classmethod
    def GetAllTemplates(cls, company):
        base_url = cls.BASE_URL
        headers = {
            'Authorization':f"{company.integrations.filter(service_name='documenso').first().documenso_api_key}",
            'Content-Type': 'application/json'
        }
        response = unsafe_get(base_url + '/api/v1/templates', headers=headers)
        return response.json()
    
    @classmethod
    def CreateDocumentFromTemplate(cls, signers, company, employee):
        base_url = cls.BASE_URL

        # Get API key and headers
        api_key = company.integrations.filter(service_name='documenso').first().documenso_api_key
        headers = {
            'Authorization': f'{api_key}',
            'Content-Type': 'application/json'
        }

        # Fetch templates
        templates = cls.GetAllTemplates(company).get('templates', [])
        document_list = []

        for template in templates:
            template_id = template.get('id')  # ✅ define template_id early

            if not template_id:
                continue
            for i, signer in enumerate(signers):
                try:
                    signer["id"] = template.get('recipients', [])[i].get('id')
                except (IndexError, AttributeError):
                    logger.warning(f"No recipient at index {i} for template ID {template.get('id')}")
                    continue  # or handle error appropriately

            # Load stored DocumensoFieldsData for this template
            try:
                field_data_instance = DocumensoFieldsData.objects.get(template_id=template_id)
                field_values = field_data_instance.fields or {}
            except DocumensoFieldsData.DoesNotExist:
                field_values = {}

            # Fetch template fields
            fields = template.get('fields', [])
            prefill_fields = []

            for field in fields:
                logger.info(f'========= Field: {field} ========')
                field_type = field.get("type", "").upper()
                field_id = field.get("id")
                custom_text = cls.extract_field_key(field)
                logger.info(f'========= Custom text: {custom_text} ========')
                field_label = field.get("fieldMeta")
                
                if not field_label:
                    continue                    

                logger.info(f'========= Field label: {field_label.get("label")} ========')
                value = cls.SetVariablesValues(field_label.get("label"), company, employee)

                if field_type == "DATE" and not value and "date" in custom_text:
                    value = str(datetime.today())

                if value:
                    prefill_fields.append({
                        "id": field_id,
                        "type": field_type.lower(),
                        "label": value,
                        "value": value
                    })

            request_data = {
                "title": template.get('title'),
                "recipients": signers,
                "signers": signers,
                "meta": {
                    "subject": "Document from Template",
                    "message": "",
                    "timezone": "UTC",
                    "dateFormat": "YYYY-MM-DD",
                    "redirectUrl": "",
                    "signingOrder": "PARALLEL",
                    "allowDictateNextSigner": True,
                    "language": "en",
                    "distributionMethod": "EMAIL",
                    "typedSignatureEnabled": True,
                    "uploadSignatureEnabled": True,
                    "drawSignatureEnabled": True,
                    "emailSettings": None
                },
                "formValues": {},
                "prefillFields": prefill_fields
            }
            
            print('======= request_data =======  : ', request_data)

            logger.info(f'Request to generate document from template {template_id} with data: {request_data}')
            response = unsafe_post(f"{base_url}/api/v1/templates/{template_id}/generate-document", headers=headers, json=request_data)

            logger.info(f'Documenso response: {response.status_code} - {response.text}')
            if response.status_code == 200:
                doc_id = response.json().get('documentId')
                cls.SendDocument(doc_id, company)
                document_list.append(doc_id)

        return document_list

    
    @classmethod
    def GetDocument(cls, document_id, company):
        base_url = cls.BASE_URL
        headers = {
            'Authorization': f"{company.integrations.filter(service_name='documenso').first().documenso_api_key}",
            'Content-Type': 'application/json'
        }
        response = unsafe_get(base_url + f'/api/v1/documents/{document_id}', headers=headers)
        return response.json()
    
    @classmethod
    def SendDocument(cls, document_id, company):
        logger.info(f'========= Sending document ========')
        logger.info(f'document id in sending document =======  : {document_id}')
        document = cls.GetDocument(document_id, company)
        base_url = cls.BASE_URL
        headers = {
            'Authorization': f"{company.integrations.filter(service_name='documenso').first().documenso_api_key}",
            'Content-Type': 'application/json'
        }
        for recipient in document.get('recipients'):
            if recipient.get('sendStatus') == 'NOT_SENT':
                logger.info(f'document id in sending document =======  : {document_id}')
                json_data = {
                    "sendEmail": True,
                    "sendCompletionEmails": True
                }
                print('======= json_data =======  : ', json_data)
                response = unsafe_post(base_url + f"/api/v1/documents/{document_id}/send", headers=headers, json=json_data)
                logger.info(f' status code of sending document =======  : {response.status_code}')
                if response.status_code == 200:
                    return True
        return False

    @classmethod
    def ConnectDocumenso(cls, integration):
        logger.info(f'========= Connecting Documenso ========')
        logger.info(f"=========== integrations documenso key {integration.documenso_api_key}")
        headers = {
            'Authorization': f'{integration.documenso_api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{cls.BASE_URL}/api/v1/me', headers=headers)
        logger.info(f'status code of connecting documenso =======  : {response.status_code}')
        if response.status_code == 200:
            integration.is_connected = True
            integration.save()
            return True
        else:
            return False
    
    @classmethod
    def DisconnectDocumenso(cls, service, company):
        integration = CompanyIntegration.objects.get(company=company, service_name=service.service_name)
        integration.is_connected = False    
        integration.save()
        return True

    @classmethod
    def IsDocumensoConnected(cls, company_instance):
        logger.info(f'========= Documenso Connection Check ========')
        logger.info(f'========== {company_instance}')
        integration = CompanyIntegration.objects.filter(company=company_instance, service_name='documenso', is_connected=True)
        logger.info(f"============ {integration}")
        if integration.exists():
            return True
        else:
            return False

    @classmethod
    def DocumensoAvailability(cls, company_id):
        if AvailableIntegration.objects.filter(name='documenso').exists():
            return True
        else:
            return False
    
    @classmethod
    def IsDocumensoService(cls, service):
        if service == 'documenso':
            return True
        else:
            return False
    
    @classmethod
    def GetTemplatesFields(cls, company):
        templates = cls.GetAllTemplates(company)
        
        result = []
        for template in templates.get("templates", []):  # Adjust based on actual key
            template_data = {
                "name": template.get("title"),
                "fields": []
            }

            for f in template.get("fields", []):
                field_meta = f.get("fieldMeta")
                if not field_meta:
                    continue
                template_data["fields"].append({
                    "id": f.get("id"),
                    "label": field_meta.get("label", "")
                })
            result.append(template_data)
        return result
    
    
    @classmethod
    def CheckSelectedFields(cls, company):
        company = Company.objects.get(id=company)
        templates = cls.GetAllTemplates(company)
        all_ok = True
        missing_fields = []
        documenso_integration = CompanyIntegration.objects.filter(company=company, service_name='documenso', is_connected=True).first()
        if documenso_integration and documenso_integration.documenso_notification_message is None:
            return False            
        
        for template in templates.get('templates', []):
            template_name = template.get("title")
            template_fields = template.get("fields", [])

            try:
                saved_data = DocumensoFieldsData.objects.get(template_id=template_name)
            except DocumensoFieldsData.DoesNotExist:
                all_ok = False
                # Only collect fields with labels
                missing = [field["label"] for field in template_fields if "label" in field]
                missing_fields.append({
                    "template": template_name,
                    "missing": missing
                })
                continue

            mapped_fields = saved_data.fields or []
            mapped_field_ids = [item.get("id") for item in mapped_fields if item.get("id") is not None]
            logger.info(f" ==== maped keys {mapped_field_ids}")

            for field in template_fields:
                # Skip fields without labels
                if not field.get("label"):
                    continue
                # Also skip if fieldMeta doesn't exist
                if not field.get("fieldMeta"):
                    continue
                if field.get("id") not in mapped_field_ids:
                    all_ok = False
                    missing_fields.append({
                        "template": template_name,
                        "fieldId": field.get("id"),
                        "label": field.get("label")
                    })

        if not all_ok:
            return False

        return True

    
    
    @classmethod
    def SetVariablesValues(cls, field_label, company, employee):
        work_info = employee.employee_work_info
        available_variables =[
                { 'id': 'company_id', 'label': 'Company ID', 'value': company.id },
                { 'id': 'company_email', 'label': 'Company Email', 'value': company.email },
                { 'id': 'company_name', 'label': 'Company Name', 'value': company.company },
                { 'id': 'company_phone', 'label': 'Company Phone', 'value': company.phone },
                { 'id': 'company_address', 'label': 'Company Address', 'value': company.address },

                { 'id': 'employee_name', 'label': 'Employee Name', 'value': f"{employee.employee_first_name} {employee.employee_last_name}" },
                { 'id': 'email', 'label': 'Employee Email', 'value': employee.email },
                { 'id': 'phone', 'label': 'Employee Phone', 'value': employee.phone },
                { 'id': 'employee_address', 'label': 'Employee Address', 'value': employee.address },
                { 'id': 'employee_city', 'label': 'Employee City', 'value': employee.city },
                { 'id': 'employee_state', 'label': 'Employee State', 'value': employee.state },
                { 'id': 'employee_zip', 'label': 'Employee Zip', 'value': employee.zip },
                { 'id': 'employee_country', 'label': 'Employee Country', 'value': employee.country },
                { 'id': 'date_of_birth', 'label': 'Employee Date of Birth', 'value': employee.dob },
                { 'id': 'gender', 'label': 'Employee Gender', 'value': employee.gender },
                { 'id': 'marital_status', 'label': 'Employee Marital Status', 'value': employee.marital_status },
                { 'id': 'salary', 'label': 'Salary', 'value': work_info.basic_salary if work_info else None },
                { 'id': 'department_id', 'label': 'Department ID', 'value': work_info.department_id if work_info else None },
                { 'id': 'job_position', 'label': 'Job Position', 'value': work_info.job_position_id if work_info else None },
                { 'id': 'work_type', 'label': 'Work Type', 'value': work_info.work_type_id if work_info else None },
                { 'id': 'employee_type', 'label': 'Employee Type', 'value': work_info.employee_type_id if work_info else None },
                { 'id': 'shift', 'label': 'Shift', 'value': work_info.shift_id if work_info else None },
            ]

        for var in available_variables:
            if var['id'].strip().lower() == field_label:
                return var['value']

        return None
    
    @classmethod
    def GetListDocuments(cls, documents_ids, company):
        base_url = cls.BASE_URL
        headers = {
            'Authorization':f"{company.integrations.filter(service_name='documenso').first().documenso_api_key}",
            'Content-Type': 'application/json'
        }
        documents = unsafe_get(base_url + f"/api/v1/documents?page=1&perPage=100&ids={documents_ids}", headers=headers)
        logger.info(f'======== documents response {documents.json()}')
        return documents.json()
        
    @classmethod
    def ResendReminderDocuments(cls, document_id, company):
        base_url = cls.BASE_URL
        headers = {
            'Authorization':f"{company.integrations.filter(service_name='documenso').first().documenso_api_key}",
            'Content-Type': 'application/json'
        }
        documents = cls.GetListDocuments(document_id, company)
        for document in documents.get('documents'):
            recipient_ids = document.get('recipients')
            recipient_ids = [recipient.get('id') for recipient in recipient_ids]
        body = {
            "recipients":recipient_ids
        }
        logger.info(f'=============== the body {body}')
        resend_document = unsafe_post(base_url + f"/api/v1/documents/{document_id}/resend", json=body, headers=headers)
        logger.info(f"============= resend document status code {resend_document.status_code}")
        logger.info(f"============= resend document responses {resend_document.text}")
        if resend_document.status_code == 200:
            return True
        return 
    

    @classmethod
    def GetUnsignedDocuments(cls, documenso_api_key, processing_hours):
        base_url = cls.BASE_URL
        headers = {
            'Authorization':f"{documenso_api_key}",
            'Content-Type': 'application/json'
        }
        response = unsafe_get(base_url + f"/api/v1/documents?page=1&perPage=100", headers=headers)
        logger.info(f"============= processing hours {processing_hours}")
        # Filter for unsigned documents only
        all_documents = response.json()
        unsigned_documents = []
        
        for document in all_documents.get('documents', []):
            # Check if any recipient has not signed
            has_unsigned_recipients = False
            for recipient in document.get('recipients', []):
                if recipient.get('signingStatus') == 'NOT_SIGNED':
                    has_unsigned_recipients = True
                    break
            
            # Check if document was created more than 48 hours ago
            created_at_str = document.get('createdAt')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    current_time = datetime.now(created_at.tzinfo)
                    time_difference = current_time - created_at
                    
                    # Only include documents that are unsigned AND older than 48 hours
                    if has_unsigned_recipients and time_difference > timedelta(hours=int(processing_hours)):
                        unsigned_documents.append(document)
                        logger.info(f"============= Document {document.get('id')} created {time_difference} ago - adding to unsigned list")
                    else:
                        logger.info(f"============= Document {document.get('id')} created {time_difference} ago - skipping (signed or too recent)")
                except (ValueError, TypeError) as e:
                    logger.error(f"============= Error parsing date for document {document.get('id')}: {e}")
                    # If we can't parse the date, skip this document
                    continue
            else:
                logger.warning(f"============= Document {document.get('id')} has no createdAt field")

        # Return filtered response with only unsigned documents
        return {
            'documents': unsigned_documents
        }
    
    @classmethod
    def ReplaceNotificationVariables(cls, notification_message, employee, document=None):
        """
        Replace variables in notification message with actual values
        """
        if not notification_message:
            return notification_message
            
        # Define available variables for notification message
        available_variables = {
            'document': document.get('title', 'Unknown Document') if document else 'Unknown Document',
            'employee_name': f"{employee.get_full_name()}",
        }
        
        # Replace variables in the message
        # Handle both {{variable}} and {% templatetag openvariable %} variable {% templatetag closevariable %} formats
        import re
        
        # First, replace the Django template tag format
        for var_name, var_value in available_variables.items():
            if var_value is not None:
                # Replace Django template tag format
                pattern = r'\{%\s*templatetag\s+openvariable\s*%\}\s*' + re.escape(var_name) + r'\s*{%\s*templatetag\s+closevariable\s*%\}'
                notification_message = re.sub(pattern, str(var_value), notification_message, flags=re.IGNORECASE)
                
                # Replace simple {{variable}} format
                pattern2 = r'\{\{\s*' + re.escape(var_name) + r'\s*\}\}'
                notification_message = re.sub(pattern2, str(var_value), notification_message, flags=re.IGNORECASE)
                
        notification_message = re.sub(r'<[^>]+>', '', notification_message)
        logger.info(f"============= notification message {notification_message}")
        
        return notification_message.strip()
    