from flask import Flask, request, make_response, send_file
import easyocr
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

app = Flask(__name__)

# Initialize the EasyOCR reader. Note: Adjust 'gpu=False' if you don't have GPU support.
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)

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

        # Process the image with EasyOCR
        detections = reader.readtext(np.array(image), detail=1)

        # Create a drawing context on the image
        draw = ImageDraw.Draw(image)
        # Adjust the path and size as needed for your environment
        font = ImageFont.truetype("arial.ttf", 40)

        for detection in detections:
            top_left = tuple(map(int, detection[0][0]))
            bottom_right = tuple(map(int, detection[0][2]))
            text = detection[1][::-1]  # Reverse the detected text

            # Draw a semi-transparent rectangle behind text
            draw.rectangle([top_left, bottom_right], fill=(255, 255, 255, 128))
            # Re-calculate text position if needed
            text_width, text_height = draw.textsize(text, font=font)
            text_x = top_left[0] + (bottom_right[0] - top_left[0] - text_width) / 2
            text_y = top_left[1] + (bottom_right[1] - top_left[1] - text_height) / 2
            # Draw the reversed and resized text
            draw.text((text_x, text_y), text, fill='black', font=font)

        # Save the modified image to a byte stream
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
