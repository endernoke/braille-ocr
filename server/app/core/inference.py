from ultralytics import YOLO
from PIL import Image
import json
from app.core.temp import CustomYOLO
import torch
import numpy as np
import cv2
from dataclasses import dataclass
from app.core.postprocess import boxes_to_lines, lines_to_text, Line, LineChar
import time
import uuid
import os
import numpy as np

model = CustomYOLO("model.pt")

def process_box(box):
    xyxy = box.xyxy
    if isinstance(xyxy, torch.Tensor):
        xyxy = xyxy.detach().cpu().squeeze().numpy()
    return xyxy.tolist()

def braille_char_from_classl(cls):
    cls += 1
    codepoint = 0x2800
    for p in range(6):
        codepoint += ((cls >> p) & 1) << p
    return chr(codepoint)

def yolo_inference(image: np.ndarray) -> list[str]:
    result = model.predict(
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


    boxes = [process_box(b) for b in result.boxes]
    labels = [int(b.cls.item()) for b in result.boxes]

    lines: list[Line] = boxes_to_lines(boxes, labels, "georgian")
    str_lines = []
    for line in lines:
        line_str = ""
        for char in line.chars:
            char: LineChar
            line_str += chr(0x2800) * char.spaces_before
            line_str += braille_char_from_classl(char.label)
        str_lines.append(line_str)
    for box in result.boxes:
        xyxy = box.xyxy
        if isinstance(xyxy, torch.Tensor):
            xyxy = xyxy.detach().cpu().squeeze().numpy()
        p1, p2 = np.split(xyxy.round().astype(int), 2)
        cv2.rectangle(image, p1, p2, (0, 0, 128), 2)
        cv2.putText(image, str(int(box.cls.cpu().item())), p1, cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 128), 2, cv2.LINE_AA)
    if not os.path.exists("results"):
        os.makedirs("results", exist_ok=True)
    cv2.imwrite(f"results/{int(time.time())}-{uuid.uuid4()}.jpg", image)

    return str_lines

