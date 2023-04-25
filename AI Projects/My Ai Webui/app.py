import os
import torch
from flask import Flask, render_template, request, jsonify, send_from_directory
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from flask import send_from_directory

# ...

app = Flask(__name__)

# Load the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Create an instance of the GPT-2 model
model_instance = GPT2LMHeadModel.from_pretrained('gpt2')

# Load the state dictionary from the .pt file
model_state_dict = torch.load('Models/GPT2-trained/pytorch_model.pt', map_location=torch.device('cpu'))

# Load the state dictionary into the model instance
model_instance.load_state_dict(model_state_dict)

# Put the model into evaluation mode
model_instance.eval()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    input_text = request.json['input_text']

    # Preprocess the input data
    input_tokens = preprocess(input_text, tokenizer)

    # Generate a response using the AI model
    with torch.no_grad():
        output_tensors = model_instance.generate(input_tokens, max_length=100)  # Increase the max_length value as needed


    # Postprocess the model's output
    response = postprocess(output_tensors, tokenizer)

    return jsonify({'response': response})

@app.route('/send_css/<path:path>')
def send_css(path):
    return send_from_directory('static', path)

def preprocess(input_data, tokenizer):
    tokens = tokenizer.encode(input_data, return_tensors='pt')
    return tokens

def postprocess(output_tensor, tokenizer):
    generated_text = tokenizer.decode(output_tensor[0], skip_special_tokens=True)
    return generated_text

if __name__ == '__main__':
    app.run(debug=True, port=5000)
