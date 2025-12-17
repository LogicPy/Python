# =============================================================================
# Zerza's Upgraded AI-Powered COLOR Aimbot with Terminator Overlay
# =============================================================================
# Description: A color-based auto-aiming tool that targets specific colors,
# features intelligent target selection, auto-shoot, aim-key activation,
# and a Terminator-style HUD.
#
# REQUIRED LIBRARIES:
# pip install opencv-python numpy pyautogui pynput
# =============================================================================

import cv2
import numpy as np
import pyautogui
import time
import threading
import random
import logging
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import font as tkfont

# --- 1. CONFIGURATION ---
CONFIG = {
    # --- General Settings ---
    "AIM_KEY": "right",  # The mouse button to hold for aiming ('left', 'right', 'middle')
    "QUIT_KEY": keyboard.KeyCode.from_char('q'),

    # --- Color Detection Settings ---
    # Red is tricky in HSV because it wraps around 0 and 180. We use two ranges.
    # These ranges cover most shades of red.
    "LOWER_RED_1": np.array([0, 120, 70]),
    "UPPER_RED_1": np.array([10, 255, 255]),
    "LOWER_RED_2": np.array([170, 120, 70]),
    "UPPER_RED_2": np.array([180, 255, 255]),
    # Minimum area for a contour to be considered a target (filters out noise)
    "MIN_CONTOUR_AREA": 500,

    # --- Aimbot Behavior Settings ---
    "AIM_SPEED": 0.3,  # Speed of mouse movement. Higher is faster.
    "FIRE_THRESHOLD_PX": 20,  # How close the cursor needs to be to the target's center to shoot.
    "FIRE_DELAY": 0.15,  # Delay between shots in seconds.

    # --- Screen Capture & Debug Settings ---
    "CAPTURE_REGION": (0, 0, 1920, 1080),  # (left, top, width, height)
    "SHOW_DETECTION_WINDOW": False,  # Set to False for better performance

    # --- Overlay Settings ---
    "OVERLAY_ENABLED": False,
    "OVERLAY_OPACITY": 0.7,
    "OVERLAY_TEXT_COLOR": "#FF0000",  # Terminator Red for the color bot!
    "OVERLAY_BG_COLOR": "#000000",
}

# --- 2. INITIALIZATION & GLOBALS ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Initializing Zerza's Upgraded Color Aimbot...")

pyautogui.FAILSAFE = False
running = True
aiming = False
last_fire_time = 0

# --- 3. TERMINATOR OVERLAY CLASS (Reused from our other tool) ---

