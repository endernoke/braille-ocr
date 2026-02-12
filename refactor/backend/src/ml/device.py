import torch
from typing import Literal

from ..common.config import settings


DeviceType = Literal["cuda", "cpu"]


def get_device() -> torch.device:
    """Get the compute device (GPU if available, else CPU).
    
    Returns:
        torch.device: Selected device
    """
    if settings.device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        device = torch.device("cpu")
        print("Using CPU")
    
    return device


def print_device_info():
    """Print detailed device information."""
    device = get_device()
    print(f"\nDevice: {device}")
    
    if device.type == "cuda":
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"PyTorch version: {torch.__version__}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"\nGPU {i}: {props.name}")
            print(f"  Memory: {props.total_memory / 1e9:.2f} GB")
            print(f"  Compute Capability: {props.major}.{props.minor}")
    else:
        print("CPU Information:")
        print(f"  PyTorch version: {torch.__version__}")
