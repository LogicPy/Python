import os
# Reset model download by changing the directory and delete it when finished to reset the training process!
os.environ['TRANSFORMERS_CACHE'] = os.getcwd() + '/modelbase/'

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch.optim as optim
import tkinter as tk
import platform
import sys

user_input = 2e-5
def get_input():
    global user_input
    user_input = input_entry.get()
    root.quit()

"""
GPT-2 Small: 117 million parameters
GPT-2 Medium: 345 million parameters
GPT-2 Large: 774 million parameters
GPT-2 XL: 1.5 billion parameters

model_name = "gpt2-xl"
"""
os_name = platform.system()
intcontrol = 0
def commandconsole():
    global intcontrol
    global os_name
    while(intcontrol == 0):
        cmd = input("Type command to start training! Type 'help' for training commands: ")
        if(cmd=="help"):
            print ("--- Commands ---\n\nlearningrate.value - Set the training value \ncompile - Compile the training\nexit - Self-explanatory I think...\n")
        elif cmd == "learningrate.value":

            if os_name == 'Linux':
                print("Running on Linux - Console-based input")

                user_input = int(input("Enter your learning rate value here (Default: 2e-5): ") or 2e-5)

            elif os_name == 'Windows':
                print("Running on Windows - GUI-based input")

                root = tk.Tk()
                input_label = tk.Label(root, text="Enter your ai's learning rate::")
                input_label.pack()

                input_entry = tk.Entry(root)
                input_entry.insert(0, "2e-5")  # Insert default text at the beginning
                input_entry.pack()

                submit_button = tk.Button(root, text="Submit", command=get_input)
                submit_button.pack()

                root.mainloop()
        elif(cmd == "exit"):
            sys.exit()

        elif(cmd =="compile"):
            intcontrol = 1
            break

        else:
            print ("Invalid command...")

commandconsole()

os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# Load pre-trained model and tokenizer
model_name = "gpt2-medium"  # Replace this with the desired model, e.g. "gpt2-medium", "gpt2-large", or "gpt2-xl"
config = GPT2Config.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name, config=config)
learning_rate = user_input
optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

# Check new model directory
os.path.isdir(os.getcwd() + '/modelbase/')

# Load dataset
train_file = "./alpaca-lora-main/templates/story_template2.json"  # Replace with the path to your training data
train_dataset = TextDataset(tokenizer=tokenizer, file_path=train_file, block_size=128)

# Initialize data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Set up training arguments
training_args = TrainingArguments(
    output_dir="output/folder2",
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

