import os
import sys
import requests
from anthropic import Anthropic
from PIL import Image
import base64
from io import BytesIO
import time
import logging
import json
from tqdm import tqdm
from datetime import datetime
from typing import Dict, List, Any
import hashlib

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metadata_updater.log'),
        logging.StreamHandler()
    ]
)

class ShutterstockMetadataUpdater:
    """
    A class to handle the download, analysis, and metadata update of Shutterstock images.
    
    Environment Variables:
        ANTHROPIC_API_KEY: API key for Anthropic
        SHUTTERSTOCK_CLIENT_ID: Client ID for Shutterstock API
        SHUTTERSTOCK_CLIENT_SECRET: Client secret for Shutterstock API
        DOWNLOAD_FOLDER: Folder to store downloaded images
        MAX_RETRIES: Maximum number of retry attempts (default: 3)
        RETRY_DELAY: Delay between retries in seconds (default: 5)
        BATCH_SIZE: Number of images to process in each batch (default: 10)
        ANTHROPIC_MODEL: Model name for Anthropic API
    """

    def __init__(self):
        self._initialize_configuration()
        self._setup_apis()
        self._initialize_stats()
        self._create_directories()

    def _initialize_configuration(self):
        """Initialize configuration from environment variables."""
        self.max_retries = int(os.environ.get("MAX_RETRIES", 3))
        self.retry_delay = int(os.environ.get("RETRY_DELAY", 5))
        self.batch_size = int(os.environ.get("BATCH_SIZE", 10))
        self.download_folder = os.environ.get("DOWNLOAD_FOLDER", "downloaded_images")
        self.cache_folder = "cache"
        self.supported_formats = {'.jpg', '.jpeg', '.png'}

    def _setup_apis(self):
        """Set up API clients."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing Anthropic API key")
        self.anthropic = Anthropic(api_key=api_key)
        self.shutterstock_token = None
        self.anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    def _initialize_stats(self):
        """Initialize statistics tracking."""
        self.stats = {
            'downloaded': 0,
            'analyzed': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now(),
        }

    def _create_directories(self):
        """Create necessary directories."""
        for directory in [self.download_folder, self.cache_folder]:
            os.makedirs(directory, exist_ok=True)

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def authenticate_shutterstock(self, client_id: str, client_secret: str) -> None:
        """
        Authenticate with Shutterstock API.
        
        Args:
            client_id: Shutterstock API client ID
            client_secret: Shutterstock API client secret
        
        Raises:
            requests.exceptions.RequestException: If authentication fails
        """
        auth_url = "https://api.shutterstock.com/v2/oauth/access_token"
        auth_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(auth_url, data=auth_data)
                response.raise_for_status()
                self.shutterstock_token = response.json()["access_token"]
                logging.info("Successfully authenticated with Shutterstock.")
                return
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"Failed to authenticate with Shutterstock after {self.max_retries} attempts: {e}")
                    raise
                time.sleep(self.retry_delay)

    def download_images_from_shutterstock(self) -> None:
        """
        Download images from Shutterstock with pagination support.
        """
        headers = {"Authorization": f"Bearer {self.shutterstock_token}"}
        page = 1
        per_page = 50
        
        while True:
            params = {
                'page': page,
                'per_page': per_page
            }
            
            try:
                response = requests.get(
                    "https://api.shutterstock.com/v2/images/contributor",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                images = response.json()["data"]
                
                if not images:
                    break
                
                self._process_image_batch(images, headers, page)
                page += 1
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to retrieve images on page {page}: {e}")
                break

    def _process_image_batch(self, images: List[Dict], headers: Dict, page: int) -> None:
        """
        Process a batch of images for download.
        
        Args:
            images: List of image data from Shutterstock API
            headers: Request headers for API calls
            page: Current page number for progress display
        """
        existing_images = {f.split('.')[0] for f in os.listdir(self.download_folder)}
        
        for image in tqdm(images, desc=f"Downloading images - Page {page}"):
            image_id = image["id"]
            if image_id in existing_images:
                logging.info(f"Skipping existing image {image_id}")
                self.stats['skipped'] += 1
                continue

            self._download_single_image(image_id, headers)

    def _download_single_image(self, image_id: str, headers: Dict) -> None:
        """Download a single image from Shutterstock."""
        download_url = f"https://api.shutterstock.com/v2/images/{image_id}/download"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(download_url, headers=headers)
                response.raise_for_status()
                image_url = response.json()["url"]
                
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                image_path = f"{self.download_folder}/{image_id}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(img_response.content)
                
                # Verify checksum
                checksum = self._calculate_checksum(image_path)
                with open(f"{self.cache_folder}/{image_id}_checksum.txt", 'w') as f:
                    f.write(checksum)
                
                self.stats['downloaded'] += 1
                logging.info(f"Downloaded image {image_id}")
                time.sleep(1)  # Rate limiting
                break
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"Failed to download image {image_id}: {e}")
                    self.stats['failed'] += 1
                time.sleep(self.retry_delay)

    def analyze_images_with_anthropic(self) -> Dict[str, Dict]:
        """
        Analyze images using Anthropic's Claude Vision API with batch processing.
        
        Returns:
            Dict containing analysis results for each image
        """
        results = {}
        failed_images = []
        processed_images = self._load_processed_images()

        files = [f for f in os.listdir(self.download_folder)
                if any(f.lower().endswith(ext) for ext in self.supported_formats)]

        for i in range(0, len(files), self.batch_size):
            batch = files[i:i + self.batch_size]
            batch_results = self._process_image_batch_analysis(batch, processed_images)
            results.update(batch_results)

        self._save_failed_analyses(failed_images)
        return results

    def _load_processed_images(self) -> set:
        """Load the set of previously processed images."""
        if os.path.exists('processed_images.txt'):
            with open('processed_images.txt', 'r') as f:
                return set(f.read().splitlines())
        return set()

    def _process_image_batch_analysis(self, batch: List[str], processed_images: set) -> Dict[str, Dict]:
        """Process a batch of images for analysis."""
        batch_results = {}
        
        for filename in tqdm(batch, desc="Analyzing images"):
            image_id = filename.split('.')[0]
            
            if image_id in processed_images:
                logging.info(f"Skipping already processed image {image_id}")
                self.stats['skipped'] += 1
                continue

            result = self._analyze_single_image(image_id, filename)
            if result:
                batch_results[image_id] = result
                
        return batch_results

    def _analyze_single_image(self, image_id: str, filename: str) -> Dict[str, Any]:
        """Analyze a single image using Anthropic API."""
        image_path = os.path.join(self.download_folder, filename)
        
        try:
            with Image.open(image_path) as img:
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

            response = self.anthropic.completions.create(
                model=self.anthropic_model,
                max_tokens_to_sample=300,
                prompt=self._generate_analysis_prompt(),
                attachments={"image": img_str},
            )

            result = self._parse_analysis_response(response)
            self._mark_as_processed(image_id)
            self.stats['analyzed'] += 1
            
            return result

        except Exception as e:
            logging.error(f"Failed to analyze image {image_id}: {e}")
            self.stats['failed'] += 1
            return None

    def _generate_analysis_prompt(self) -> str:
        """Generate the prompt for image analysis."""
        return f"""{Anthropic.HUMAN_PROMPT}
