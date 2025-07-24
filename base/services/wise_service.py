import os
import requests
from horilla.utils.logger import HorillaLogger
from integrations.models import CompanyIntegration, EmployeeWiseRecipient

logger = HorillaLogger('base.services.wise_service')

class WiseService:
    WISE_API_URL = os.environ.get("WISE_API_URL")
    WISE_API_BASE = os.environ.get("TRANSFER_WISE_API_URL")
    
    @classmethod
    def ConnectToWise(cls, company_integration):
        if company_integration.wise_api_key is None:
            raise ValueError("Wise API key is required")
        
        # Get the Wise API key from the company integration
        api_key = company_integration.wise_api_key
        headers = {
            'Authorization': f'Bearer {company_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }        
        # Initialize Wise API client
        response = requests.get(f"{cls.WISE_API_BASE}/profiles", headers=headers)
        logger.info(f"========= response of profiles in wise service {response.json()} ==========")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"========= error in wise service {response.status_code} {response.text} ==========")
            raise ValueError(f"Failed to connect to Wise: {response.status_code} {response.text}")
    
    @classmethod
    def DisconnectWise(cls, service, company):
        """
        Disconnect Wise integration by clearing the API key and setting is_connected to False
        """
        logger.info("Disconnecting Wise in service DisconnectWise")
        try:
            if service.is_connected:
                # Clear the API key and connection status
                service.wise_api_key = None
                service.is_connected = False
                service.save()
                logger.info(f"Successfully disconnected Wise for company: {company}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error disconnecting Wise: {str(e)}")
            return False
    
    @classmethod
    def IsWiseService(cls, service):
        """
        Check if the given service is a Wise service
        """
        if service == 'wise':
            return True
        else:
            return False
    
    @classmethod
    def IsWiseConnected(cls, company_instance):
        """
        Check if Wise is connected for the given company
        """
        logger.info(f'========= Wise Connection Check ========')
        logger.info(f'========== {company_instance}')
        integration = CompanyIntegration.objects.filter(company=company_instance, service_name='wise', is_connected=True)
        logger.info(f"============ {integration}")
        if integration.exists():
            return True
        else:
            return False
        
    @classmethod
    def GetWiseRecipientId(cls, service_integration, iban):
        """
        Get the Wise recipient ID for the given company
        """
        logger.info(f'========= Wise Recipient ID Check ========')
        logger.info(f'========== {service_integration}')
        url = f"{cls.WISE_API_BASE}/accounts"
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        logger.info(f"========= response of get wise recipient {response.json()} ==========")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch recipients: {response.text}")

        for recipient in response.json():
            details = recipient.get("details", {})
            if details.get("iban") == iban:
                return recipient["id"]
        return None
    
    @classmethod
    def CreateWiseRecipient(cls, service_integration, name, email, iban, country, currency):
        url = f"{cls.WISE_API_BASE}/accounts"
        profile_id = cls.GetProfileId(service_integration)
        logger.info(f"========= profile_id in wise service {profile_id} ==========")
        logger.info(f"========= name in wise service {name} ==========")
        logger.info(f"========= email in wise service {email} ==========")
        logger.info(f"========= iban in wise service {iban} ==========")
        logger.info(f"========= country in wise service {country} ==========")
        logger.info(f"========= currency in wise service {currency} ==========")
        payload = {
            "profile": profile_id,
            "currency": currency,
            "type": "iban",
            "details": {
                "accountHolderName": name,
                "iban": iban,
                "legalType": "PRIVATE",
                "country": country,
                "email": email
            }
        }
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"========= response of create wise recipient {response.json()} ==========")
        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception(f"Recipient creation failed: {response.status_code} {response.text}")
        
    @classmethod
    def GetWiseRecipients(cls, service_integration):
        url = f"{cls.WISE_API_BASE}/accounts"
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        logger.info(f"========= response of get wise recipients {response.json()} ==========")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch recipients: {response.text}")

        recipients = []
        for recipient in response.json():
            id = recipient.get("id")
            if id:
                recipients.append({
                    "id": id,
                    "name": recipient.get("accountHolderName"),
                    "email": recipient.get("details", {}).get("email", ""),
                    "iban": recipient.get("details", {}).get("iban", ""),
                })
        return recipients
    

    @classmethod
    def GetProfileId(cls, service_integration):
        url = "https://api.transferwise.com/v1/profiles"
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            profiles = response.json()
            # Pick the first business profile, or fallback to the first profile
            for p in profiles:
                if p.get("type") == "business":
                    return p["id"]
            return profiles[0]["id"]
        else:
            raise Exception("Could not fetch Wise profile ID")
        
        
    @classmethod
    def FindRecipientByEmail(cls, service_integration, email):
        logger.info(f"========= email in wise service {email} ==========")
        url = f"{cls.WISE_API_BASE}/accounts"
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            recipients = response.json()
            for recipient in recipients:
                logger.info(f"========= email in wise service fetch is  {recipient.get('details', {}).get('email')} ==========")
                logger.info(f"========= email in wise service check {recipient.get('details', {}).get('email') == email} ==========")
                if str(recipient.get("details", {}).get("email")) == str(email):
                    return recipient  # ✅ Found a match
        return None
    
    @classmethod
    def ExecuteWiseTransfer(cls, service_integration, payslip, employee):
        """
        Executes a transfer using Wise when salary is marked as paid.
        """
        try:
            logger.info(f"========= payslip in wise service initiated in thread ==========")
            profile_id = cls.GetProfileId(service_integration)
            recipient = cls.FindRecipientByEmail(service_integration, employee.email)
            logger.info(f"========= recipient in wise service {recipient} ==========")
            if recipient is None:
                raise Exception(f"Recipient not found: {recipient_id}")
            recipient_id = recipient['id']
            target_currency = recipient['currency']
            logger.info(f"========= target_currency in wise service {target_currency} ==========")
            logger.info(f"========= amount in wise service {payslip.net_pay} ==========")
            logger.info(f"========= payroll_record in wise service {payslip} ==========")
            logger.info(f"Creating quote for amount: {payslip.net_pay} {target_currency}")
            quote = cls._CreateQuote(service_integration, profile_id, target_currency, payslip.net_pay, employee, payslip)

            logger.info(f"Creating transfer for recipient: {recipient_id}")
            transfer = cls._CreateTransfer(service_integration, profile_id, recipient_id, quote['id'], employee, payslip)

            # Optionally poll until status changes (or rely on webhook)
            logger.info(f"Wise Transfer {transfer.get('id')} created for payroll record {payslip.id}")
            return transfer
        except Exception as e:
            logger.error(f"Wise transfer failed: {str(e)}")
            raise

    @classmethod
    def _CreateQuote(cls, service_integration, profile_id, target_currency, amount, payslip, employee):
        logger.info(f"========= Create Quote in wise service initiated ==========")
        url = f"{cls.WISE_API_BASE}/quotes"
        payload = {
            "profile": profile_id,
            "source": "EUR",  # Adjust as needed
            "target": target_currency,
            "rateType": "FIXED",
            "targetAmount": amount
        }
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"========= response of create quote {response.json()} ==========")
        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception(f"Quote creation failed: {response.text}")

    @classmethod
    def _CreateTransfer(cls, service_integration, profile_id, recipient_id, quote_id, employee, payslip):
        logger.info(f"========= Create Transfer in wise service initiated ==========")
        if EmployeeWiseRecipient.objects.filter(payslip_id=payslip).exists():
            raise Exception(f"You have already paid this payslip")
        url = f"{cls.WISE_API_BASE}/transfers"
        payload = {
            "targetAccount": recipient_id,
            "quoteUuid": quote_id,
            "customerTransactionId": cls._GenerateTransactionId(),
            "details": {
                "reference": "Salary Payment",
            }
        }
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in (200, 201):
            response_data = response.json()
            logger.info(f"========= response_data in wise service {response_data} ==========")
            EmployeeWiseRecipient.objects.create(
                employee_id=employee,
                payslip_id=payslip,
                recipient_id=recipient_id,
                transfer_id=response_data.get('id'),
                status="pending"
            )
            logger.info(f"========= response of create transfer {response.json()} ==========")
            return response_data
        else:
            raise Exception(f"Transfer creation failed: {response.text}")

    @staticmethod
    def _GenerateTransactionId():
        import uuid
        return str(uuid.uuid4())
    
    @classmethod
    def GetWiseDashboardData(cls, service_integration):
        logger.info("========= Fetching Wise Dashboard Data =========")
        
        profile_id = cls.GetProfileId(service_integration)

        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
       
        # Fetch transfers
        transfers_url = f"{cls.WISE_API_BASE}/transfers?profile={profile_id}&limit=100"
        transfers_resp = requests.get(transfers_url, headers=headers)
        transfers_data = transfers_resp.json() if transfers_resp.status_code == 200 else []

        logger.info(f"========= Wise Dashboard Transfers: {transfers_data} =========")
        
        return {
            "transfers": transfers_data
        }
        
    @classmethod
    def GetWiseDashboardDataForSinglePayslip(cls, service_integration, id, payslip_id):
        logger.info("========= Fetching Wise Dashboard Data For single payslip =========")
        
        profile_id = cls.GetProfileId(service_integration)

        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }
        logger.info(f"========= id in wise service {id} ==========")
        payslip_history = EmployeeWiseRecipient.objects.filter(recipient_id=id, payslip_id=payslip_id)
        if not payslip_history.exists():
            return None
        payslip_history = payslip_history.first()
        logger.info(f"========= payslip_history in wise service {payslip_history} ==========")
        # Fetch transfers
        transfers_url = f"{cls.WISE_API_BASE}/transfers?profile={profile_id}&limit=100"
        transfers_resp = requests.get(transfers_url, headers=headers)
        transfers_data = transfers_resp.json() if transfers_resp.status_code == 200 else []
        for transfer in transfers_data:
            logger.info(f"========= targetAccount  {transfer.get('targetAccount')} and id {transfer.get('id')} and transfer_id {payslip_history.transfer_id} ==========")
            if str(transfer.get('targetAccount')) == str(id) and str(transfer.get('id')) == str(payslip_history.transfer_id):
                logger.info(f"========= transfer in wise service for payslip is  {transfer} ==========")
                return transfer
        return None
    
    @classmethod
    def FindRecipientByIBAN(cls, service_integration, iban):
        logger.info(f"========= iban in wise service {iban} ==========")
        url = f"{cls.WISE_API_BASE}/accounts"
        headers = {
            'Authorization': f'Bearer {service_integration.wise_api_key}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            recipients = response.json()
            for recipient in recipients:
                logger.info(f"========= iban in wise service fetch is  {recipient.get('details', {}).get('iban')} ==========")
                logger.info(f"========= iban in wise service check {recipient.get('details', {}).get('iban') == iban} ==========")
                if str(recipient.get("details", {}).get("iban")) == str(iban):
                    return recipient  # ✅ Found a match
        return None