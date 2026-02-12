from typing import Dict, Any
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .celery_app import celery_app
from ..ml.ocr import OCRInference, BoundingBox
from ..ml.classifier import ClassifierInference
from ..ml.postprocessing import get_postprocessor
from ..ml.device import print_device_info
from ..common.config import settings
from ..common import storage


# Global model instances (loaded once per worker process)
_ocr_model: OCRInference = None
_classifier_model: ClassifierInference = None


def get_ocr_model() -> OCRInference:
    """Get or load OCR model (lazy loading)."""
    global _ocr_model
    if _ocr_model is None:
        print("Loading OCR model...")
        _ocr_model = OCRInference(settings.ocr_model_path)
    return _ocr_model


def get_classifier_model() -> ClassifierInference:
    """Get or load classifier model (lazy loading)."""
    global _classifier_model
    if _classifier_model is None:
        print("Loading classifier model...")
        _classifier_model = ClassifierInference(settings.classifier_model_path)
    return _classifier_model


@celery_app.task(bind=True, name="process_image")
def process_image(self, image_path: str) -> Dict[str, Any]:
    """Process an image through the full ML pipeline.
    
    Pipeline:
    1. Load image
    2. Run OCR model (detect text + bounding boxes)
    3. Run classifier on extracted text
    4. Postprocess with C library
    5. Draw bounding boxes on image
    6. Save and return results
    
    Args:
        image_path: Path to uploaded image
        
    Returns:
        Dictionary with results
    """
    try:
        # Print device info on first task
        if not hasattr(process_image, "_device_printed"):
            print_device_info()
            process_image._device_printed = True
        
        print(f"Processing image: {image_path}")
        
        # Update status
        self.update_state(state="PROCESSING", meta={"step": "loading_image"})
        
        # 1. Load image
        image = Image.open(image_path)
        print(f"Image loaded: {image.size} {image.mode}")
        
        # 2. Run OCR
        self.update_state(state="PROCESSING", meta={"step": "ocr"})
        ocr_model = get_ocr_model()
        bounding_boxes, extracted_text = ocr_model.predict(image)
        print(f"OCR complete: {len(bounding_boxes)} boxes, {len(extracted_text)} chars")
        
        # 3. Run classifier
        self.update_state(state="PROCESSING", meta={"step": "classification"})
        classifier_model = get_classifier_model()
        category, confidence = classifier_model.predict(extracted_text)
        print(f"Classification: {category} (confidence: {confidence:.2f})")
        
        # 4. Postprocess with C library
        self.update_state(state="PROCESSING", meta={"step": "postprocessing"})
        postprocessor = get_postprocessor()
        processed_text = postprocessor.postprocess_text(extracted_text, category)
        print(f"Postprocessing complete")
        
        # 5. Draw bounding boxes on image
        self.update_state(state="PROCESSING", meta={"step": "annotation"})
        annotated_image = draw_bounding_boxes(image, bounding_boxes)
        
        # 6. Save result
        self.update_state(state="PROCESSING", meta={"step": "saving"})
        result_path = storage.save_result_image(annotated_image, self.request.id)
        result_url = storage.get_result_url(result_path)
        
        # Prepare result
        result = {
            "extracted_text": processed_text,
            "classification": category,
            "confidence": confidence,
            "bounding_boxes": [box.to_dict() for box in bounding_boxes],
            "annotated_image_url": result_url,
        }
        
        print(f"Processing complete for job {self.request.id}")
        return result
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        # Update state to FAILURE
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "type": type(e).__name__}
        )
        raise


def draw_bounding_boxes(
    image: Image.Image,
    boxes: list[BoundingBox],
    color: str = "red",
    width: int = 3,
) -> Image.Image:
    """Draw bounding boxes on image.
    
    Args:
        image: Input PIL Image
        boxes: List of bounding boxes
        color: Box color
        width: Line width
        
    Returns:
        Annotated image
    """
    # Create a copy
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw each box
    for box in boxes:
        # Draw rectangle
        x1, y1 = box.x, box.y
        x2, y2 = box.x + box.width, box.y + box.height
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
        
        # Draw text label
        text_label = f"{box.text[:20]}... ({box.confidence:.2f})"
        
        # Draw text background
        try:
            bbox = draw.textbbox((x1, y1 - 20), text_label, font=font)
            draw.rectangle(bbox, fill=color)
            draw.text((x1, y1 - 20), text_label, fill="white", font=font)
        except:
            # Fallback for older Pillow versions
            draw.text((x1, y1 - 20), text_label, fill=color, font=font)
    
    return annotated


# Worker startup event
@celery_app.task(bind=True)
def warmup_models(self):
    """Warmup task to preload models."""
    print("Warming up models...")
    get_ocr_model()
    get_classifier_model()
    get_postprocessor()
    print("Models ready!")
