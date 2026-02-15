from typing import Literal
import os
from pathlib import Path
import json
import re

from jyutping2characters import JyutpingTranscriber
import louis

class BrailleBacktranslator:
    def __init__(self):
        # Let it throw FileNotFound errors as normal
        with open(Path(__file__).parent / "braille_chars.json", "r") as f:
            self.braille_chars_map = json.load(f)
        with open(Path(__file__).parent / "zhhk_braille_jyutping.json", "r") as f:
            self.zhhk_braille_jyutping_map = json.load(f)
        self.jyutping2characters = JyutpingTranscriber.from_file(os.getenv("JYUTPING_CHARACTERS_DATA_PATH"))
        
    def backtranslate(self, braille: list[str], lang: Literal["en-us-g2", "zh-hk"]) -> str:
        """
        Convert braille to text
        """
        # NOTE: English grade 1 is treated as grade 2 as well since grade 2 is (mostly) a superset of grade 1
        if lang == "en-ueb-g2":
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

        elif lang == "zh-hk":
            back_translation = "\n".join(list(map(
                lambda braille_line: self.backtranslate_zhhk(braille_line),
                braille
            )))
            return back_translation
        else:
            raise ValueError(f"Unsupported language: {lang}")
        
    def braille_to_jyutping(self, braille: str) -> str:
        # Convert braille to ascii
        braille = "".join([self.braille_chars_map[char] for char in braille])
        
        i = 0
        result = ""
        while i < len(braille):
            # standalone
            if (braille[i] in self.zhhk_braille_jyutping_map["standalone_long"]
                and i+1 < len(braille)
                and braille[i+1] in self.zhhk_braille_jyutping_map["tones_long"] 
            ):
                result += self.zhhk_braille_jyutping_map["standalone_long"][braille[i]] + self.zhhk_braille_jyutping_map["tones_long"][braille[i+1]] + " "
                i += 2
            elif (braille[i] in self.zhhk_braille_jyutping_map["standalone_short"]
                and i+1 < len(braille)
                and braille[i+1] in self.zhhk_braille_jyutping_map["tones_short"] 
            ):
                result += self.zhhk_braille_jyutping_map["standalone_short"][braille[i]] + self.zhhk_braille_jyutping_map["tones_short"][braille[i+1]] + " "
                i += 2
            elif braille[i] in self.zhhk_braille_jyutping_map["initials"]:
                if i+1 < len(braille) and braille[i+1] in self.zhhk_braille_jyutping_map["finals_long"]:
                    if i+2 < len(braille) and braille[i+2] in self.zhhk_braille_jyutping_map["tones_long"]:
                        result += self.zhhk_braille_jyutping_map["initials"][braille[i]] + self.zhhk_braille_jyutping_map["finals_long"][braille[i+1]] + self.zhhk_braille_jyutping_map["tones_long"][braille[i+2]] + " "
                        i += 3
                    else:  # no tone specified, tone = 1
                        result += self.zhhk_braille_jyutping_map["initials"][braille[i]] + self.zhhk_braille_jyutping_map["finals_long"][braille[i+1]] + "1 "
                        i += 2
                elif i+1 < len(braille) and braille[i+1] in self.zhhk_braille_jyutping_map["finals_short"]:
                    if i+2 < len(braille) and braille[i+2] in self.zhhk_braille_jyutping_map["tones_short"]:
                        result += self.zhhk_braille_jyutping_map["initials"][braille[i]] + self.zhhk_braille_jyutping_map["finals_short"][braille[i+1]] + self.zhhk_braille_jyutping_map["tones_short"][braille[i+2]] + " "
                        i += 3
                    else:  # no tone specified, tone = 1
                        result += self.zhhk_braille_jyutping_map["initials"][braille[i]] + self.zhhk_braille_jyutping_map["finals_short"][braille[i+1]] + "1 "
                        i += 2
                else:
                    i += 1 # skip invalid character
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
        return result

    def backtranslate_zhhk(self, braille: str) -> str:
        jyutping = self.braille_to_jyutping(braille)
        print(f"Backtranslated jyutping: {jyutping}")
        characters = self.split_and_rejoin_with_processing(jyutping.replace(" ", ""), self.jyutping2characters.transcribe, '[，、。；！？「」…（）\\(\\)]|[\u2800-\u28FF]')
        print(f"Converted to characters: {characters}")
        return characters

    def split_and_rejoin_with_processing(self, text_string, process_func, sep_pattern: str):
        """
        Split the input text_string using the provided sep_pattern, apply process_func to the non-delimiter parts, and rejoin everything together.

        Args:            text_string (str): The input string to process.
            process_func (callable): A function that takes a string and returns a processed string. This will be applied to the non-delimiter parts of the text.
            sep_pattern (str): A regex pattern that matches the delimiters in the text. The function will split the text using this pattern, and the delimiters will be preserved in the output.
        Returns:
            str: The processed string with non-delimiter parts transformed by process_func and delimiters preserved.
        """
        split_pattern = f"({sep_pattern})"
        split_parts = re.split(split_pattern, text_string)
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


braille_backtranslator = BrailleBacktranslator()