import socketio
import speech_recognition as sr
import requests
from github import Github
import io
import pygame
import time
import threading

# Global variables to manage the state
complete_text = ""
last_chunk_time = None
message_complete = False
lock = threading.Lock()

#import sys
#print(sys.getrecursionlimit())  # Output: 1000

# Initialize Socket.IO client
sio = socketio.Client()
audio_generated = False
# Flag to indicate if the current message has been fully received and processed
message_complete = False

input_text = ""
output_text = ""
complete_text = ""
# Configuration variables
XI_API_KEY = "bc3f6fab1c2fb9c92c55xxxxxxxxxxxx"
VOICE_ID = "dMYsx8iuXK03HbedIrt9"
GITHUB_TOKEN = 'ghp_AfRgsCYNZsVmJmtxs9729W68xxxxxxxxxxx'
REPO_NAME = "LogicPy/Python"
FILE_PATH = 'output.mp3'  # Local path for saving the audio file
TARGET_PATH = 'output.mp3'  # Target path in the GitHub repository

# Initialize Socket.IO client
sio = socketio.Client()

def networkSetup():
    ssid = "Wayne.Cool headquarters"
    psk = "Aquabat1337"
    with open("wlan.cfg", "w") as f:
        f.write(f"SSID = {ssid}\n")
        f.write(f"PSK = {psk}\n")

def generate_audio_with_eleven_labs(text_to_speak):
    """
    Generates audio from text using ElevenLabs API and saves to a file.
    """
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text_to_speak,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    response = requests.post(tts_url, json=data, headers=headers, stream=True)
    if response.status_code == 200:
        with open(FILE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Finished writing audio file to {FILE_PATH}")
    else:
        print("Failed to generate audio")

def upload_to_github(file_path, target_path, commit_message):
    """
    Uploads a file to GitHub, updating it if it exists or creating it otherwise.
    """
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        contents = repo.get_contents(target_path)
        sha = contents.sha
        with open(file_path, 'rb') as file:
            repo.update_file(target_path, commit_message, file.read(), sha)
            print(f'File updated at {target_path}')
    except:
        with open(file_path, 'rb') as file:
            repo.create_file(target_path, commit_message, file.read())
            print(f'File created at {target_path}')


# Function to append and display messages (for demonstration purposes, this could be logging the messages or handling them as needed in your application)
def append_message(text, sender='user'):
    # In a console application, you might just print the messages
    # In a more complex application, you would handle the message display differently
    print(f"{sender}: {text}")

# Sample message sending
def send_message(prompt, temperature=0.5, n_predicts=100):
    append_message(prompt, 'user')  # Display the user's message
    # Emit an event to the server with the message and additional parameters
    sio.emit('generate_text', {
        'prompt': prompt,
        'temperature': temperature,
        'n_predicts': n_predicts
    })


def play_audio_from_url(mp3_url):
    """
    Plays audio from a given URL using pygame.
    """
    pygame.mixer.init()
    response = requests.get(mp3_url)
    if response.status_code == 200:
        mp3_io = io.BytesIO(response.content)
        pygame.mixer.music.load(mp3_io)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    else:
        print("Failed to fetch the MP3 file")

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def disconnect():
    print("Disconnected from the server")

def reset_message_state():
    global complete_text, last_chunk_time, message_complete
    with lock:
        complete_text = ""
        last_chunk_time = None
        message_complete = False

def handle_text_chunk(data):
    global complete_text, last_chunk_time, message_complete
    with lock:
        complete_text += data['chunk']
        last_chunk_time = time.time()
        if not message_complete:
            # Start a timer on the first chunk
            threading.Timer(2.0, check_message_completion).start()

def check_message_completion():
    global complete_text, last_chunk_time, message_complete
    with lock:
        if time.time() - last_chunk_time >= 2.0 and not message_complete:
            print('Complete text:', complete_text)
            generate_audio_with_eleven_labs(complete_text)  # Generate audio
            upload_to_github(FILE_PATH, TARGET_PATH, 'Upload MP3 file')  # Upload generated audio
            play_audio_from_url(f'https://raw.githubusercontent.com/{REPO_NAME}/master/{TARGET_PATH}?raw=true')  # Play the uploaded audio
            complete_text = ''  # Reset for the next message
            message_complete = True

@sio.on('text_chunk')
def on_message(data):
    handle_text_chunk(data)

def start_speech_recognition():
    """
    Captures speech input, generates audio, uploads it to GitHub, and plays it back.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something!")
        try:
            audio = recognizer.listen(source)
            recognized_text = recognizer.recognize_google(audio)
            print("Speech recognized: ", recognized_text)
            send_message(recognized_text, 0.5, 100)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google; {e}")

if __name__ == "__main__":
    try:
        sio.connect("http://localhost:9600")
        start_speech_recognition()
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"Connection to the server failed: {e}")


