import cv2
import os
from datetime import datetime

def capture_image(output_dir):
    """
    Captures an image from the default camera and saves it to the specified output directory.

    This function performs the following steps:
    1. Opens the default camera.
    2. Captures a single frame.
    3. Creates the output directory if it doesn't exist.
    4. Generates a unique filename using the current date and time.
    5. Saves the captured image to the output directory.
    6. Releases the camera.

    Args:
        output_dir (str): The directory path where the captured image will be saved.

    Returns:
        None

    Raises:
        None, but prints an error message if frame capture fails.

    Note:
        The image is saved in PNG format with a filename in the format "DDMMYYYY_HHMMSS.png".
    """
    cam = cv2.VideoCapture(0)

    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate a unique filename with the current date and time
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    img_name = f"{timestamp}.png"

    # Save the image in the output directory
    cv2.imwrite(os.path.join(output_dir, img_name), frame)

    cam.release()

# Specify the output directory when calling the function
capture_image("/home/erangross/capture")