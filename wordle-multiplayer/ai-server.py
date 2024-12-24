from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_groq_word():
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Think of a five-letter word for Wordle."}
        ],
        model="llama3-8b-8192",
    )
    word = chat_completion.choices[0].message.content.strip()
    if len(word) == 5 and word.isalpha():  # Ensure it's valid
        return word.upper()
    return "APPLE"  # Fallback if the response is invalid

@app.route('/groq', methods=['POST'])
def groq_word_endpoint():
    word = get_groq_word()
    return jsonify({"word": word})

if __name__ == "__main__":
    app.run(port=5000)
