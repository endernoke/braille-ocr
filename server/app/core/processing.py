import asyncio
from PIL import Image
import logging
from app.api.schemas import ImageProcessingResult
from typing import List

# Create a lock for the non-thread-safe image processing
image_processing_lock = asyncio.Lock()

async def process_braille_image(image: Image.Image, original_filename: str, lang: str) -> ImageProcessingResult:
    """
    1. OCR the image and extract braille text.
    2. Convert braille to print text using liblouis.
    """
    try:
        braille = recognize_braille(image)
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

import os
from pathlib import Path
from PIL import Image
import AngelinaReader.model.infer_retinanet as infer_retinanet
import louis
from typing import NewType, Optional, Literal
import re
import json
# from openai import OpenAI

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
            lambda braille_line: louis.backTranslateString(["braille-patterns.cti", "zh-hk.ctb"], braille_line),
            braille
        )))
        # jyutping = "\n".join(list(map(
        #     lambda braille_line: back_translate_zhhk(braille_line),
        #     braille
        # )))
        # back_translation = correct_homophones(back_translation)
    
    # Clean the transcribed text
    # The text might contain braille literals like \1/, \123/, etc.
    # which are results of untranslatable braille patterns
    # Remove these patterns
    cleaned_text = re.sub(r"\\(\d+)/", "", back_translation)
    return cleaned_text

def back_translate_zhhk(braille: str) -> str:
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
            else:  # Invalid character
                i += 1  # Skip invalid character
                pass
    return result


# def jyutping_to_text(jyutping: str) -> str:
#     client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="<OPENROUTER_API_KEY>",
#     )

#     completion = client.chat.completions.create(
#     extra_headers={
#         "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#         "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#     },
#     extra_body={},
#     model="google/gemini-2.0-flash-001",
#     messages=[
#         {
#         "role": "user",
#         "content": [
#             {
#             "type": "text",
#             "text": "What is in this image?"
#             },
#             {
#             "type": "image_url",
#             "image_url": {
#                 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#             }
#             }
#         ]
#         }
#     ]
#     )
#     print(completion.choices[0].message.content)