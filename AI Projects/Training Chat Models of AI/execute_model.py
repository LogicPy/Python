from transformers import GPT2Tokenizer, GPTNeoForCausalLM

model_name = "alpaca.pt"
tokenizer = GPT2Tokenizer.from_pretrained(model_name, ignore_mismatched_sizes=True)
model = GPTNeoForCausalLM.from_pretrained(model_name, ignore_mismatched_sizes=True)


def generate_text(prompt, max_length=50, num_return_sequences=1):
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    attention_mask = (input_ids != tokenizer.eos_token_id).float()

    generated_output = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_p=0.95,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id,  # Set pad_token_id to eos_token_id
        attention_mask=attention_mask,  # Pass attention_mask
    )
    generated_text = tokenizer.decode(generated_output[0], skip_special_tokens=True)
    return generated_text

prompt = "Write a story for me."
generated_text = generate_text(prompt)
print(generated_text)
