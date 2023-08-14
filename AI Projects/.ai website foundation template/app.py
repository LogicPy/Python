from flask import Flask, render_template, request, jsonify, abort
from gpt4all import GPT4All

model = GPT4All("ggml-gpt4all-j-v1.3-groovy.bin")
app = Flask(__name__)

# This is just a sample API key for demonstration.
# In a real-world scenario, you'd probably store this in a more secure manner, like environment variables.
VALID_API_KEY = "YOUR_SECRET_API_KEY"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Here, we get the JSON data from the request.
    data = request.json

    user_message = data.get('message', "")
    user_status = data.get('status', "unregistered")

    processed_message = user_status + ": " + user_message

    # Send to AI for response
    ai_response = get_ai_response(processed_message)

    return jsonify({"reply": ai_response})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    api_key = request.headers.get('Authorization')

    if not api_key or api_key != f"Bearer {VALID_API_KEY}":
        abort(401, description="Invalid API key")

    data = request.json
    user_message = data.get("message", "")
    
    # Here, integrate your Unreal Chatbot to get a response
    bot_response = "Hello from the External Python-connected Chatbot!"  # Placeholder response
    
    return jsonify({"response": bot_response})

def get_ai_response(message):
    if "unregistered:" in message:
        return " Please register for more features."
    else:
        messages = [{"role": "user", "content": message}]
        output = model.chat_completion(messages)
        return output

if __name__ == "__main__":
    app.run(debug=True)
