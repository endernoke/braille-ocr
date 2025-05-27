import os
import json
from pathlib import Path

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
                i += 1
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
                i += 1
                pass
    return result

if __name__ == "__main__":
    # Test the function
    braille = "⠅⠸⠾⠲⠤⠛⠕⠠⠞⠧⠈⠋⠕⠓⠻⠄⠆⠄⠏⠓⠁⠭⠣⠈⠿⠀⠎⠢⠄⠋⠫⠓⠣⠎⠸⠊⠠⠗⠢⠄⠄⠄⠄⠿⠿"
    print(back_translate_zhhk(braille))