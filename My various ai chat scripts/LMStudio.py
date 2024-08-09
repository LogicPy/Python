import random
from openai import OpenAI

# Point to the local LM Studio server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Function to send a message to the model and get a response
def chat_with_model(user_input):
    # Create chat completion request
    completion = client.chat.completions.create(
        model="YourModelName",  # Replace with your actual model name from LM Studio
        messages=[
            {"role": "system", "content": "Always answer in rhymes."},  # Adjust system prompt as needed
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,  # Adjust temperature for creativity
        stream=True,  # Stream the response
    )

    # Display the assistant's reply letter by letter
# Assuming 'response' holds the AI's generated text

    # Modify the completion loop to prepend "Ai: " to the generated text
    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    # Prepend "Ai: " to the final response
    response_text = "Ai: " + response_text

    # Print the final formatted response
    print(response_text)


    # Print a newline to separate output
    print("\n")
    return response_text

# Main loop for user interaction
while True:
    # Get user input
    user_input = input("You: ")

    if user_input.lower() in ['exit', 'quit']:
        break

    # Chat with the model
    chat_with_model(user_input)
