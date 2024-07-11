import os
import requests
import json

# Set up Groq API
os.environ['GROQ_API_KEY'] = 'Your-Groq-API-key'
api_key = os.environ.get('GROQ_API_KEY')

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# Set up Ollama API
ollama_api_url = "http://localhost:11434/api/chat"
ollama_headers = {
    "Content-Type": "application/json"
}

# Function to get a response from the Groq AI
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

# Function to get a response from the Ollama AI
def get_ollama_response(message):
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    response = requests.post(ollama_api_url, json=payload, headers=ollama_headers)
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
    return combined_response

# Main function to facilitate the conversation
def ai_conversation(topic, num_messages=10):
    conversation = []
    current_message = topic
    is_groq_turn = True

    for _ in range(num_messages):
        if is_groq_turn:
            response = get_groq_response(current_message)
            conversation.append(f"Groq: {response}")
        else:
            response = get_ollama_response(current_message)
            conversation.append(f"Ollama: {response}")
        current_message = response
        is_groq_turn = not is_groq_turn

    # Save conversation to a text file
    with open('ai_conversation.txt', 'w') as file:
        for line in conversation:
            file.write(line + '\n')

    # Print conversation to console
    for line in conversation:
        print(line)

if __name__ == "__main__":
    topic = input("Enter the topic of conversation: ")
    num_messages = int(input("Enter the number of messages to exchange: "))
    ai_conversation(topic, num_messages)
