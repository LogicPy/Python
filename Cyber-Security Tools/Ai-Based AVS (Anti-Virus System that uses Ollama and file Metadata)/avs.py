from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import requests
import json
import os


def run_avs_and_upload(file_path):
    # Start the AVS Application
    AVSApp().run()
    
    # Proceed to scan the file after the AVS process completes
    jotti_result = scan_with_jotti(file_path)
    
    # Check and handle the result from Jotti
    if jotti_result:
        print("Jotti Scan Result:", jotti_result)
    else:
        print("Failed to get scan results from Jotti.")


def scan_file_with_ai(file_path):
    global file_dir
    file_dir = file_path
    # Extract basic metadata
    file_metadata = {
        "filename": os.path.basename(file_path),
        "filesize": os.path.getsize(file_path),
        "filetype": os.path.splitext(file_path)[1],
    }

    # Prepare AI content variable to analyze the file
    prompt = f"""
    You are an AI assistant specialized in cybersecurity. Analyze the following file metadata and ASM details to determine if the file is malicious:
    
    File Name: {file_metadata['filename']}
    File Size: {file_metadata['filesize']} bytes
    File Type: {file_metadata['filetype']}
    """
    
    # Optionally, read a portion of the file to add deeper inspection.
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read(1024)  # Read first 1KB of the file
            prompt += f"\nSample ASM Content (hex): {file_content.hex()[:512]}"
    except Exception as e:
        prompt += "\nUnable to read file content."

    # Replace with your actual Ollama API integration
    ai_response = generate_ai_response(prompt)
    return ai_response

user_context = {}

def generate_ai_response(prompt):
    user_id = "default_user"  # In a real application, you might want to use a unique ID for each user

    # Retrieve the context for the user
    context = user_context.get(user_id, "")
    
    # Update the context with the new prompt
    context += f" User: {prompt}\n"
    
    # Placeholder: Connect to the Ollama framework
    api_url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": "You're a cybersecurity AI capable of analyzing file metadata and ASM details to detect potential threats."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
 # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Print the response text for debugging
        # print(response.text)
        
        # Process each line of the response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue
        # Update the context with the AI's response
        context += f" AI: {combined_response.strip()}\n"
        user_context[user_id] = context
        return(combined_response.strip())
        # print(combined_response.strip())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")


from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
import os

class AVSApp(App):
    def build(self):
        self.selected_file = None  # Initialize the selected file path

        # Create UI elements
        layout = BoxLayout(orientation='vertical')
        scan_button = Button(text="Select File to Scan", on_press=self.open_file_chooser)
        layout.add_widget(scan_button)

        # Add a separate button to start scanning (will only be active if a file is selected)
        self.scan_start_button = Button(text="Start Scan", on_press=self.start_scan, disabled=True)
        layout.add_widget(self.scan_start_button)

        return layout

    def open_file_chooser(self, instance):
        # Create a FileChooser popup
        filechooser = FileChooserListView()
        popup = Popup(title="Select File to Scan", content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.select_file)
        popup.open()

    def select_file(self, filechooser, selection, *args):
        if selection:
            # Save the selected file path and enable the scan button
            self.selected_file = selection[0]
            print(f"File selected: {self.selected_file}")
            self.scan_start_button.disabled = False

    def start_scan(self, instance):
        if self.selected_file:
            # Use the selected file path for scanning
            jotti_result = scan_with_jotti(self.selected_file)
            if jotti_result:
                print("Jotti Scan Result:", jotti_result)
            else:
                print("Failed to get scan results from Jotti.")

# Function to upload file to Jotti for analysis
def scan_with_jotti(file_path):
    api_url = "https://virusscan.jotti.org/en-US/filescan"  # Use the Jotti API if available
    files = {'file': open(file_path, 'rb')}
    try:
        response = requests.post(api_url, files=files)
        if response.status_code == 200:
            print("File successfully uploaded for external analysis.")
            return response.json()  # Assuming the response provides useful information
        else:
            print("Error uploading file for external analysis.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    AVSApp().run()
    # Example usage
    file_path = file_dir
    jotti_result = scan_with_jotti(file_path)
    if jotti_result:
        print("Jotti Scan Result:", jotti_result)