import win32gui
import win32con
import win32api
import pyautogui
import time
import sys
import threading

# Initialize counters
detection_count = 0
shot_count = 0

# Locks for thread-safe operations
detection_lock = threading.Lock()
shot_lock = threading.Lock()

# Flag to control the scanning loop
running = True

def list_open_windows():
    def enum_handler(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            results.append((hwnd, class_name, window_text))
    
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    
    print(f"{'HWND':<10} {'Class Name':<30} {'Window Title'}")
    print("-" * 80)
    for hwnd, class_name, window_text in windows:
        print(f"{hwnd:<10} {class_name:<30} {window_text}")

def find_window_partial(title_substring):
    def enum_handler(hwnd, results):
        window_text = win32gui.GetWindowText(hwnd)
        if title_substring.lower() in window_text.lower():
            results.append(hwnd)
    
    results = []
    win32gui.EnumWindows(enum_handler, results)
    return results

def bring_window_to_foreground(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore if minimized
        win32gui.SetForegroundWindow(hwnd)
        print("Window brought to the foreground.")
    except Exception as e:
        print(f"Error bringing window to foreground: {e}")

def simulate_shot():
    """
    Simulate a mouse click to represent a shot.
    """
    # Simulate a left mouse button click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)  # Short pause
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def display_counters():
    """
    Display the detection and shot counters in the console.
    """
    global detection_count, shot_count
    with detection_lock, shot_lock:
        sys.stdout.write(f"\rDetections: {detection_count} | Shots: {shot_count}")
        sys.stdout.flush()

def scan_screen():
    global running, detection_count, shot_count

    # Example: Search for Notepad
    target_substring = "Notepad"
    matching_hwnds = find_window_partial(target_substring)
    
    if not matching_hwnds:
        print(f"No windows found containing '{target_substring}'. Exiting.")
        return
    
    # Use the first matching window
    hwnd = matching_hwnds[0]
    print(f"Found window: HWND={hwnd}, Title='{win32gui.GetWindowText(hwnd)}'")
    
    # Bring the window to foreground
    bring_window_to_foreground(hwnd)
    
    # Initialize the screen capture region based on window position
    # Get window rectangle
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        capture_region = (left, top, width, height)
        print(f"Capture region set to: {capture_region}")
    except Exception as e:
        print(f"Error getting window rectangle: {e}")
        return
    
    # Initial display
    print("Detections: 0 | Shots: 0", end='')
    
    while running:
        start_time = time.time()
        
        # Capture the screen region
        screenshot = pyautogui.screenshot(region=capture_region)
        
        # Here, you would integrate your TensorFlow or YOLO detection logic
        # For demonstration, let's assume a detection is made
        detected = True  # Replace with actual detection condition
        
        if detected:
            with detection_lock:
                detection_count += 1
            simulate_shot()
            with shot_lock:
                shot_count += 1
        
        # Display counters
        display_counters()
        
        # Control frame rate
        elapsed_time = time.time() - start_time
        sleep_time = max(0.01, 0.05 - elapsed_time)  # Aim for ~20 FPS
        time.sleep(sleep_time)
        
        # Exit condition
        if win32gui.GetForegroundWindow() != hwnd:
            print("\n[INFO] Target window is no longer in focus. Exiting.")
            running = False
    
    print("\n[INFO] Scanner terminated gracefully.")

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

if __name__ == "__main__":
    print("Listing all open windows:")
    list_open_windows()
    
    print("\nPress 'q' or 'Ctrl + E' at any time to quit.")
    
    # Start the quit listener threads
    quit_thread_q = threading.Thread(target=detect_quit, daemon=True)
    quit_thread_ctrl_e = threading.Thread(target=listen_for_exit, daemon=True)
    quit_thread_q.start()
    quit_thread_ctrl_e.start()
    
    # Start scanning
    scan_screen()
