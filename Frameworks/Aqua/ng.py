
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# Frame.py:

#Modules
import requests
from random import randint
import time
import sys

#Program Information
print '\nPyAqua-1.0 - Requests Module Prototype\nBy Pythogen'

#Main Routine.
def main():

	#Enable access to variables ANYWHERE
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global keyword
	global attempts

	#Site's Name (Banner)
	Service = 'NG Login'
	#Login URL
	login_URL = 'https://www.newgrounds.com/passport/mode/iframe/appsession/6b0d0754007b51a9c2fb7ed373862203481c2cdb1f247a'
	#The keyword that indicates successful login_URL detection
	keyword = 'You have successfully signed in!'
				
#Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def processReq():
	#Shorten method
	with requests.Session() as c:
	

		#POST Login data
		login_data = \
		{
			'username': '',
			'password': '',
			'remember': '1',
			'login': '1'
		}

		#Header data
		header_data = \
		{

		}

		r = requests.post(login_URL, data=login_data, headers=header_data)

		#print r.text.encode("utf-8")

		check = r.text.encode("utf-8").find(keyword)

		if check == -1:
			print '\n invalid \n'
		else:
			loggedIn()

def loggedIn():

	print "\n Welcome!\n"

	while(True):
		cmd = raw_input("Enter selection: ")
		if cmd == '1':
			pass
		elif cmd == "exit":
			sys.exit()
		else:
			print '\n Invalid Command. \n'

#Go to main 
main()
#Process Auth Details
processReq()