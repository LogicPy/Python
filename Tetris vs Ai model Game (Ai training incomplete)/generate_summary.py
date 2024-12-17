# generate_summary.py

import json
import os

# Define all tetromino shapes
TETROMINOES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]],
    "J": [[1, 0, 0],
          [1, 1, 1]],
    "L": [[0, 0, 1],
          [1, 1, 1]]
}

summary = {}

for piece_type in TETROMINOES.keys():
    fitness_history_file = f"fitness_history_{piece_type}.json"
    if not os.path.exists(fitness_history_file):
        print(f"No fitness history found for Tetromino {piece_type}. Skipping.")
        continue
    
    with open(fitness_history_file, "r") as f:
        fitness_history = json.load(f)
    
    best_fitness = max(entry["best_fitness"] for entry in fitness_history)
    average_fitness = sum(entry["average_fitness"] for entry in fitness_history if entry["average_fitness"] != -float('inf')) / len([entry for entry in fitness_history if entry["average_fitness"] != -float('inf')])
    
    summary[piece_type] = {
        "best_fitness": best_fitness,
        "average_fitness": average_fitness,
        "generations_trained": len(fitness_history)
    }

# Save the summary to a JSON file
with open("training_summary.json", "w") as f:
    json.dump(summary, f, indent=4)

print("Training summary saved as training_summary.json")
