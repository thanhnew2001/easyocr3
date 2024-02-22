from flask import send_file, Flask, request, make_response, after_this_request
import os
import easyocr
from PIL import Image, ImageDraw
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
        result = reader.readtext(np.array(image), detail=0)  # detail=0 for simpler output

        # Draw bounding boxes on the image
        draw = ImageDraw.Draw(image)
        for detection in reader.readtext(np.array(image)):
            top_left = tuple(detection[0][0])
            bottom_right = tuple(detection[0][2])
            text = detection[1]
            draw.rectangle([top_left, bottom_right], outline='red')
            draw.text(top_left, text, fill='red')

        # Convert the Image object back to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Go to the start of the BytesIO stream

        # Create response
        response = make_response(img_byte_arr.getvalue())
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='result.jpg')

        return response

if __name__ == '__main__':
    app.run(debug=True)
