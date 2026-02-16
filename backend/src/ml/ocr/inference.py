from ultralytics import YOLO
from PIL import Image
import json
from .model import CustomYOLO
import torch
import numpy as np
import cv2
from dataclasses import dataclass
from .postprocess import boxes_to_lines, lines_to_text, Line, LineChar
import time
import uuid
import os
import numpy as np

from ...common.schemas import BoundingBox

class OCRInference:
    def __init__(self, model_path: str):
        self.model = CustomYOLO(model_path)
    
    def predict(self, image: np.ndarray) -> tuple[list[str], list[BoundingBox], np.ndarray]:
        """
        Returns:
            (list of text lines, list of bounding boxes, image with drawn boxes)
        """
        result = self.model.predict(
            image,
            conf=0.25,
            iou=0.01,
            imgsz=1024,
            rect=True,
            max_det=99999,
            visualize=False,
            augment=False,
            save=False,
            verbose=False,
        )[0].cpu()

        boxes = [self.process_box(b) for b in result.boxes]
        labels = [int(b.cls.item()) for b in result.boxes]

        lines: list[Line] = boxes_to_lines(boxes, labels, "georgian")
        str_lines = []
        for line in lines:
            line_str = ""
            for char in line.chars:
                char: LineChar
                line_str += chr(0x2800) * char.spaces_before
                line_str += self.braille_char_from_classl(char.label)
            str_lines.append(line_str)
        for box in result.boxes:
            xyxy = box.xyxy
            if isinstance(xyxy, torch.Tensor):
                xyxy = xyxy.detach().cpu().squeeze().numpy()
            p1, p2 = np.split(xyxy.round().astype(int), 2)
            cv2.rectangle(image, p1, p2, (0, 0, 128), 2)
            cv2.putText(image, str(int(box.cls.cpu().item())), p1, cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 128), 2, cv2.LINE_AA)

        bounding_boxes: list[BoundingBox] = [
            self.convert_to_bounding_box(box) for box in result.boxes
        ]

        return str_lines, bounding_boxes, image

    def process_box(self, box):
        xyxy = box.xyxy
        if isinstance(xyxy, torch.Tensor):
            xyxy = xyxy.detach().cpu().squeeze().numpy()
        return xyxy.tolist()
    
    def convert_to_bounding_box(self, box) -> BoundingBox:
        xyxyn = box.xyxyn
        if isinstance(xyxyn, torch.Tensor):
            xyxyn = xyxyn.detach().cpu().squeeze().numpy()
        p1, p2 = np.split(xyxyn.astype(float), 2)
        label = str(int(box.cls.cpu().item()))
        conf = float(box.conf.cpu().item())
        return BoundingBox(
            x=float(p1[0]),
            y=float(p1[1]),
            width=float(p2[0] - p1[0]),
            height=float(p2[1] - p1[1]),
            text=label,
            confidence=conf,
        )

    def braille_char_from_classl(self, cls):
        cls += 1
        codepoint = 0x2800
        for p in range(6):
            codepoint += ((cls >> p) & 1) << p
        return chr(codepoint)
