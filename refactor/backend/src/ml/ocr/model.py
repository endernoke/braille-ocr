"""OCR model architecture (stub)."""
import torch
import torch.nn as nn
from typing import Tuple


class OCRModel(nn.Module):
    """Stub OCR model for text detection and recognition.
    
    In production, this would be replaced with a real architecture like:
    - CRNN (CNN + RNN + CTC)
    - Transformer-based OCR
    - DBNet + CRNN pipeline
    """
    
    def __init__(self, num_classes: int = 95):
        """Initialize OCR model.
        
        Args:
            num_classes: Number of character classes (ASCII printable)
        """
        super().__init__()
        
        # Stub: simple CNN backbone
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        # Stub: detection head (outputs dummy bounding boxes)
        self.detection_head = nn.Linear(256, 4)  # x, y, w, h
        
        # Stub: recognition head (outputs dummy text)
        self.recognition_head = nn.Linear(256, num_classes)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass.
        
        Args:
            x: Input tensor [B, 3, H, W]
            
        Returns:
            boxes: Bounding box predictions [B, 4]
            logits: Character logits [B, num_classes]
        """
        features = self.backbone(x)
        features = features.squeeze(-1).squeeze(-1)  # [B, 256]
        
        boxes = self.detection_head(features)  # [B, 4]
        logits = self.recognition_head(features)  # [B, num_classes]
        
        return boxes, logits
