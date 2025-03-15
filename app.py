import os
import base64
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io


API_KEY = os.getenv("API")
# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API key
genai.configure(api_key=API_KEY)

def chat_with_gemini(prompt):
    """Handles text-based chat functionality."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if response.text else "No response received."

def encode_image(image_path):
    """Encodes the image in base64 format for Gemini API."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def process_image(image_path, prompt="Describe the image."):
    """Processes the image using Gemini API and returns a response, then deletes the image."""
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Convert image to base64
    encoded_image = encode_image(image_path)

    # Create input content with image + prompt
    input_content = {
        "parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}
        ]
    }

    # Generate response
    response = model.generate_content(input_content)
    result = response.text if response.text else "No response received."

    # Delete the image after processing
    os.remove(image_path)
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    text = request.form['text']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save uploaded file
    image_path = os.path.join("uploads", file.filename)
    file.save(image_path)
    
    # Process image
    response_text = process_image(image_path,text)
    
    return jsonify({'response': response_text})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message']
    response_text = chat_with_gemini(user_message)
    
    return jsonify({'response': response_text})

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
