import os
import requests
from flask import Flask, request, make_response, send_file
import easyocr
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
from hf_hub_ctranslate2 import MultiLingualTranslatorCT2fromHfHub
from transformers import AutoTokenizer


app = Flask(__name__)

# Transalte
model_m2m = MultiLingualTranslatorCT2fromHfHub(
    model_name_or_path="michaelfeil/ct2fast-m2m100_1.2B",
    device="cuda",
    compute_type="int8_float16",
    tokenizer=AutoTokenizer.from_pretrained("facebook/m2m100_1.2B")
)

def translate_text(sentences, src_lang, tgt_lang):
    outputs = model_m2m.generate([sentences], src_lang=[src_lang], tgt_lang=[tgt_lang])
    return outputs[0]

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

# from langdetect import detect

# def recognize_language(text):
#     try:
#         # Detect the language of the text
#         language = detect(text)
#         return language
#     except Exception as e:
#         return f"An error occurred: {str(e)}"

from lingua import LanguageDetectorBuilder, Language

# Function for language detection using all available languages in lingua-py
def detect_language_all_languages(text):
    # Build the language detector using all available languages
    detector = LanguageDetectorBuilder.from_all_languages().build()
    
    # Detect the language of the provided text
    detected_language = detector.detect_language_of(text)
    
    # Return the name of the detected language
    return detected_language

# Example usage
text = "languages are awesome"
detected_language = detect_language_all_languages(text)
print(f"The detected language is: {detected_language}")


# Example usage
text = "This is a sample sentence."
detected_language = detect_language_all_languages(text)
print(f"The detected language is: {detected_language}")

# Example usage
text = "一天"
detected_language = detect_language_all_languages(text)
print(f"The detected language is: {detected_language}")

# Test the function
text = "今"
detected_language = detect_language_all_languages(text)
print(f"The language of the text '{text}' is: {detected_language}")
text = "How are you today"
detected_language = detect_language_all_languages(text)
print(f"The language of the text '{text}' is: {detected_language}")

def language_to_iso(detected_language):
    language_iso_map = {
        Language.AFRIKAANS: 'af',
        Language.ALBANIAN: 'sq',
        Language.ARABIC: 'ar',
        Language.ARMENIAN: 'hy',
        Language.AZERBAIJANI: 'az',
        Language.BASQUE: 'eu',
        Language.BELARUSIAN: 'be',
        Language.BENGALI: 'bn',
        Language.BOKMAL: 'nb',
        Language.BOSNIAN: 'bs',
        Language.BULGARIAN: 'bg',
        Language.CATALAN: 'ca',
        Language.CHINESE: 'zh',
        Language.CROATIAN: 'hr',
        Language.CZECH: 'cs',
        Language.DANISH: 'da',
        Language.DUTCH: 'nl',
        Language.ENGLISH: 'en',
        Language.ESPERANTO: 'eo',
        Language.ESTONIAN: 'et',
        Language.FINNISH: 'fi',
        Language.FRENCH: 'fr',
        Language.GANDA: 'lg',
        Language.GEORGIAN: 'ka',
        Language.GERMAN: 'de',
        Language.GREEK: 'el',
        Language.GUJARATI: 'gu',
        Language.HEBREW: 'he',
        Language.HINDI: 'hi',
        Language.HUNGARIAN: 'hu',
        Language.ICELANDIC: 'is',
        Language.INDONESIAN: 'id',
        Language.IRISH: 'ga',
        Language.ITALIAN: 'it',
        Language.JAPANESE: 'ja',
        Language.KAZAKH: 'kk',
        Language.KOREAN: 'ko',
        Language.LATIN: 'la',
        Language.LATVIAN: 'lv',
        Language.LITHUANIAN: 'lt',
        Language.MACEDONIAN: 'mk',
        Language.MALAY: 'ms',
        Language.MAORI: 'mi',
        Language.MARATHI: 'mr',
        Language.MONGOLIAN: 'mn',
        Language.NYNORSK: 'nn',
        Language.PERSIAN: 'fa',
        Language.POLISH: 'pl',
        Language.PORTUGUESE: 'pt',
        Language.PUNJABI: 'pa',
        Language.ROMANIAN: 'ro',
        Language.RUSSIAN: 'ru',
        Language.SERBIAN: 'sr',
        Language.SHONA: 'sn',
        Language.SLOVAK: 'sk',
        Language.SLOVENE: 'sl',
        Language.SOMALI: 'so',
        Language.SOTHO: 'st',
        Language.SPANISH: 'es',
        Language.SWAHILI: 'sw',
        Language.SWEDISH: 'sv',
        Language.TAGALOG: 'tl',
        Language.TAMIL: 'ta',
        Language.TELUGU: 'te',
        Language.THAI: 'th',
        Language.TSONGA: 'ts',
        Language.TSWANA: 'tn',
        Language.TURKISH: 'tr',
        Language.UKRAINIAN: 'uk',
        Language.URDU: 'ur',
        Language.VIETNAMESE: 'vi',
        Language.WELSH: 'cy',
        Language.XHOSA: 'xh',
        Language.YORUBA: 'yo',
        Language.ZULU: 'zu',
    }
    return language_iso_map.get(detected_language, None)

