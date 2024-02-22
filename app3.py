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
        font = ImageFont.truetype(font_path, 40)  # Use the downloaded font

        for detection in detections:
            top_left = tuple(map(int, detection[0][0]))
            bottom_right = tuple(map(int, detection[0][2]))
            text = detection[1]
            print(text)
            detected_language = detect_language_all_languages(text)
 
            if detected_language.name == 'Language.CHINESE':
                detected_language_iso = 'zh'
                print(detected_language_iso)
            if detected_language_iso == source_lang  :
                # translate:
                translated_text = translate_text(text, source_lang, target_lang)
            else:
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
