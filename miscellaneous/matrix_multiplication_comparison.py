"""
This script compares the performance of Gaussian blur applied to an image using CPU and GPU.

The script performs the following operations:
1. Loads an image from a specified path.
2. Applies Gaussian blur to the image using both CPU and GPU (if available).
3. Measures and compares the execution time for both methods.
4. Prints memory usage statistics for CPU and GPU (if available).
5. Calculates and displays average execution times and performance speedup.

The comparison is run multiple times (default 3) to get more accurate average timings.

Functions:
- print_gpu_memory(): Prints GPU memory usage if available.
- print_cpu_memory(): Prints CPU memory usage.
- cpu_gaussian_blur(image, kernel_size): Applies Gaussian blur on CPU.
- gpu_gaussian_blur(image, kernel_size): Applies Gaussian blur on GPU.
- run_comparison(image_path, runs): Main function to compare CPU and GPU performance.

Usage:
Set the 'image_path' variable to the path of the image you want to process,
then run the script. The results will be printed to the console.

Requirements:
- numpy
- torch
- torchvision
- Pillow (PIL)
- psutil
- GPUtil

Note: GPU operations require CUDA-capable hardware and appropriate CUDA setup.
"""

import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import time
import psutil
import GPUtil

# Function to print GPU memory usage
def print_gpu_memory():
    """
    Print gpu memory.
    """
    if torch.cuda.is_available():
        GPUs = GPUtil.getGPUs()
        gpu = GPUs[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

# Function to print CPU memory usage
def print_cpu_memory():
    """
    Print cpu memory.
    """
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

# Function to apply Gaussian blur on CPU
def cpu_gaussian_blur(image, kernel_size=21):
    """
    Cpu gaussian blur based on image, kernel size.
    """
    blur = transforms.GaussianBlur(kernel_size)
    return blur(image)

# Function to apply Gaussian blur on GPU
def gpu_gaussian_blur(image, kernel_size=21):
    """
    Gpu gaussian blur based on image, kernel size.
    """
    blur = transforms.GaussianBlur(kernel_size)
    return blur(image.to('cuda')).cpu()

# Main function to compare CPU and GPU performance
def run_comparison(image_path, runs=3):
    """
    Run comparison based on image path, runs.
    """
    print(f"Applying Gaussian blur to image: {image_path}")
    
    # Load image and convert to tensor
    image = Image.open(image_path)
    image = transforms.ToTensor()(image)
    
    cpu_times = []
    gpu_times = []

    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        # CPU blur
        print("CPU Gaussian Blur:")
        print_cpu_memory()
        cpu_start = time.time()
        cpu_result = cpu_gaussian_blur(image)
        cpu_end = time.time()
        cpu_time = cpu_end - cpu_start
        cpu_times.append(cpu_time)
        print(f"CPU Time: {cpu_time:.4f} seconds")
        print_cpu_memory()

        # GPU blur (if available)
        if torch.cuda.is_available():
            print("\nGPU Gaussian Blur:")
            print_gpu_memory()
            torch.cuda.synchronize()
            gpu_start = time.time()
            gpu_result = gpu_gaussian_blur(image)
            torch.cuda.synchronize()
            gpu_end = time.time()
            gpu_time = gpu_end - gpu_start
            gpu_times.append(gpu_time)
            print(f"GPU Time: {gpu_time:.4f} seconds")
            print_gpu_memory()

    # Calculate and print average times
    avg_cpu_time = sum(cpu_times) / len(cpu_times)
    print(f"\nAverage CPU Time: {avg_cpu_time:.4f} seconds")
    
    if torch.cuda.is_available():
        avg_gpu_time = sum(gpu_times) / len(gpu_times)
        print(f"Average GPU Time: {avg_gpu_time:.4f} seconds")
        
        # Compare CPU and GPU performance
        if avg_cpu_time < avg_gpu_time:
            speedup = avg_gpu_time / avg_cpu_time
            print(f"CPU is faster by {speedup:.2f}x")
        else:
            speedup = avg_cpu_time / avg_gpu_time
            print(f"GPU is faster by {speedup:.2f}x")

# Main execution
if __name__ == "__main__":
    # Replace with the path to a large image file
    image_path = "/home/erangross/Downloads/1.jpg"
    run_comparison(image_path)
