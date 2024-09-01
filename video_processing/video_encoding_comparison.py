"""
This script compares the performance of CPU and GPU video encoding using FFmpeg.

It provides functions to:
- Print GPU and CPU memory usage
- Encode video using either CPU or GPU
- Run a comparison between CPU and GPU encoding

The script measures encoding time for both CPU and GPU (if available) over multiple runs,
calculates average encoding times, and compares the performance between CPU and GPU.

Dependencies:
- subprocess: For running FFmpeg commands
- time: For measuring encoding time
- os: For file operations
- psutil: For CPU memory usage monitoring
- GPUtil: For GPU memory usage monitoring and GPU availability checking

Usage:
Replace 'input.mp4' with the path to your input video file at the end of the script.
Run the script to perform the encoding comparison.

Note: This script requires FFmpeg to be installed and accessible in the system path.
For GPU encoding, it assumes an NVIDIA GPU with NVENC support.
"""

import subprocess
import time
import os
import psutil
import GPUtil

# Function to print GPU memory usage
def print_gpu_memory():
    if GPUtil.getGPUs():
        gpu = GPUtil.getGPUs()[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

# Function to print CPU memory usage
def print_cpu_memory():
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

# Function to encode video using either CPU or GPU
def encode_video(input_file, output_file, use_gpu=False):
    if use_gpu:
        # NVIDIA GPU encoding command (adjust -preset as needed)
        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-c:v', 'h264_nvenc', '-preset', 'slow',
            '-b:v', '5M', '-maxrate', '10M', '-bufsize', '15M',
            '-acodec', 'copy', output_file
        ]
    else:
        # CPU encoding command (adjust -preset as needed)
        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-c:v', 'libx264', '-preset', 'slow',
            '-b:v', '5M', '-maxrate', '10M', '-bufsize', '15M',
            '-acodec', 'copy', output_file
        ]

    # Measure encoding time
    start_time = time.time()
    subprocess.run(cmd, check=True)
    end_time = time.time()

    return end_time - start_time

# Function to run comparison between CPU and GPU encoding
def run_comparison(input_file, runs=3):
    cpu_times = []
    gpu_times = []

    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")

        # CPU encoding
        print("CPU Encoding:")
        print_cpu_memory()
        cpu_output = f'output_cpu_{i}.mp4'
        cpu_time = encode_video(input_file, cpu_output, use_gpu=False)
        cpu_times.append(cpu_time)
        print(f"CPU Time: {cpu_time:.2f} seconds")
        print_cpu_memory()
        os.remove(cpu_output)

        # GPU encoding (if available)
        if GPUtil.getGPUs():
            print("\nGPU Encoding:")
            print_gpu_memory()
            gpu_output = f'output_gpu_{i}.mp4'
            gpu_time = encode_video(input_file, gpu_output, use_gpu=True)
            gpu_times.append(gpu_time)
            print(f"GPU Time: {gpu_time:.2f} seconds")
            print_gpu_memory()
            os.remove(gpu_output)

    # Calculate and print average times
    avg_cpu_time = sum(cpu_times) / len(cpu_times)
    print(f"\nAverage CPU Time: {avg_cpu_time:.2f} seconds")

    if gpu_times:
        avg_gpu_time = sum(gpu_times) / len(gpu_times)
        print(f"Average GPU Time: {avg_gpu_time:.2f} seconds")

        # Compare CPU and GPU performance
        if avg_cpu_time < avg_gpu_time:
            speedup = avg_gpu_time / avg_cpu_time
            print(f"CPU is faster by {speedup:.2f}x")
        else:
            speedup = avg_cpu_time / avg_gpu_time
            print(f"GPU is faster by {speedup:.2f}x")

# Replace 'input.mp4' with the path to your input video file
input_file = '/home/erangross/Downloads/1.mp4'
run_comparison(input_file)
