import streamlit as st
import random
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

# FastAPI setup
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameRequest(BaseModel):
    word_length: int

class GuessRequest(BaseModel):
    guess: str

# Word lists by length with descriptions
word_lists = {
    4: [
        {'word': 'deer', 'desc': 'A forest animal with antlers', 'category': 'Animal'},
        {'word': 'cake', 'desc': 'A sweet baked dessert', 'category': 'Food'},
        {'word': 'bike', 'desc': 'A two-wheeled vehicle', 'category': 'Transport'},
        {'word': 'moon', 'desc': 'Earth\'s natural satellite', 'category': 'Space'},
        {'word': 'tree', 'desc': 'A tall plant with a trunk', 'category': 'Nature'}
    ],
    5: [
        {'word': 'apple', 'desc': 'A round fruit, often red or green', 'category': 'Food'},
        {'word': 'house', 'desc': 'A building where people live', 'category': 'Building'},
        {'word': 'smile', 'desc': 'A happy facial expression', 'category': 'Expression'},
        {'word': 'river', 'desc': 'A natural flow of water', 'category': 'Nature'},
        {'word': 'stone', 'desc': 'A piece of rock', 'category': 'Nature'}
    ],
    6: [
        {'word': 'pencil', 'desc': 'A tool for writing or drawing', 'category': 'Object'},
        {'word': 'window', 'desc': 'An opening in a wall for light and air', 'category': 'Building'},
        {'word': 'forest', 'desc': 'A large area covered with trees', 'category': 'Nature'},
        {'word': 'circle', 'desc': 'A round shape with no corners', 'category': 'Shape'},
        {'word': 'bridge', 'desc': 'A structure for crossing rivers or valleys', 'category': 'Structure'}
    ],
    7: [
        {'word': 'rainbow', 'desc': 'A colorful arc in the sky after rain', 'category': 'Nature'},
        {'word': 'freedom', 'desc': 'The power or right to act, speak, or think', 'category': 'Abstract'},
        {'word': 'journey', 'desc': 'An act of traveling from one place to another', 'category': 'Travel'},
        {'word': 'picture', 'desc': 'A visual representation of something', 'category': 'Art'},
        {'word': 'village', 'desc': 'A small community or group of houses', 'category': 'Place'}
    ],
    8: [
        {'word': 'mountain', 'desc': 'A large natural elevation of the earth\'s surface', 'category': 'Nature'},
        {'word': 'computer', 'desc': 'An electronic device for storing and processing data', 'category': 'Technology'},
        {'word': 'building', 'desc': 'A structure with a roof and walls', 'category': 'Architecture'},
        {'word': 'sunshine', 'desc': 'The light and warmth received from the sun', 'category': 'Nature'},
        {'word': 'language', 'desc': 'A system of communication used by a particular community', 'category': 'Abstract'}
    ],
    9: [
        {'word': 'beautiful', 'desc': 'Pleasing the senses or mind aesthetically', 'category': 'Abstract'},
        {'word': 'adventure', 'desc': 'An unusual and exciting experience', 'category': 'Experience'},
        {'word': 'knowledge', 'desc': 'Information and skills acquired through experience or education', 'category': 'Abstract'},
        {'word': 'discovery', 'desc': 'The act of finding or learning something for the first time', 'category': 'Abstract'},
        {'word': 'treasure', 'desc': 'A quantity of precious metals, gems, or other valuable items', 'category': 'Object'}
    ],
    10: [
        {'word': 'friendship', 'desc': 'The emotions or conduct of friends', 'category': 'Abstract'},
        {'word': 'creativity', 'desc': 'The use of imagination or original ideas to create something', 'category': 'Abstract'},
        {'word': 'inspiration', 'desc': 'The process of being mentally stimulated to do or feel something', 'category': 'Abstract'},
        {'word': 'landscape', 'desc': 'All the visible features of an area of land', 'category': 'Nature'},
        {'word': 'generation', 'desc': 'All of the people born and living at about the same time', 'category': 'Abstract'}
    ]
}

word_associations = {
    'deer': ['mammal', 'hooves', 'graceful'],
    'cake': ['birthday', 'sweet', 'dessert'],
    'bike': ['wheels', 'pedal', 'ride'],
    'moon': ['night', 'sky', 'round'],
    'tree': ['leaves', 'branches', 'shade'],
    'apple': ['fruit', 'red', 'orchard'],
    'house': ['home', 'roof', 'family'],
    'smile': ['happy', 'face', 'joy'],
    'river': ['water', 'flow', 'stream'],
    'stone': ['rock', 'hard', 'solid']
    # Add associations for other words similarly
}

# Game state
game_state = {
    'word': '',
    'attempts': 5,
    'hint': '',
    'game_over': False,
    'correct_positions': []  # Add this line
}

def generate_hint(word_data):
    word = word_data['word']
    length = len(word)
    num_hints = min(2, length - 2)  # Reduced number of letter hints
    indices = random.sample(range(length), num_hints)
    letter_hints = [f"Letter '{word[i]}' at position {i+1}" for i in indices]
    
    # Get word associations and create additional hints
    associations = word_associations.get(word, ['no additional hints'])
    random.shuffle(associations)
    
    hints = {
        'letters': ', '.join(letter_hints),
        'description': f"Description: {word_data['desc']}",
        'associations': f"Think about: {', '.join(associations[:2])}",  # Show 2 random associations
        'length': f"Word length: {length} letters"
    }
    game_state['correct_positions'] = indices
    return hints

@app.post("/start_game")
async def start_game(request: GameRequest):
    word_length = request.word_length
    if word_length not in word_lists:
        return {"error": "Invalid word length"}
    
    word_data = random.choice(word_lists[word_length])
    game_state['word'] = word_data['word']
    game_state['attempts'] = 5
    game_state['hint'] = generate_hint(word_data)
    game_state['game_over'] = False
    
    return {
        "hint": game_state['hint'],
        "attempts": game_state['attempts'],
        "word_length": len(game_state['word']),
        "correct_positions": game_state['correct_positions']
    }

@app.post("/submit_guess")
async def submit_guess(request: GuessRequest):
    guess = request.guess.lower().strip()
    if game_state['game_over']:
        return {"message": "Game is over. Start a new game!", "attempts": game_state['attempts'], "game_over": True}
    
    if len(guess) != len(game_state['word']):
        return {"message": f"Guess must be {len(game_state['word'])} letters long!", "attempts": game_state['attempts'], "game_over": False}
    
    game_state['attempts'] -= 1
    if guess == game_state['word']:
        game_state['game_over'] = True
        return {"message": "Correct! You win!", "attempts": game_state['attempts'], "game_over": True}
    
    feedback = ""
    if not game_state['game_over']:
        # Add feedback about correct letters
        correct_letters = sum(1 for i, c in enumerate(guess) if c == game_state['word'][i])
        feedback = f"{correct_letters} letters in correct position"
    
    if game_state['attempts'] <= 0:
        game_state['game_over'] = True
        return {"message": f"Game over! The word was '{game_state['word']}'.", "attempts": game_state['attempts'], "game_over": True}
    
    return {
        "message": f"Incorrect guess. {feedback}. Try again!",
        "attempts": game_state['attempts'],
        "game_over": game_state['game_over']
    }

# Streamlit setup
def run_streamlit():
    st.set_page_config(page_title="Word Guessing Game", layout="centered")
    with open("./templates/index.html") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=800, scrolling=True)

# Run FastAPI in a separate thread
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="error")

if __name__ == "__main__":
    # Start FastAPI server in a thread
    threading.Thread(target=run_fastapi, daemon=True).start()
    # Run Streamlit
    run_streamlit()