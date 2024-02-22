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
            # Extract the bounding box coordinates
            top_left = tuple(map(int, detection[0][0]))
            bottom_right = tuple(map(int, detection[0][2]))
        
            # Ensure we have the correct format for the coordinates
            # (i.e., ((x1, y1), (x2, y2)) for the top-left and bottom-right corners)
            box = [top_left, bottom_right]
        
            # Shade original text area: draw a rectangle over the detected area
            draw.rectangle(box, fill=(255, 255, 255, 128))  # Use the corrected 'box' variable
        

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
