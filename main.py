import streamlit as st
import random

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
    return hints

def new_game(word_length):
    if word_length not in word_lists:
        st.session_state.error = "Invalid word length"
        return
    
    word_data = random.choice(word_lists[word_length])
    st.session_state.word = word_data['word']
    st.session_state.attempts = 5
    st.session_state.hint = generate_hint(word_data)
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.correct_letters = 0

def submit_guess():
    guess = st.session_state.guess.lower().strip()
    if st.session_state.game_over:
        st.session_state.message = "Game is over. Start a new game!"
        return
    
    if len(guess) != len(st.session_state.word):
        st.session_state.message = f"Guess must be {len(st.session_state.word)} letters long!"
        return
    
    st.session_state.attempts -= 1
    if guess == st.session_state.word:
        st.session_state.game_over = True
        st.session_state.message = "Correct! You win!"
        return
    
    correct_letters = sum(1 for i, c in enumerate(guess) if c == st.session_state.word[i])
    st.session_state.correct_letters = correct_letters
    st.session_state.message = f"Incorrect guess. {correct_letters} letters in correct position. Try again!"
    
    if st.session_state.attempts <= 0:
        st.session_state.game_over = True
        st.session_state.message = f"Game over! The word was '{st.session_state.word}'."

def main():
    st.set_page_config(page_title="Word Guessing Game", layout="centered")
    st.title("Word Guessing Game")

    if 'word' not in st.session_state:
        st.session_state.word = ''
    if 'attempts' not in st.session_state:
        st.session_state.attempts = 5
    if 'hint' not in st.session_state:
        st.session_state.hint = {}
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'message' not in st.session_state:
        st.session_state.message = ""
    if 'correct_letters' not in st.session_state:
        st.session_state.correct_letters = 0
    if 'error' not in st.session_state:
        st.session_state.error = ""
    if 'guess' not in st.session_state:
        st.session_state.guess = ""

    word_length = st.slider("Select Word Length:", 4, 10, 5)

    if st.button("Start New Game"):
        new_game(word_length)

    if st.session_state.error:
        st.error(st.session_state.error)

    if st.session_state.word:
        st.write(f"Attempts left: {st.session_state.attempts}")
        st.write(f"Description: {st.session_state.hint['description']}")
        st.write(f"Associations: {st.session_state.hint['associations']}")
        st.write(f"Letter hints: {st.session_state.hint['letters']}")

        st.text_input("Enter your guess:", key="guess", on_change=submit_guess, disabled=st.session_state.game_over)
        if st.session_state.correct_letters > 0 and not st.session_state.game_over:
            st.write(f"{st.session_state.correct_letters} letters in correct position")

        if st.session_state.message:
            st.write(st.session_state.message)

if __name__ == "__main__":
    main()