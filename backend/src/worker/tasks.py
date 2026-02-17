from typing import Dict, Any
from pathlib import Path

from PIL import Image
import numpy as np
from celery.app.task import Task

from .celery_app import celery_app
from ..ml.ocr import OCRInference
from ..ml.classifier import ClassifierInference
from ..braille import braille_backtranslator
from ..common.config import settings
from ..common.schemas import Language
from ..common import storage


# Global model instances (loaded once per worker process)
_ocr_model: OCRInference = None
_classifier_model: ClassifierInference = None

def get_ocr_model() -> OCRInference:
    """Get or load OCR model (lazy loading)."""
    global _ocr_model
    if _ocr_model is None:
        print("Loading OCR model...")
        _ocr_model = OCRInference("/app/models/ocr_model.pt")
    return _ocr_model


def get_classifier_model() -> ClassifierInference:
    """Get or load classifier model (lazy loading)."""
    global _classifier_model
    if _classifier_model is None:
        print("Loading classifier model...")
        _classifier_model = ClassifierInference("/app/models/classifier_model.pt")
    return _classifier_model


@celery_app.task(bind=True, name="process_image")
def process_image(self: Task, image_path: str, language: str = None) -> Dict[str, Any]:
    """Process an image through the full ML pipeline.
    
    Args:
        image_path: Path to uploaded image
        language: Optional language code (en-ueb-g1, en-ueb-g2, zh-hk). 
                  If provided, skips classification stage.
        
    Returns:
        Dictionary with results
    """
    try:        
        print(f"Processing image: {image_path}")
        if language:
            print(f"Language provided: {language} (skipping classification)")
        self.update_state(state="PROCESSING", meta={"step": "loading_image"})
        
        image = Image.open(image_path)
        print(f"Image loaded: {image.size} {image.mode}")
        
        self.update_state(state="PROCESSING", meta={"step": "ocr"})
        ocr_model = get_ocr_model()
        extracted_text, bounding_boxes, annotated_image = ocr_model.predict(np.array(image))
        text_length = len("\n".join(extracted_text))
        print(f"OCR complete: {text_length} chars")
        print(f"Extracted text (first 100 chars): {' '.join(extracted_text)[:100]}...")
        
        # Skip classification if language is provided
        if language:
            category = language
            confidence = 1.0  # 100% confidence since user provided it
            print(f"Using provided language: {category}")
        else:
            self.update_state(state="PROCESSING", meta={"step": "classification"})
            classifier_model = get_classifier_model()
            category, confidence = classifier_model.predict("".join(extracted_text))
            print(f"Classification: {category} (confidence: {confidence:.2f})")
        
        self.update_state(state="PROCESSING", meta={"step": "postprocessing"})
        processed_text = braille_backtranslator.backtranslate(extracted_text, lang=Language(category))
        print(f"Postprocessing complete")

        self.update_state(state="PROCESSING", meta={"step": "saving_results"})
        result_path = storage.save_result_image(Image.fromarray(annotated_image), self.request.id)
        
        result = {
            "extracted_text": processed_text,
            "classification": category,
            "confidence": confidence,
            "bounding_boxes": [dict(box) for box in bounding_boxes],
            "annotated_image_url": storage.get_result_url(result_path)
        }
        
        print(f"Processing complete for job {self.request.id}")
        return result
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise


# Worker startup event
@celery_app.task(bind=True)
def warmup_models(self):
    """Warmup task to preload models."""
    print("Warming up models...")
    get_ocr_model()
    get_classifier_model()
    print("Models ready!")
