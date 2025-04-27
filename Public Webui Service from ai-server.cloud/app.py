from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, g
from flask_sqlalchemy import SQLAlchemy
from models import ChatSession
import os
import requests
import uuid
import openai
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # This allows all origins, customize if needed
app = Flask(__name__)
import json

# API Configuration

# Your API keys
openai.api_key = "API Key here."

os.environ['GROQ_API_KEY'] = 'API Key here'
os.environ['XAI_API_KEY'] = 'API Key here'

from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

API_KEYS = {
    "ai21_j1-jumbo": "API Key Here",
    "codellama_34b": "API Key Here"
}

API_ENDPOINTS = {
    "ai21_j1-jumbo": "https://api.ai21.com/studio/v1/j2-jumbo/complete",
    "codellama_34b": "https://api.codellama.ai/some-endpoint"
}

api_keys = {
    'groq': os.environ.get('GROQ_API_KEY'),
    'grok': os.environ.get('XAI_API_KEY'),
    'ai21_j1-jumbo': "API Key Here",  # Use environment variables in production
    'cohere-gen': "API Key Here",  # Cohere API Key
    'ollama': None,
}

api_urls = {
    'groq': "https://api.groq.com/openai/v1/chat/completions",
    'grok': "https://api.x.ai/v1/chat/completions",
    'ai21_j1-jumbo': "https://api.ai21.com/studio/v1/chat/completions",
    'cohere-gen': "https://api.cohere.ai/v1/generate",  # Cohere endpoint for generation
    'ollama': "http://localhost:11434/api/chat"  
}
class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.count = 0

    def add(self, item):
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.size
        self.count = min(self.count + 1, self.size)

    def get_all(self):
        if self.count < self.size:
            return self.buffer[:self.count]
        return self.buffer[self.head:] + self.buffer[:self.head]

# Memory size for AI to remember past N messages
MEMORY_SIZE = 5
memory = CircularBuffer(size=MEMORY_SIZE)

@app.route('/')
def index():
    """Render the initial page with model selection."""
    return render_template('index.html', models=["groq", "grok"])

@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.json
    prompt = data.get("prompt")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response["data"][0]["url"]
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test')
def test_page():
    """Render the initial page with model selection."""
    return render_template('index2.html', models=["groq", "grok"])

@app.route('/o1')
def o1_page():
    """Render the initial page with model selection."""
    return render_template('o1.html', models=["groq", "grok"])

# Redirect HTTP to HTTPS
@app.before_request
def redirect_to_https():
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)

# Initialize the memory for AI21
ai21_memory = CircularBuffer(size=5)  # Memory size for past prompts/responses

