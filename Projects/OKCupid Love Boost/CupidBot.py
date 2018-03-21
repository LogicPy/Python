
#  ___  _  _____          _    _   _                  ___              _   
# / _ \| |/ / __|  _ _ __(_)__| | | |   _____ _____  | _ ) ___  ___ __| |_ 
#| (_) | ' < (_| || | '_ \ / _` | | |__/ _ \ V / -_) | _ \/ _ \/ _ (_-<  _|
# \___/|_|\_\___\_,_| .__/_\__,_| |____\___/\_/\___| |___/\___/\___/__/\__|
#                   |_|                                                    

# Wayne Kenney - 2016

# OKCupid Love Booster - OKCupid Spider Bot
# Get attention by mass-browsing profiles!


#Modules
import requests
from random import randint
from time import sleep

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
	Service = 'OKCupid Love Booster'
	#Login URL
	login_URL = 'https://www.okcupid.com/login'
	#login_URL redirected to after login_URL containing keyword
	landing = 'https://www.okcupid.com/home'
	#The keyword that indicates successful login_URL detection
	keyword = 'sign-out'

	#Display Banner
	print ' _____ _____ _____         _   _    _____             _   '
	print '|     |  |  |     |_ _ ___|_|_| |  | __  |___ ___ ___| |_ '
	print '|  |  |    -|   --| | | . | | . |  | __ -| . | . |_ -|  _|'
	print '|_____|__|__|_____|___|  _|_|___|  |_____|___|___|___|_|  '
	print '                      |_|                                '
	print 'Wayne Kenney (github/pythogen) - Wayne.Cool'

	#Authentication prompt
	USERNAME = raw_input("\nEnter Username: ")
	PASSWORD = raw_input("Enter Password: ")


#Go to main 
main()

#Console prompt after successful login
def cpPrompt():
	global c

	pone = 'similar2015-users">  <a href="/profile/'
	ptwo = '?cf=profile_similar_2015'

	#Command line Construct. Add commands here..
	while(True):

		#Listen for command input
		cmd = raw_input('%s>' % (USERNAME))

		#Command Construct
		if cmd == '?':
			#Show list of commands
			print '\n- go (Start checking profiles..)\n- quit\n'

		#Start mass-search with 'go'
		elif cmd == 'go':

			# Profile Cycle Count
			cnt = 0

			#Search loop
			while(True):
	
			#Request Payloads:
			#[
				#RANDOM
				payload = '{"fields":"location,percentages,thumbs,userinfo","has_photo":1,"limit":5,"gentation":[34],"maximum_age":38,"minimum_age":20,"order_by":"RANDOM","use_looking_for_plus":true}'
			
				#'Online'
				#payload = '{"fields":"location,percentages,thumbs,userinfo","has_photo":1,"limit":5,"gentation":[34],"maximum_age":38,"minimum_age":20,"order_by":"LOGIN","use_looking_for_plus":true}'
			#]
				
				#POST data, 
				processReq.page = c.post("https://www.okcupid.com/1/apitun/match/search",data=payload,headers=header_data_2)

				#Username Extraction Values (Username found between these values)
				pone = 'name" : "'
				ptwo = '",'

				#Extract Username, put in 'grab' variable...
				grab =  find_between( processReq.page.content, pone, ptwo)

				print "\nUsername %s found. Visiting profile.." % (grab)
				
				#Setup get query
				go = 'https://www.okcupid.com/profile/%s' % (grab)
				
				cnt = cnt + 1

				print "%s - %s" % (go,cnt)

				#Check profile
				processReq.page = c.get(go)
				#Pause 
				#sleep(1)


		#Command to exit 'quit'
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
	global c
	global search_data
	global header_data_2

	with requests.Session() as c:
	

		#POST Login data
		login_data = \
		{
			'okc_api': '1',
			'password': PASSWORD,
			'username': USERNAME,


		}

		#POST Love Search Data
		search_data = \
		{
			'use_looking_for_plus': 'true',
			'order_by': '"RANDOM"',
			'minimum_age': '20',
			'maximum_age': '38',
			'limit': '5',
			'has_photo': '1',
			'gentation': '[34]',
			'fields': '"location,percentages,thumbs,userinfo"',
		}

		#Header data for Login
		header_data = \
		{
			'x-requested-with': 'XMLHttpRequest',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
			'referer': 'https://www.okcupid.com/',
			'origin': 'https://www.okcupid.com',
			'content-length': '53',
			'cookie': '__cfduid=d162876423501e7f6aaaba0277604cf6d1462060557; override_session=0; authlink=4d0381a5; secure_check=1; guest=14396167291447722984; secure_login=0; signup_exp_2014_09_13=2014_simpleblue; nano=k%3Diframe_prefix_lock_1%2Ce%3D1462068078998%2Cv%3D1',
			'accept-language': 'en-US,en;q=0.8',
			'accept-encoding': 'gzip, deflate',
			'accept': 'application/json, text/javascript, */*; q=0.01',
			'scheme': 'https',
			'path': '/login',
			'method': 'POST',
			'authority': 'www.okcupid.com',

		}

		#Header data for Love Search
		header_data_2 = \
		{
			'x-requested-with': 'XMLHttpRequest',
			'x-okcupid-platform': 'DESKTOP',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
			'referer': 'https://www.okcupid.com/home',
			'origin': 'https://www.okcupid.com',
			'cookie': '__cfduid=d35ac5e1ac16c2a8b354737b6f637fb921465003664; authlink=4d0381a5; signup_exp_2014_09_13=2014_simpleblue; override_session=0; secure_login=1; secure_check=1; session=2307226958307333179%3a10375088598156584158; nano=k%3Diframe_prefix_lock_1%2Ce%3D1467474089059%2Cv%3D1%7Ck%3Diframe_prefix_lock_2%2Ce%3D1467474158259%2Cv%3D1',
			'content-type': 'application/json; charset=UTF-8',
			'content-length': '172',
			'authorization': 'Bearer 1,0,1467559551,0x2004eab1c21d143b;63eab68cc4ed4cf0907bfd4919c78b74658aba76',
			'accept-language': 'en-US,en;q=0.8',
			'accept-encoding': 'gzip, deflate, br',
			'accept': 'application/json, text/javascript, */*; q=0.01',
			'scheme': 'https',
			'path': '/1/apitun/match/search',
			'method': 'POST',
			'authority': 'www.okcupid.com',

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