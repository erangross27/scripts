"""
Watermark Detection Application

This application provides a graphical user interface for detecting watermarks in images and videos using a YOLOv5 model.

Features:
- Load a custom YOLOv5 model for watermark detection
- Process individual images or video files
- Display processing progress and log information
- Save processed images/videos with detected watermarks highlighted

The application uses PyTorch for the deep learning model, OpenCV for image and video processing,
and Tkinter for the graphical user interface.

Usage:
1. Select a YOLOv5 model file (.pt)
2. Choose an input image or video file
3. Specify an output file location
4. Click "Process File" to start the watermark detection

The application will display progress and log information during processing.
Detected watermarks are highlighted with green rectangles in the output.

Classes:
- WatermarkDetectionApp: Main application class handling the GUI and processing logic
- GUILogHandler: Custom logging handler to update the GUI log display

Note: This application requires PyTorch, OpenCV, and other dependencies to be installed.
"""

import torch
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
import logging
import threading
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WatermarkDetectionApp:
    """
    Represents a watermark detection app.
    """
    def __init__(self, master):
        """
        Special method __init__.
        """
        # Initialize the main application window
        self.master = master
        self.master.title("Watermark Detection")
        self.master.geometry("900x800")

        # Initialize variables for file paths and model
        self.model_path = tk.StringVar()
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.model = None
        self.processing = False

        # Create GUI widgets
        self.create_widgets()

    def create_widgets(self):
        """
        Creates widgets.
        """
        # Create and arrange GUI elements
        # Model selection
        tk.Label(self.master, text="YOLOv5 Model:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.master, textvariable=self.model_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.master, text="Browse", command=self.browse_model).grid(row=0, column=2, padx=5, pady=5)

        # Input selection
        tk.Label(self.master, text="Input File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.master, textvariable=self.input_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.master, text="Browse", command=self.browse_input).grid(row=1, column=2, padx=5, pady=5)

        # Output selection
        tk.Label(self.master, text="Output File:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.master, textvariable=self.output_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.master, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5, pady=5)

        # Process button
        self.process_button = tk.Button(self.master, text="Process File", command=self.start_processing)
        self.process_button.grid(row=3, column=1, padx=5, pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Log display
        self.log_text = scrolledtext.ScrolledText(self.master, height=20)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        # Configure grid
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(5, weight=1)

    def browse_model(self):
        """
        Browse model.
        """
        # Open file dialog to select YOLOv5 model
        filename = filedialog.askopenfilename(filetypes=[("PyTorch Model", "*.pt")])
        if filename:
            self.model_path.set(filename)
            logger.info(f"Model selected: {filename}")
            self.load_model()

    def load_model(self):
        """
        Load model.
        """
        # Load the selected YOLOv5 model
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path.get())
            logger.info("Model loaded successfully")
            messagebox.showinfo("Success", "Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.model = None

    def browse_input(self):
        """
        Browse input.
        """
        # Open file dialog to select input file (video or image)
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4"), ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if filename:
            self.input_path.set(filename)
            logger.info(f"Input file selected: {filename}")

    def browse_output(self):
        """
        Browse output.
        """
        # Open file dialog to select output file location
        filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("JPEG files", "*.jpg")])
        if filename:
            self.output_path.set(filename)
            logger.info(f"Output path selected: {filename}")

    def start_processing(self):
        """
        Start processing.
        """
        # Start processing in a separate thread
        if not self.processing:
            self.processing = True
            self.process_button.config(state=tk.DISABLED)
            threading.Thread(target=self.process_file, daemon=True).start()

    def process_file(self):
        """
        Process file.
        """
        # Main processing function for both images and videos
        if self.model is None:
            messagebox.showerror("Error", "Please load a model first.")
            logger.error("No model loaded")
            self.processing = False
            self.process_button.config(state=tk.NORMAL)
            return

        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output paths.")
            logger.error("Input or output path not selected")
            self.processing = False
            self.process_button.config(state=tk.NORMAL)
            return

        try:
            if input_path.lower().endswith(('.mp4', '.avi', '.mov')):
                self.process_video(input_path, output_path)
            else:
                self.process_image(input_path, output_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error during processing: {str(e)}", exc_info=True)
        finally:
            self.processing = False
            self.process_button.config(state=tk.NORMAL)
            self.progress_var.set(0)

    def process_image(self, input_path, output_path):
        """
        Process image based on input path, output path.
        """
        # Process a single image
        img = cv2.imread(input_path)
        logger.info(f"Image read successfully: {input_path}")

        processed_img = self.detect_watermark(img)
        cv2.imwrite(output_path, processed_img)
        logger.info(f"Processed image saved: {output_path}")

        self.progress_var.set(100)
        messagebox.showinfo("Success", "Image processing completed successfully!")

    def process_video(self, input_path, output_path):
        """
        Process video based on input path, output path.
        """
        # Process a video file
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        logger.info(f"Processing video: {input_path}")
        logger.info(f"Total frames: {total_frames}")

        for frame_num in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = self.detect_watermark(frame)
            out.write(processed_frame)

            progress = (frame_num + 1) / total_frames * 100
            self.progress_var.set(progress)
            self.master.update_idletasks()

        cap.release()
        out.release()

        logger.info(f"Processed video saved: {output_path}")
        messagebox.showinfo("Success", "Video processing completed successfully!")

    def detect_watermark(self, img):
        """
        Detect watermark based on img.
        """
        # Detect watermarks in an image using the YOLOv5 model
        results = self.model(img)

        if len(results.xyxy[0]) > 0:
            for det in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = det.tolist()
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                logger.info(f"Watermark detected at ({x1}, {y1}, {x2}, {y2}) with confidence {conf:.2f}")
        else:
            logger.warning("No watermark detected in the frame")

        return img

    def update_log(self, message):
        """
        Updates log based on message.
        """
        # Update the log display in the GUI
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

class GUILogHandler(logging.Handler):
    """
    Handles g u i log operations.
    """
    # Custom logging handler to update GUI log display
    def __init__(self, callback):
        """
        Special method __init__.
        """
        super().__init__()
        self.callback = callback

    def emit(self, record):
        """
        Emit based on record.
        """
        log_entry = self.format(record)
        self.callback(log_entry)

if __name__ == "__main__":
    # Create and run the main application
    root = tk.Tk()
    app = WatermarkDetectionApp(root)
    gui_handler = GUILogHandler(app.update_log)
    logger.addHandler(gui_handler)
    root.mainloop()
