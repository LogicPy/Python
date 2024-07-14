import os
import requests
import json

# Initialize Groq client
os.environ['GROQ_API_KEY'] = 'Your API Key'
api_key = os.environ.get('GROQ_API_KEY')

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_response(message):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
        "model": "llama3-8b-8192",
    }
    response = requests.post(groq_api_url, json=payload, headers={"Authorization": f"Bearer {api_key}"})
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def converse_with_groq():
    while True:
        prompt = input("Enter your prompt: ")
        response = get_groq_response(prompt)
        print(f"Groq: {response}")

if __name__ == "__main__":
    converse_with_groq()
