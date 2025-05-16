import asyncio
from PIL import Image
import logging
from app.api.schemas import ImageProcessingResult
from typing import List

# Create a lock for the non-thread-safe image processing
image_processing_lock = asyncio.Lock()

async def process_braille_image(image: Image.Image, original_filename: str) -> ImageProcessingResult:
    """
    1. OCR the image and extract braille text.
    2. Convert braille to print text using liblouis.
    """
    try:
        braille = recognize_braille(image)
        text = None
        if braille is not None:
            text = braille_to_text(braille, lang="EN")
            braille = "\n".join(braille)
        
        return ImageProcessingResult(
            original_filename=original_filename,
            recognized_braille=braille,
            recognized_text=text
        )
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise

import os
from pathlib import Path
from PIL import Image
import AngelinaReader.model.infer_retinanet as infer_retinanet
import louis
from typing import NewType, Optional, Literal
import re

ANGELINA_READER_DIR = os.path.normpath(os.path.join(__file__, "..", "..", "..", "AngelinaReader"))

recognizer = infer_retinanet.BrailleInference(
    params_fn=os.path.join(ANGELINA_READER_DIR, 'weights', 'param.txt'),
    model_weights_fn=os.path.join(ANGELINA_READER_DIR, 'weights', 'model.t7'),
    create_script=None
)

def recognize_braille(
    input_image: Image.Image,
) -> List[str] | None:
    result_dict = recognizer.run(
        input_image,
        lang="EN",  # Language isn't important here, as we are only using AngelinaReader for the braille
        draw_refined=recognizer.DRAW_NONE,
        find_orientation=False,
        process_2_sides=False,
        align_results=True,
        repeat_on_aligned=False,
    )
    
    if result_dict is None:
        return None
    return result_dict['braille']

def correct_homophones(text: str) -> str:
    """
    Correct homophones in Cantonese text.
    """
    # Placeholder for actual homophone correction logic
    # This could involve a dictionary lookup or a more complex NLP model
    return text

def braille_to_text(braille: List[str], lang: Literal["EN", "ZH-HK"]) -> str:
    """
    Convert braille to text using liblouis.
    """
    back_translation = ""
    if lang == "EN":
        back_translation = "\n".join(list(map(
            lambda braille_line: louis.backTranslateString(["en-ueb-g2.ctb"], braille_line),
            braille
        )))
    elif lang == "ZH-HK":
        back_translation = "\n".join(list(map(
            lambda braille_line: louis.backTranslateString(["zh-hk.ctb"], braille_line),
            braille
        )))
        back_translation = correct_homophones(back_translation)
    
    # Clean the transcribed text
    # The text might contain braille literals like \1/, \123/, etc.
    # which are results of untranslatable braille patterns
    # Remove these patterns
    cleaned_text = re.sub(r"\\(\d+)/", "", back_translation)
    return cleaned_text