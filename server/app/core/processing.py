import asyncio
import logging
from app.api.schemas import ImageProcessingResult
from typing import List
import time
import cv2
import numpy as np
import os
from pathlib import Path
import louis
from typing import NewType, Optional, Literal
import re
import json
import jyutping2characters


from app.core.inference import yolo_inference

jyutping2characters.ensure_data_available()

# Create a lock for the non-thread-safe image processing
image_processing_lock = asyncio.Lock()

async def process_braille_image(image: np.ndarray, original_filename: str, lang: str) -> ImageProcessingResult:
    """
    1. OCR the image and extract braille text.
    2. Convert braille to print text using liblouis.
    """
    try:
        braille = yolo_inference(image)
        text = None
        print("language: ", lang)
        if braille is not None:
            text = braille_to_text(braille, lang=lang)
            braille = "\n".join(braille)
        
        return ImageProcessingResult(
            original_filename=original_filename,
            recognized_braille=braille,
            recognized_text=text
        )
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise

    
def correct_homophones(text: str) -> str:
    """
    Correct homophones in Cantonese text.
    """
    # Placeholder for actual homophone correction logic
    # This could involve a dictionary lookup or a more complex NLP model
    return text

def braille_to_text(braille: List[str], lang: Literal["EN", "ZH-HK"]) -> str:
    """
    Convert braille to text
    """
    back_translation = ""
    if lang == "EN":
        back_translation = "\n".join(list(map(
            lambda braille_line: louis.backTranslateString(["en-ueb-g2.ctb"], braille_line),
            braille
        )))
        # Clean the transcribed text
        # The text might contain braille literals like \1/, \123/, etc.
        # which are results of untranslatable braille patterns
        # Remove these patterns
        cleaned_text = re.sub(r"\\(\d+)/", "", back_translation)
        return cleaned_text

    elif lang == "ZH-HK":
        jyutping = "\n".join(list(map(
            lambda braille_line: back_translate_zhhk(braille_line),
            braille
        )))
        back_translation = correct_homophones(jyutping)
        return back_translation
    
def back_translate_zhhk(braille: str) -> str:
    print("received", braille)
    chars_map = json.load(open(os.path.join(Path(__file__).parent, "braille_chars_mapping.json"), "r"))
    # Convert braille to ascii
    braille = "".join([chars_map[char] for char in braille])
    
    dict_map = json.load(open(os.path.join(Path(__file__).parent, "zhhk_braille_jyutping_mapping.json"), "r"))
    i = 0
    result = ""
    while i < len(braille):
        # standalone
        if (braille[i] in dict_map["standalone_long"]
            and i+1 < len(braille)
            and braille[i+1] in dict_map["tones_long"] 
        ):
            result += dict_map["standalone_long"][braille[i]] + dict_map["tones_long"][braille[i+1]] + " "
            i += 2
        elif (braille[i] in dict_map["standalone_short"]
            and i+1 < len(braille)
            and braille[i+1] in dict_map["tones_short"] 
        ):
            result += dict_map["standalone_short"][braille[i]] + dict_map["tones_short"][braille[i+1]] + " "
            i += 2
        elif braille[i] in dict_map["initials"]:
            if i+1 < len(braille) and braille[i+1] in dict_map["finals_long"]:
                if i+2 < len(braille) and braille[i+2] in dict_map["tones_long"]:
                    result += dict_map["initials"][braille[i]] + dict_map["finals_long"][braille[i+1]] + dict_map["tones_long"][braille[i+2]] + " "
                    i += 3
                else:  # no tone specified, tone = 1
                    result += dict_map["initials"][braille[i]] + dict_map["finals_long"][braille[i+1]] + "1 "
                    i += 2
            elif i+1 < len(braille) and braille[i+1] in dict_map["finals_short"]:
                if i+2 < len(braille) and braille[i+2] in dict_map["tones_short"]:
                    result += dict_map["initials"][braille[i]] + dict_map["finals_short"][braille[i+1]] + dict_map["tones_short"][braille[i+2]] + " "
                    i += 3
                else:  # no tone specified, tone = 1
                    result += dict_map["initials"][braille[i]] + dict_map["finals_short"][braille[i+1]] + "1 "
                    i += 2
            else:
                # Invalid
                i += 1  # skip invalid character
                pass
        else:  # punctuation or invalid character
            if braille[i] == "-":
                result += "，"
                i += 1
            elif braille[i] == "~":
                result += "、"
                i += 1
            elif braille[i] == "=" and i+1 < len(braille) and braille[i+1] == " ":
                result += "。"
                i += 1
            elif braille[i] == "(":
                result += "（"
                i += 1
            elif braille[i] == "}":
                result += "）"
                i += 1
            else:  # Invalid character
                i += 1  # Skip invalid character
                pass
    print("result", result)

    def split_and_rejoin_with_processing(text_string, process_func, sep_pattern: str):
        split_pattern = f"({sep_pattern})"
        try:
            split_parts = re.split(split_pattern, text_string)
        except:
            print("here")
            raise

        processed_parts = []
        for part in split_parts:
            if part is None:
                # re.split can sometimes return None for non-matching groups,
                # though less common with simple alternation patterns.
                continue
            
            if re.fullmatch(split_pattern, part):
                processed_parts.append(part)  # It's a delimiter, keep it as is
            else:
                processed_parts.append(process_func(part))  # It's a data part, apply the function

        return "".join(processed_parts)

    characters = split_and_rejoin_with_processing(result.replace(" ", ""), jyutping2characters.transcribe, '[，、。；！？「」…（）\\(\\)]|[\u2800-\u28FF]')
    print(characters)
    return characters


