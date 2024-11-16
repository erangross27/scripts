import os
import requests
from anthropic import Anthropic
from PIL import Image
import base64
from io import BytesIO
import time
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)

class ShutterstockMetadataUpdater:
    def __init__(self):
        # Retrieve the Anthropic API key from environment variables
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logging.error("Anthropic API key must be set in the ANTHROPIC_API_KEY environment variable.")
            raise ValueError("Missing Anthropic API key")
        self.anthropic = Anthropic(api_key=api_key)
        self.shutterstock_token = None
        self.download_folder = os.environ.get("DOWNLOAD_FOLDER", "downloaded_images")

    def authenticate_shutterstock(self, client_id, client_secret):
        """
        Authenticate with Shutterstock API.
        Returns access token for further API calls.
        """
        auth_url = "https://api.shutterstock.com/v2/oauth/access_token"
        auth_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        try:
            response = requests.post(auth_url, data=auth_data)
            response.raise_for_status()
            self.shutterstock_token = response.json()["access_token"]
            logging.info("Successfully authenticated with Shutterstock.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to authenticate with Shutterstock: {e}")
            raise

    def download_images_from_shutterstock(self):
        """
        Download images from Shutterstock.
        Skips already downloaded images and creates progress bar.
        """
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        # Check for existing images to avoid re-downloading
        existing_images = {f.split('.')[0] for f in os.listdir(self.download_folder)}

        headers = {"Authorization": f"Bearer {self.shutterstock_token}"}
        images_url = "https://api.shutterstock.com/v2/images/contributor"

        try:
            response = requests.get(images_url, headers=headers)
            response.raise_for_status()
            images = response.json()["data"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve images: {e}")
            return

        for image in tqdm(images, desc="Downloading images"):
            image_id = image["id"]
            if image_id in existing_images:
                logging.info(f"Skipping existing image {image_id}")
                continue

            download_url = f"https://api.shutterstock.com/v2/images/{image_id}/download"
            try:
                response = requests.get(download_url, headers=headers)
                response.raise_for_status()
                image_url = response.json()["url"]
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                img_data = img_response.content
                with open(f"{self.download_folder}/{image_id}.jpg", 'wb') as f:
                    f.write(img_data)
                logging.info(f"Downloaded image {image_id}")
                time.sleep(1)  # Avoid API rate limits
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to download image {image_id}: {e}")

    def analyze_images_with_anthropic(self):
        """
        Analyze images using Anthropic's Claude Vision API.
        Includes resume capability and progress tracking.
        """
        results = {}
        failed_images = []

        # Load previously processed images if any
        processed_images = set()
        if os.path.exists('processed_images.txt'):
            with open('processed_images.txt', 'r') as f:
                processed_images = set(f.read().splitlines())

        files = [f for f in os.listdir(self.download_folder)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        # Get the Anthropic model name from environment variable or use default
        model_name = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        for filename in tqdm(files, desc="Analyzing images"):
            image_id = filename.split('.')[0]

            # Skip if already processed
            if image_id in processed_images:
                logging.info(f"Skipping already processed image {image_id}")
                continue

            image_path = os.path.join(self.download_folder, filename)

            try:
                with Image.open(image_path) as img:
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                response = self.anthropic.completions.create(
                    model=model_name,
                    max_tokens_to_sample=300,
                    prompt=f"""{Anthropic.HUMAN_PROMPT}
Provide exactly in this format:
Description: [70 chars max description]
Keywords: [7 relevant keywords separated by commas]
Category: [one of: nature/wildlife/landscape/people/business/food]

[Attached Image]

{Anthropic.AI_PROMPT}""",
                    attachments={"image": img_str},
                )

                # Parse Claude's response
                lines = response.completion.strip().split('\n')
                results[image_id] = {
                    'description': lines[0].replace('Description: ', '')[:70],
                    'keywords': [k.strip() for k in lines[1].replace('Keywords: ', '').split(',')][:7],
                    'category': lines[2].replace('Category: ', '').strip().lower()
                }

                # Mark as processed
                with open('processed_images.txt', 'a') as f:
                    f.write(f"{image_id}\n")

                logging.info(f"Analyzed image {image_id}")
                time.sleep(1)  # Avoid API rate limits

            except Exception as e:
                failed_images.append((image_id, str(e)))
                logging.error(f"Failed to analyze image {image_id}: {e}")
                continue

        # Save failed analyses for review
        if failed_images:
            with open('failed_analyses.txt', 'w') as f:
                for img, error in failed_images:
                    f.write(f"{img}: {error}\n")

        return results

    def update_shutterstock_metadata(self, metadata_results):
        """
        Update metadata on Shutterstock.
        Includes resume capability and error handling.
        """
        # Track already updated images
        updated_images = set()
        if os.path.exists('updated_images.txt'):
            with open('updated_images.txt', 'r') as f:
                updated_images = set(f.read().splitlines())

        headers = {
            "Authorization": f"Bearer {self.shutterstock_token}",
            "Content-Type": "application/json"
        }

        for image_id, metadata in tqdm(metadata_results.items(), desc="Updating metadata"):
            if image_id in updated_images:
                logging.info(f"Skipping {image_id} - already updated")
                continue

            endpoint = f"https://api.shutterstock.com/v2/images/{image_id}"
            data = {
                "description": metadata['description'],
                "keywords": metadata['keywords'],
                "categories": [metadata['category']]
            }

            try:
                response = requests.patch(endpoint, headers=headers, json=data)
                response.raise_for_status()

                # Mark as updated
                with open('updated_images.txt', 'a') as f:
                    f.write(f"{image_id}\n")

                logging.info(f"Updated metadata for image {image_id}")
                time.sleep(1)  # Avoid API rate limits
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to update metadata for image {image_id}: {e}")

def main():
    # Retrieve credentials from environment variables
    SHUTTERSTOCK_CLIENT_ID = os.environ.get("SHUTTERSTOCK_CLIENT_ID")
    SHUTTERSTOCK_CLIENT_SECRET = os.environ.get("SHUTTERSTOCK_CLIENT_SECRET")
    # Anthropic API key is retrieved in the class initialization

    if not SHUTTERSTOCK_CLIENT_ID or not SHUTTERSTOCK_CLIENT_SECRET:
        logging.error("Shutterstock Client ID and Secret must be set in environment variables.")
        return

    updater = ShutterstockMetadataUpdater()

    try:
        # 1. Authenticate with Shutterstock
        updater.authenticate_shutterstock(SHUTTERSTOCK_CLIENT_ID, SHUTTERSTOCK_CLIENT_SECRET)

        # 2. Download images
        updater.download_images_from_shutterstock()

        # 3. Analyze images with Anthropic
        metadata_results = updater.analyze_images_with_anthropic()

        # 4. Update metadata on Shutterstock
        updater.update_shutterstock_metadata(metadata_results)

    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")

if __name__ == "__main__":
    main()
