import requests

API_ENDPOINT = "https://waynecool.ngrok.app/api/chat"
API_KEY = "YOUR_SECRET_API_KEY"

def send_message_to_chatbot(message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"message": message}
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.text}"

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        response = send_message_to_chatbot(user_input)
        print(f"Bot: {response}")
