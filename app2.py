from flask import Flask, request, jsonify, send_file
import easyocr
import numpy as np
import cv2
import io

app = Flask(__name__)

# Initialize the EasyOCR reader
# Note: This is a heavy operation, so do this only once and keep it outside of your request handling
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # Set gpu=False if you are using CPU

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Read the image file
        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)

        # Use EasyOCR to read text
        results = reader.readtext(image)

        # Draw the bounding boxes on the image
        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        # Convert the image with bounding boxes back into a file
        _, encoded_image = cv2.imencode('.jpg', image)
        image_bytes = io.BytesIO(encoded_image)

        return send_file(image_bytes, attachment_filename='result.jpg', mimetype='image/jpg')

if __name__ == '__main__':
    app.run(debug=True)
