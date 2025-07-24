import requests
from django.conf import settings
import os 
from horilla.utils.logger import HorillaLogger
from django.template.loader import render_to_string
from django.template import Template, Context
import base64
import mimetypes
from horilla.utils.logger import HorillaLogger
from base.models import EmailLog

# Initialize logger
logger = HorillaLogger("horilla.email_service")

class SynetechEmailService:
    def __init__(self):
        self.api_url = os.environ.get('EMAIL_SERVICE_URL')
        self.api_key = os.environ.get('EMAIL_SERVICE_API_KEY', '')
        self.token = os.environ.get('MESSAGING_SERVICE_TOKEN', '')
        
        if not self.api_url:
            logger.error("EMAIL_SERVICE_URL is not configured")
        if not self.api_key:
            logger.error("EMAIL_SERVICE_API_KEY is not configured")
        if not self.token:
            logger.error("MESSAGING_SERVICE_TOKEN is not configured")
            
    def render_template(self, template_content, context_data):
        """
        Render template content with context data
        """
        try:
            template = Template(template_content)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.log_error(f"Error rendering template: {str(e)}")
            return template_content
        
    def render_subject(self, subject, context):
        """
        Replace placeholders in the subject with actual values
        """
        try:
            template = Template(subject)
            return template.render(context)
        except Exception as e:
            logger.log_error(e, {"subject": subject, "context": context})
            return subject

    def _get_mime_type(self, file_name):
        """
        Get the MIME type based on file extension
        """
        mime_type, _ = mimetypes.guess_type(file_name)
        return mime_type or 'application/octet-stream'

    def _encode_attachment(self, file_content, file_name):
        """
        Encode file content to base64 with proper MIME type
        """
        try:
            # If content is already a string (base64), return as is
            if isinstance(file_content, str):
                if file_content.startswith('data:'):
                    return file_content
                # If it's a base64 string without data URI, add the prefix
                mime_type = self._get_mime_type(file_name)
                return f"data:{mime_type};base64,{file_content}"

            # If content is bytes, encode to base64
            if isinstance(file_content, bytes):
                mime_type = self._get_mime_type(file_name)
                base64_content = base64.b64encode(file_content).decode('ascii')
                return base64_content

            logger.error(f"Unsupported file content type: {type(file_content)}")
            return None
        except Exception as e:
            logger.log_error(e, {"file_name": file_name, "content_type": type(file_content)})
            return None

    def process_attachments(self, attachments):
        """
        Process attachments to ensure they are properly formatted for the API
        """
        processed_attachments = []
        
        if not attachments:
            return processed_attachments

        logger.info(f"Processing {len(attachments)} attachments")
        
        for attachment in attachments:
            try:
                # Handle both tuple and dictionary formats
                if isinstance(attachment, tuple) and len(attachment) >= 2:
                    file_name = attachment[0]
                    file_content = attachment[1]
                elif isinstance(attachment, dict):
                    file_name = attachment.get('fileName', '')
                    file_content = attachment.get('fileContent') or attachment.get('file')
                else:
                    logger.error(f"Invalid attachment format: {attachment}")
                    continue

                # Validate file name and content
                if not file_name:
                    logger.error("Empty file name provided")
                    continue
                if file_content is None:
                    logger.error(f"No content for file: {file_name}")
                    continue

                # Log raw content size
                size = len(file_content) if isinstance(file_content, (bytes, str)) else 'Unknown'
                logger.info(f"File: {file_name}, Raw content size: {size}")

                # Encode the attachment
                encoded_content = self._encode_attachment(file_content, file_name)
                if encoded_content:
                    processed_attachments.append({
                        'fileName': file_name,
                        'file': encoded_content
                    })
                    logger.info(f"Successfully processed attachment: {file_name}")
                else:
                    logger.error(f"Failed to encode attachment: {file_name}")

            except Exception as e:
                logger.log_error(e, {"attachment": attachment})
                continue

        logger.info(f"Successfully processed {len(processed_attachments)} attachments")
        return processed_attachments

    def send_email(self, emails, subject, message, sender=None, custom_variables=None, cc=None, attachments=None, credential_id=0, template_id=None, is_template=False):
        """
        Send email using Synetech messaging API
        
        Args:
            emails (list): List of recipient email addresses
            subject (str): Email subject
            message (str): Email body content or template content
            sender (str): Sender email address
            sender_name (str): Sender name
            custom_variables (dict): Optional custom variables for template
            cc (list): Optional list of CC email addresses
            attachments (list): Optional list of attachments with fileName and file content
            credential_id (int): Optional credential ID for the email service
            template_id (str): Optional template ID if using a predefined template
            provider (int): Email provider ID
            is_template (bool): Whether the message is a template that needs rendering
        """
        sender = settings.DEFAULT_FROM_EMAIL or sender
        sender_name = settings.DEFAULT_FROM_NAME
        logger.info(f"Sending email to {emails}")
        # Ensure emails is a list and not empty
        if not emails:
            logger.error("No email addresses provided")
            return False
            
        # Convert single email to list if needed
        if isinstance(emails, str):
            emails = [emails]
            
        # Render template if needed
        if is_template and custom_variables:
            message = self.render_template(message, custom_variables)
            subject = self.render_subject(subject, custom_variables)
            
        payload = {
            "emails": emails,
            "subject": subject,
            "message": message,
            "senderName": sender_name,
            "sender": sender
        }

        # Add CC if provided
        if cc:
            if isinstance(cc, str):
                cc = [cc]
            payload["cc"] = cc

        # Process and add attachments if provided
        if attachments:
            processed_attachments = self.process_attachments(attachments)
            if processed_attachments:
                payload["attachments"] = processed_attachments
            else:
                logger.warning("No valid attachments were processed")

        # Add template ID if provided
        if template_id:
            payload["templateId"] = template_id

        logger.info(f"Prepared email payload for {emails}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        logger.info(f"payload: {payload}")
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            
            try:
                response_json = response.json()
                logger.info(f"Email API response: {response_json}")
            except ValueError:
                logger.warning("Response is not valid JSON")
                response_json = None
                
            response.raise_for_status()
            logger.info(f"Email sent successfully to {emails}")
            EmailLog.objects.create(
                subject=payload.get("subject", ""),
                body=payload.get("body", ""),
                from_email=payload.get("from_email", ""),
                to=payload.get("emails", ""),
                status="sent"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            logger.log_api_error(
                e,
                endpoint=self.api_url,
                request_data=payload,
                response=response_json if 'response_json' in locals() else None
            )
            EmailLog.objects.create(
                subject=payload.get("subject", ""),
                body=payload.get("body", ""),
                from_email=payload.get("from_email", ""),
                to=payload.get("to", ""),
                status="failed"
            )
            return False

# Create a singleton instance
email_service = SynetechEmailService()
