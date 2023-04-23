import os
# Reset model download by changing the directory and delete it when finished to reset the training process!
os.environ['TRANSFORMERS_CACHE'] = os.getcwd() + '/modelbase2/'

import json
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch

# Set up the necessary parameters
model_name = "gpt2"
num_cycles = 100
data_files = ["./alpaca-lora-main/templates/story_template2.json"]  # Replace with your own JSON files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Define the training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=2,  # Adjust batch size according to your GPU memory
    save_steps=10_000,
    save_total_limit=2,
)

for cycle in range(num_cycles):
    print(f"Cycle {cycle + 1}/{num_cycles}")

    # Train the model with each dataset
    for data_file in data_files:
        print(f"Training with {data_file}")

        # Load dataset from JSON file
        with open(data_file, "r") as f:
            texts = json.load(f)

        # Prepare the dataset
        train_dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=data_file,
            block_size=128,
        )
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer, mlm=False,
        )

        # Initialize the Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
        )

        # Train the model
        trainer.train()

# Save the final model after all cycles
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
torch.save(model.state_dict(), os.path.join(output_dir, "model_final.pt"))

print("Training completed.")
