import requests
import json

# Dictionary to store user context
user_context = {}

def generate(user_id: str, prompt: str):
    # Retrieve the context for the user
    context = user_context.get(user_id, "")
    
    # Update the context with the new prompt
    context += f" User: {prompt}\n"
    
    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the JSON payload with context
    payload = {
        "model": "dolphin-llama3",
        "messages": [
            {
                "role": "system",
                "content": "You are a role-playing AI. You're my ai girlfriend. "
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }

    # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Print the response text for debugging
        print(response.text)
        
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

        # Update the context with the AI's response
        context += f" AI: {combined_response.strip()}\n"
        user_context[user_id] = context

        print(combined_response.strip())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")

if __name__ == "__main__":
    user_id = "default_user"  # In a real application, you might want to use a unique ID for each user
    while True:
        prompt = input("Enter your prompt: ")
        generate(user_id, prompt)
