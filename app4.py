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

# Translate
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
    im = Image.new(mode="P", size=(10, 10))  # Small image for text size measurement
    draw = ImageDraw.Draw(im)
    return draw.textsize(text, font=font)

from lingua import LanguageDetectorBuilder, Language

def detect_language_all_languages(text):
    detector = LanguageDetectorBuilder.from_all_languages().build()
    detected_language = detector.detect_language_of(text)
    return detected_language

def language_to_iso(detected_language):
    language_iso_map = {
        # Mapping from Language Enum to ISO Language Codes
        # Add all necessary language conversions here
    }
    return language_iso_map.get(detected_language, None)

@app.route('/upload', methods=['POST'])
def upload_file():
    source_lang = request.form.get('source_lang', 'en')
    target_lang = request.form.get('target_lang', 'es')

    reader = easyocr.Reader(['en', source_lang], gpu=True)  # Adjust GPU according to your setup
 
    file = request.files.get('file')
    if file and file.filename:
        font_path = "NotoSansSC-Regular.otf"  # Ensure this path is correct
        image = Image.open(io.BytesIO(file.read()))
        detections = reader.readtext(np.array(image), detail=1)

        draw = ImageDraw.Draw(image)
        # Start with a default font size
        default_font_size = 15  # You might need to adjust this default size
        font = ImageFont.truetype(font_path, default_font_size)

        for detection in detections:
            top_left, bottom_right = tuple(detection[0][0]), tuple(detection[0][2])
            original_text = detection[1]
            detected_language = detect_language_all_languages(original_text)
            detected_language_iso = language_to_iso(detected_language)

            if detected_language_iso == source_lang:
                translated_text = translate_text(original_text, source_lang, target_lang)
            else:
                translated_text = original_text

            # Calculate original and new text sizes
            original_text_size = textsize(original_text, font)
            font_size = default_font_size
            translated_text_size = textsize(translated_text, ImageFont.truetype(font_path, font_size))

            # Adjust font size to match the original text size
            while translated_text_size[0] > original_text_size[0] and font_size > 1:
                font_size -= 1  # Decrease font size by 1
                translated_text_size = textsize(translated_text, ImageFont.truetype(font_path, font_size))

            # Use the adjusted font size for the translated text
            font = ImageFont.truetype(font_path, font_size)
            draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))
            draw.text(top_left, translated_text, fill='black', font=font)

        # Save the image as a byte array
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        response = make_response(img_byte_arr.getvalue())
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='translated_result.jpg')
        return response
    return 'No file selected or file has no name'

if __name__ == '__main__':
    app.run(debug=True)
