import win32gui

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

if __name__ == "__main__":
    list_open_windows()
