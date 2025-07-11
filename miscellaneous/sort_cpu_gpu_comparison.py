"""
This script compares the performance of CPU and GPU sorting algorithms.

It uses NumPy for CPU sorting and PyTorch for GPU sorting. The script performs the following tasks:
1. Checks for CUDA availability and sets the device accordingly.
2. Prints information about the GPU if available.
3. Defines functions for CPU and GPU sorting.
4. Defines functions to print CPU and GPU memory usage.
5. Runs a comparison between CPU and GPU sorting:
   - Generates random data
   - Sorts the data using both CPU and GPU
   - Measures and reports the time taken for each method
   - Calculates and reports average times and speedup
   
The comparison is run multiple times with a large array to get a reliable performance measure.

Requirements:
- NumPy
- PyTorch
- psutil
- GPUtil

Note: GPU sorting will only be performed if CUDA is available.
"""

import numpy as np
import torch
import time
import psutil
import GPUtil

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Print GPU information if available
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"CUDA Version: {torch.version.cuda}")

def cpu_sort(arr):
    """
    Cpu sort based on arr.
    """
    return np.sort(arr)

def gpu_sort(arr):
    """
    Gpu sort based on arr.
    """
    return torch.sort(arr)[0]

def print_gpu_memory():
    """
    Print gpu memory.
    """
    if torch.cuda.is_available():
        GPUs = GPUtil.getGPUs()
        gpu = GPUs[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

def print_cpu_memory():
    """
    Print cpu memory.
    """
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

def run_comparison(size=10_000_000, runs=5):
    """
    Run comparison based on size, runs.
    """
    print(f"\nSorting array of size {size}")
    
    cpu_times = []
    gpu_times = []

    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        # Generate random data
        data = np.random.rand(size).astype(np.float32)
        
        # CPU sorting
        print("CPU Sorting:")
        print_cpu_memory()
        cpu_start = time.time()
        cpu_sorted = cpu_sort(data)
        cpu_end = time.time()
        cpu_time = cpu_end - cpu_start
        cpu_times.append(cpu_time)
        print(f"CPU Time: {cpu_time:.4f} seconds")
        print_cpu_memory()

        # GPU sorting
        if torch.cuda.is_available():
            print("\nGPU Sorting:")
            print_gpu_memory()
            gpu_data = torch.from_numpy(data).to(device)
            torch.cuda.synchronize()
            gpu_start = time.time()
            gpu_sorted = gpu_sort(gpu_data)
            torch.cuda.synchronize()
            gpu_end = time.time()
            gpu_time = gpu_end - gpu_start
            gpu_times.append(gpu_time)
            print(f"GPU Time: {gpu_time:.4f} seconds")
            print_gpu_memory()
        else:
            print("\nCUDA is not available. Skipping GPU sorting.")

    # Print average times
    avg_cpu_time = sum(cpu_times) / len(cpu_times)
    print(f"\nAverage CPU Time: {avg_cpu_time:.4f} seconds")
    
    if torch.cuda.is_available():
        avg_gpu_time = sum(gpu_times) / len(gpu_times)
        print(f"Average GPU Time: {avg_gpu_time:.4f} seconds")
        speedup = avg_cpu_time / avg_gpu_time
        print(f"GPU speedup over CPU: {speedup:.2f}x")


# Run the comparison
run_comparison()

