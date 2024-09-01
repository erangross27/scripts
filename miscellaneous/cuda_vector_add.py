import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import time

# CUDA kernel for vector addition
cuda_code = """
__global__ void vector_add(float *a, float *b, float *c, int n)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n)
        c[tid] = a[tid] + b[tid];
}
"""

# Compile the CUDA kernel
mod = SourceModule(cuda_code)

# Get the kernel function
vector_add = mod.get_function("vector_add")

# Set up the data
n = 1000000
print(f"Generating {n} random numbers for each vector...")
a = np.random.randn(n).astype(np.float32)
b = np.random.randn(n).astype(np.float32)
c = np.zeros_like(a)

# Print first few elements of input vectors
print("\nFirst 5 elements of vector a:")
print(a[:5])
print("\nFirst 5 elements of vector b:")
print(b[:5])

# Allocate memory on the GPU
a_gpu = cuda.mem_alloc(a.nbytes)
b_gpu = cuda.mem_alloc(b.nbytes)
c_gpu = cuda.mem_alloc(c.nbytes)

# Copy data to the GPU
cuda.memcpy_htod(a_gpu, a)
cuda.memcpy_htod(b_gpu, b)

# Set up the grid and block sizes
block_size = 256
grid_size = (n + block_size - 1) // block_size

print(f"\nLaunching CUDA kernel with grid size: {grid_size}, block size: {block_size}")

# Record the start time
start_time = time.time()

# Call the kernel function
vector_add(a_gpu, b_gpu, c_gpu, np.int32(n), block=(block_size, 1, 1), grid=(grid_size, 1))

# Record the end time
end_time = time.time()

# Copy the result back to the host
cuda.memcpy_dtoh(c, c_gpu)

# Calculate and print the execution time
execution_time = end_time - start_time
print(f"\nCUDA kernel execution time: {execution_time:.6f} seconds")

# Print first few elements of the result
print("\nFirst 5 elements of the result vector c:")
print(c[:5])

# Verify the result
print("\nVerifying the result...")
np.testing.assert_almost_equal(c, a + b)
print("Vector addition successful!")

# Calculate and print some statistics
max_diff = np.max(np.abs(c - (a + b)))
print(f"\nMaximum absolute difference: {max_diff}")
print(f"Mean of vector a: {np.mean(a):.6f}")
print(f"Mean of vector b: {np.mean(b):.6f}")
print(f"Mean of result vector c: {np.mean(c):.6f}")
