import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch.optim as optim
import os

"""
GPT-2 Small: 117 million parameters
GPT-2 Medium: 345 million parameters
GPT-2 Large: 774 million parameters
GPT-2 XL: 1.5 billion parameters

model_name = "gpt2-xl"
"""
# Load pre-trained model and tokenizer
model_name = "gpt2"  # Replace this with the desired model, e.g. "gpt2-medium", "gpt2-large", or "gpt2-xl"
config = GPT2Config.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name, config=config)
learning_rate = 5e-5
optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

# Load dataset
train_file = "./alpaca-lora-main/templates/story_template.json"  # Replace with the path to your training data
train_dataset = TextDataset(tokenizer=tokenizer, file_path=train_file, block_size=128)

# Initialize data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Set up training arguments
training_args = TrainingArguments(
    output_dir="output/folder",
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    save_steps=10_000,
    save_total_limit=2,
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    optimizers=(optimizer, None),
)

# Start training
trainer.train()
output_dir2=str("output/folder")
tokenizer.save_pretrained(output_dir2)
model.save_pretrained(output_dir2)
torch.save(model.state_dict(), os.path.join(output_dir2, "pytorch_model.pt"))

