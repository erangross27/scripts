"""
This script handles CUDA matrix multiplication using PyTorch.
"""

import numpy as np
import torch
import time

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# GPU matrix multiplication function using PyTorch
def gpu_matrix_mul(a, b):
    """
    GPU matrix multiplication using PyTorch and CUDA events for timing.
    """
    a_gpu = torch.from_numpy(a).to(device)
    b_gpu = torch.from_numpy(b).to(device)
    
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    
    start_event.record()
    c_gpu = torch.matmul(a_gpu, b_gpu)
    end_event.record()
    
    torch.cuda.synchronize()  # Wait for the events to be recorded!
    
    gpu_time = start_event.elapsed_time(end_event) / 1000  # Convert to seconds
    
    c = c_gpu.cpu().numpy()
    return c, gpu_time

# CPU matrix multiplication function
def cpu_matrix_mul(a, b):
    """
    CPU matrix multiplication using NumPy.
    """
    start_time = time.perf_counter()
    c = np.dot(a, b)
    cpu_time = time.perf_counter() - start_time
    return c, cpu_time

# Define matrix sizes to test
sizes = [128, 256, 512, 1024, 2048]
iterations = 10

# Main loop for different matrix sizes
for n in sizes:
    print(f"\nMatrix size: {n}x{n}")
    
    # Generate random matrices
    a = np.random.rand(n, n).astype(np.float32)
    b = np.random.rand(n, n).astype(np.float32)
    
    # CPU multiplication
    cpu_times = []
    for _ in range(iterations):
        cpu_result, cpu_time = cpu_matrix_mul(a, b)
        cpu_times.append(cpu_time)
    cpu_time = np.mean(cpu_times)
    print(f"CPU time: {cpu_time:.6f} seconds")
    
    # GPU multiplication
    if torch.cuda.is_available():
        gpu_times = []
        for _ in range(iterations):
            gpu_result, gpu_time = gpu_matrix_mul(a, b)
            gpu_times.append(gpu_time)
        gpu_time = np.mean(gpu_times)
        print(f"GPU time: {gpu_time:.6f} seconds")
        
        # Verify results
        np.testing.assert_allclose(cpu_result, gpu_result, rtol=1e-3, atol=1e-3)
        print("Results match!")
        
        # Calculate and print speedup
        speedup = cpu_time / gpu_time
        print(f"GPU compute speedup: {speedup:.2f}x")

print("\nAll tests completed successfully!")
