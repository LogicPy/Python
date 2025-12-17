# =============================================================================
# Zerza's Upgraded AI-Powered Aimbot with Terminator Overlay
# =============================================================================
# Description: An advanced auto-aiming tool for local game testing, leveraging
# TensorFlow Hub for object detection and pynput for cross-platform input control.
# Features intelligent target selection, aim-key activation, and a Terminator-style HUD.
#
# REQUIRED LIBRARIES:
# pip install tensorflow tensorflow-hub numpy opencv-python pyautogui pynput
# =============================================================================

import os
# Force TensorFlow to use CPU to avoid CUDA/CuDNN issues on systems without a compatible GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import cv2
import numpy as np
import pyautogui
import time
import tensorflow as tf
import tensorflow_hub as hub
import logging
import sys
import random
import threading
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import font as tkfont

# --- 1. CONFIGURATION ---
CONFIG = {
    # --- General Settings ---
    "AIM_KEY": "right",
    "QUIT_KEY": keyboard.KeyCode.from_char('q'),

    # --- Model & Detection Settings ---
    "MODEL_URL": "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2",
    "CONFIDENCE_THRESHOLD": 0.5,
    "TARGET_CLASS_ID": 1,

    # --- Aimbot Behavior Settings ---
    "AIM_SPEED": 0.4,
    "FIRE_THRESHOLD_PX": 15,
    "FIRE_DELAY": 0.1,

    # --- Screen Capture & Debug Settings ---
    "CAPTURE_REGION": (0, 0, 1920, 1080),
    "SHOW_DETECTION_WINDOW": False,

    # --- NEW: Overlay Settings ---
    "OVERLAY_ENABLED": True,
    "OVERLAY_OPACITY": 0.7,  # 0.0 (fully transparent) to 1.0 (fully opaque)
    "OVERLAY_TEXT_COLOR": "#00FF00", # Classic Terminator Green
    "OVERLAY_BG_COLOR": "#000000",  # Black background
}

# --- 2. INITIALIZATION & GLOBALS ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Initializing Zerza's Upgraded Aimbot with Terminator Overlay...")

pyautogui.FAILSAFE = False
running = True
aiming = False
last_fire_time = 0

# Check if GPU is available
gpu_available = len(tf.config.list_physical_devices('GPU')) > 0
logging.info(f"GPU Available: {gpu_available}")

# Load the TensorFlow Hub model
try:
    logging.info(f"Loading model from: {CONFIG['MODEL_URL']}")
    detector = hub.load(CONFIG["MODEL_URL"])
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    running = False

# --- 3. NEW: TERMINATOR OVERLAY CLASS ---

# --- 3. NEW: TERMINATOR OVERLAY CLASS (Corrected for Linux) ---

class TerminatorOverlay(threading.Thread):
    def __init__(self, config):
        super().__init__(daemon=True) # Use daemon thread so it exits when main program does
        self.config = config
        self.num_targets = 0
        self.scan_accuracy = 80
        self.power_level = 100
        self.root = None

    def run(self):
        """Initializes and runs the Tkinter main loop in a new thread."""
        self.root = tk.Tk()
        self.root.title("Terminator Vision System")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window geometry and properties
        window_width = 450
        window_height = screen_height
        self.root.geometry(f"{window_width}x{window_height}+0+0") # Left side of the screen
        self.root.overrideredirect(True)  # Remove window border and title bar
        self.root.attributes('-topmost', True)  # Keep window on top
        self.root.attributes('-alpha', self.config["OVERLAY_OPACITY"]) # Set transparency

        # --- LINUX COMPATIBILITY FIX ---
        # The '-transparentcolor' attribute is for Windows only.
        # On Linux, we set the background to a solid color and let the alpha channel handle transparency.
        # Note: This overlay will capture mouse clicks on Linux. True "click-through" requires
        # system-specific libraries (like Xlib) which are more complex.
        bg_color = self.config["OVERLAY_BG_COLOR"]
        self.root.config(bg=bg_color)

        # Create a text widget
        self.text_widget = tk.Text(
            self.root,
            bg=bg_color,
            fg=self.config["OVERLAY_TEXT_COLOR"],
            font=tkfont.Font(family="Consolas", size=10),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Start the update loop
        self.update_text()
        self.root.mainloop()

    def update_text(self):
        """Updates the text content of the overlay."""
        if not self.root:
            return

        # Generate random hex/binary data for visual effect
        hex_data = "\n".join(
            [f"0x{random.randint(0x0040, 0x0050):04X}\t\t" +
             " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)]) +
             f"\t{' '.join([format(random.randint(0, 255), '08b') for _ in range(2)])}"
             for _ in range(10)]
        )

        # Create the full text string
        full_text = f"""TERMINATOR VISION SYSTEM - LIVE
==================================================
MEMORY ADDRESS	HEX DATA		BINARY DATA
----------------------------------------------------------------------
{hex_data}

SYSTEM STATUS:
• TARGETS DETECTED: {self.num_targets}
• SCAN ACCURACY: {self.scan_accuracy + random.randint(-5, 5)}%
• PROCESSING: MEDIUM
• POWER: {self.power_level}%
"""

        # Update the text widget
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, full_text)

        # Schedule the next update
        self.root.after(500, self.update_text) # Update every 500ms

    def set_status(self, num_targets):
        """Public method to update the status from the main thread."""
        self.num_targets = num_targets


