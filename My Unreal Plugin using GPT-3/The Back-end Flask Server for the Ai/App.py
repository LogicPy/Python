from flask import Flask, request, jsonify, render_template
from gpt4all import GPT4All
from collections import deque
from transformers import GPTJModel, GPTJConfig
from transformers import AutoTokenizer, GPTJModel

app = Flask(__name__)

gptj = GPT4All("ggml-gpt4all-j-v1.3-groovy")

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/api', methods=['POST'])
def respond():
    data = request.get_json()
    input_text = data['message']

    # Create messages list for chat_completion
    messages = [{"role": "user", "content": input_text}]

    text = gptj.chat_completion(messages)
    print(request.data)
    return jsonify({'message': text})


@app.route('/your_endpoint', methods=['GET'])
def handle_get():
    # Process the GET request...
    return 'Response content'

@app.route('/api', methods=['POST'])
def handle_post():
    try:
        data = request.get_json()
        message = data['message']

        # Add the new message to the history
        history.append(message)

        # Join the messages in the history into a single string
        context = ' '.join(history)

        # Create messages list for chat_completion
        messages = [{"role": "user", "content": message}]

        text = gptj.chat_completion(messages)
        print(request.data)
        return jsonify({'message': text})
    except Exception as e:
        # Log the error here
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)