import sys
import torch
import numpy as np
import moviepy.editor as mp
import cv2
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PIL import Image, ImageDraw
from diffusers import StableDiffusionInpaintPipeline

# Set up logging
logging.basicConfig(filename='video_watermark_remover.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Thread class for video processing
class VideoProcessingThread(QThread):
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    def __init__(self, video_path, output_path, pipeline):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.pipeline = pipeline
        self.progress = 0
    # Method to detect watermark in a frame
    def detect_watermark(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 2 < aspect_ratio < 5 and 0.05 < (w * h) / (frame.shape[0] * frame.shape[1]) < 0.2:
                return (x, y, x + w, y + h)
        return None

    # Method to inpaint a frame (remove watermark)
    def inpaint_frame(self, frame, region):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)
        mask = Image.new("RGB", im.size, (0, 0, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle(region, fill=(255, 255, 255))

        # Perform inpainting
        result = self.pipeline(
            prompt="",  # Empty prompt or you can add a general description
            image=im,
            mask_image=mask,
            num_inference_steps=50
        ).images[0]
        
        inpainted_frame = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
        return inpainted_frame

    # Main processing method
    def run(self):
        try:
            logging.info(f"Starting video processing: {self.video_path}")
            video = mp.VideoFileClip(self.video_path)
            total_frames = int(video.fps * video.duration)
            
            first_frame = video.get_frame(0)
            watermark_region = self.detect_watermark(first_frame)
            
            if not watermark_region:
                error_msg = "No watermark detected. Please check the video."
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            logging.info(f"Watermark region detected: {watermark_region}")

            processed_frames = []
            for i, frame in enumerate(video.iter_frames()):
                processed_frame = self.inpaint_frame(frame, watermark_region)
                processed_frames.append(processed_frame)
                
                self.progress = int((i + 1) / total_frames * 100)
                if (i + 1) % 10 == 0:
                    logging.info(f"Processed frame {i + 1}/{total_frames}")

            logging.info(f"Writing processed video to: {self.output_path}")
            processed_video = mp.ImageSequenceClip(processed_frames, fps=video.fps)
            processed_video.write_videofile(self.output_path, codec='libx264')
            
            logging.info("Video processing completed successfully")
            self.finished.emit()
        except Exception as e:
            error_msg = f"An error occurred during video processing: {str(e)}"
            logging.exception(error_msg)
            self.error_occurred.emit(error_msg)

    # Method to get current progress
    def get_progress(self):
        return self.progress

# Main application class
class VideoEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.processing_thread = None
        self.initUI()

    # Initialize the user interface
    def initUI(self):
        self.setWindowTitle("Video Watermark Remover")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

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

        self.video_file_path = ""
        self.output_file_path = ""

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

    # Method to load input video file
    def load_file(self):
        self.video_file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4)")
        self.file_label.setText(self.video_file_path)
        logging.info(f"Input video file selected: {self.video_file_path}")

    # Method to set output video file
    def save_file(self):
        self.output_file_path, _ = QFileDialog.getSaveFileName(self, "Save Output File", "", "Video Files (*.mp4)")
        self.output_label.setText(self.output_file_path)
        logging.info(f"Output video file selected: {self.output_file_path}")

    # Method to load the inpainting pipeline
    def load_pipeline(self):
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
                
                # Optional: Enable attention slicing for lower memory usage
                self.pipeline.enable_attention_slicing()
                
                logging.info("Pipeline loaded successfully")
            except Exception as e:
                error_msg = f"Error loading pipeline: {str(e)}"
                logging.exception(error_msg)
                QMessageBox.critical(self, "Error", error_msg)

    # Method to start video processing
    def process_video(self):
        if not self.video_file_path or not self.output_file_path:
            error_msg = "Please select both input and output file locations."
            logging.error(error_msg)
            QMessageBox.warning(self, "Input Error", error_msg)
            return

        self.load_pipeline()
        self.progress_bar.setValue(0)

        self.processing_thread = VideoProcessingThread(
            self.video_file_path, self.output_file_path, self.pipeline
        )
        self.processing_thread.error_occurred.connect(self.show_error)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.start()

        # Start the timer to update progress
        self.timer.start(100)  # Update every 100 ms

    # Method to update progress bar
    def update_progress(self):
        if self.processing_thread and self.processing_thread.isRunning():
            progress = self.processing_thread.get_progress()
            self.progress_bar.setValue(progress)
    # Method to show error messages
    def show_error(self, error_message):
        self.timer.stop()
        logging.error(f"Error in processing: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    # Method called when processing is finished
    def processing_finished(self):
        self.timer.stop()
        logging.info("Video processing completed successfully")
        QMessageBox.information(self, "Success", "Video processing completed successfully!")

# Main entry point
if __name__ == '__main__':
    logging.info("Starting application")
    app = QApplication(sys.argv)
    window = VideoEditorApp()
    window.show()
    sys.exit(app.exec_())
