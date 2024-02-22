from flask import Flask, request, make_response
import easyocr
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

app = Flask(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)  # Adjust gpu according to your setup

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Convert the Image file to an OpenCV image object
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Process the image
        detections = reader.readtext(np.array(image), detail=1)  # Keep detail to get bounding boxes

        # Prepare to draw on the image
        draw = ImageDraw.Draw(image)
        # Specify a larger font size
        font_size = 40
        font = ImageFont.truetype("arial.ttf", font_size)

        for detection in detections:
            top_left, top_right, bottom_right, bottom_left = detection[0]
            original_text = detection[1]  # Original detected text
            
            # Shade original text area: draw a rectangle over the detected area
            draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))  # Change fill as needed

            # Increase text size and draw reversed text
            text = original_text[::-1]  # Reverse the detected text
            # Calculate text position for center alignment if desired
            text_width, text_height = draw.textsize(text, font=font)
            text_x = top_left[0] + (bottom_right[0] - top_left[0] - text_width) / 2
            text_y = top_left[1] + (bottom_right[1] - top_left[1] - text_height) / 2
            # Draw the reversed and enlarged text
            draw.text((text_x, text_y), text, fill='black', font=font)

        # Convert the Image object back to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Go to the start of the BytesIO stream

        # Create response
        response = make_response(img_byte_arr.getvalue())
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='enhanced_result.jpg')

        return response

if __name__ == '__main__':
    app.run(debug=True)
