
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
	Service = 'Newgrounds - Login'
	#Login URL
	login_URL = 'https://www.newgrounds.com/passport/mode/iframe/appsession/812703283236516b81e11ed4ddac931b30b292034ba228'
	#login_URL redirected to after login_URL containing keyword
	landing = 'http://www.newgrounds.com/bbs'
	#The keyword that indicates successful login_URL detection
	keyword = "user_logged_in', true)"

	#Display Banner
	print '\n%s\n' % (Service)

	#Authentication prompt
	USERNAME = raw_input("Username: ")
	PASSWORD = raw_input("Password: ")


#Go to main 
main()

#Console prompt after successful login
def cpPrompt():

	#Command line Construct. Add commands here..
	while(True):

		#Listen for command input
		cmd = raw_input('%s>' % (USERNAME))

		#Command Construct
		if cmd == '?':
			#Show list of commands
			print '\n- who (Users Online)\n- quit\n'
		elif cmd == 'who':
			#Call function to extract data between tags. Function name included in var for global access
			print '\n' + find_between( processReq.page.content,"Online: (<strong>","</strong>)" ) + '\n'
		elif cmd == 'quit':
			quit()
			
	
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
			'username' : USERNAME,
			'password' : PASSWORD,
			'remember' : 1,
			'login' : 1,
		}

		#Header data
		header_data = \
		{
			'Host': 'www.newgrounds.com',
			'Connection': 'keep-alive',
			'Content-Length': '455',
			'Accept': '*/*',
			'Origin': 'http://www.newgrounds.com',
			'X-Requested-With': 'XMLHttpRequest',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Referer': 'http://www.newgrounds.com/',
		}


		# 1) Direct to login url. Prepare for POST login
		c.get(login_URL)

		# 2) Submit POST data. Initialize login
		c.post(login_URL, data=login_data, headers=header_data)

		# 3) Landing page after login attempt. Function name as object. func.var = x
		processReq.page = c.get(landing)

		# 4) Looking for keyword indicating successful login
		Check = processReq.page.content.find(keyword)


		#Continuous auth checking. Line by line
		while(True):
			if Check == -1:
				print '\nlogin failed. (Try again)'
				#print processReq.page.content
				main()
				processReq()
			else:
				print '\nWelcome, ' + USERNAME + '\n'
				#Login success. Go to command console
				cpPrompt()


#Process Auth Details
processReq()