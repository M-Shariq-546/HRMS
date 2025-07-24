import os
import base64
import urllib.parse
import requests
from typing import Optional, Dict, Any
from horilla.utils.logger import HorillaLogger
from base.services.http import unsafe_get, unsafe_post, unsafe_delete

logger = HorillaLogger("horilla.image_service")

class FileStorageService:
    def __init__(self):
        self.url = os.environ.get('FILE_STORAGE_API_URL', '')
        
        if not self.url:
            logger.error("Service url is required")

    @classmethod
    def UploadImage(cls, image_file, image_type):
        """
        Upload image to File Storage API
        """
        try:
            # FileStorage API endpoint
            url = os.environ.get('FILE_STORAGE_API_URL')
            logger.debug(f'Upload URL: {url}')
            
            # Read file content and encode to base64
            image_file.seek(0)
            file_content = image_file.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare payload in required format
            payload = {
                'FileData': base64_content,
                'fileName': image_file.name,
                "metadata": {
                    "type": f"{image_type}",
                }
            }
            # Get authorization headers
            token = os.environ.get('FILE_STORAGE_SERVICE_TOKEN')
            headers =  {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            headers['Content-Type'] = 'application/json'  # Set content type to JSON
            
            # Make the API request with authorization
            response = unsafe_post(
                url, 
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return data
            return False
        except Exception as e:
            logger.error(f"Error uploading to FileStorage: {str(e)}")
            return False
    @classmethod
    def GetImageUrl(cls, image_id):
        """
        Fetch image from FileStorage API
        """
        base_url = os.environ.get('FILE_STORAGE_API_URL')
        image_path = urllib.parse.quote(str(image_id), safe='')
        url = base_url + f'{image_path}' + f'/url'
        token = os.environ.get('FILE_STORAGE_SERVICE_TOKEN')
        headers =  {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        headers['Content-Type'] = 'application/json'
        try:
            url_response = unsafe_get(url, headers=headers)
            return url_response.text.strip('"')
        except Exception as e:
            return False
        
    @classmethod
    def GetImageUrlForEmail(cls, image_id):
        """
        Fetch base64 image content from FileStorage API for email attachments
        """
        base_url = os.environ.get('FILE_STORAGE_API_URL')
        logger.info(f"image_id ======================= : {image_id}")
        
        if '.' in str(image_id):
            name_part, extension = str(image_id).rsplit('.', 1)
            modified_image_id = f"{name_part}-sm.{extension}"
        else:
            modified_image_id = f"{image_id}-sm"
        
        logger.info(f"modified_image_id ======================= : {modified_image_id}")
        image_path = urllib.parse.quote(modified_image_id, safe='')
        url = base_url + f'{image_path}'
        token = os.environ.get('FILE_STORAGE_SERVICE_TOKEN')
        headers =  {
            'Authorization': f'Bearer {token}',
            'Accept': 'text/plain'
        }
        try:
            url_response = unsafe_get(url, headers=headers)
            
            # Check if response is successful
            if url_response.status_code == 200:
                # The response should already be base64 encoded content
                base64_content = url_response.text.strip('"')
                
                # Validate that it's actually base64 content
                try:
                    # Try to decode a small portion to validate it's base64
                    import base64 as b64
                    b64.b64decode(base64_content[:100])
                    return f"data:image/{extension};base64,{base64_content}"
                except Exception as decode_error:
                    logger.error(f"Invalid base64 content received: {str(decode_error)}")
                    return None
            else:
                logger.error(f"Failed to fetch image. Status code: {url_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching base64 image content: {str(e)}")
            return None

    @classmethod
    def DeleteImage(cls, image_url):
        """
        Delete image from FileStorage API
        """
        if image_url:
            try:
                base_url = os.environ.get('FILE_STORAGE_API_URL')
                image_path = urllib.parse.quote(str(image_url), safe='')
                url = base_url + f'?fileName={image_path}' 
                # Get authorization headers
                token = os.environ.get('FILE_STORAGE_SERVICE_TOKEN')
                headers =  {
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                }
                headers['Content-Type'] = 'application/json'
                response = unsafe_delete(url, headers=headers)
                return response.status_code == 200
            except Exception as e:
                logger.info(f'Error deleting image from server =============== {e}')
                return False
        return True