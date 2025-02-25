"""
This script compares the performance of CPU and GPU for finding prime numbers.

It uses NumPy and PyTorch to generate random numbers and perform calculations.
The script includes functions for prime number checking and finding on both CPU and GPU.
It also monitors and reports CPU and GPU memory usage during the process.

The main function, run_comparison(), performs multiple runs of prime number finding
on both CPU and GPU (if available), and reports the average execution times.

Dependencies:
- numpy
- torch
- time
- psutil
- GPUtil

Usage:
Run the script to perform the CPU-GPU comparison for prime number finding.
The comparison parameters (number size, maximum number, and number of runs)
can be adjusted in the run_comparison() function call at the end of the script.
"""

# Import necessary libraries
import numpy as np
import torch
import time
import psutil
import GPUtil

# Set the device to GPU if available, otherwise use CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Print GPU information if CUDA is available
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"CUDA Version: {torch.version.cuda}")

# Function to check if a number is prime
def is_prime(n):
    """
    Checks if prime based on n.
    """
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Function to find prime numbers using CPU
def cpu_find_primes(numbers):
    """
    Cpu find primes based on numbers.
    """
    return [num for num in numbers if is_prime(num)]

# JIT-compiled function to check if a number is prime using GPU
@torch.jit.script
def gpu_is_prime(n):
    """
    Gpu is prime based on n.
    """
    if n <= 1:
        return False
    for i in range(2, int(torch.sqrt(n.float())) + 1):
        if n % i == 0:
            return False
    return True

# Function to find prime numbers using GPU
def gpu_find_primes(numbers):
    """
    Gpu find primes based on numbers.
    """
    results = torch.zeros_like(numbers, dtype=torch.bool)
    for i in range(len(numbers)):
        results[i] = gpu_is_prime(numbers[i])
    return numbers[results].cpu().numpy()

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

# Main function to run the comparison between CPU and GPU
def run_comparison(size=100000, max_num=1000000, runs=5):
    """
    Run comparison based on size, max num, runs.
    """
    print(f"\nFinding primes in {size} numbers up to {max_num}")
    
    cpu_times = []
    gpu_times = []

    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        # Generate random numbers for testing
        numbers = np.random.randint(2, max_num, size=size)
        
        # CPU prime finding
        print("CPU Prime Finding:")
        print_cpu_memory()
        cpu_start = time.time()
        cpu_primes = cpu_find_primes(numbers)
        cpu_end = time.time()
        cpu_time = cpu_end - cpu_start
        cpu_times.append(cpu_time)
        print(f"CPU Time: {cpu_time:.4f} seconds")
        print(f"CPU Primes found: {len(cpu_primes)}")
        print_cpu_memory()

        # GPU prime finding (if CUDA is available)
        if torch.cuda.is_available():
            print("\nGPU Prime Finding:")
            print_gpu_memory()
            gpu_numbers = torch.tensor(numbers, device=device)
            torch.cuda.synchronize()
            gpu_start = time.time()
            gpu_primes = gpu_find_primes(gpu_numbers)
            torch.cuda.synchronize()
            gpu_end = time.time()
            gpu_time = gpu_end - gpu_start
            gpu_times.append(gpu_time)
            print(f"GPU Time: {gpu_time:.4f} seconds")
            print(f"GPU Primes found: {len(gpu_primes)}")
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

# Run the comparison
run_comparison()
