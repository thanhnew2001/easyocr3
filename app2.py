from flask import send_file, Flask, request, after_this_request
import os
import easyocr
from PIL import Image, ImageDraw
import io
import numpy as np  # Add this line

app = Flask(__name__)

# Ensure the reader is loaded once when the server starts
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
        
        # Process the image with EasyOCR
        # The result will include bounding boxes and text, adjust according to your needs
        result = reader.readtext(np.array(image), detail=0)  # Using numpy to convert PIL Image to numpy array

        # Create a new image with bounding boxes (if required)
        draw = ImageDraw.Draw(image)
        for detection in reader.readtext(np.array(image)):  # Convert image to numpy array again for EasyOCR
            top_left = tuple(detection[0][0])
            bottom_right = tuple(detection[0][2])
            text = detection[1]
            draw.rectangle([top_left, bottom_right], outline='red')
            draw.text(top_left, text, fill='red')

        # Convert the Image object back to bytes for response
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Clean up after sending the file
        @after_this_request
        def remove_file(response):
            return response

        return send_file(
            io.BytesIO(img_byte_arr),
            mimetype='image/jpeg',
            as_attachment=True,
            attachment_filename='result.jpg'
        )

if __name__ == '__main__':
    app.run(debug=True)
