import os
import requests
import json
from torch.nn import functional as F
import base64
import uuid 

from flask import Flask, request, jsonify, make_response, send_file, render_template, Response, send_from_directory
from flask_cors import CORS

import easyocr
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
from hf_hub_ctranslate2 import MultiLingualTranslatorCT2fromHfHub
from transformers import MarianMTModel, MarianTokenizer, AutoTokenizer
import torch
import time

app = Flask(__name__)

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define a mapping for directly supported language pairs
direct_model_mapping = {
    'en-vi': 'Eugenememe/netflix-en-vi',
    'en-es': 'Eugenememe/netflix-en-es-100k',
    'en-fr': 'Eugenememe/netflix-en-fr',
    'en-de': 'Eugenememe/netflix-en-de',
    'en-zh': 'Eugenememe/netflix-en-zh',

    'vi-en': 'Eugenememe/netflix-vi-en',
    'es-en': 'Eugenememe/netflix-es-en-100k',
    'fr-en': 'Eugenememe/netflix-fr-en',
    'de-en': 'Eugenememe/netflix-de-en',
    'zh-en': 'Eugenememe/netflix-zh-en',

    'ko-en': 'Eugenememe/netflix-ko-en',
    'th-en': 'Eugenememe/netflix-th-en',
    'ja-en': 'Eugenememe/netflix-ja-en',
    # Add other directly supported language pairs here...
}

# Supported languages for intermediate translation
#supported_langs = ['en', 'es', 'fr', 'it', 'de', 'zh', 'vi', 'ko', 'ja', 'th']
supported_langs = ['en', 'es', 'fr', 'de', 'zh', 'vi', 'ko', 'th', 'ja']

xtts_supported_langs = ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'ja', 'hu', 'ko']

HF_TOKEN = "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"
# Pre-load models and tokenizers
opus_models_tokenizers = {}
for model_name in direct_model_mapping.values():
    tokenizer_ = MarianTokenizer.from_pretrained(model_name, token= HF_TOKEN)
    model_ = MarianMTModel.from_pretrained(model_name, token= HF_TOKEN).to(device)
    opus_models_tokenizers[model_name] = (model_, tokenizer_)

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

def translate_with_timing(text, source_lang, target_lang):
    def perform_translation(text, model_name):
        start_time = time.time()
        model_, tokenizer_ = opus_models_tokenizers[model_name]
        tokenized_text = tokenizer_.prepare_seq2seq_batch([text], return_tensors='pt').to(device)
        translated = model_.generate(**tokenized_text)
        translated_text = tokenizer_.batch_decode(translated, skip_special_tokens=True)[0]
        end_time = time.time()
        return translated_text, end_time - start_time
    
    if f"{source_lang}-{target_lang}" in ["en-ko", "en-th", "en-ja"]:
        translated_text = translate_text(text, source_lang, target_lang)
        return translated_text

    if f"{source_lang}-{target_lang}" in direct_model_mapping:
        # Direct translation
        translated_text, time_taken = perform_translation(text, direct_model_mapping[f"{source_lang}-{target_lang}"])
        print(f"Direct translation time ({source_lang}-{target_lang}): {time_taken:.4f} seconds")
    elif source_lang in supported_langs and target_lang in supported_langs:
        # Two-step translation via English
        intermediate_text, time_taken_1 = perform_translation(text, direct_model_mapping[f"{source_lang}-en"])
        final_text, time_taken_2 = perform_translation(intermediate_text, direct_model_mapping[f"en-{target_lang}"])
        translated_text = final_text
        total_time_taken = time_taken_1 + time_taken_2
        print(f"2-step translation time ({source_lang}-en-{target_lang}): {total_time_taken:.4f} seconds")
    else:
        # use m2m instead
        # translated_text = translate_text(text, source_lang, target_lang)
        # raise ValueError(f"Unsupported language pair: {source_lang}-{target_lang}")
        translated_text = translate_text(text, source_lang, target_lang)
    return translated_text

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
            print(text)
                 # Assuming detect_language_all_languages returns an enum instance of Language
            detected_language = detect_language_all_languages(text)
            detected_language_iso = ''
            
            # Compare enum directly instead of converting to string for comparison
            detected_language_iso = language_to_iso(detected_language)
            
            # Check if the detected language ISO code matches the source language for translation
            if detected_language_iso == source_lang:
                # Translate the text from source_lang to target_lang
                
                translated_text = translate_with_timing(text, source_lang, target_lang)
            else:
                # If languages match or detection is unsure, keep the original text
                translated_text = text

            print(text + ': ' + translated_text)
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


@app.route('/upload_textonly', methods=['POST'])
def upload_textonly():
    source_lang = request.form.get('source_lang', 'en')  # Default source language
    target_lang = request.form.get('target_lang', 'es')  # Default target language

    # Initialize the EasyOCR reader with dynamic language support based on source language
    ocr_source_lang = 'ch_sim' if source_lang == 'zh' else source_lang
    reader = easyocr.Reader(['en', ocr_source_lang], gpu=True)

    # Check if files were uploaded
    files = request.files.getlist('file')
    if not files:
        return 'No files provided', 400

    # Prepare a list to hold results for all processed images
    results = []

    for file in files:
        if file:  # If a file is present
            image_bytes = file.read()
            image = Image.open(io.BytesIO(image_bytes))
            detections = reader.readtext(np.array(image), detail=1)

            # Process each detected piece of text
            text_results = []
            for detection in detections:
                original_text = detection[1]
                detected_language = detect_language_all_languages(original_text)
                detected_language_iso = language_to_iso(detected_language)

                if detected_language_iso == source_lang:
                    translated_text = translate_with_timing(original_text, source_lang, target_lang)
                else:
                    # If the detected language is the same as the target, keep original
                    translated_text = original_text

                text_results.append({
                    'original_text': original_text,
                    'translated_text': translated_text
                })

            # Add the file results to the overall results
            results.append({
                'file_name': file.filename,
                'texts': text_results
            })

    return jsonify(results)

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'GET':
        original_text = request.args.get('text', '')
        source_lang = request.args.get('source_lang', 'en')
        target_lang = request.args.get('target_lang', 'es')
    else:  # POST
        data = request.json
        original_text = data.get('text', '')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'es')

    translated_text = translate_with_timing(original_text, source_lang, target_lang)
    return jsonify({
        'original_text': original_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'translated_text': translated_text
    })


if __name__ == '__main__':
    app.run(debug=True)
