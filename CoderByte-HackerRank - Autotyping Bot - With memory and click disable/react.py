import keyboard
import pyautogui
import time
from pynput.mouse import Listener as MouseListener
import random
import requests
import speech_recognition as sr
import pyttsx3
from ollama import Client

last_position = 0  # Variable to store the last position in the text
last_positions = {}  # Dictionary to store the last position for each file


def recognize_speech_from_mic(recognizer, microphone, timeout=10, phrase_time_limit=20):
    """Transcribe speech recorded from `microphone`."""
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response


def text_to_speech(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    #engine.say(text)
    engine.runAndWait()

def query_ollama_model(text):
    """Send the recognized text to the Ollama model and get a response."""
    client = Client(host='http://localhost:11434')
    response = client.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': text,
        },
    ])

    response_message = response.get("message", {}).get("content", "")
    sentences = [s.strip() for s in response_message.split("\n")]
    formatted_response = "\n".join(sentences)
    return formatted_response

def audioLlama_input():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Say something to the microphone...")

    try:
        response = recognize_speech_from_mic(recognizer, microphone)
        if response["success"]:
            print(f"You said: {response['transcription']}")
            ollama_response = query_ollama_model(response['transcription'])
            print(f"Ollama says: {ollama_response}")
            text_to_speech(ollama_response)
        else:
            print(f"Error: {response['error']}")
    except Exception as e:
        print(f"Microphone access error: {e}")

def on_click(x, y, button, pressed):
    global typing_active
    if pressed:
        print(f"Mouse clicked at {(x, y)} with {button}")
        if typing_active:
            cancel_typing()

# Setting up the mouse listener
mouse_listener = MouseListener(on_click=on_click)
mouse_listener.start()

# Global flag to control typing
typing_active = False

def load_react_snippet_0():
    global typing_active, last_position
    file_name = 'to-do'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False


def load_react_snippet():
    global typing_active, last_position
    file_name = 'react_snippets'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippet2():
    global typing_active, last_position, last_positions
    file_name = 'react_snippets2'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippet3():
    global typing_active
    file_name = 'react_snippets3'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippet4():
    global typing_active
    file_name = 'sorting-array'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def load_react_snippet5():
    global typing_active
    file_name = 'filtering-array'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippet6():
    global typing_active
    file_name = 'mapping-an-array'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def load_react_snippet7():
    global typing_active
    file_name = 'simplelistrender'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def load_react_snippet8():
    global typing_active
    file_name = 'tablerendering'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def load_react_snippeta_1():
    global typing_active
    file_name = 'buttonToggle'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_b():
    global typing_active
    file_name = 'color-dropdown'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_c():
    global typing_active
    file_name = 'context-api'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_d():
    global typing_active
    file_name = 'letter-tiles'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_e():
    global typing_active
    file_name = 'list'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_f():
    global typing_active
    file_name = 'live-paragraph'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_g():
    global typing_active
    file_name = 'phone-book'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_i():
    global typing_active
    file_name = 'quiz-builder'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_j():
    global typing_active
    file_name = 'react-native-simple-counter'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_k():
    global typing_active
    file_name = 'weather-dashboard'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_10():
    global typing_active
    file_name = 'employee-list'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False


def load_react_snippeta_l():
    global typing_active
    file_name = 'simple-counter'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)  # Adjust the interval if needed
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_m():
    global typing_active
    file_name = 'tic-tac-toe'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def load_react_snippeta_o():
    global typing_active
    file_name = 'ReactStrictRender'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_9():
    global typing_active
    file_name = 'text-editor'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_11():
    global typing_active
    file_name = 'fizzbuzz'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_12():
    global typing_active
    file_name = 'cyclecounter'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_13():
    global typing_active
    print('test activated...')
    file_name = 'translator'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_14():
    global typing_active
    print('test activated...')
    file_name = 'slideshow'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_15():
    global typing_active
    print('test activated...')
    file_name = 'articleSort'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def FactoralQuestion():
    global typing_active
    file_name = 'FirstFactoral'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
def SubArrFunc():
    global typing_active
    file_name = 'SubArr'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False
    
    
