"""
Watermark Detection and Inpainting Application

This script implements a graphical user interface (GUI) application for detecting
and removing watermarks from images and videos using machine learning models.

Key Features:
1. YOLOv5 model for watermark detection
2. Stable Diffusion Inpainting model for watermark removal
3. Support for processing both images and videos
4. Real-time progress tracking and logging
5. Intermediate frame saving for video processing

The application allows users to:
- Load a custom YOLOv5 model for watermark detection
- Select input images or videos for processing
- Choose output locations for processed files
- View progress and logs in real-time
- Save intermediate frames during video processing for analysis

Dependencies:
- torch
- cv2
- numpy
- tkinter
- logging
- threading
- diffusers
- PIL

Usage:
Run this script to launch the GUI application. Use the interface to load models,
select input/output files, and process images or videos for watermark removal.

Note: Ensure all required dependencies are installed and CUDA is available
for optimal performance when processing large files or videos.
"""

import torch
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import logging
import threading
from diffusers import StableDiffusionInpaintPipeline
import os
from datetime import datetime
from PIL import Image, ImageOps
from huggingface_hub import login, HfFolder
from huggingface_hub.utils import LocalTokenNotFoundError
import tkinter as tk
from tkinter import simpledialog
from diffusers import StableDiffusionXLInpaintPipeline

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WatermarkDetectionApp:
    def __init__(self, master):
        # Initialize the main application window
        self.master = master
        self.master.title("Watermark Detection and Inpainting")
        self.master.geometry("900x800")
        
        # Initialize variables for file paths
        self.model_path = tk.StringVar()
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Initialize model variables
        self.watermark_model = None
        self.inpainting_pipeline = None
        self.processing = False
        
        # Set the device (CPU/GPU) based on availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Set the default inpainting model type
        self.inpainting_model_type = "SDXL"
        
        # Create the GUI elements
        self.create_widgets()
        
    def create_widgets(self):
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

    def download_and_load_inpainting_model(self):
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        try:
            # Check if the user is already logged in
            token = HfFolder.get_token()
            if token is None:
                # If not logged in, prompt for the token
                token = simpledialog.askstring("Hugging Face Login", "Enter your Hugging Face token:", parent=self.master)
                if token:
                    login(token)
                else:
                    raise ValueError("Hugging Face token is required to download the model.")
            
            # Determine the device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Attempting to use device: {device}")
            
            if device == "cuda":
                logger.info(f"CUDA is available. GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA version: {torch.version.cuda}")
            else:
                logger.info("CUDA is not available. Using CPU.")
            
            # Load the model
            logger.info(f"Loading model from {model_id}")
            self.inpainting_pipeline = StableDiffusionXLInpaintPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                use_safetensors=True,
                variant="fp16" if device == "cuda" else None,
                use_auth_token=token
            )
            logger.info("Model loaded successfully")
            
            # Move to appropriate device
            logger.info(f"Moving model to {device}")
            self.inpainting_pipeline = self.inpainting_pipeline.to(device)
            logger.info(f"Model moved to {device}")
            
            # Enable memory optimizations
            logger.info("Enabling attention slicing")
            self.inpainting_pipeline.enable_attention_slicing()
            if device == "cuda":
                logger.info("Enabling VAE slicing for CUDA")
                self.inpainting_pipeline.enable_vae_slicing()
            
            # Disable safety checker to save memory
            logger.info("Disabling safety checker to save memory")
            self.inpainting_pipeline.safety_checker = None
            
            # Log model components
            logger.info("Model components:")
            for name, module in self.inpainting_pipeline.components.items():
                logger.info(f"  {name}: {type(module).__name__}")
            
            # Check if model is on correct device
            logger.info(f"Model device: {self.inpainting_pipeline.device}")
            
            success_message = f"Inpainting model loaded successfully on {device} with memory optimizations"
            logger.info(success_message)
            messagebox.showinfo("Success", success_message)
        
        except Exception as e:
            error_message = f"Error loading inpainting model: {str(e)}"
            logger.error(error_message, exc_info=True)
            messagebox.showerror("Error", error_message)


    def inpaint(self, prompt, image, mask_image):
        try:
            with torch.no_grad():
                result = self.inpainting_pipeline(
                    prompt=prompt,
                    image=image,
                    mask_image=mask_image,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                ).images[0]
            return result
        except Exception as e:
            logger.error(f"Error during inpainting: {str(e)}")
            messagebox.showerror("Error", f"Inpainting failed: {str(e)}")
            return None




    def browse_model(self):
        # Open file dialog to select the YOLOv5 model
        filename = filedialog.askopenfilename(filetypes=[("PyTorch Model", "*.pt")])
        if filename:
            self.model_path.set(filename)
            logger.info(f"Model selected: {filename}")
            self.load_watermark_model()

    def load_watermark_model(self):
        # Load the selected YOLOv5 model for watermark detection
        try:
            self.watermark_model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path.get(), force_reload=True)
            self.watermark_model.to('cpu')
            self.watermark_model.eval()
            for param in self.watermark_model.parameters():
                param.requires_grad = False
            logger.info("Watermark detection model loaded successfully")
            messagebox.showinfo("Success", "Watermark detection model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading watermark detection model: {str(e)}")
            messagebox.showerror("Error", f"Failed to load watermark detection model: {str(e)}")
            self.watermark_model = None

    def browse_input(self):
        # Open file dialog to select input file (video or image)
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4"), ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if filename:
            self.input_path.set(filename)
            logger.info(f"Input file selected: {filename}")

    def browse_output(self):
        # Open file dialog to select output file location
        filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("JPEG files", "*.jpg")])
        if filename:
            self.output_path.set(filename)
            logger.info(f"Output path selected: {filename}")

    def start_processing(self):
        # Start the processing of the input file
        if not self.processing:
            self.processing = True
            self.process_button.config(state=tk.DISABLED)

            # Load the inpainting model synchronously if it hasn't been loaded yet
            if self.inpainting_pipeline is None:
                self.download_and_load_inpainting_model()

            # Only start processing if the model was loaded successfully
            if self.inpainting_pipeline is not None:
                threading.Thread(target=self.process_file, daemon=True).start()
            else:
                self.processing = False
                self.process_button.config(state=tk.NORMAL)
                messagebox.showerror("Error", "Failed to load the inpainting model. Cannot process file.")

    def process_file(self):
        # Process the input file (either image or video)
        if self.watermark_model is None:
            messagebox.showerror("Error", "Please load a watermark detection model first.")
            logger.error("No watermark detection model loaded")
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
        # Process a single image
        img = cv2.imread(input_path)
        logger.info(f"Image read successfully: {input_path}")

        watermark_mask = self.detect_watermark(img)
        inpainted_img = self.inpaint_image(img, watermark_mask)

        cv2.imwrite(output_path, inpainted_img)
        logger.info(f"Processed image saved: {output_path}")

        self.progress_var.set(100)
        messagebox.showinfo("Success", "Image processing completed successfully!")
       
    def save_intermediate_frame(self, frame, frame_number):
        # Save intermediate frames during video processing
        output_dir = os.path.join(os.path.dirname(self.output_path.get()), "intermediate_frames")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"frame_{frame_number:04d}.jpg")
        cv2.imwrite(output_path, frame)
        logger.info(f"Saved intermediate frame: {output_path}")

    def process_video(self, input_path, output_path):
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
        
        # Create timestamped directory for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.dirname(output_path)
        run_dir = os.path.join(base_dir, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        
        # Create subdirectories for each step
        original_frames_dir = os.path.join(run_dir, "original_frames")
        detected_frames_dir = os.path.join(run_dir, "detected_frames")
        inpainted_frames_dir = os.path.join(run_dir, "inpainted_frames")
        os.makedirs(original_frames_dir, exist_ok=True)
        os.makedirs(detected_frames_dir, exist_ok=True)
        os.makedirs(inpainted_frames_dir, exist_ok=True)
        
        for frame_num in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Failed to read frame {frame_num}")
                break
            
            # Save original frame
            original_frame_path = os.path.join(original_frames_dir, f"frame_{frame_num:04d}.jpg")
            cv2.imwrite(original_frame_path, frame)
            
            # Detect watermark and save frame with detection
            watermark_mask, detected_frame = self.detect_and_mark_watermark(frame)
            detected_frame_path = os.path.join(detected_frames_dir, f"frame_{frame_num:04d}.jpg")
            cv2.imwrite(detected_frame_path, detected_frame)
            
            # Visualize and save the mask
            mask_vis = self.visualize_mask(frame, watermark_mask)
            mask_vis_path = os.path.join(detected_frames_dir, f"frame_{frame_num:04d}_mask.jpg")
            cv2.imwrite(mask_vis_path, mask_vis)
            
            # Only proceed with inpainting if watermark is detected
            if np.any(watermark_mask > 0):
                try:
                    inpainted_frame, inpaint_vis = self.inpaint_image(
                        frame,
                        watermark_mask,
                        prompt="high quality, detailed image without any watermark, text, or logo. Clear, sharp, and consistent with the surrounding image content.",
                        negative_prompt="text, watermark, logo, blurry, low quality, distorted, inconsistent lighting or texture",
                        num_inference_steps=50,
                        guidance_scale=7.5,
                        strength=1.0,
                        seed=frame_num
                    )
                    
                    # Save inpainted frame and visualization
                    inpainted_frame_path = os.path.join(inpainted_frames_dir, f"frame_{frame_num:04d}.jpg")
                    cv2.imwrite(inpainted_frame_path, inpainted_frame)
                    inpaint_vis_path = os.path.join(inpainted_frames_dir, f"frame_{frame_num:04d}_vis.jpg")
                    cv2.imwrite(inpaint_vis_path, inpaint_vis)
                    
                    logger.info(f"Successfully inpainted frame {frame_num}")
                except Exception as e:
                    logger.error(f"Inpainting failed for frame {frame_num}: {str(e)}")
                    inpainted_frame = frame
            else:
                logger.info(f"No watermark detected in frame {frame_num}. Skipping inpainting.")
                inpainted_frame = frame
            
            # Write to output video
            out.write(inpainted_frame)
            
            progress = (frame_num + 1) / total_frames * 100
            self.progress_var.set(progress)
            self.master.update_idletasks()
            
            if frame_num % 10 == 0:  # Log every 10 frames for more frequent updates
                logger.info(f"Processed frame {frame_num}/{total_frames} ({progress:.2f}%)")
        
        cap.release()
        out.release()
        logger.info(f"Processed video saved: {output_path}")
        logger.info(f"Intermediate frames saved in: {run_dir}")
        messagebox.showinfo("Success", f"Video processing completed successfully!\nResults saved in: {run_dir}")




    def detect_and_mark_watermark(self, img):
        results = self.watermark_model(img)
        height, width = img.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        marked_img = img.copy()
        
        total_area = 0
        for det in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = det.tolist()
            if conf > 0.5:  # Confidence threshold
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
                cv2.rectangle(marked_img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
                
                # Calculate area for this detection
                area = (x2 - x1) * (y2 - y1)
                total_area += area
                area_percentage = (area / (height * width)) * 100
                logger.info(f"Detected watermark area: {area_percentage:.2f}% of the image")

        # Calculate correct coverage percentage
        coverage_percentage = (total_area / (height * width)) * 100
        logger.info(f"Total watermark coverage: {coverage_percentage:.2f}% of the image")

        # Adjust the sanity check threshold
        if coverage_percentage > 25:  # Warning if more than 25% is covered
            logger.warning(f"Watermark detection covered {coverage_percentage:.2f}% of the image, which is unusually large. Proceeding with caution.")
        
        return mask, marked_img



    def visualize_mask(self, img, mask):
        vis = img.copy()
        if mask is not None and np.any(mask > 0):
            vis[mask > 0] = cv2.addWeighted(img[mask > 0], 0.5, np.full_like(img[mask > 0], [0, 255, 0]), 0.5, 0)
        return vis


        

    def inpaint_image(self, img, mask, prompt="", negative_prompt="", num_inference_steps=50, guidance_scale=7.5, strength=1.0, seed=None):
        if mask is None or np.sum(mask) == 0:
            return img, img
        
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        mask_pil = Image.fromarray(mask)
        
        # Get the bounding box of the mask
        rows, cols = np.where(mask > 0)
        if len(rows) == 0 or len(cols) == 0:
            return img, img
        
        top, left = np.min(rows), np.min(cols)
        bottom, right = np.max(rows), np.max(cols)
        
        # Expand the bounding box slightly
        padding = 40
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(img.shape[0], bottom + padding)
        right = min(img.shape[1], right + padding)
        
        # Crop the image and mask to the expanded bounding box
        img_crop = img[top:bottom, left:right]
        mask_crop = mask[top:bottom, left:right]
        
        # Convert cropped image and mask to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB))
        mask_pil = Image.fromarray(mask_crop)
        
        # Resize to 1024x1024 (SDXL's preferred size)
        orig_size = img_pil.size
        img_pil = img_pil.resize((1024, 1024), Image.LANCZOS)
        mask_pil = mask_pil.resize((1024, 1024), Image.NEAREST)
        
        # Ensure mask is binary
        mask_pil = mask_pil.convert('L')
        mask_pil = mask_pil.point(lambda x: 255 if x > 128 else 0, '1')
        
        # Invert mask (SDXL expects white for inpainting area)
        mask_pil = ImageOps.invert(mask_pil)
        
        generator = torch.manual_seed(seed) if seed is not None else None
        
        # Perform inpainting
        inpainted = self.inpainting_pipeline(
            prompt=prompt,
            image=img_pil,
            mask_image=mask_pil,
            negative_prompt=negative_prompt or "text, watermark, logo, shutterstock, copyright, blurry, distorted, low quality",
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            strength=strength,
            generator=generator
        ).images[0]
        
        # Resize back to original crop size
        inpainted = inpainted.resize(orig_size, Image.LANCZOS)
        
        # Convert back to OpenCV format
        inpainted = cv2.cvtColor(np.array(inpainted), cv2.COLOR_RGB2BGR)
        
        # Blend the inpainted area back into the original image
        result = img.copy()
        mask_crop_3d = np.repeat(mask_crop[:, :, np.newaxis], 3, axis=2) / 255.0
        result[top:bottom, left:right] = (1 - mask_crop_3d) * img_crop + mask_crop_3d * inpainted
        
        # Create visualization
        vis = img.copy()
        vis[top:bottom, left:right] = cv2.addWeighted(img_crop, 0.5, inpainted, 0.5, 0)
        cv2.rectangle(vis, (left, top), (right, bottom), (0, 255, 0), 2)
        
        return result, vis

    def resize_and_pad(self, img, mask, size=512):
        # Resize image and mask, maintaining aspect ratio
        img.thumbnail((size, size))
        mask.thumbnail((size, size))

        # Create new images with padding
        new_img = Image.new("RGB", (size, size), (0, 0, 0))
        new_mask = Image.new("L", (size, size), 0)

        # Paste resized image and mask onto padded images
        new_img.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
        new_mask.paste(mask, ((size - mask.width) // 2, (size - mask.height) // 2))

        return new_img, new_mask

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
