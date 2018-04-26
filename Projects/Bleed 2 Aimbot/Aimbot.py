
# Bleed 2 - Color Aimbot
# Wayne Kenney 2018 (Pythogen)

# This aimbot automatically locks onto enemies by detecting pixel color locations 
# and automatically positioning your mouse,

# 1) Set enemy color(s) in variable OR array 
# 2) Run Aimbot

from PIL import Image
import pyautogui
from time import sleep
import sys


# Enemy Color (Blue Robot / First Level)
color = (29, 116, 165)

# (Mouse Position / Monitor Resolution) Calculation Variables
xCord = 0
yCord = 0


def main():
	while(True):
		cmd = raw_input("Enter Aimbot Command: ")
		cmd = cmd.lower()
		if cmd == "help":
			# List of Commands
			print "\nList of commands:\n\n  help\n  start  \n  exit\n"
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
	# Loop for process...
	while(True):
		# Take screenshots (Continuous Screen Captures)
		pic = pyautogui.screenshot()
		 
		# Save the image
		pic.save('img.png') 

		# Open image for analysis
		im = Image.open("img.png","r")

		# Set list with screenshot pixel colors
		pix_val = list(im.getdata())

		if color in pix_val:
			print pix_val.index(color)
			xCord = pix_val.index(color) / 1920
			yCord = pix_val.index(color) / 1080
			pyautogui.moveTo(yCord, xCord)
			print "%s:%s" %(xCord,yCord)
			print "True (Enemy Detected! Aiming...)"
		else:
			print "False (Enemy not detected)"

main()