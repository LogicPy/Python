
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
	global landing
	global keyword
	global attempts

	#Site's Name (Banner)
	Service = 'NyDSD Login'
	#Login URL
	login_URL = 'http://www.nydsd.com/dx/cgi-bin/dxserver.cgi'
	#login_URL redirected to after login_URL containing keyword
	landing = 'http://www.nydsd.com/dx/cgi-bin/dxserver.cgi?SESSION=2ACA9E120F826F4FDE282A118F06ECE139B747BDB423563C7A0D1458417482FD52649233E510A1042EE617313FC8FD34&OPTION=OPTIONS'
	#The keyword that indicates successful login_URL detection
	keyword = '(url.indexOf("OPTION=OPTIONS")'
				
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
			'ID' : '',
			'Password' : '',
		}

		#Header data
		header_data = \
		{

		}

		r = requests.post(login_URL, data=login_data, headers=header_data)

		print r.text.encode("utf-8")

		check = r.text.encode("utf-8").find(keyword)

		if check == -1:
			print 'invalid'
		else:
			print '\n NY-DSD - Login Successful\n'
			loggedIn()

def loggedIn():

	print "\n Welcome!\n"

	while(True):
		cmd = raw_input("Enter selection: ")
		if cmd == '1':
			pass
		elif cmd == 'help':
			print '\n Commands:\n\n 1) 10-Day Sheet\n 2) Credit Memo \n 3) Boar\'s Head PO\n\n'
		elif cmd == "exit":
			sys.exit()
		else:
			print '\n Invalid Command. Type "help" for list of commands... \n'

#Go to main 
main()
#Process Auth Details
processReq()