import os
import torch
from transformers import AutoTokenizer
import json
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
from transformers import LlamaForCausalLM, LlamaTokenizer
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

if not torch.cuda.is_available():
    print("CUDA is not available in the current environment. Please install PyTorch with CUDA support.")

def main():

    model_name = "huggyllama/llama-7b"

    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    #tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = LlamaForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
    model.cuda()

    # Local Model Address Training from Directory
    #model = GPTJForCausalLM.from_pretrained("E:/debian/pytorch_model.bin", torch_dtype=torch.float16).to("cuda")
    torch.cuda.empty_cache()

    train_file = "E:/Debian/dataset.txt"
    test_file = "E:/Debian/dataset.txt"

    # Check if CUDA is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Get the device

    # Create the generator with the specified seed
    generator = torch.Generator(device).manual_seed(seed)
    
    # Disable TF32 mode and enable device-side assertions
    torch.backends.cuda.matmul.allow_tf32 = False

    print('Using device:', device)

    # Create tensors on the device
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)

    # Create model on the device
    model = torch.nn.Linear(1000, 1000).to(device)

    # Run forward pass on the device
    output = model(x)

    # Calculate loss and backpropagate on the device
    criterion = torch.nn.MSELoss()
    loss = criterion(output, y)
    loss.backward()

    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=train_file,
        block_size=128,
    )

    test_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=test_file,
        block_size=128,
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False,
    )

    training_args = TrainingArguments(
        output_dir="/results",
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        eval_steps=400,
        save_steps=800,
        warmup_steps=500,
        prediction_loss_only=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=None,
    )

    trainer.train()
    trainer.save_model("./results")

    # Save the model as a .pt file
    torch.save(model.state_dict(), "model.pt")

if __name__ == "__main__":
    main()
