# utils.py
import random

TETROMINOES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']

def get_random_tetromino():
    return random.choice(TETROMINOES)
