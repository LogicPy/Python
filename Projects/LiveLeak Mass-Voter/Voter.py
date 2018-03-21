
# _      _           _                _    
#| |    (_)         | |              | |   
#| |     ___   _____| |     ___  __ _| | __
#| |    | \ \ / / _ \ |    / _ \/ _` | |/ /
#| |____| |\ V /  __/ |___|  __/ (_| |   < 
#|______|_| \_/ \___|______\___|\__,_|_|\_\                                                                                   
#__      __   _              _   _      _   
#\ \    / /  | |            | \ | |    | |  
# \ \  / /__ | |_ ___ ______|  \| | ___| |_ 
#  \ \/ / _ \| __/ _ \______| . ` |/ _ \ __|
#   \  / (_) | ||  __/      | |\  |  __/ |_ 
#    \/ \___/ \__\___|      |_| \_|\___|\__|
# By Wayne Kenney

# Mass-UP/DOWN Voter

# Frame.py:

#Modules
import requests
from random import randint
import time
from tqdm import tqdm

#Program banner
print '\n'
print '     -------------------------'
print '    -                        -'
print '   -  LiveLeak VoteNet      -'
print '  -                        -'
print '  -------------------------' 

def Complete():
	#Indicate completion
	ext = raw_input("\n Operation Complete! Press Enter to exit..\n")

#Console prompt
def cpPrompt():
	global c
	global commentID
	global head2
	global logout_URL
	global header_data
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global landing
	global keyword
	global attempts
	global head2
	global logout_URL
	global sel

	#Site's Name (Banner)
	Service = 'LiveLeak - VoteNet'
	#Login URL
	login_URL = 'http://www.liveleak.com/index.php'
	#Logout URL
	logout_URL = 'http://www.liveleak.com/?a=logout'
	#login_URL redirected to after login_URL containing keyword
	landing = 'http://www.liveleak.com/index.php'
	#The keyword that indicates successful login_URL detection
	keyword = 'Logout'

	#Store Comment ID for processing
	commentID = raw_input("\n Enter Comment ID: ")
	#Select Vote Type (Either UP or DOWN vote)
	seltype = raw_input(" Vote 'up' or 'down'?: ")
	print " "
	if seltype == "up":
		print " Powering up!\n"
	elif seltype == "down":
		print " Dropping the nuke!\n"

	#Change from 3 to however many bots you include
	#You can add/cycle as many bots as you'd like
	for sel in tqdm(range(1,3)):

		with requests.Session() as c:

			#Header data
			header_data = \
			{
				#Not needed
			}

			if seltype == "down":
				#Request headers for DOWN vote
				data2 = {
						'ajax': '1',
						'rating': '-1',
						'comment_id': commentID,
						'a': 'rate_comment',
						}

			elif seltype == "up":
				#Request headers for UP vote
				data2 = {
						'ajax': '1',
						'rating': '1',
						'comment_id': commentID,
						'a': 'rate_comment',
						}

			#First declare link where POST will happen
			theCom = 'http://www.liveleak.com/comment?a=rate_comment&comment_id=%s&rating=-1&ajax=1' % (commentID)

			#Cycle logins 

			#Bot number 1
			if sel == 1:

				head2 = {
					#Configure header
					'X-Requested-With': 'XMLHttpRequest',
					'Accept-Language': 'en-US,en;q=0.8',
					'Accept-Encoding': 'gzip, deflate, sdch',
					'Accept': 'application/json, text/javascript, */*; q=0.01',
						}
				#Include login details bot 1
				USERNAME = 'username'
				PASSWORD = 'password'

			#Bot number 2
			elif sel == 2:

				head2 = {
					#Configure header
					'X-Requested-With': 'XMLHttpRequest',
					'Accept-Language': 'en-US,en;q=0.8',
					'Accept-Encoding': 'gzip, deflate, sdch',
					'Accept': 'application/json, text/javascript, */*; q=0.01',
						}
				#Include login details for bot 2
				USERNAME = 'username'
				PASSWORD = 'password'

				#And so on....
				#Add more bots by copying and pasting condition for sel==3, then 4, 5, etc...
				#ADD more bots manually:
			#elif sel == 3:


			#Login form data
			login_data = \
			{
				'user_name': USERNAME,
				'user_password': PASSWORD,
				'login': '1',
			}

			#Logout form data
			logout_data = \
			{
				'a': 'logout',
			}

			# 1) [Login] Direct to login url. Prepare for POST login
			c.get(login_URL)

			# 2) [Login] Submit POST data. Initialize login
			c.post(login_URL, data=login_data, headers=header_data)

			# 3) [Login] Landing page after login attempt. Function name as object. func.var = x
			c.get(landing)

			# 4) [Vote] POST data
			c.post(theCom, headers=head2, data=data2)
			
			# 5) [Logout] POST Logout
			c.post(logout_URL, data=logout_data, headers=header_data)		

# Operation
cpPrompt()
# Completion Notice
Complete()