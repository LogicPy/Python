import openai

# Replace <your_api_key> with your actual API key
api_key = "Your API Key here"
openai.api_key = api_key

# Set the model you want to use, e.g., "text-davinci-003" for GPT-3.5
model_name = "text-davinci-003"

prompt = input("Ask a question: ")

response = openai.Completion.create(
    engine=model_name,
    prompt=prompt,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=0.5,
)

print(response.choices[0].text.strip())