def ask_ai21(prompt):
    # Add the new prompt to memory
    ai21_memory.add({"role": "user", "content": prompt})
    # Construct the conversation context using memory
    messages = ai21_memory.get_all()

    headers = {
        "Authorization": f"Bearer {api_keys['ai21_j1-jumbo']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "jamba-1.5-large",  # or use the model you're actually using
        "messages": messages,
        "documents": [],
        "tools": [],
        "n": 1,
        "max_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "stop": [],
        "response_format": {"type": "text"}
    }
    response = requests.post(api_urls['ai21_j1-jumbo'], headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        generated_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', "No response generated.")
        # Add the AI's response to memory
        ai21_memory.add({"role": "assistant", "content": generated_content})
        return generated_content
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None

def ask_codellama(prompt):
    # CodeLlama-specific function
    headers = {
        "Authorization": f"Bearer {API_KEYS['codellama_34b']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "maxTokens": 100,
        "temperature": 0.5
    }
    response = requests.post(API_ENDPOINTS['codellama_34b'], headers=headers, json=payload)
    response.raise_for_status()
    response_data = response.json()
    return response_data.get('completion', "No response generated.")

@app.route('/call-model', methods=['POST'])
def call_model():
    data = request.json
    model = data.get('model')
    question = data.get('question', "Hello! Can you answer this?")

    if model in ["groq", "grok"]:
        response = ask_groq_grok(model, question)
    elif model == "ai21_j1-jumbo":
        response = ask_ai21(question)
    elif model == "codellama_34b":
        response = ask_codellama(question)
    else:
        return jsonify({"error": "Invalid model selected"}), 400

    return jsonify({"response": response})

ollama_memory = CircularBuffer(size=5)

def ask_ollama(prompt):
    # Add the new prompt to memory
    ollama_memory.add({"role": "user", "content": prompt})
    # Construct the conversation context using memory
    messages = ollama_memory.get_all()

    # Prepare payload
    payload = {
        "model": "eramax/aura_v3:Q5",  # or use the model you're actually using with Ollama
        "messages": messages
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_urls['ollama'], json=payload, headers=headers)
        response.raise_for_status()
        
        # Process each line of the response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        # Add the AI's response to memory
        ollama_memory.add({"role": "assistant", "content": combined_response})
        return combined_response

    except requests.RequestException as e:
        print(f"Ollama error: {e}")
        return None

# Initialize the memory for Cohere
cohere_memory = CircularBuffer(size=5)  # Memory size for past prompts/responses

def ask_cohere(prompt):
    # Add the new prompt to memory
    cohere_memory.add(f"User: {prompt}")
    # Construct the conversation context using memory
    full_prompt = "\n".join(cohere_memory.get_all())

    headers = {
        "Authorization": f"Bearer {api_keys['cohere-gen']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "command-xlarge",  # Adjust to Cohere's model offerings
        "prompt": full_prompt,
        "max_tokens": 50,
        "temperature": 0.7,
        "stream": False
    }
    response = requests.post(api_urls['cohere-gen'], headers=headers, json=payload)
    if response.status_code == 200:
        generated_text = response.json().get("generations", [{}])[0].get("text", "No response text available.")
        # Add the AI's response to memory
        cohere_memory.add(f"AI: {generated_text}")
        return generated_text
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None


from flask import request, jsonify
import requests
from collections import deque

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Extract prompt and model from the JSON request
        data = request.json
        if not data or 'prompt' not in data or 'model' not in data:
            return jsonify({"error": "Missing prompt or model in request"}), 400
        
        user_prompt = data['prompt']
        model = data['model']

        # Check if the model is valid
        if model not in api_keys:
            return jsonify({"error": "Invalid model selected"}), 400

        # Handle specific models separately
        if model == 'cohere-gen':
            response = ask_cohere(user_prompt)
            if not response:
                return jsonify({"error": "Failed to generate response from Cohere."}), 500
            return jsonify({"response": response})
        
        elif model == 'ai21_j1-jumbo':
            response = ask_ai21(user_prompt)
            if not response:
                return jsonify({"error": "Failed to generate response from AI21."}), 500
            return jsonify({"response": response})
        
        elif model == 'ollama':
            response = ask_ollama(user_prompt)  # Changed 'prompt' to 'user_prompt'
            if not response:
                return jsonify({"error": "Failed to generate response from Ollama."}), 500
            return jsonify({"response": response})
        
        # For other models, use a generic approach
        memory.add({"role": "user", "content": user_prompt})
        memory_messages = memory.get_all()
        
        payload = {
            "messages": [{"role": "system", "content": "You are a helpful assistant."}] + memory_messages,
            "model": "llama-3.3-70b-specdec" if model == 'groq' else "grok-beta",
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_keys[model]}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        }

        response = requests.post(api_urls[model], headers=headers, json=payload)
        if response.status_code == 200:
            json_response = response.json()
            if 'choices' in json_response and json_response['choices']:
                message_content = json_response['choices'][0]['message']['content']
                memory.add({"role": "assistant", "content": message_content})
                return jsonify({"response": message_content})
            else:
                return jsonify({"error": "Unexpected response format from API"}), 500
        else:
            return jsonify({"error": f"API request failed with status code {response.status_code}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    # Paths to your SSL certificate and private key
    cert_file = 'SSL/certificate.crt'
    key_file = 'SSL/private.key'

    # Validate the existence of SSL files
    if not os.path.exists(cert_file):
        raise FileNotFoundError(f"Certificate file not found: {cert_file}")
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Private key file not found: {key_file}")


    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=('SSL/fullchain.pem', 'SSL/private.key')  # Use fullchain.pem here
    )
