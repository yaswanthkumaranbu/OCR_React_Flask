import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define a dictionary of food suggestions based on keywords
food_suggestions = {
    'tumor': {
        'morning': 'Include antioxidant-rich foods like berries and green tea.',
        'afternoon': 'Opt for a balanced meal with lean protein, vegetables, and whole grains.',
        'night': 'Consider a light, early dinner with vegetables and lean protein.'
    },
    'sugar': {
        'morning': 'Start the day with a high-fiber breakfast, like oatmeal with fruit.',
        'afternoon': 'Choose whole grains, lean proteins, and plenty of vegetables.',
        'night': 'Have a balanced dinner, but be mindful of portion sizes.'
    }
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    keywords = list(food_suggestions.keys())  # Get keywords from the 'food_suggestions' dictionary

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        text = pytesseract.image_to_string(img)

        # Initialize a list to store food suggestions
        food_suggestion_list = []

        # Check if keywords are found in the extracted text
        for keyword in keywords:
            if keyword.lower() in text.lower():  # Perform a case-insensitive search
                food_suggestion = food_suggestions[keyword]
                food_suggestion_list.append(food_suggestion)
        if(len(food_suggestion_list)==0):
           return jsonify({
            'text': "None",
            'found_keywords': "None",  # List of keywords present in the extracted text
            'food_suggestions': "None",
            'message': 'Image received successfully'
        })

        return jsonify({
            'text': text,
            'found_keywords': keywords,  # List of keywords present in the extracted text
            'food_suggestions': food_suggestion_list,
            'message': 'Image received successfully'
        })

    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    app.run(debug=True)
