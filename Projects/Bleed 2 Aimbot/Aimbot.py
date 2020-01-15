
#  _|_|_|                            _|_|                        _|            _|_|    _|                  _|                    _|      
#  _|    _|    _|_|    _|  _|_|    _|        _|_|      _|_|_|  _|_|_|_|      _|    _|      _|_|_|  _|_|    _|_|_|      _|_|    _|_|_|_|  
#  _|_|_|    _|_|_|_|  _|_|      _|_|_|_|  _|_|_|_|  _|          _|          _|_|_|_|  _|  _|    _|    _|  _|    _|  _|    _|    _|      
#  _|        _|        _|          _|      _|        _|          _|          _|    _|  _|  _|    _|    _|  _|    _|  _|    _|    _|      
#  _|          _|_|_|  _|          _|        _|_|_|    _|_|_|      _|_|      _|    _|  _|  _|    _|    _|  _|_|_|      _|_|        _|_|                                                                                                                                                                                                                                                                        
# Wayne Kenney (Pythogen) - 4/25/2018

#                                 ,----.___________,-,
#         ,__                    (________________|__|
#      __/()(_________________________/o(____)o(__  ``            _
#     (__________________________(_(_(_(_(________Y_....-----====//
#                   ( , , , , , , (______________)--            ((
#                    \_____________|________|[ )) JW  ____   __  \\
#                                   |____|    "" \.__-'`". \(__) \\\
#                                   |____|        `""      ```"""=,))
#                                   |    |
#                                    ====

# My aimbot configured to Bleed 2

# This aimbot automatically locks onto enemies by detecting pixel color locations 
# and automatically positioning your mouse. This script will continuously capture 
# desktop screeshots and scan those screenshots immediately after. If the target's
# pixel color is found, then the aimbot will calculate the screen coordinates and
# finally position your mouse directly over the target.

# Note: I've also developed a 3D shooter aimbot, but I'm not going to share it right away.
# My 3D shooter aimbot is almost perfect and I've configured it to GunZ 2 and MicroVolts using
# a brand new algorithm for instant color capturing. I'll share it soon!

# Note 2: This aimbot needs to be updated as well... Going to upload a full 2D/3D aimbot framework
# that is easily configured to any game with a built in detection box template selection feature.

# Full source code coming very soon...

# 1) Set enemy color(s) in variable OR array 
# 2) Run Aimbot

from PIL import Image
import pyautogui
from time import sleep
import sys

# Enemy Color (Blue Robot / First Level)
#color = (66, 183, 42) // Test color
color = (29, 116, 165)
color2 = (0, 73, 46)
color3 = (184, 44, 7)

# (Mouse Position / Monitor Resolution) Calculation Variables
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
	# Loop for process...
	while(True):
		# Take screenshots (Continuous Screen Captures)
		pic = pyautogui.screenshot()
		 
		# Save the image
		#pic.save('img.png') 

		# Open image for analysis
		#im = Image.open("img.png","r")

		# Set list with screenshot pixel colors
		pix_val = list(pic.getdata())

		# Blue enemy
		if color in pix_val:
			print "\nPixel index: %s" % (pix_val.index(color))
			print "Pixel total: %s" % (len(pix_val))
			xCord = pix_val.index(color) / 1920
			yCord = pix_val.index(color) % 1920


			pyautogui.moveTo(yCord, xCord)
			print "Mouse Coordinates: Y: %s , X: %s\n" %(xCord,yCord)
			print "True (Blue Detected! Aiming...)"
		# First Stage Boss
		elif color2 in pix_val:
			print "\nPixel index: %s" % (pix_val.index(color2))
			print "Pixel total: %s" % (len(pix_val))
			xCord = pix_val.index(color2) / 1920
			yCord = pix_val.index(color2) % 1920


			pyautogui.moveTo(yCord, xCord)
			print "Mouse Coordinates: Y: %s , X: %s\n" %(xCord,yCord)
			print "True (First Stage Boss Detected! Aiming...)"
		# First Stage Boss 2
		elif color3 in pix_val:
			print "\nPixel index: %s" % (pix_val.index(color3))
			print "Pixel total: %s" % (len(pix_val))
			xCord = pix_val.index(color3) / 1920
			yCord = pix_val.index(color3) % 1920


			pyautogui.moveTo(yCord, xCord)
			print "Mouse Coordinates: Y: %s , X: %s\n" %(xCord,yCord)
			print "True (First Stage Boss 2 Detected! Aiming...)"
		else:
			print "False (Enemy not detected)"

main()