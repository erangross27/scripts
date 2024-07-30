import torch
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import logging
import os
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WatermarkDetectionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Watermark Detection")
        self.master.geometry("900x750")

        self.model_path = tk.StringVar()
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.model = None

        self.create_widgets()

    def create_widgets(self):
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
        tk.Button(self.master, text="Process File", command=self.process_file).grid(row=3, column=1, padx=5, pady=10)

        # Log display
        self.log_text = scrolledtext.ScrolledText(self.master, height=20)
        self.log_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Configure grid
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(4, weight=1)
    def browse_model(self):
        filename = filedialog.askopenfilename(filetypes=[("PyTorch Model", "*.pt")])
        if filename:
            self.model_path.set(filename)
            logger.info(f"Model selected: {filename}")
            self.load_model()

    def load_model(self):
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path.get())
            logger.info("Model loaded successfully")
            messagebox.showinfo("Success", "Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.model = None

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4"), ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if filename:
            self.input_path.set(filename)
            logger.info(f"Input file selected: {filename}")

    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("JPEG files", "*.jpg")])
        if filename:
            self.output_path.set(filename)
            logger.info(f"Output path selected: {filename}")

    def process_file(self):
        if self.model is None:
            messagebox.showerror("Error", "Please load a model first.")
            logger.error("No model loaded")
            return

        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output paths.")
            logger.error("Input or output path not selected")
            return

        try:
            if input_path.lower().endswith(('.mp4', '.avi', '.mov')):
                self.process_video(input_path, output_path)
            else:
                self.process_image(input_path, output_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error during processing: {str(e)}", exc_info=True)

    def process_image(self, input_path, output_path):
        img = cv2.imread(input_path)
        logger.info(f"Image read successfully: {input_path}")

        processed_img = self.detect_watermark(img)
        cv2.imwrite(output_path, processed_img)
        logger.info(f"Processed image saved: {output_path}")

        messagebox.showinfo("Success", "Image processing completed successfully!")

    def process_video(self, input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        logger.info(f"Processing video: {input_path}")
        logger.info(f"Total frames: {total_frames}")

        # Process each frame
        for _ in tqdm(range(total_frames), desc="Processing frames"):
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = self.detect_watermark(frame)
            out.write(processed_frame)

        # Release everything
        cap.release()
        out.release()

        logger.info(f"Processed video saved: {output_path}")
        messagebox.showinfo("Success", "Video processing completed successfully!")

    def detect_watermark(self, img):
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
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

class GUILogHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkDetectionApp(root)
    gui_handler = GUILogHandler(app.update_log)
    logger.addHandler(gui_handler)
    root.mainloop()
