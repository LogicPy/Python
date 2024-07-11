import requests
import json
import os

# Initialize Groq client
groq_api_key = 'API-Key'
os.environ['GROQ_API_KEY'] = groq_api_key

# Initialize OpenAI API key for GPT-4
openai_api_key = 'API-Key'

openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# Define the Ollama API endpoint and headers
ollama_url = "http://localhost:11434/api/chat"
ollama_headers = {
    "Content-Type": "application/json"
}

# Mock Groq response function for demonstration purposes

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
    response = requests.post(groq_api_url, json=payload, headers={"Authorization": f"Bearer {groq_api_key}"})
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def get_ollama_response(prompt):
    ollama_payload = {
        "model": "llama3",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(ollama_url, json=ollama_payload, headers=ollama_headers)
    response.raise_for_status()
    lines = response.text.strip().split('\n')
    combined_response = ""
    for line in lines:
        try:
            data = json.loads(line)
            if 'message' in data and 'content' in data['message']:
                combined_response += data['message']['content']
        except json.JSONDecodeError:
            continue
    return combined_response.strip()

def get_gpt4_response(prompt):
    openai_payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", json=openai_payload, headers=openai_headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def talk_to_ais(groq_initial_prompt, ollama_initial_prompt, gpt4_initial_prompt, num_messages):
    groq_response = get_groq_response(groq_initial_prompt)
    ollama_response = get_ollama_response(ollama_initial_prompt)
    gpt4_response = get_gpt4_response(gpt4_initial_prompt)

    conversation = [f"Groq: {groq_response}", f"Ollama: {ollama_response}", f"GPT-4: {gpt4_response}"]

    for _ in range(num_messages - 1):
        ollama_response = get_ollama_response(groq_response)
        gpt4_response = get_gpt4_response(ollama_response)
        groq_response = get_groq_response(gpt4_response)
        conversation.append(f"Groq: {groq_response}")
        conversation.append(f"Ollama: {ollama_response}")
        conversation.append(f"GPT-4: {gpt4_response}")

    return conversation

# Example usage
groq_initial_prompt = input("Enter the topic of conversation: ")
ollama_initial_prompt = groq_initial_prompt
gpt4_initial_prompt = groq_initial_prompt
num_messages = int(input("Enter the number of messages to exchange: "))

conversation = talk_to_ais(groq_initial_prompt, ollama_initial_prompt, gpt4_initial_prompt, num_messages)

for message in conversation:
    print(message)
