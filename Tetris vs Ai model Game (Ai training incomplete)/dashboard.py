import streamlit as st
import json
import matplotlib.pyplot as plt

st.title("Tetris AI Training Dashboard")

tetromino_types = ["I", "O", "T", "S", "Z", "J", "L"]

selected_piece = st.selectbox("Select Tetromino", tetromino_types)

with open(f"fitness_history_{selected_piece}.json", "r") as f:
    fitness_history = json.load(f)

generations = [entry["generation"] for entry in fitness_history]
best_fitness = [entry["best_fitness"] for entry in fitness_history]
average_fitness = [entry["average_fitness"] for entry in fitness_history]

fig, ax = plt.subplots()
ax.plot(generations, best_fitness, label='Best Fitness')
ax.plot(generations, average_fitness, label='Average Fitness')
ax.set_title(f'Fitness Over Generations for Tetromino {selected_piece}')
ax.set_xlabel('Generation')
ax.set_ylabel('Fitness')
ax.legend()
ax.grid(True)

st.pyplot(fig)
