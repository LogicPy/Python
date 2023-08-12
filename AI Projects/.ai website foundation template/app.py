from flask import Flask, render_template, request, jsonify
from gpt4all import GPT4All
model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    response = chat_response()
    return response

def chat_response():
    data = request.json
    user_message = data.get('message')
    user_status = data.get('status')

    # Preprocess the message
    processed_message = user_status + ": " + user_message

    # Send to AI for response
    ai_response = get_ai_response(processed_message)

    return jsonify({"reply": ai_response})

def get_ai_response(message):
    # Mocked for now, integrate with your AI model as needed
    if "unregistered:" in message:
        return " Please register for more features."
    else:
        messages = [{"role": "user", "content": message}]
        output = model.chat_completion(messages)
        return output

if __name__ == "__main__":
    app.run(debug=True)