Provide exactly in this format:
Description: [70 chars max description]
Keywords: [7 relevant keywords separated by commas]
Category: [one of: nature/wildlife/landscape/people/business/food]

[Attached Image]

{Anthropic.AI_PROMPT}"""

    def _parse_analysis_response(self, response) -> Dict[str, Any]:
        """Parse the analysis response from Anthropic."""
        lines = response.completion.strip().split('\n')
        return {
            'description': lines[0].replace('Description: ', '')[:70],
            'keywords': [k.strip() for k in lines[1].replace('Keywords: ', '').split(',')][:7],
            'category': lines[2].replace('Category: ', '').strip().lower()
        }

    def _mark_as_processed(self, image_id: str) -> None:
        """Mark an image as processed."""
        with open('processed_images.txt', 'a') as f:
            f.write(f"{image_id}\n")

    def update_shutterstock_metadata(self, metadata_results: Dict[str, Dict]) -> None:
        """
        Update metadata on Shutterstock with retry capability.
        
        Args:
            metadata_results: Dictionary containing metadata for each image
        """
        updated_images = self._load_updated_images()
        headers = {
            "Authorization": f"Bearer {self.shutterstock_token}",
            "Content-Type": "application/json"
        }

        for image_id, metadata in tqdm(metadata_results.items(), desc="Updating metadata"):
            if image_id in updated_images:
                logging.info(f"Skipping {image_id} - already updated")
                self.stats['skipped'] += 1
                continue

            self._update_single_image_metadata(image_id, metadata, headers)

    def _load_updated_images(self) -> set:
        """Load the set of previously updated images."""
        if os.path.exists('updated_images.txt'):
            with open('updated_images.txt', 'r') as f:
                return set(f.read().splitlines())
        return set()

    def _update_single_image_metadata(self, image_id: str, metadata: Dict, headers: Dict) -> None:
        """Update metadata for a single image."""
        endpoint = f"https://api.shutterstock.com/v2/images/{image_id}"
        data = {
            "description": metadata['description'],
            "keywords": metadata['keywords'],
            "categories": [metadata['category']]
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.patch(endpoint, headers=headers, json=data)
                response.raise_for_status()
                
                self._mark_as_updated(image_id)
                self.stats['updated'] += 1
                logging.info(f"Updated metadata for image {image_id}")
                time.sleep(1)  # Rate limiting
                break
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"Failed to update metadata for image {image_id}: {e}")
                    self.stats['failed'] += 1
                time.sleep(self.retry_delay)

    def _mark_as_updated(self, image_id: str) -> None:
        """Mark an image as updated."""
        with open('updated_images.txt', 'a') as f:
            f.write(f"{image_id}\n")

    def generate_report(self) -> str:
        """
        Generate a detailed report of the operation.
        
        Returns:
            Formatted string containing the operation report
        """
        duration = datetime.now() - self.stats['start_time']
        report = (
            f"Operation Report\n"
            f"{'='* 50}\n"
            f"Start Time: {self.stats['start_time']}\n"
            f"Duration: {duration}\n\n"
            f"Statistics:\n"
            f"- Images Downloaded: {self.stats['downloaded']}\n"
            f"- Images Analyzed: {self.stats['analyzed']}\n"
            f"- Metadata Updates: {self.stats['updated']}\n"
            f"- Failed Operations: {self.stats['failed']}\n"
            f"- Skipped (Already Processed): {self.stats['skipped']}\n"
        )
        
        logging.info("Report generated successfully")
        return report

def main():
    """Main execution function."""
    # Retrieve credentials from environment variables
    SHUTTERSTOCK_CLIENT_ID = os.environ.get("SHUTTERSTOCK_CLIENT_ID")
    SHUTTERSTOCK_CLIENT_SECRET = os.environ.get("SHUTTERSTOCK_CLIENT_SECRET")

    if not SHUTTERSTOCK_CLIENT_ID or not SHUTTERSTOCK_CLIENT_SECRET:
        logging.error("Shutterstock Client ID and Secret must be set in environment variables.")
        return

    try:
        # Initialize the updater
        updater = ShutterstockMetadataUpdater()
        
        # Start the workflow
        logging.info("Starting metadata update workflow")
        
        # Step 1: Authenticate
        logging.info("Authenticating with Shutterstock...")
        updater.authenticate_shutterstock(SHUTTERSTOCK_CLIENT_ID, SHUTTERSTOCK_CLIENT_SECRET)
        
        # Step 2: Download images
        logging.info("Starting image download process...")
        updater.download_images_from_shutterstock()
        
        # Step 3: Analyze images
        logging.info("Starting image analysis with Anthropic...")
        metadata_results = updater.analyze_images_with_anthropic()
        
        # Save intermediate results
        with open('metadata_results.json', 'w') as f:
            json.dump(metadata_results, f, indent=2)
        
        # Step 4: Update metadata
        logging.info("Updating metadata on Shutterstock...")
        updater.update_shutterstock_metadata(metadata_results)
        
        # Generate and save final report
        report = updater.generate_report()
        report_filename = f"operation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logging.info(f"Operation completed successfully. Report saved to {report_filename}")
        
    except KeyboardInterrupt:
        logging.warning("Operation interrupted by user")
        # Generate partial report for interrupted operation
        report = updater.generate_report()
        with open('interrupted_operation_report.txt', 'w') as f:
            f.write(report)
        raise
        
    except Exception as e:
        logging.error(f"An error occurred during the process: {str(e)}")
        # Generate error report
        if 'updater' in locals():
            report = updater.generate_report()
            with open('error_operation_report.txt', 'w') as f:
                f.write(report)
                f.write(f"\nError Details:\n{str(e)}")
        raise
    
    finally:
        # Cleanup temporary files if needed
        cleanup_temp_files()

def cleanup_temp_files():
    """Clean up temporary files created during processing."""
    try:
        temp_files = [
            'temp_downloads',
            'temp_analysis'
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    import shutil
                    shutil.rmtree(temp_file)
                    
        logging.info("Temporary files cleaned up successfully")
        
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nOperation failed: {str(e)}")
        sys.exit(1)