# Example usage
detected_language = Language.CHINESE  # Simulate a detected language
detected_language_iso = language_to_iso(detected_language)
print(f"The ISO 639-1 code for the detected language is: {detected_language_iso}")

def fit_text_to_box(text, font_path, box_width, box_height):
    # Start with a large font size to scale down
    font_size = 100  
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = font.getsize(text)
    
def fit_text_to_box(text, font_path, box_width, box_height):
    font_size = 100  # Start with a large font size
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = font.getsize(text)  # Correct method call

    # Scale down font size until the text fits the box
    while text_width > box_width or text_height > box_height and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = font.getsize(text)

    return font
    
    # Decrease the font size until the text fits within the box
    while text_width > box_width or text_height > box_height:
        font_size -= 1  # Decrease the font size
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = font.getsize(text)
    
    return font


@app.route('/upload', methods=['POST'])
def upload_file():
    source_lang = request.form.get('source_lang', 'en')  # Default to English if no language is provided
    if source_lang == 'zh':
        ocr_source_lang = 'ch_sim'
    else:
        ocr_source_lang = source_lang
        
    target_lang = request.form.get('target_lang', 'es')  # Default to English if no language is provided

    # Initialize the EasyOCR reader. Only support 1 language as this is a translation
    languages = ['en',ocr_source_lang]
    reader = easyocr.Reader(languages, gpu=True)  # Adjust GPU according to your setup
 
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Ensure the font is downloaded
        font_path = "NotoSansSC-Regular.otf"  # Font file name

        # Convert the uploaded file to an image object
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Process the image with EasyOCR
        detections = reader.readtext(np.array(image), detail=1)

        # Create a drawing context on the image
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, 15)  # Use the downloaded font

        for detection in detections:
            top_left = tuple(map(int, detection[0][0]))
            bottom_right = tuple(map(int, detection[0][2]))
            text = detection[1]
            box_width, box_height = bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]

            font = fit_text_to_box(text, font_path, box_width, box_height)
    
            print(text)
                 # Assuming detect_language_all_languages returns an enum instance of Language
            detected_language = detect_language_all_languages(text)
            detected_language_iso = ''
            
            # Compare enum directly instead of converting to string for comparison
            detected_language_iso = language_to_iso(detected_language)
            
            # Check if the detected language ISO code matches the source language for translation
            if detected_language_iso == source_lang:
                # Translate the text from source_lang to target_lang
                translated_text = translate_text(text, source_lang, target_lang)
            else:
                # If languages match or detection is unsure, keep the original text
                translated_text = text


            print(translated_text)
            if translated_text != text:
                # Draw a semi-transparent rectangle behind text
                draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))
                # Re-calculate text position if needed
                text_width, text_height = textsize(text, font=font)
                text_x = top_left[0] + (bottom_right[0] - top_left[0] - text_width) / 2
                text_y = top_left[1] + (bottom_right[1] - top_left[1] - text_height) / 2
                # Draw the reversed and resized text
                draw.text((text_x, text_y), translated_text, fill='black', font=font)

        # Before saving the image, convert from RGBA to RGB if necessary
        if image.mode == 'RGBA':
            # Create a new background image in RGB mode with white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            # Paste the original image onto the background
            background.paste(image, mask=image.split()[3])  # 3 is the index of the alpha channel
            image = background  # Replace the original image with the background
        
        # Now save the image as JPEG
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Reset the stream position to the start
        
        # Create and send the response
        response = make_response(img_byte_arr.getvalue())
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='modified_result.jpg')
        return response

    return 'Something went wrong'

if __name__ == '__main__':
    app.run(debug=True)
