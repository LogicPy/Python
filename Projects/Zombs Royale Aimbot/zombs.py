
# Zombs Royale Aimbot
# LogicPy - Wayne Kenney

from PIL import Image
import pyautogui
from time import sleep
import win32api
import sys

# Enemy Color
color = (253, 200, 118)

# x, y coordinates
xCord = 0
yCord = 0

def main():
	while(True):
		cmd = raw_input("Enter Aimbot Command: ")
		cmd = cmd.lower()
		if cmd == "help":
			# List of Commands
			print """\nList of commands:\n  
	help - Displays a List of Commands
	start - Activate the Aimbot
	exit - Exit this Script\n"""
		elif cmd == "start":
			# Execute Aimbot
			Aimbot_GO()
		elif cmd == "exit":
			# Exit
			sys.exit()
		else:
			print "\nInvalid command...\n"


def Aimbot_GO():

	print "\nAimbot Activated!\n"

	while(True):

		# Capture screenshot
		pic = pyautogui.screenshot()

		# screenshot to array
		pix_val = list(pic.getdata())

		# if color in array
		if color in pix_val:

			# x, y calculations
			xCord = pix_val.index(color) / 1920
			yCord = pix_val.index(color) % 1920

			# Position mouse
			pyautogui.moveTo(yCord, xCord)

		else:
			pass

main()