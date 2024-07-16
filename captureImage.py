import cv2
import os
from datetime import datetime

def capture_image(output_dir):
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