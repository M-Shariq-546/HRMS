import requests
from horilla.utils.logger import HorillaLogger
from base.models import Company
from django.http import HttpResponse, JsonResponse
from integrations.models import CompanyIntegration, AvailableIntegration
from django.shortcuts import get_object_or_404  
from datetime import datetime, timedelta
from django.contrib import messages 
from django.utils import timezone
import os 
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

logger = HorillaLogger('base.services.slack_service')

class SlackService:
    TOKEN_URL = os.environ.get("SLACK_TOKEN_URL")
    CHANNELS_URL = os.environ.get("SLACK_CHANNELS_URL")
    TOKEN_REVOKE_URL = os.environ.get("SLACK_TOKEN_REVOKE_URL")
    def __init__(self, slack_client):
        self.slack_client = slack_client
        
    @classmethod
    def GetChannelsList(cls , access_token):
        logger.info("Fetching Slack channels list in service GetChannelsList")
        url = cls.CHANNELS_URL
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if data.get("ok"):
                # Return a list of channel names and IDs
                return [{"id": channel["id"], "name": channel["name"]} for channel in data["channels"]]
            else:
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Slack channels: {e}")
            return []
    
    @classmethod
    def ConnectToSlack(cls, slack, company, code):
        logger.info("Connecting to Slack in service ConnectToSlack")
        token_url = cls.TOKEN_URL
        payload = {
        "client_id": slack.client_id,
        "client_secret": slack.client_secret,
        "code": code,
        "redirect_uri": slack.redirect_uri,
        }

        response = requests.post(token_url, data=payload)
        data = response.json()

        if not data.get("ok"):
            return HttpResponse(f"Slack auth failed: {data.get('error')}", status=400)

        # Extract tokens and info
        access_token = data.get("access_token")
        team_name = data.get("team", {}).get("name")
        bot_user_id = data.get("bot_user_id")
        authed_user = data.get("authed_user", {})

        integration = CompanyIntegration.objects.get(
            company=company,
            service_name='slack'
            )

        integration.access_token = access_token
        integration.is_connected = True
        integration.connected_at = datetime.now()
        integration.config = {
            "team_name": team_name,
            "bot_user_id": bot_user_id,
            # Add any other relevant info here
        }
        integration.save()
        
        return cls.GetChannelsList(access_token) 
    
    @classmethod
    def ChannelInfoSave(cls, channel_id, company_id):
        logger.info("Saving channel info in service ChannelInfoSave")
        # Ensure company exists
        company = get_object_or_404(Company, id=company_id)

        # Update the integration with the selected channel ID
        integration = CompanyIntegration.objects.get(company=company, service_name='slack')

        # Save the selected channel ID in the config or as a separate field
        integration.channel_id = channel_id
        integration.save()
        
        return integration
    
    @classmethod
    def DisconnectSlack(cls, service, user, company):
        logger.info("Disconnecting Slack in service DisconnectSlack")
        # Ensure company exists
        logger.info(f"Disconnecting Slack for company: {company} and service: {service}")
        integration = get_object_or_404(CompanyIntegration, company=company, service_name=service.service_name)
        if integration.is_connected:
            requests.post(cls.TOKEN_REVOKE_URL, data={"token": integration.access_token})
            integration.access_token = None
            integration.refresh_token = None
            integration.token_expiry = None
            integration.is_connected = False
            integration.save()
            return True
        return False
    
    @classmethod
    def OauthCallback(cls, code, company, provider, service):
        logger.info("Handling Slack OAuth callback in service OauthCallback")
        # Exchange code for tokens
        token_data = {
            'client_id': provider.client_id,
            'client_secret': provider.client_secret,
            'code': code,
            'redirect_uri': provider.redirect_uri,
            'grant_type': 'authorization_code',  # For services that require it (e.g., Google)
        }

        token_response = requests.post(provider.auth_uri, data=token_data).json()

        if not token_response.get('access_token'):
            return False

        # Save integration
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in', 3600)

        CompanyIntegration.objects.create(
            company=company,
            service=service,
            is_connected=True,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=timezone.now() + timedelta(seconds=int(expires_in)),
            connected_at=timezone.now(),
            client_id=provider.client_id,
            client_secret=provider.client_secret,
            auth_uri=provider.auth_uri,
            redirect_uri=provider.redirect_uri,
            scopes=provider.get_scopes() if hasattr(provider, 'get_scopes') else "",  # optional method if implemented
        )
        return True 
    
    @classmethod
    def SendMessage(cls, company_integration, employee, datetime_now, message):
        '''
        Send message to slack channel
        '''
        try:
            client = WebClient(token=company_integration.access_token)
            response = client.chat_postMessage(
                channel=company_integration.channel_id,
                text=message.format(
                        name=f"{employee.employee_first_name} {employee.employee_last_name}",
                    ),
                )            
            if response and response.get('ok'):
                logger.info(f"Successfully sent message to {employee} for {message}")
            else:
                logger.error(f"Failed to send message to {employee} for {message}")
        except SlackApiError as e:
            if e.response["error"] == "channel_not_found" or e.response["error"] == "not_in_channel":
                logger.warning(f"Bot is not in the channel or channel not found. Skipping Slack notification for {employee}")
            else:
                logger.error(f"Slack API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending Slack message: {str(e)}")