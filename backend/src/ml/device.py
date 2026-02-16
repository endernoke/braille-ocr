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
