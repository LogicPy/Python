import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2
import pyautogui
import time
import threading
import keyboard  # Install using: pip install keyboard
import threading
import win32api, win32con, win32gui

# Disable the fail-safe (not recommended)
pyautogui.FAILSAFE = False

# -----------------------------
# Configuration
# -----------------------------

# Load the SSD MobileNet V2 model from TensorFlow Hub
MODEL_URL = "https://tfhub.dev/tensorflow/centernet/hourglass_512x512_kpts/1"  # You can choose other models as well
detector = hub.load(MODEL_URL)

# Define the capture region (left, top, width, height)
capture_region = (0, 0, 1920, 1080)  # Full screen

# Set the mouse movement speed (pixels per second)
movement_speed = 500

# Example boundaries
MIN_X, MIN_Y = 100, 100
MAX_X, MAX_Y = 1820, 980  # Assuming a 1920x1080 screen

# Set the minimum distance (pixels) to move the mouse
min_distance = 10

# Flag to control the scanning loop
running = True

# -----------------------------
# Helper Functions
# -----------------------------

def move_mouse_to_target(target_x, target_y):
    """
    Move the mouse cursor to the specified (x, y) coordinates.
    """
    # Ensure target is within boundaries
    target_x = max(MIN_X, min(target_x, MAX_X))
    target_y = max(MIN_Y, min(target_y, MAX_Y))
    
    current_x, current_y = pyautogui.position()
    distance = np.hypot(target_x - current_x, target_y - current_y)

    if distance < min_distance:
        return  # No need to move

    time_to_move = distance / movement_speed
    pyautogui.moveTo(target_x, target_y, duration=time_to_move, tween=pyautogui.easeInOutQuad)

def detect_quit():
    """
    Listen for the 'q' key press to terminate the scanning loop.
    """
    global running
    keyboard.wait('q')
    running = False
    print("\n[INFO] 'q' pressed. Exiting the scanner...")

def listen_for_exit():
    """
    Listen for the 'ctrl+e' key combination to terminate the scanning loop.
    """
    global running
    keyboard.wait('ctrl+e')
    running = False
    print("\n[INFO] 'Ctrl + E' pressed. Exiting the scanner...")

def preprocess_image(image):
    """
    Preprocess the image for TensorFlow model.
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image, (320, 320))  # Resize to model's expected input size
    image_normalized = image_resized / 255.0  # Normalize to [0,1]
    image_expanded = np.expand_dims(image_normalized, axis=0)  # Add batch dimension
    return image_expanded

def detect_objects(image):
    """
    Perform object detection on the image using the loaded model.
    Returns bounding boxes, class IDs, and scores.
    """
    input_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
    detections = detector(input_tensor)
    
    # Extract detection results
    boxes = detections['detection_boxes'][0].numpy()
    class_ids = detections['detection_classes'][0].numpy().astype(np.int32)
    scores = detections['detection_scores'][0].numpy()
    
    return boxes, class_ids, scores

def process_frame(screenshot):
    """
    Process the captured frame to detect objects and return their center coordinates.
    """
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    preprocessed = preprocess_image(frame)
    boxes, class_ids, scores = detect_objects(preprocessed)
    
    centers = []
    height, width, _ = frame.shape
    
    for box, cls_id, score in zip(boxes, class_ids, scores):
        if score < 0.5:
            continue  # Filter out low-confidence detections
        
        # Convert box coordinates from normalized [0,1] to pixel values
        y_min, x_min, y_max, x_max = box
        (left, right, top, bottom) = (x_min * width, x_max * width, y_min * height, y_max * height)
        
        # Calculate center coordinates
        center_x = int((left + right) / 2)
        center_y = int((top + bottom) / 2)
        
        centers.append((center_x, center_y))
        
        # Optional: Draw bounding boxes and labels for visualization
        cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
        #label = f"ID:{cls_id} Score:{score:.2f}"
        cv2.putText(frame, label, (int(left), int(top) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame, centers

# -----------------------------
# Main Scanning Function
# -----------------------------

def scan_screen():
    global running

    # Initialize the screen capture region
    left, top, width, height = capture_region

    while running:
        start_time = time.time()

        # Capture the screen
        screenshot = pyautogui.screenshot(region=capture_region)

        # Process the captured frame
        frame, centers = process_frame(screenshot)

        # Iterate over the detected centers and move the mouse
        for center in centers:
            move_mouse_to_target(center[0] + left, center[1] + top)

        # Display the frame with detections
        cv2.imshow("Aimbot Tool - YOLO TensorFlow Detection Feed", frame)

        # Calculate elapsed time and sleep if necessary to control frame rate
        elapsed_time = time.time() - start_time
        sleep_time = max(0.01, 0.05 - elapsed_time)  # Aim for ~20 FPS
        time.sleep(sleep_time)

        # Exit if 'q' is pressed (alternative termination method)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    cv2.destroyAllWindows()

# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    print("[INFO] Starting the Aimbot Tool with TensorFlow Hub Object Detection...")
    print("[INFO] Press 'q' or 'Ctrl + E' at any time to quit.")

    # Start the quit listener threads
    quit_thread_q = threading.Thread(target=detect_quit, daemon=True)
    quit_thread_ctrl_e = threading.Thread(target=listen_for_exit, daemon=True)
    quit_thread_q.start()
    quit_thread_ctrl_e.start()

    # Start scanning
    scan_screen()

    print("[INFO] Scanner terminated gracefully.")
