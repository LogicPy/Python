
import gpt4all as ga
from datasets import load_dataset, concatenate_datasets
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer, AutoTokenizer

# Load your datasets
dataset1 = load_dataset('schooly/Cyber-Security-Breaches')
dataset2 = load_dataset('zeroshot/cybersecurity-corpus')
#dataset3 = load_dataset('squad')

# Concatenate datasets
combined_dataset = concatenate_datasets([dataset1["train"], dataset2["train"]])

# Load tokenizer and model
model_name = "lmsys/vicuna-7b-v1.3"
tokenizer = AutoTokenizer.from_pretrained(model_name, add_special_tokens = False)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Tokenize your datasets
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_datasets = combined_dataset.map(tokenize_function, batched=True)

# Define training arguments and initialize trainer
training_args = TrainingArguments(
    per_device_train_batch_size=8,
    num_train_epochs=1,  # Adjust as needed
    logging_dir="./logs",
    logging_steps=500,  # Adjust as needed
    save_steps=5000,  # Adjust as needed
    output_dir="./results",
    save_total_limit=2,
    push_to_hub=False,  # Set to True if you want to push model checkpoints to the Hugging Face Hub
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
)

# Train the model
trainer.train()