class TerminatorOverlay(threading.Thread):
    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config
        self.num_targets = 0
        self.scan_accuracy = 90
        self.power_level = 100
        self.root = None

    def run(self):
        self.root = tk.Tk()
        self.root.title("Terminator Vision System - Color Mode")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 450
        window_height = screen_height
        self.root.geometry(f"{window_width}x{window_height}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.config["OVERLAY_OPACITY"])
        bg_color = self.config["OVERLAY_BG_COLOR"]
        self.root.config(bg=bg_color)

        self.text_widget = tk.Text(
            self.root, bg=bg_color, fg=self.config["OVERLAY_TEXT_COLOR"],
            font=tkfont.Font(family="Consolas", size=10), relief=tk.FLAT, bd=0, padx=10, pady=10
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.update_text()
        self.root.mainloop()

    def update_text(self):
        if not self.root:
            return
        hex_data = "\n".join(
            [f"0x{random.randint(0x0040, 0x0050):04X}\t\t" +
             " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)]) +
             f"\t{' '.join([format(random.randint(0, 255), '08b') for _ in range(2)])}"
             for _ in range(10)]
        )
        full_text = f"""COLOR TARGET ACQUISITION - LIVE
==================================================
MEMORY ADDRESS	HEX DATA		BINARY DATA
----------------------------------------------------------------------
{hex_data}

SYSTEM STATUS:
• RED TARGETS DETECTED: {self.num_targets}
• SCAN ACCURACY: {self.scan_accuracy + random.randint(-5, 5)}%
• PROCESSING: HIGH
• POWER: {self.power_level}%
"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, full_text)
        self.root.after(500, self.update_text)

    def set_status(self, num_targets):
        self.num_targets = num_targets

# --- 4. CORE FUNCTIONS ---

def get_screen_shot():
    """Captures a screenshot of the specified region."""
    try:
        screenshot = pyautogui.screenshot(region=CONFIG["CAPTURE_REGION"])
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Could not capture screen: {e}")
        return None

def find_red_targets(frame):
    """Detects red objects in a frame and returns their centers and contours."""
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create two masks for the red color ranges and combine them
    mask1 = cv2.inRange(hsv_frame, CONFIG["LOWER_RED_1"], CONFIG["UPPER_RED_1"])
    mask2 = cv2.inRange(hsv_frame, CONFIG["LOWER_RED_2"], CONFIG["UPPER_RED_2"])
    mask = cv2.add(mask1, mask2)

    # Apply morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    target_data = []
    for cnt in contours:
        if cv2.contourArea(cnt) > CONFIG["MIN_CONTOUR_AREA"]:
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2
            target_data.append({'center': (center_x, center_y), 'contour': cnt})
            
    return mask, target_data

def select_closest_target(targets):
    """Selects the target closest to the current mouse position."""
    if not targets:
        return None

    crosshair_x, crosshair_y = pyautogui.position()
    min_distance = float('inf')
    closest_target = None

    for target in targets:
        tx, ty = target['center']
        distance = np.hypot(crosshair_x - tx, crosshair_y - ty)
        if distance < min_distance:
            min_distance = distance
            closest_target = target

    return closest_target

def aim_and_shoot(target):
    """Moves the mouse towards the target and shoots when close enough."""
    global last_fire_time
    target_x, target_y = target['center']

    pyautogui.moveTo(target_x, target_y, duration=CONFIG["AIM_SPEED"], tween=pyautogui.easeOutQuad)

    current_x, current_y = pyautogui.position()
    distance_to_target = np.hypot(current_x - target_x, current_y - target_y)

    if distance_to_target < CONFIG["FIRE_THRESHOLD_PX"]:
        current_time = time.time()
        if (current_time - last_fire_time) > CONFIG["FIRE_DELAY"]:
            logging.info("Firing at red target!")
            pyautogui.click(button='left') # Auto-shoot with left click
            last_fire_time = current_time

# --- 5. EVENT HANDLERS ---

def on_click(x, y, button, pressed):
    """Handle mouse button events."""
    global aiming
    if button == mouse.Button.right:
        aiming = pressed
    return running

def on_press(key):
    """Handle keyboard press events."""
    global running
    try:
        if key == CONFIG["QUIT_KEY"]:
            logging.info("Quit key pressed. Shutting down.")
            running = False
            return False
    except AttributeError:
        pass
    return True

# --- 6. MAIN LOOP ---

def main_loop():
    """The main loop of the color aimbot."""
    global running
    logging.info("Color Aimbot is active. Hold the right mouse button to aim.")
    logging.info(f"Press '{CONFIG['QUIT_KEY']}' to quit.")

    # Initialize and start the overlay thread
    overlay_thread = None
    if CONFIG["OVERLAY_ENABLED"]:
        overlay_thread = TerminatorOverlay(CONFIG)
        overlay_thread.start()
        time.sleep(1) # Give Tkinter a moment to initialize

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

        mask, targets = find_red_targets(frame)

        if overlay_thread:
            overlay_thread.set_status(len(targets))

        if targets:
            closest_target = select_closest_target(targets)
            if closest_target:
                aim_and_shoot(closest_target)

        if CONFIG["SHOW_DETECTION_WINDOW"]:
            # Draw all detected targets for visualization
            for target in targets:
                cv2.drawContours(frame, [target['contour']], -1, (0, 255, 0), 2)
                cv2.circle(frame, target['center'], 5, (0, 0, 255), -1)
            
            cv2.imshow("Color Aimbot Detection Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

    # Clean up
    mouse_listener.stop()
    keyboard_listener.stop()
    if CONFIG["SHOW_DETECTION_WINDOW"]:
        cv2.destroyAllWindows()
    logging.info("Color Aimbot terminated gracefully.")

# --- 7. ENTRY POINT ---

if __name__ == "__main__":
    if running:
        main_loop()
