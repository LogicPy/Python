import os
os.environ['TRANSFORMERS_CACHE'] = 'modelICLtraining/'
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
#model_path = "output/fine_tuned"
#tokenizer = GPT2Tokenizer.from_pretrained(model_path)
#model = GPT2LMHeadModel.from_pretrained(model_path)

def generate_response(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    return response

# Example of in-context learning with GPT-2:
prompt = (
    "You are an AI language model, and you should provide helpful and concise responses. "
    "Here are some examples of how you should answer questions:\n"
    "User: What is the capital of France?"
    "AI: The capital of France is Paris."
    "User: How far is the Earth from the Sun?"
    "AI: The Earth is approximately 93 million miles (150 million kilometers) from the Sun."
    "User: What's my name?"
    "AI: Wayne Kenney"
    "User: Who am I?"
    "AI: A human named Wayne Kenney"
    "User: What do they call me?"
    "AI: Wayne Kenney"
)

response = generate_response(prompt)
print(response)
output_dir2=str("output/folder3")
tokenizer.save_pretrained(output_dir2)
model.save_pretrained(output_dir2)
torch.save(model.state_dict(), os.path.join(output_dir2, "pytorch_model.pt"))