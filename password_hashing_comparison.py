"""
This script compares the performance of password hashing using CPU and GPU.

It includes functions to:
- Print GPU and CPU memory usage
- Hash passwords using CPU and GPU
- Run a comparison between CPU and GPU hashing performance

The main function, run_comparison(), generates a set of sample passwords and
performs multiple runs of hashing using both CPU and GPU (if available).
It then calculates and prints the average time taken for each method and
compares their performance.

Dependencies:
- hashlib: For SHA-256 hashing
- torch: For GPU operations
- time: For timing the operations
- psutil: For CPU memory usage
- GPUtil: For GPU memory usage

Usage:
Run this script directly to perform the comparison with default parameters.
You can modify the parameters in the run_comparison() function call if needed.
"""

import hashlib
import torch
import time
import psutil
import GPUtil

# Function to print GPU memory usage
def print_gpu_memory():
    if torch.cuda.is_available():
        GPUs = GPUtil.getGPUs()
        gpu = GPUs[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

# Function to print CPU memory usage
def print_cpu_memory():
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

# Function to hash passwords using CPU
def cpu_hash_passwords(passwords):
    return [hashlib.sha256(p.encode()).digest() for p in passwords]

# Function to hash passwords using GPU
def gpu_hash_passwords(passwords):
    # Convert passwords to tensor and move to GPU
    passwords_tensor = torch.tensor([list(p.encode()) for p in passwords]).cuda()
    # Create a tensor to store hashed passwords
    hashed = torch.zeros(passwords_tensor.size(0), 32, dtype=torch.uint8).cuda()
    # Hash each password
    for i in range(passwords_tensor.size(0)):
        h = hashlib.sha256(passwords_tensor[i].cpu().numpy().tobytes())
        hashed[i] = torch.tensor(list(h.digest()), dtype=torch.uint8).cuda()
    return hashed.cpu()

# Main function to run the comparison
def run_comparison(num_passwords=10000, password_length=10, runs=3):
    print(f"Hashing {num_passwords} passwords of length {password_length}")
    
    # Generate sample passwords
    passwords = [''.join(chr(ord('a') + i % 26) for i in range(password_length)) for _ in range(num_passwords)]
    
    cpu_times = []
    gpu_times = []

    # Run the comparison multiple times
    for i in range(runs):
        print(f"\nRun {i+1}/{runs}")
        
        # CPU hashing
        print("CPU Password Hashing:")
        print_cpu_memory()
        cpu_start = time.time()
        cpu_result = cpu_hash_passwords(passwords)
        cpu_end = time.time()
        cpu_time = cpu_end - cpu_start
        cpu_times.append(cpu_time)
        print(f"CPU Time: {cpu_time:.4f} seconds")
        print_cpu_memory()

        # GPU hashing (if available)
        if torch.cuda.is_available():
            print("\nGPU Password Hashing:")
            print_gpu_memory()
            torch.cuda.synchronize()
            gpu_start = time.time()
            gpu_result = gpu_hash_passwords(passwords)
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

# Run the comparison if this script is executed directly
if __name__ == "__main__":
    run_comparison()
