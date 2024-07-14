import requests
import json

# Initialize OpenAI API key for GPT-4
openai_api_key = 'Your API Key'

openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

def get_gpt4_response(prompt):
    openai_payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", json=openai_payload, headers=openai_headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def converse_with_gpt4():
    while True:
        prompt = input("Enter your prompt: ")
        response = get_gpt4_response(prompt)
        print(f"GPT-4: {response}")

if __name__ == "__main__":
    converse_with_gpt4()
