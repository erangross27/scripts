import numpy as np
import torch

def main():
    """
    Vector addition using PyTorch CUDA tensors and timing with torch.cuda.Event.
    """
    # 1. Initialize data on the host (CPU)
    N = 1_000_000
    A = torch.arange(N, dtype=torch.float32)
    B = torch.arange(N, dtype=torch.float32) * 2

    # 2. Move data to the device (GPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    d_A = A.to(device)
    d_B = B.to(device)

    # 3. Prepare CUDA events for timing
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    # 4. Launch the vector addition and time it
    print("Launching CUDA vector addition with PyTorch...")
    start_event.record()
    d_C = d_A + d_B
    end_event.record()

    # Wait for the events to be recorded
    torch.cuda.synchronize()

    # 5. Copy result back to the host
    C = d_C.cpu().numpy()
    print("Vector addition complete.")

    # 6. Verification
    print(f"First 5 elements of A: {A[:5].numpy()}")
    print(f"First 5 elements of B: {B[:5].numpy()}")
    print(f"Result (A + B)[:5]:    {C[:5]}")

    expected = (A + B).numpy()
    if np.allclose(C, expected):
        print("\nResult is correct!")
    else:
        print("\nResult is INCORRECT!")

    # 7. Print timing
    elapsed_ms = start_event.elapsed_time(end_event)
    print(f"\nCUDA vector addition took {elapsed_ms:.3f} ms.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nPlease ensure your CUDA toolkit, NVIDIA drivers, and PyTorch are installed correctly.")
        print("If issues persist, consider using a more widely supported Python version like 3.11 or 3.12, as Python 3.13 is very new.")
