
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# Frame.py:

# Modules
import requests
from random import randint
import time
import os

# Program Information
print '\n(Powered by PyAqua-1.0 Framework - Wayne Kenney)'

# Main Routine.
def main():

	# Enable access to variables anywhere
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global land
	global keyword
	global attempts

	# Site's Name (Banner)
	Service = 'WordPress Version - Check'

	# Read urls (home base directory) from text file
	# index dir (wp_content accessible)
	# Ex: http://server.com/
	text_file = open("list.txt", "r")

	# split out new line in each array element
	# and put in variable 'land'
	land = text_file.read().split('\n')

	# Define username
	USERNAME = raw_input("\n[?] Enter console handle: ")
	#USERNAME = 'Pythogen'

# Display Banner
print '__      _____  __   __                ___ _           _    '
print '\ \    / / _ \ \ \ / /__ _ _   ___   / __| |_  ___ __| |__ '
print ' \ \/\/ /|  _/  \ V / -_)  _| |___| | (__|   \/ -_) _| / / '
print '  \_/\_/ |_|     \_/\___|_|          \___|_||_\___\__|_\_\ '
                                                                                                
# Go to main routine
main()

def cmdList():

	# Call function to extract data between tags. Function name included in var for global access
	# Cycle for loop from 0 to size of array
	for i in range(0, len(land)):

		# Home directory contained in array for display in console
		home = land[i]

		# Concatenate for landing page
		land[i] = land[i] + '/wp-login.php?'

		# Get from next link in array
		processReq.page = c.get(land[i])

		# Fully extracted source
		src = processReq.page.content

		# Grab version number inbetween specific elements
		elOne = "buttons.min.css?ver="
		elTwo = "' type='text/css'"

		# Check and print
		print '\nSite: %s\n[i] Version: [ ' % (home) + find_between(src, elOne, elTwo ) + ' ]\n'

# Console prompt
def cpPrompt():

	# Command line Construct. Add commands here..
	cmdList()

	# Finished checking. Go to prompt
	print '\n[!] Check complete.\n'

	while(True):

		# Listen for command input
		cmd = raw_input('%s>' % (USERNAME))

		# Check
		if cmd == "?":
			cmdList()

		# Exit
		elif cmd == 'quit':
			quit()

# Clipboard function [Not used in this script..]
def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)
	
# Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def processReq():

	# Shorten method
	global c
	with requests.Session() as c:
	
		while(True):

			# Greetings friend
			print '\n - Welcome, ' + USERNAME + '.\n'

			# Starting..
			print '\n[!] Grabbing from list...\n'

			# Go to command console
			cpPrompt()


# Process Auth Details
processReq()
 

