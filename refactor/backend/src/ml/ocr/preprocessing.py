"""Preprocessing utilities for OCR."""
from typing import Tuple

import torch
from torchvision import transforms
from PIL import Image
import numpy as np


class OCRPreprocessor:
    """Preprocessing pipeline for OCR model input."""
    
    def __init__(self, target_size: Tuple[int, int] = (640, 640)):
        """Initialize preprocessor.
        
        Args:
            target_size: Target (height, width) for input images
        """
        self.target_size = target_size
        self.transform = transforms.Compose([
            transforms.Resize(target_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])
    
    def __call__(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model input.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed tensor [C, H, W]
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Apply transforms
        tensor = self.transform(image)
        
        return tensor
    
    def preprocess_batch(self, images: list[Image.Image]) -> torch.Tensor:
        """Preprocess a batch of images.
        
        Args:
            images: List of PIL Images
            
        Returns:
            Batched tensor [B, C, H, W]
        """
        tensors = [self(img) for img in images]
        return torch.stack(tensors)
