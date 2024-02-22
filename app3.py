import os
import requests
from flask import Flask, request, make_response, send_file
import easyocr
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

app = Flask(__name__)

# Initialize the EasyOCR reader
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height
    
# Function to ensure font is downloaded
def ensure_font_downloaded():
    font_path = "NotoSans-Thin.ttf"  # Font file name
    font_url = "https://noto-website-2.storage.googleapis.com/pkgs/NotoSans-unhinted.zip"  # URL to download font

    if not os.path.exists(font_path):
        # Download the font ZIP file
        print("Downloading font...")
        response = requests.get(font_url)
        zip_path = "NotoSans.zip"

        # Save the ZIP file
        with open(zip_path, "wb") as zip_file:
            zip_file.write(response.content)

        # Extract the font file
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(".")  # Extract all files to the current directory

        # Clean up ZIP file after extraction
        os.remove(zip_path)

    return font_path  # Return the path to the font file

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Ensure the font is downloaded
        font_path = ensure_font_downloaded()

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

            # Draw a semi-transparent rectangle behind text
            draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))
            # Re-calculate text position if needed
            text_width, text_height = textsize(text, font=font)
            text_x = top_left[0] + (bottom_right[0] - top_left[0] - text_width) / 2
            text_y = top_left[1] + (bottom_right[1] - top_left[1] - text_height) / 2
            # Draw the reversed and resized text
            draw.text((text_x, text_y), text, fill='black', font=font)

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