# --- 4. CORE FUNCTIONS (Mostly Unchanged) ---

def get_screen_shot():
    """Captures a screenshot of the specified region."""
    try:
        screenshot = pyautogui.screenshot(region=CONFIG["CAPTURE_REGION"])
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Could not capture screen: {e}")
        return None

def detect_objects(frame):
    """Runs object detection on a frame and returns bounding boxes, classes, and scores."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    input_tensor = tf.convert_to_tensor(rgb_frame)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detector(input_tensor)

    boxes = detections['detection_boxes'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(int)
    scores = detections['detection_scores'][0].numpy()

    return boxes, classes, scores

def select_target_and_count(boxes, classes, scores, screen_width, screen_height):
    """Selects the best target and returns the count of all valid targets."""
    best_target = None
    min_distance = float('inf')
    valid_target_count = 0
    
    crosshair_x, crosshair_y = pyautogui.position()

    for i in range(len(boxes)):
        is_valid_target = scores[i] > CONFIG["CONFIDENCE_THRESHOLD"] and classes[i] == CONFIG["TARGET_CLASS_ID"]
        if not is_valid_target:
            continue

        valid_target_count += 1

        y_min, x_min, y_max, x_max = boxes[i]
        start_x = int(x_min * screen_width)
        start_y = int(y_min * screen_height)
        end_x = int(x_max * screen_width)
        end_y = int(y_max * screen_height)

        target_x = (start_x + end_x) // 2
        target_y = (start_y + end_y) // 2
        distance = np.hypot(crosshair_x - target_x, crosshair_y - target_y)

        if distance < min_distance:
            min_distance = distance
            best_target = (target_x, target_y, (start_x, start_y, end_x, end_y))

    return best_target, valid_target_count

def aim_and_shoot(target_coords):
    """Moves the mouse towards the target and shoots when close enough."""
    global last_fire_time
    target_x, target_y, _ = target_coords

    pyautogui.moveTo(target_x, target_y, duration=CONFIG["AIM_SPEED"], tween=pyautogui.easeOutQuad)
    current_x, current_y = pyautogui.position()
    distance_to_target = np.hypot(current_x - target_x, current_y - target_y)

    if distance_to_target < CONFIG["FIRE_THRESHOLD_PX"]:
        current_time = time.time()
        if (current_time - last_fire_time) > CONFIG["FIRE_DELAY"]:
            logging.info("Firing!")
            pyautogui.click(button=CONFIG["AIM_KEY"])
            last_fire_time = current_time

# --- 5. EVENT HANDLERS (Unchanged) ---

def on_click(x, y, button, pressed):
    global aiming
    if button == mouse.Button.right:
        aiming = pressed
    return running

def on_press(key):
    global running
    try:
        if key == CONFIG["QUIT_KEY"]:
            logging.info("Quit key pressed. Shutting down.")
            running = False
            return False
    except AttributeError:
        pass
    return True

# --- 6. MAIN LOOP (Modified to use Overlay) ---

def main_loop():
    """The main loop of the aimbot."""
    global running
    logging.info("Aimbot is active. Hold the right mouse button to aim.")
    logging.info(f"Press '{CONFIG['QUIT_KEY']}' to quit.")

    # Initialize and start the overlay thread
    overlay_thread = None
    if CONFIG["OVERLAY_ENABLED"]:
        overlay_thread = TerminatorOverlay(CONFIG)
        overlay_thread.start()
        # Give Tkinter a moment to initialize
        time.sleep(1)

    # Set up listeners
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    keyboard_listener.start()

    while running:
        if not aiming:
            time.sleep(0.01)
            continue

        frame = get_screen_shot()
        if frame is None:
            continue

        height, width, _ = frame.shape
        boxes, classes, scores = detect_objects(frame)
        
        target_coords, num_targets = select_target_and_count(boxes, classes, scores, width, height)

        if overlay_thread:
            overlay_thread.set_status(num_targets)

        if target_coords:
            aim_and_shoot(target_coords)

        if CONFIG["SHOW_DETECTION_WINDOW"]:
            cv2.imshow("Aimbot Debug Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

    # Clean up
    mouse_listener.stop()
    keyboard_listener.stop()
    if CONFIG["SHOW_DETECTION_WINDOW"]:
        cv2.destroyAllWindows()
    logging.info("Aimbot terminated gracefully.")

# --- 7. ENTRY POINT ---

if __name__ == "__main__":
    if running:
        main_loop()
