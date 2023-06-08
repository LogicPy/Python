from transformers import GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

# Load pre-trained model and tokenizer
model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Prepare dataset for fine-tuning
file_path = 'your_dataset.txt'
dataset = TextDataset(
    tokenizer=tokenizer,
    file_path=file_path,
    block_size=128,
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False,
)

# Set up training arguments
training_args = TrainingArguments(
    output_dir="./gpt2_finetuned", #The output directory
    overwrite_output_dir=True, #overwrite the content of the output directory
    num_train_epochs=1, # number of training epochs
    per_device_train_batch_size=1, # batch size for training
    save_steps=10_000, # after # steps model is saved 
    save_total_limit=2, # the total amount of checkpoints. Deletes the older checkpoints.
)

# Initialize Trainer and start training
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)

trainer.train()
