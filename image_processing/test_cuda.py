"""
This script contains test cases for cuda.
"""

try:
    import torch
    print("PyTorch imported successfully")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
except Exception as e:
    print(f"An error occurred: {e}")

