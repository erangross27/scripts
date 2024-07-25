import sys
import torch
import numpy as np
import cv2
import logging
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar, QMessageBox, QInputDialog
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline

# Set up logging
log_file = 'video_watermark_remover.log'
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')  # 'w' mode overwrites the file each run

# Add console handler for logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

# Test logging
logging.info(f"Logging initialized. Log file: {os.path.abspath(log_file)}")

class VideoProcessingThread(QThread):
    # Signals for communication with main thread
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    def __init__(self, video_path, output_path, pipeline):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.pipeline = pipeline
        self.watermark_region = None
    def detect_watermark(self, frame):
        # Convert frame to grayscale and detect edges
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Save first frame and edge detection results for debugging
        cv2.imwrite('first_frame.png', frame)
        cv2.imwrite('edge_detection.png', edges)

        # Iterate through contours to find potential watermark
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            area_ratio = (w * h) / (frame.shape[0] * frame.shape[1])
            
            # Check if contour meets criteria for watermark
            if 1.5 < aspect_ratio < 10 and 0.01 < area_ratio < 0.1:
                logging.info(f"Potential watermark detected: x={x}, y={y}, w={w}, h={h}")
                return (int(x), int(y), int(x + w), int(y + h))
        
        logging.warning("No watermark detected with current criteria")
        return None

    def inpaint_frame(self, frame):
        # Extract watermark region coordinates
        x, y, x2, y2 = self.watermark_region
        h, w = y2 - y, x2 - x

        # Pad region to ensure dimensions are multiples of 8
        pad_h, pad_w = (8 - h % 8) % 8, (8 - w % 8) % 8
        padded_region = frame[max(0, y-pad_h//2):min(frame.shape[0], y2+pad_h//2),
                              max(0, x-pad_w//2):min(frame.shape[1], x2+pad_w//2)]

        # Create mask for inpainting
        mask = np.ones(padded_region.shape[:2], dtype=np.uint8) * 255
        pil_region = Image.fromarray(cv2.cvtColor(padded_region, cv2.COLOR_BGR2RGB))
        pil_mask = Image.fromarray(mask)

        # Perform inpainting using the pipeline
        result = self.pipeline(
            prompt="",
            image=pil_region,
            mask_image=pil_mask,
            num_inference_steps=50,
        ).images[0]

        # Process and insert inpainted region back into frame
        inpainted_region = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
        crop_y, crop_x = (inpainted_region.shape[0] - h) // 2, (inpainted_region.shape[1] - w) // 2
        inpainted_region = inpainted_region[crop_y:crop_y+h, crop_x:crop_x+w]
        frame[y:y2, x:x2] = inpainted_region

        return frame

    def run(self):
        try:
            logging.info(f"Starting video processing: {self.video_path}")
            cap = cv2.VideoCapture(self.video_path)
            
            # Check if video file is opened successfully
            if not cap.isOpened():
                raise Exception("Error opening video file")

            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Set up video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
            # Read first frame and detect watermark
            ret, first_frame = cap.read()
            if not ret:
                raise Exception("Failed to read the first frame")
            self.watermark_region = self.detect_watermark(first_frame)
            if not self.watermark_region:
                error_msg = "No watermark detected automatically. Manual input required."
                logging.warning(error_msg)
                self.error_occurred.emit(error_msg)
                return

            logging.info(f"Watermark region detected: {self.watermark_region}")

            # Process each frame
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                processed_frame = self.inpaint_frame(frame)
                out.write(processed_frame)
                
                # Update progress
                frame_count += 1
                progress = int((frame_count / total_frames) * 100)
                self.progress_updated.emit(progress)
                if frame_count % 100 == 0:
                    logging.info(f"Processed frame {frame_count}/{total_frames}")

            # Clean up
            cap.release()
            out.release()
            logging.info("Video processing completed successfully")
            self.finished.emit()
        except Exception as e:
            error_msg = f"An error occurred during video processing: {str(e)}"
            logging.exception(error_msg)
            self.error_occurred.emit(error_msg)

class VideoEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.processing_thread = None
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Video Watermark Remover")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        # Add UI elements
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        browse_file_btn = QPushButton("Browse for Video File")
        browse_file_btn.clicked.connect(self.load_file)
        layout.addWidget(browse_file_btn)

        self.output_label = QLabel("No output file selected")
        layout.addWidget(self.output_label)

        save_file_btn = QPushButton("Browse for Save Location")
        save_file_btn.clicked.connect(self.save_file)
        layout.addWidget(save_file_btn)

        process_btn = QPushButton("Process Video")
        process_btn.clicked.connect(self.process_video)
        layout.addWidget(process_btn)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Initialize file paths
        self.video_file_path = ""
        self.output_file_path = ""

    def load_file(self):
        # Open file dialog to select input video
        self.video_file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4)")
        self.file_label.setText(self.video_file_path)
        logging.info(f"Input video file selected: {self.video_file_path}")

    def save_file(self):
        # Open file dialog to select output location
        self.output_file_path, _ = QFileDialog.getSaveFileName(self, "Save Output File", "", "Video Files (*.mp4)")
        self.output_label.setText(self.output_file_path)
        logging.info(f"Output video file selected: {self.output_file_path}")

    def load_pipeline(self):
        # Load the Stable Diffusion inpainting pipeline if not already loaded
        if not self.pipeline:
            try:
                model_name = "stabilityai/stable-diffusion-2-inpainting"
                logging.info(f"Loading pipeline: {model_name}")
                if torch.cuda.is_available():
                    logging.info("CUDA is available. Using GPU.")
                    self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16
                    )
                    self.pipeline = self.pipeline.to("cuda")
                else:
                    logging.info("CUDA is not available. Using CPU.")
                    self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(model_name)
                self.pipeline.enable_attention_slicing()
                logging.info("Pipeline loaded successfully")
            except Exception as e:
                error_msg = f"Error loading pipeline: {str(e)}"
                logging.exception(error_msg)
                QMessageBox.critical(self, "Error", error_msg)

    def process_video(self):
        # Check if input and output files are selected
        if not self.video_file_path or not self.output_file_path:
            error_msg = "Please select both input and output file locations."
            logging.error(error_msg)
            QMessageBox.warning(self, "Input Error", error_msg)
            return

        # Load pipeline and start processing thread
        self.load_pipeline()
        self.progress_bar.setValue(0)
        self.processing_thread = VideoProcessingThread(
            self.video_file_path, self.output_file_path, self.pipeline
        )
        self.processing_thread.error_occurred.connect(self.show_error)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.start()

    def update_progress(self, value):
        # Update progress bar
        self.progress_bar.setValue(value)
    def show_error(self, error_message):
        # Handle errors, including manual watermark input if needed
        logging.error(f"Error in processing: {error_message}")
        if "Manual input required" in error_message:
            self.get_manual_watermark_region()
        else:
            QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def get_manual_watermark_region(self):
        # Prompt user for manual watermark region input
        x, ok = QInputDialog.getInt(self, "Manual Input", "Enter x coordinate:")
        if ok:
            y, ok = QInputDialog.getInt(self, "Manual Input", "Enter y coordinate:")
            if ok:
                w, ok = QInputDialog.getInt(self, "Manual Input", "Enter width:")
                if ok:
                    h, ok = QInputDialog.getInt(self, "Manual Input", "Enter height:")
                    if ok:
                        self.processing_thread.watermark_region = (x, y, x+w, y+h)
                        logging.info(f"Manual watermark region set: {self.processing_thread.watermark_region}")
                        self.processing_thread.start()
                        return
        self.processing_finished()

    def processing_finished(self):
        # Display completion message
        logging.info("Video processing completed")
        QMessageBox.information(self, "Success", "Video processing completed!")

if __name__ == '__main__':
    logging.info("Starting application")
    app = QApplication(sys.argv)
    window = VideoEditorApp()
    window.show()
    sys.exit(app.exec_())
