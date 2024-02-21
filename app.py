
from flask import Flask, request, jsonify
import os
import re
import uuid  # for generating random directory names
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define the base path for saving uploaded images
BASE_UPLOAD_FOLDER = 'uploads'
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
app.config['BASE_UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER

# Define the path for models: no need

# Define the models
models = {
    'None-ResNet-None-CTC.pth': 'https://drive.google.com/uc?id=1FocnxQzFBIjDT2F9BkNUiLdo1cC3eaO0',
    'None-VGG-BiLSTM-CTC.pth': 'https://drive.google.com/uc?id=1GGC2IRYEMQviZhqQpbtpeTgHO_IXWetG',
    'None-VGG-None-CTC.pth': 'https://drive.google.com/uc?id=1FS3aZevvLiGF1PFBm5SkwvVcgI6hJWL9',
    'TPS-ResNet-BiLSTM-Attn-case-sensitive.pth': 'https://drive.google.com/uc?id=1ajONZOgiG9pEYsQ-eBmgkVbMDuHgPCaY',
    'TPS-ResNet-BiLSTM-Attn.pth': 'https://drive.google.com/uc?id=1b59rXuGGmKne1AuHnkgDzoYgKeETNMv9',
    'TPS-ResNet-BiLSTM-CTC.pth': 'https://drive.google.com/uc?id=1FocnxQzFBIjDT2F9BkNUiLdo1cC3eaO0',
}

# Download models if they don't already exist
for k, v in models.items():
    model_path = os.path.join('', k)
    if not os.path.exists(model_path):
        os.system(f'gdown -O {model_path} "{v}"')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    files = request.files.getlist('files')

    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No selected files'}), 400

    # Create a unique directory for this batch of uploads
    upload_dir = os.path.join(app.config['BASE_UPLOAD_FOLDER'], uuid.uuid4().hex)
    os.makedirs(upload_dir, exist_ok=True)

    # Assuming the language code is part of the form data
    language = request.form.get('language', 'english')  # Default to English if not provided

    if language == 'english':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif language == 'chinese':
        # Include your Chinese character set here
        character = '的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进样道理体知世什二期等十用'
    elif language == 'vietnamese':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
    elif language == 'spanish':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíñóúüÁÉÍÑÓÚÜ'
    elif language == 'italian':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàèéìíîòóùú'
    elif language == 'french':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàâçéèêëîïôûùüÿ'
    elif language == 'german':
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZäöüßÄÖÜ'
    elif language == 'thai':
        # Include a basic set of Thai characters; you might need to add more
        character = '0123456789กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอ'
    elif language == 'korean':
        # Include a basic set of Korean characters; you might need to extend this
        character = '0123456789가각간갇갈감갑강개객거건걸검겁게겨격결겸경계고곡곤골공과관광구국군굴권귀규균귤그극금급기긴길김끼나낙난날남납내녀년념녕노농뇌누눈뉴느늑는니다단달담답당'

    results = []

    character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    print(character)

    for file in files:
        if file:  # if file is not empty
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # Add your own conditions to select the model based on the language_code or other criteria
            model_path = "TPS-ResNet-BiLSTM-Attn.pth"

            # Run the model
            result = os.popen(f"CUDA_VISIBLE_DEVICES=0 python3 demo.py \
                    --Transformation TPS --FeatureExtraction ResNet --SequenceModeling BiLSTM --Prediction Attn \
                    --image_folder {upload_dir}/ --saved_model {model_path} --character '{character}'").read()


            # Extract recognized texts for the image
            recognized_labels = extract_predicted_labels(result)

            # Store the filename and the recognized texts as a pair
            results.append({'filename': filename, 'recognized_labels': recognized_labels})
            
            # Optionally remove the file after processing
            os.remove(file_path)

    # Optionally remove the upload directory after processing all files
    os.rmdir(upload_dir)
    
    results_data = {'results': results}
    results_ = filter_results(results_data)
    return jsonify(results_)
    

# Function to extract predicted labels from the recognized text
def extract_predicted_labels(recognized_text):
    # Split the text by lines
    lines = recognized_text.split('\n')
    # Initialize an empty list to hold the predicted labels
    predicted_labels = []
    # Regex pattern to match lines with predicted labels
    pattern = re.compile(r'\t([^\t]+)\t')
    # Start processing lines after the header part
    for line in lines:
        # Check if the line contains predicted label information
        match = pattern.search(line)
        if match:
            # Add the extracted label to the list
            predicted_labels.append(match.group(1).strip())
    return predicted_labels  # Return all labels

def filter_results(results_data):
    # Create a new list to hold the filtered results
    filtered_results = []

    # Iterate through each item in the original results list
    for item in results_data['results']:
        # Get the filename
        filename = item['filename']
        
        # Filter out 'predicted_labels' from the recognized_labels list
        recognized_labels = [label for label in item['recognized_labels'] if label != 'predicted_labels']
        
        # Append the filtered data to the new list
        filtered_results.append({'filename': filename, 'recognized_labels': recognized_labels})

    # Return the new list as part of a dictionary
    return {'results': filtered_results}
    
if __name__ == '__main__':
    app.run(debug=True)
