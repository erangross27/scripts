import sys
import cv2
import numpy as np
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import os
import logging
import datetime
from yolov5.models.experimental import attempt_load
import torch.nn.functional as F

print(f"PyTorch version: {torch.__version__}")
print(f"Python version: {sys.version}")


# Set up logging
log_filename = f"watermark_detection_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class WatermarkDetector:
    def __init__(self, model_path):
        logging.info(f"Initializing WatermarkDetector with model: {model_path}")
        try:
            if not os.path.isfile(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            # Load YOLOv5 model
            self.model = attempt_load(model_path, device='cpu')
            self.model.eval()
            logging.info(f"Model architecture: {type(self.model).__name__}")
            logging.info(f"Model summary: {self.model}")
            logging.info("Model loaded successfully from local file")
            
            # Get the input size that the model expects
            self.input_size = self.model.stride.max().int().item() * 32  # This is typically 640 for YOLOv5
            logging.info(f"Model expected input size: {self.input_size}x{self.input_size}")
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            raise

    def detect_watermark(self, frame):
        logging.debug(f"Processing frame: shape={frame.shape}, dtype={frame.dtype}")
        try:
            # Convert frame to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert numpy array to PyTorch tensor
            frame_tensor = torch.from_numpy(frame_rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            
            # Resize the tensor to match the model's expected input size
            frame_tensor = F.interpolate(frame_tensor, size=(self.input_size, self.input_size), mode='bilinear', align_corners=False)
            
            # Move tensor to the same device as the model
            frame_tensor = frame_tensor.to(next(self.model.parameters()).device)
            
            logging.debug(f"Frame tensor shape after resize: {frame_tensor.shape}")
            
            # Perform detection
            with torch.no_grad():
                results = self.model(frame_tensor)
                logging.debug(f"Raw model output type: {type(results)}")
                logging.debug(f"Raw model output: {results}")
            # Process results
            if isinstance(results, tuple):
                # If results is a tuple, it might contain multiple outputs
                # Let's assume the first element contains the detections
                detections = results[0]
            else:
                detections = results
            
            # Convert detections to numpy array
            if isinstance(detections, torch.Tensor):
                detections = detections.cpu().numpy()
            
            # If detections is a list of tensors, take the first one
            if isinstance(detections, list):
                detections = detections[0]
            
            # Ensure detections is a 2D array
            if len(detections.shape) == 1:
                detections = detections.reshape(1, -1)
            
            # Scale back the detections to match the original image size
            scale_x = frame.shape[1] / self.input_size
            scale_y = frame.shape[0] / self.input_size
            detections[:, [0, 2]] *= scale_x
            detections[:, [1, 3]] *= scale_y
            
            logging.debug(f"Raw detections shape: {detections.shape}")
            logging.debug(f"Raw detections: {detections}")
            return detections
        except Exception as e:
            logging.error(f"Error during detection: {str(e)}")
            logging.error(f"Results type: {type(results)}")
            logging.error(f"Results content: {results}")
            return []


class VideoProcessingThread(QThread):
    update_frame = pyqtSignal(np.ndarray)
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, input_path, output_path, model_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        logging.info(f"Initializing VideoProcessingThread with input: {input_path}, output: {output_path}")
        try:
            self.watermark_detector = WatermarkDetector(model_path)
        except Exception as e:
            logging.error(f"Failed to initialize WatermarkDetector: {str(e)}")
            raise

    def run(self):
        logging.info("Starting video processing")
        cap = cv2.VideoCapture(self.input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logging.info(f"Video properties: FPS={fps}, Width={width}, Height={height}, Total Frames={total_frames}")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.info("Reached end of video")
                break

            detections = self.watermark_detector.detect_watermark(frame)
            logging.debug(f"Frame {frame_count} detections:")

            for det in detections:
                x1, y1, x2, y2, conf, cls = det
                x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                logging.debug(f"Confidence: {conf:.2f}, Class: {cls}, Coordinates: ({x1}, {y1}, {x2}, {y2})")
                
                # Draw rectangle regardless of confidence
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Watermark {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                logging.info(f"Watermark detected in frame {frame_count} with confidence {conf:.2f}")

            out.write(frame)
            self.update_frame.emit(frame)
            frame_count += 1
            progress = int((frame_count / total_frames) * 100)
            self.update_progress.emit(progress)

            if frame_count == 1:
                preview_path = os.path.splitext(self.output_path)[0] + "_preview.png"
                cv2.imwrite(preview_path, frame)
                logging.info(f"Preview frame saved as {preview_path}")

        
        cap.release()
        out.release()
        logging.info("Video processing completed")
        self.finished.emit()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO Watermark Detector")
        self.setGeometry(100, 100, 800, 600)
        logging.info("Initializing MainWindow")

        layout = QVBoxLayout()
        self.model_button = QPushButton("Select Model File")
        self.model_button.clicked.connect(self.select_model)
        layout.addWidget(self.model_button)
        self.input_button = QPushButton("Select Input Video")
        self.input_button.clicked.connect(self.select_input)
        layout.addWidget(self.input_button)

        self.output_button = QPushButton("Select Output Location")
        self.output_button.clicked.connect(self.select_output)
        layout.addWidget(self.output_button)

        self.process_button = QPushButton("Process Video")
        self.process_button.clicked.connect(self.process_video)
        layout.addWidget(self.process_button)

        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.frame_label = QLabel()
        layout.addWidget(self.frame_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.model_path = ""
        self.input_path = ""
        self.output_path = ""
    def select_model(self):
        self.model_path, _ = QFileDialog.getOpenFileName(self, "Select Model File (best.pt)", "", "PyTorch Model (*.pt)")
        if self.model_path:
            if os.path.basename(self.model_path) != "best.pt":
                logging.warning(f"Selected file is not named 'best.pt': {self.model_path}")
            self.model_button.setText(f"Model: {os.path.basename(self.model_path)}")
            logging.info(f"Selected model: {self.model_path}")


    def select_input(self):
        self.input_path, _ = QFileDialog.getOpenFileName(self, "Select Input Video", "", "Video Files (*.mp4 *.avi)")
        if self.input_path:
            self.input_button.setText(f"Input: {self.input_path}")
            logging.info(f"Selected input video: {self.input_path}")

    def select_output(self):
        self.output_path, _ = QFileDialog.getSaveFileName(self, "Select Output Location", "", "Video Files (*.mp4)")
        if self.output_path:
            self.output_button.setText(f"Output: {self.output_path}")
            logging.info(f"Selected output location: {self.output_path}")

    def process_video(self):
        if not self.model_path or not self.input_path or not self.output_path:
            self.status_label.setText("Status: Please select model, input, and output files")
            logging.warning("Attempted to process video without all necessary paths selected")
            return
        
        logging.info(f"Starting video processing with model: {self.model_path}")
        logging.info(f"Input video: {self.input_path}")
        logging.info(f"Output video: {self.output_path}")
        self.status_label.setText("Status: Processing...")
        self.progress_bar.setValue(0)
        
        try:
            self.thread = VideoProcessingThread(self.input_path, self.output_path, self.model_path)
            self.thread.update_frame.connect(self.update_frame)
            self.thread.update_progress.connect(self.update_progress)
            self.thread.finished.connect(self.processing_finished)
            self.thread.start()
        except Exception as e:
            logging.error(f"Error starting video processing: {str(e)}")
            self.status_label.setText(f"Status: Error - {str(e)}")

    def update_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.frame_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        logging.debug(f"Progress updated: {value}%")
    def processing_finished(self):
        preview_path = os.path.splitext(self.output_path)[0] + "_preview.png"
        self.status_label.setText(f"Status: Processing complete. Preview saved as {preview_path}")
        logging.info("Video processing finished")
if __name__ == "__main__":
    logging.info("Starting application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
