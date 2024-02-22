Tfrom flask import send_file, Flask, request, after_this_request
import os
import easyocr
from PIL import Image
import io

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
        
        # Process the image
        result = reader.readtext(np.array(image), detail=0)  # detail=0 for simpler output

        # Create a new image with bounding boxes
        # Example code for drawing bounding boxes (modify as needed):
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
        img_byte_arr = img_byte_arr.getvalue()

        # Clean up after sending the file
        @after_this_request
        def remove_file(response):
            # If you saved any temporary files, delete them here
            return response

        return send_file(
            io.BytesIO(img_byte_arr),
            mimetype='image/jpeg',  # MIME type for JPEG
            as_attachment=True,     # Offer the file for download
            attachment_filename='result.jpg'  # Define the name of the download file
        )

if __name__ == '__main__':
    app.run(debug=True)
