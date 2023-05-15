from flask import Flask, request, jsonify, render_template
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)

modelname = 'gpt2-medium'

tokenizer = GPT2Tokenizer.from_pretrained(modelname)
model = GPT2LMHeadModel.from_pretrained(modelname)

@app.route('/')
def home():
    return render_template('index2.html')  # Your HTML file should be named 'index.html' and placed in a folder named 'templates'.

@app.route('/api', methods=['POST'])
def respond():
    data = request.get_json()
    input_text = data['message']
    
    inputs = tokenizer.encode(input_text, return_tensors='pt')
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return jsonify({'message': text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
