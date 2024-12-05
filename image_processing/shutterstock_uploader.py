#!/usr/bin/env python3
# shutterstock_uploader.py

import os
import base64
import json
import requests
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime
import logging

class ShutterstockAutoUploader:
    def __init__(self):
        load_dotenv()
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.shutterstock_api_token = os.getenv('SHUTTERSTOCK_API_TOKEN')
        self.shutterstock_base_url = 'https://api.shutterstock.com/v2'
        self.setup_logging()
        self.load_keyword_blacklist()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            filename=os.path.join(log_dir, f'shutterstock_uploader_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_keyword_blacklist(self):
        """Load blacklisted keywords"""
        # This could be expanded to load from a file or API
        self.keyword_blacklist = set(['offensive', 'trademarked', 'inappropriate'])

    def add_delay(self, seconds=1):
        """Add delay for rate limiting"""
        time.sleep(seconds)

    def encode_image(self, image_path):
        """Encode image to base64"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {str(e)}")
            return None

    def analyze_image_with_claude(self, image_path):
        """Analyze image using Claude AI"""
        try:
            base64_image = self.encode_image(image_path)
            if not base64_image:
                return None
            
            prompt = """Please analyze this image and provide the following information in JSON format:
            {
                "description": "Provide a detailed description of the image (50-200 words)",
                "keywords": "List exactly 15-25 relevant keywords, separated by commas",
                "categories": "Select exactly 2 categories from this list: Abstract, Animals/Wildlife, Arts, Backgrounds/Textures, Beauty/Fashion, Buildings/Landmarks, Business/Finance, Celebrities, Education, Food and drink, Healthcare/Medical, Holidays, Industrial, Interiors, Miscellaneous, Nature, Objects, Parks/Outdoor, People, Religion, Science, Signs/Symbols, Sports/Recreation, Technology, Transportation, Vintage",
                "image_type": "Specify if this is a photo, illustration, or vector",
                "location": "Specify location if identifiable (city, country)",
                "usage": "commercial"
            }"""

            response = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            metadata = json.loads(response.content)
            self.logger.info(f"Successfully analyzed image: {image_path}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error analyzing image with Claude: {str(e)}")
            return None

    def validate_metadata(self, metadata):
        """Validate metadata before submission"""
        try:
            errors = []
            
            # Validate description
            if not metadata.get('description'):
                errors.append("Description is required")
            elif len(metadata['description']) < 50 or len(metadata['description']) > 200:
                errors.append("Description must be between 50-200 characters")

            # Validate keywords
            if not metadata.get('keywords'):
                errors.append("Keywords are required")
            else:
                keywords = [k.strip() for k in metadata['keywords'].split(',')]
                if len(keywords) < 15 or len(keywords) > 25:
                    errors.append("Must have between 15-25 keywords")
                
                # Check for blacklisted keywords
                blacklisted = [k for k in keywords if k.lower() in self.keyword_blacklist]
                if blacklisted:
                    errors.append(f"Contains prohibited keywords: {', '.join(blacklisted)}")

            # Validate categories
            if not isinstance(metadata.get('categories'), list):
                if isinstance(metadata.get('categories'), str):
                    metadata['categories'] = [c.strip() for c in metadata['categories'].split(',')]
                else:
                    errors.append("Categories must be a list or comma-separated string")

            if len(metadata.get('categories', [])) != 2:
                errors.append("Exactly 2 categories are required")

            return {
                'success': len(errors) == 0,
                'error': '\n'.join(errors) if errors else None,
                'metadata': metadata
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Validation error: {str(e)}",
                'metadata': metadata
            }

    def submit_to_shutterstock(self, image_path, metadata):
        """Submit image and metadata to Shutterstock"""
        headers = {
            'Authorization': f'Bearer {self.shutterstock_api_token}',
            'Content-Type': 'application/json'
        }

        try:
            # Step 1: Upload the image
            self.logger.info(f"Starting image upload: {image_path}")
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                upload_response = requests.post(
                    f'{self.shutterstock_base_url}/images/uploads',
                    headers=headers,
                    files=files
                )
                
                if not upload_response.ok:
                    return self.handle_api_error('upload', upload_response)

                upload_id = upload_response.json().get('upload_id')

            # Step 2: Submit metadata
            submission_data = {
                "description": metadata['description'],
                "keywords": metadata['keywords'].split(',') if isinstance(metadata['keywords'], str) else metadata['keywords'],
                "categories": metadata['categories'],
                "image_type": metadata['image_type'],
                "location": metadata.get('location', ''),
                "editorial": False,
                "releases": {
                    "model": False,
                    "property": False
                }
            }

            metadata_response = requests.post(
                f'{self.shutterstock_base_url}/images/uploads/{upload_id}',
                headers=headers,
                json=submission_data
            )

            if not metadata_response.ok:
                return self.handle_api_error('metadata', metadata_response)

            # Step 3: Submit for review
            review_data = {
                "upload_ids": [upload_id],
                "submit_for_review": True
            }

            review_response = requests.post(
                f'{self.shutterstock_base_url}/images/uploads/submit',
                headers=headers,
                json=review_data
            )

            if not review_response.ok:
                return self.handle_api_error('review', review_response)
            
            return {
                'success': True,
                'upload_id': upload_id,
                'status': 'submitted_for_review'
            }

        except Exception as e:
            self.logger.error(f"Error submitting to Shutterstock: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general'
            }

    def handle_api_error(self, stage, response):
        """Handle API errors with specific responses"""
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown error')
            
            self.logger.error(f"{stage.capitalize()} stage error: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'error_type': stage,
                'error_details': error_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error in {stage} stage: {str(e)}",
                'error_type': stage
            }

    def check_submission_status(self, upload_id):
        """Check the status of a submitted image"""
        headers = {
            'Authorization': f'Bearer {self.shutterstock_api_token}'
        }

        try:
            response = requests.get(
                f'{self.shutterstock_base_url}/images/uploads/{upload_id}',
                headers=headers
            )
            
            if not response.ok:
                return self.handle_api_error('status_check', response)
                
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error checking submission status: {str(e)}")
            return None