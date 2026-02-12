from pathlib import Path
from typing import List, Tuple, Dict

import torch
from PIL import Image
import numpy as np

from .model import OCRModel
from .preprocessing import OCRPreprocessor
from ..device import get_device


class BoundingBox:
    """Bounding box with text content."""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 text: str, confidence: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.confidence = confidence
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "confidence": self.confidence,
        }


class OCRInference:
    """OCR inference engine."""
    
    def __init__(self, model_path: str):
        """Initialize inference engine.
        
        Args:
            model_path: Path to model weights
        """
        self.device = get_device()
        self.preprocessor = OCRPreprocessor()
        
        # Load model
        self.model = OCRModel()
        
        # In production, load actual weights:
        # self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        self.model.to(self.device)
        self.model.eval()
        
        print(f"OCR model loaded from {model_path}")
    
    @torch.no_grad()
    def predict(self, image: Image.Image) -> Tuple[List[BoundingBox], str]:
        """Run OCR on an image.
        
        Args:
            image: Input PIL Image
            
        Returns:
            bounding_boxes: List of detected text regions
            full_text: Concatenated text content
        """
        # Preprocess
        input_tensor = self.preprocessor(image).unsqueeze(0).to(self.device)
        
        # Run model (stub - returns dummy predictions)
        boxes, logits = self.model(input_tensor)
        
        # Post-process (stub - create dummy bounding boxes)
        bounding_boxes = self._create_stub_boxes(image.size)
        
        # Extract full text
        full_text = " ".join([box.text for box in bounding_boxes])
        
        return bounding_boxes, full_text
    
    def _create_stub_boxes(self, image_size: Tuple[int, int]) -> List[BoundingBox]:
        """Create stub bounding boxes for demonstration.
        
        Args:
            image_size: (width, height) of original image
            
        Returns:
            List of dummy bounding boxes
        """
        width, height = image_size
        
        # Stub: create some realistic-looking boxes
        boxes = [
            BoundingBox(
                x=0.1 * width,
                y=0.1 * height,
                width=0.3 * width,
                height=0.05 * height,
                text="Sample Text Line 1",
                confidence=0.95,
            ),
            BoundingBox(
                x=0.1 * width,
                y=0.2 * height,
                width=0.5 * width,
                height=0.05 * height,
                text="This is a stub OCR result",
                confidence=0.92,
            ),
            BoundingBox(
                x=0.1 * width,
                y=0.3 * height,
                width=0.4 * width,
                height=0.05 * height,
                text="Replace with real model",
                confidence=0.89,
            ),
        ]
        
        return boxes