def palindromeFunc():
    global typing_active
    file_name = 'Palindrome'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def loadReactSQL():
    global typing_active
    file_name = 'SQL Problem'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def load_react_snippeta_p():
    global typing_active
    file_name = 'React App Index Import Fix'
    #file_path = 'react_snippets.txt'
    file_path = f'{file_name}.txt'

    with open(file_path, 'r') as file:
        react_code = file.read()
        
    last_position = last_positions.get(file_name, 0)

    typing_active = True
    time.sleep(3)  # Wait for 3 seconds to switch to Notepad or any other text editor
    
    # Start typing from the last position saved
    for position in range(last_position, len(react_code)):
        if not typing_active:
            last_positions[file_name] = position  # Save the position where typing was paused
            break
        random_interval = random.uniform(0.1, 0.3)  # Generate a random typing interval between 0.1 and 0.3
        pyautogui.write(react_code[position], interval=random_interval)
    else:
        last_positions[file_name] = 0  # Reset position if the end of the text is reached
    typing_active = False

def ask_llama3(question):
    client = ollama.Client()
    try:
        response = client.chat(
            model="llama3",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        if response and 'message' in response:
            print("Llama3 Response:", response['message']['content'])
        else:
            print("Error: Unexpected response format", response)
    except Exception as e:
        print("Error:", str(e))

def prompt_for_question():
    question = input("Enter your question for Llama3: ")
    ask_llama3(question)

def load_react_snippeta_q():
    pass

def cancel_typing():
    global typing_active
    typing_active = False
    print("Typing canceled.")  # Adding a print statement to confirm function execution

print('\n\nRemember: npm start\n npm run build')

keyboard.add_hotkey('ctrl+alt+c', cancel_typing)  # Using a more specific hotkey
print('\n-=CoderByte Example Projects=-:')
print('ctrl + shift + 1 - Button Toggle')
print('ctrl + shift + 2 - color-dropdown')
print('ctrl + shift + 3 - context-api')
print('ctrl + shift + 4 - letter-tiles')
print('ctrl + shift + 5 - list')
print('ctrl + shift + 6 - live-paragraph')
print('ctrl + shift + 7 - phone-book')
print('ctrl + shift + 8 - quiz-builder')
print('ctrl + shift + 9 - react-native-simple-counter')
print('ctrl + shift + 0 - weather-dashboard.jsx')
print('ctrl + shift + p - simple-counter.jsx')
print('ctrl + shift + k - HackerRank-TextEditor.jsx')
print('ctrl + shift + x - tic-tac-toe')
print('ctrl + shift + t - typescript-button-toggle')
print('ctrl + alt + i - First Factorial')
print('ctrl + alt + k - SubArr')
print('ctrl + shift + g - To-Do List')
print('ctrl + alt + l - Palindrome')

print('\n-=HackerRank Example Projects=-:')
print('[Order of operations]:')
print('Start with TextEditor.js, then open up App.jsx, then index.js, and finally app.css')
print('ctrl + shift + k - Text Editor project\n')

print('[Order of operations]:')
print('Start with EmployeeList.js, then App.jsx, then index.js, and finally app.css')
print('ctrl + shift + z - Filtered Employee List Project\n')

print('CyclicCounter order of operations:')
print('ctrl + shift + v - CyclicCounter')
print('Operation order: CycleCounter.jsx, index.js, App.jsx, App.css...\n')

print('Translator code - ctrl + alt + a')
print('Order of Operations: Translator.js, index.js, app.js, app.css...\n')

print('React Slideshow - ctrl + alt + b')
print('Order of Operations: Slides.js, index.js, app.js, app.css...\n')

print('Paginated Articles using Api - ctrl + alt + d\n')
print('Order of operations: Articles.js, index.js, App.js, index.css, app.css....')
print('ArticleSort React Function - ctrl + alt + e\n')

print('Autocomplete words assessment - ctrl alt + j\n')
print('Order of Operations: ')

print('\n-=Pieces of a project=-:')
print('ctrl + shift + y - Modifiable code with original snippet text file')
print('ctrl + shift + q - Single Input Handling')
print('ctrl + shift + w - Multiple Inputs Handling')
print('ctrl + shift + e - Data Processing Functions')
print('ctrl + shift + a - Sorting an Array')
print('ctrl + shift + f - Filtering an Array')
print('ctrl + shift + m - Mapping an Array')
print('ctrl + shift + s - Simple list rendering')
print('ctrl + shift + h - Table Rendering')
print('ctrl + shift + d - Fizz-Buzz algorithm')
print('ctrl + alt + h - React SQL problem with employees') 

print('\nDebug after creation:')
print('ctrl + shift + u - React Strict in app.js')
print('ctrl + shift + y - React app import fix in index file\n')
# Register hotkeys for different snippets and cancellation

print("Press Ctrl+Shift+l to input a question for Llama3.")
print("Press Ctrl+Shift+o to Audio input for a question for Llama3.\n")

# Set up the hotkey
keyboard.add_hotkey('ctrl+shift+o', audioLlama_input)
keyboard.add_hotkey('ctrl+shift+l', prompt_for_question)
keyboard.add_hotkey('ctrl+shift+1', load_react_snippeta_1)
keyboard.add_hotkey('ctrl+shift+2', load_react_snippeta_b)
keyboard.add_hotkey('ctrl+shift+3', load_react_snippeta_c)
keyboard.add_hotkey('ctrl+shift+4', load_react_snippeta_d)
keyboard.add_hotkey('ctrl+shift+5', load_react_snippeta_e)
keyboard.add_hotkey('ctrl+shift+6', load_react_snippeta_f)
keyboard.add_hotkey('ctrl+shift+7', load_react_snippeta_g)
keyboard.add_hotkey('ctrl+shift+8', load_react_snippeta_i)
keyboard.add_hotkey('ctrl+shift+9', load_react_snippeta_j)
keyboard.add_hotkey('ctrl+shift+0', load_react_snippeta_k)
keyboard.add_hotkey('ctrl+shift+p', load_react_snippeta_l)
keyboard.add_hotkey('ctrl+shift+r', load_react_snippeta_q)
keyboard.add_hotkey('ctrl+shift+x', load_react_snippeta_m)
keyboard.add_hotkey('ctrl+shift+t', load_react_snippeta_l)
keyboard.add_hotkey('ctrl+shift+u', load_react_snippeta_o)
keyboard.add_hotkey('ctrl+shift+y', load_react_snippeta_p)
keyboard.add_hotkey('ctrl+shift+q', load_react_snippet)
keyboard.add_hotkey('ctrl+alt+c', load_react_snippet_0)
keyboard.add_hotkey('ctrl+shift+w', load_react_snippet2)
keyboard.add_hotkey('ctrl+shift+e', load_react_snippet3)
keyboard.add_hotkey('ctrl+shift+a', load_react_snippet4)
keyboard.add_hotkey('ctrl+shift+f', load_react_snippet5)
keyboard.add_hotkey('ctrl+shift+m', load_react_snippet6)
keyboard.add_hotkey('ctrl+shift+s', load_react_snippet7)
keyboard.add_hotkey('ctrl+shift+h', load_react_snippet8)
keyboard.add_hotkey('ctrl+shift+k', load_react_snippeta_9)
keyboard.add_hotkey('ctrl+shift+z', load_react_snippeta_10)
keyboard.add_hotkey('ctrl+shift+d', load_react_snippeta_11)
keyboard.add_hotkey('ctrl+shift+v', load_react_snippeta_12)
keyboard.add_hotkey('ctrl+alt+a', load_react_snippeta_13)
keyboard.add_hotkey('ctrl+alt+b', load_react_snippeta_14)
keyboard.add_hotkey('ctrl+alt+e', load_react_snippeta_15)
keyboard.add_hotkey('ctrl+alt+h', loadReactSQL)
keyboard.add_hotkey('ctrl+alt+i', FactoralQuestion)
keyboard.add_hotkey('ctrl+alt+k', SubArrFunc)
keyboard.add_hotkey('ctrl+alt+l', palindromeFunc)
keyboard.add_hotkey('c', cancel_typing)

print("Script running... Press Ctrl+Shift+R or Ctrl+Shift+X to type React snippets. Press Ctrl+Shift+C to cancel.")
keyboard.wait()
