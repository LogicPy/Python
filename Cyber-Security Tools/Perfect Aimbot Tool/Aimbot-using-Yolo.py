import cv2
import numpy as np
import pyautogui
import time
import threading
import keyboard  # Install using: pip install keyboard
from queue import Queue

# Disable the fail-safe (not recommended)
pyautogui.FAILSAFE = False

# -----------------------------
# Configuration
# -----------------------------

# Path to YOLO directory
YOLO_DIR = 'yolo/'  # Update this path if necessary

# YOLO Files
YOLO_CONFIG_PATH = YOLO_DIR + 'yolov3.cfg'
YOLO_WEIGHTS_PATH = YOLO_DIR + 'yolov3.weights'
YOLO_NAMES_PATH = YOLO_DIR + 'coco.names'

# Load class labels
with open(YOLO_NAMES_PATH, 'r') as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]

# Initialize YOLO network
net = cv2.dnn.readNetFromDarknet(YOLO_CONFIG_PATH, YOLO_WEIGHTS_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # Change to DNN_TARGET_CUDA if you have CUDA installed

# Determine output layer names
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

# Confidence and Non-Maximum Suppression thresholds
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# Set the capture region (left, top, width, height)
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

def preprocess_frame(frame):
    """
    Preprocess the frame for YOLO object detection.
    """
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    return blob

def get_detections(blob, frame):
    """
    Get detections from YOLO for the given frame.
    Returns bounding boxes, confidences, and class IDs.
    """
    net.setInput(blob)
    layer_outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    height, width = frame.shape[:2]

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > CONFIDENCE_THRESHOLD:
                # Scale the bounding box coordinates back relative to the image size
                box = detection[0:4] * np.array([width, height, width, height])
                (center_x, center_y, w, h) = box.astype("int")

                # Calculate the top-left corner of the bounding box
                x = int(center_x - (w / 2))
                y = int(center_y - (h / 2))

                boxes.append([x, y, int(w), int(h)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply Non-Maximum Suppression to suppress weak, overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    filtered_boxes = []
    filtered_confidences = []
    filtered_class_ids = []

    if len(indices) > 0:
        for i in indices.flatten():
            filtered_boxes.append(boxes[i])
            filtered_confidences.append(confidences[i])
            filtered_class_ids.append(class_ids[i])

    return filtered_boxes, filtered_confidences, filtered_class_ids

def process_frame_yolo(screenshot):
    """
    Process the captured frame using YOLO for object detection.
    Returns bounding boxes, confidences, and class IDs.
    """
    # Convert the screenshot to a NumPy array and then to BGR color space
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Preprocess the frame
    blob = preprocess_frame(frame)

    # Get detections
    boxes, confidences, class_ids = get_detections(blob, frame)

    return frame, boxes, confidences, class_ids

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

        # Process the captured frame with YOLO
        frame, boxes, confidences, class_ids = process_frame_yolo(screenshot)

        centers = []

        for i, box in enumerate(boxes):
            x, y, w, h = box
            # Calculate the center of the bounding box
            center_x = x + w // 2
            center_y = y + h // 2
            centers.append((center_x, center_y))

            # Draw bounding boxes and labels on the frame
            label = f"{CLASS_NAMES[class_ids[i]]}: {confidences[i]:.2f}"
            color = (0, 255, 0)  # Green color for boxes
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Iterate over the detected centers and move the mouse
        for center in centers:
            move_mouse_to_target(center[0] + left, center[1] + top)

        # Display the frame with detections
        cv2.imshow("Aimbot Tool - YOLO Detection Feed", frame)

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
    print("[INFO] Starting the Aimbot Tool with YOLO Object Detection...")
    print("[INFO] Press 'q' or 'Ctrl + E' at any time to quit.")

    # Start the quit listener threads
    quit_thread_q = threading.Thread(target=detect_quit, daemon=True)
    quit_thread_ctrl_e = threading.Thread(target=listen_for_exit, daemon=True)
    quit_thread_q.start()
    quit_thread_ctrl_e.start()

    # Start scanning
    scan_screen()

    print("[INFO] Scanner terminated gracefully.")
