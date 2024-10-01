import os
import requests
import json
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Initialize Groq client
os.environ['GROQ_API_KEY'] = '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'
api_key = os.environ.get('GROQ_API_KEY')

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# Function to send email content to Groq's API for phishing detection
def get_groq_response(message):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": message  # Send the email content
            }
        ],
        "model": "llama3-8b-8192",  # Using the specified model
    }
    try:
        response = requests.post(groq_api_url, json=payload, headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')  # Landing page

# Route to handle phishing detection
@app.route('/detect-phishing', methods=['POST'])
def detect_phishing():
    email_content = request.form.get('email_content')
    
    # Send the email content to Groq for phishing detection
    ai_response = get_groq_response(email_content)
    
    # Simple logic to determine if the response indicates phishing
    if 'phishing' in ai_response.lower():
        result = 'This email appears to be a phishing attempt.'
    else:
        result = 'This email seems safe.'

    return jsonify({'result': result, 'ai_response': ai_response})

if __name__ == "__main__":
    app.run(port=5214, debug=True)
