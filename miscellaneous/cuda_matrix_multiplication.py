"""
This script handles cuda matrix multiplication that performs numerical operations.
"""

import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import time

# CUDA kernel definition
cuda_code = """
#define TILE_SIZE 32

__global__ void matrix_mul(float *a, float *b, float *c, int N)
{
    __shared__ float s_a[TILE_SIZE][TILE_SIZE];
    __shared__ float s_b[TILE_SIZE][TILE_SIZE];
    
    int bx = blockIdx.x, by = blockIdx.y;
    int tx = threadIdx.x, ty = threadIdx.y;
    
    int row = by * TILE_SIZE + ty;
    int col = bx * TILE_SIZE + tx;
    
    float sum = 0.0f;
    
    for (int i = 0; i < (N + TILE_SIZE - 1) / TILE_SIZE; i++) {
        if (row < N && i * TILE_SIZE + tx < N)
            s_a[ty][tx] = a[row * N + i * TILE_SIZE + tx];
        else
            s_a[ty][tx] = 0.0f;
        
        if (col < N && i * TILE_SIZE + ty < N)
            s_b[ty][tx] = b[(i * TILE_SIZE + ty) * N + col];
        else
            s_b[ty][tx] = 0.0f;
        
        __syncthreads();
        
        for (int k = 0; k < TILE_SIZE; k++)
            sum += s_a[ty][k] * s_b[k][tx];
        
        __syncthreads();
    }
    
    if (row < N && col < N)
        c[row * N + col] = sum;
}
"""

# Compile the CUDA kernel
mod = SourceModule(cuda_code)
matrix_mul = mod.get_function("matrix_mul")

# CPU matrix multiplication function
def cpu_matrix_mul(a, b):
    """
    Cpu matrix mul based on a, b.
    """
    return np.dot(a, b)

# GPU matrix multiplication function
def gpu_matrix_mul(a, b, a_gpu, b_gpu, c_gpu):
    """
    Gpu matrix mul based on a, b, a gpu, b gpu, c gpu.
    """
    n = a.shape[0]
    c = np.zeros((n, n), dtype=np.float32)
    
    block_size = (32, 32, 1)
    grid_size = ((n + block_size[0] - 1) // block_size[0], (n + block_size[1] - 1) // block_size[1])
    
    matrix_mul(a_gpu, b_gpu, c_gpu, np.int32(n), block=block_size, grid=grid_size)
    
    cuda.memcpy_dtoh(c, c_gpu)
    return c

# Define matrix sizes to test
sizes = [128, 256, 512, 1024, 2048]
iterations = 10

# Warm-up GPU
dummy = np.random.rand(100, 100).astype(np.float32)
dummy_gpu = cuda.mem_alloc(dummy.nbytes)
cuda.memcpy_htod(dummy_gpu, dummy)
gpu_matrix_mul(dummy, dummy, dummy_gpu, dummy_gpu, dummy_gpu)

# Main loop for different matrix sizes
for n in sizes:
    print(f"\nMatrix size: {n}x{n}")
    
    # Generate random matrices
    a = np.random.rand(n, n).astype(np.float32)
    b = np.random.rand(n, n).astype(np.float32)
    
    # CPU multiplication
    cpu_times = []
    for _ in range(iterations):
        cpu_start = time.perf_counter()
        cpu_result = cpu_matrix_mul(a, b)
        cpu_times.append(time.perf_counter() - cpu_start)
    cpu_time = np.mean(cpu_times)
    print(f"CPU time: {cpu_time:.6f} seconds")
    
    # GPU multiplication
    a_gpu = cuda.mem_alloc(a.nbytes)
    b_gpu = cuda.mem_alloc(b.nbytes)
    c_gpu = cuda.mem_alloc(a.nbytes)
    
    transfer_times = []
    compute_times = []
    for _ in range(iterations):
        # Measure transfer time
        transfer_start = time.perf_counter()
        cuda.memcpy_htod(a_gpu, a)
        cuda.memcpy_htod(b_gpu, b)
        transfer_times.append(time.perf_counter() - transfer_start)
        
        # Measure compute time
        compute_start = time.perf_counter()
        gpu_result = gpu_matrix_mul(a, b, a_gpu, b_gpu, c_gpu)
        compute_times.append(time.perf_counter() - compute_start)
    
    # Calculate average times
    transfer_time = np.mean(transfer_times)
    compute_time = np.mean(compute_times)
    total_gpu_time = transfer_time + compute_time
    print(f"GPU transfer time: {transfer_time:.6f} seconds")
    print(f"GPU compute time: {compute_time:.6f} seconds")
    print(f"GPU total time: {total_gpu_time:.6f} seconds")
    
    # Verify results
    np.testing.assert_allclose(cpu_result, gpu_result, rtol=1e-3, atol=1e-3)
    print("Results match!")
    
    # Calculate and print speedup
    speedup = cpu_time / compute_time
    print(f"GPU compute speedup: {speedup:.2f}x")
    total_speedup = cpu_time / total_gpu_time
    print(f"GPU total speedup: {total_speedup:.2f}x")

print("\nAll tests completed successfully!")
