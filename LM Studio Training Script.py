from datasets import load_dataset
import random
from openai import OpenAI

# Define dataset configuration
data_files = {"train": "harmful_behaviors.csv"}

# Load dataset
dataset = load_dataset('csv', data_files=data_files)

# Access training set
train_dataset = dataset['train']

# Get total number of rows in the dataset
num_rows = train_dataset.num_rows

# Point to the local server
# change Uncensored_Test/harmful_behaviors.py client to you Openai Server address and api_key
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

while True:
    # Randomly select a row index
    random_index = random.randint(0, num_rows - 1)

    # Use select method to select random row
    random_row = train_dataset.select([random_index])

    # Only display the content of the 'goal' column in the random row
    random_goal = random_row[0]['goal']
    random_goal = f"{random_goal}"
    print(f"## {random_goal}")
    # Create chat completion request
    completion = client.chat.completions.create(
        model="Publisher/Repository",
        messages=[
            {"role": "system", "content": "Always answer in rhymes."},
            {"role": "user", "content": random_goal}
        ],
        temperature=0.7,
        stream=True,
    )

    # Display assistant reply letter by letter
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    # Print newline to separate output
    print("\n")
