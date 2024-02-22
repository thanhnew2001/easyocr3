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
        # Convert the uploaded file to an image object
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Process the image
        detections = reader.readtext(np.array(image), detail=1)

        # Prepare to draw on the image
        draw = ImageDraw.Draw(image)
        # Specify a larger font size
        font_size = 40
        font = ImageFont.truetype("arial.ttf", font_size)

        for detection in detections:
            top_left, _, bottom_right, _ = detection[0]
            original_text = detection[1]

            # Shade original text area: draw a rectangle over the detected area
            draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))

            # Reverse the detected text and increase text size
            text = original_text[::-1]
            # Draw the reversed and enlarged text
            draw.text(top_left, text, fill='black', font=font)

        # Save the modified image to a byte stream
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Reset byte pointer to the start

        # Create and send the response
        response = make_response(img_byte_arr.getvalue())
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='enhanced_result.jpg')

        return response

if __name__ == '__main__':
    app.run(debug=True)
