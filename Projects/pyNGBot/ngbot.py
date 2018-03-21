#Wayne Kenney 2015 

import requests
from random import randint
import time
import re

def judgeEm():
	global pointMe
	global NumCTRL

	if pointMe == 5 or pointMe == 6:

		NGDir = ['games','movies']
		Genre = ''

		url2 = 'http://www.newgrounds.com/portal/vote'

		if NumCTRL == 0:
			url5 = 'http://www.newgrounds.com/%s/under_judgment' % (NGDir[0])
			NumCTRL = 1
			Genre = 'Games'
			#print 'Testing.... : %s' % NGDir[0]
		elif NumCTRL == 1:
			url5 = 'http://www.newgrounds.com/%s/under_judgment' % (NGDir[1])
			NumCTRL = 0
			Genre = 'Movies'
			#print 'Testing.... : %s' % NGDir[1]

	
		judge = c.get(url5)
		judged = find_between( judge.content,'	<a href="','">' )
		judged = 'http://www.newgrounds.com%s' % judged

		stuffPage = c.get(judged)
		ukey = find_between(stuffPage.content,'userkey" value="','/> <input ty')
		ukey = ukey[:-1]
		titleName = find_between( stuffPage.content,'<title>','</title>')
		voteseed = find_between( stuffPage.content, 'vote_seed" value', '/>' )
		voteseed = voteseed[:-1]
		voteseed = voteseed[2:]
		votekey = find_between( stuffPage.content, 'vote_key" value', '/>' )
		votekey = votekey[:-1]
		votekey = votekey[2:]
		voteGO = find_between( stuffPage.content, 'v0">', '>' )
		voteFin = find_between( voteGO, 'value="', '/' )
		voteFin = voteFin[:-1]
		subID = find_between( stuffPage.content,'submission_id" value=','/>')
		subID = subID[:-1]
		subID = subID[1:]

		head2 = {
			'Host': 'www.newgrounds.com',
			'Connection': 'keep-alive',
			'Content-Length': '455',
			'Accept': '*/*',
			'Origin': 'http://www.newgrounds.com',
			'X-Requested-With': 'XMLHttpRequest',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Referer': 'http://www.newgrounds.com/portal/view/664703',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US,en;q=0.8',
			# Dynamic
			'Cookie': '__cfduid=d0280b2e5603e61a0490ee49b0597f5e61443492016; __gads=ID=4a8bdbdfc8c587f7:T=1444621581:S=ALNI_MaYZGDCKYqVCpTSOOag-lGSiF2bzQ; ng_adcode_country_id=2; remember_me_checkbox=1; __utma=1.626776772.1446153177.1446251722.1447816297.4; __utmz=1.1447816297.4.4.utmcsr=newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/portal/view/666222; vmk1du5I8m=G8EbR5mA0MIqgtM12Zz80%2FFTHwI_knBAbcPKNrw3LNehDm3U8ckqJVKi%2FyLtcNpbb8LVBFw7UQYptTCxmPLAKuGrH2DM6ZYoYROXJ8uMdc4W6airAoT6ly1r7lInqZH6jh3AE6E86WnGvsAsJzwTmy_qXWG4qAk7otRBeFfpto0%3D; NGBBS_timestamp=1447984270; NGBBS_last_visit=1447962509; __utmt=1; __utma=158261541.131652178.1443499216.1447962507.1447984268.116; __utmb=158261541.3.10.1447984268; __utmc=158261541; __utmz=158261541.1447813910.111.13.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __pRlCldnABP__=1447984280; __pRlCldn__=1447984280; __pRlCDf665109__=1447984280; vmkIdu5l8m=1AgQYsED2XUZdK64gE0pb1ep3_HRRpKtMsVblojMJV7E5ErdljlHc0LcIjJY7v0rw2C1tHcbyJR2pfPNVnymzFXPGxw44xML72F3ZCwAaSKVP03Xnfe4N8DggsdwW7PXn8hijG4tJYgVOAfgpYLfnUT2vyKWBjXvAVBUBq7jMq4%3D; NG_GG_username=Wayne; ng_user0=a%3A2%3A%7Bs%3A7%3A%22default%22%3Ba%3A0%3A%7B%7Ds%3A12%3A%22Flash_portal%22%3Ba%3A1%3A%7Bs%3A21%3A%22suitabilities_to_view%22%3Ba%3A3%3A%7Bi%3A0%3Bs%3A1%3A%22e%22%3Bi%3A1%3Bs%3A1%3A%22t%22%3Bi%3A2%3Bs%3A1%3A%22m%22%3B%7D%7D%7D',
		}
		data2={
			'userkey': ukey,
			'vote_seed': voteseed,
			'vote_key': votekey,
			'item_id': subID,
			'portal_id': '1',
			'vote': voteFin,
			}

		r = requests.post(url2, headers=head2, data=data2)

		#Check status code between 200 and 403
		if r.status_code==200:
			#Resume vote if 200 is found
			print '\n [ Blamming: ' + judged + ' at ' + (time.strftime("%I:%M:%S") + ' ]')
			print ' [ Title: %s ]' % titleName
			print ' [ Genre: %s ]' %  Genre
			

			getoutp = r.text
			getoutp2 = r.text
			#Text between tags to display message
			getoutp = find_between( getoutp,'<\/strong>! ','<\/strong><\/p>')
			#Text between tags to display vote power
			getoutp2 = find_between( getoutp2,'orth <strong>','<\/strong> v')

			#print '\n'
		else:
			if pointMe == 5:
				print ' \n[You\'ve already fired upon this target. Hold the canons..]\n'

		if pointMe == 6:
			time.sleep(60)
			judgeEm()
		else:
			pointMe = 0


def myInfo():
	infURL = 'http://wayne.newgrounds.com/stats'
	getInf = c.get(infURL)
	expInf = find_between( getInf.content, '<dt>Exp. Points</dt>', '</dd>' )
	lvlInf = find_between( getInf.content, '<dt>Level</dt>', '</dd>' )
	voteInf = find_between( getInf.content, '<dt>Vote Power</dt>', '</dd>' )
	blamInf = find_between( getInf.content, '<dt>Blams</dt>', '</dd>' )
	saveInf = find_between( getInf.content, '<dt>Saves</dt>', '</dd>' )
	expInf = expInf[5:]
	lvlInf = lvlInf[5:]
	voteInf = voteInf[5:]
	blamInf = blamInf[5:]
	saveInf = saveInf[5:]
	print '\nLevel: %s' % (lvlInf)
	print 'Experience Points: %s' % (expInf)
	print 'Vote Power: %s' % (voteInf)
	print 'Blams: %s' % (blamInf)
	print 'Saves: %s\n' % (saveInf)
	


def rapidGo():
	print '\nRapid vote activated.\n'
	while(True):
		time.sleep(1)
		v0te()

def cpTime():
	print '\nTimed votes activated.\nTimer set to 5 minutes.\n'
	while(True):
		time.sleep(300)
		v0te()

def cpPrompt():
	global pointMe

	while(True):
		cmd = raw_input('Enter command: ')
		if cmd == '?':
			#Commands and their descriptions
			print ('\n- vote (Vote on random entry)'
				'\n- timed (Vote on random entry every five minutes)\n- '
				 'rapid (Rapidly vote on random entry)\n- '
				 'info (Display your user information)\n- '
				 'blam (Blam first new upload)\n- '
				 'blam.all (Blam all entries under judgement)\n- '
				 'blam.bot (Waits for new upload then blams it)\n')
		elif cmd == 'vote':
			pointMe = 1
			v0te()
		elif cmd == 'timed':
			pointMe = 2
			cpTime()
		elif cmd == 'rapid':
			pointMe = 3
			rapidGo()
		elif cmd == 'blam.all':
			pointMe = 4
			v0te()
		elif cmd == 'info':
			myInfo()
		elif cmd == "judge":
			pointMe = 5
			judgeEm()
		elif cmd == 'blam.bot':
			pointMe = 6
			judgeEm()
		#elif cmd == 'my':
			#pointMe = 5
			#v0te()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def v0te():
	#Vote Routine
	global numy
	global pointMe

	url4 = 'http://www.newgrounds.com/portal'
	portal = c.get(url4)
	newPort = find_between( portal.content,'<h4>Vote on their entry rank!</h4>', '<script type="text/javascript">')
	if numy < 10:
		stuffPortal = find_between( newPort,'0%s<a href="' % (numy),' class=' )
		stuffPortal = stuffPortal[:-1]
	else:
		stuffPortal = find_between( newPort,'%s<a href="' % (numy),' class=' )
		stuffPortal = stuffPortal[:-1]
	
	numy=numy+1

	url2 = 'http://www.newgrounds.com/portal/vote'
	iid = (randint(500000,700000))

	if pointMe <= 3:
		url3 = 'http://www.newgrounds.com/portal/view/%s' % (iid) 
	elif pointMe == 4:
		url3 = stuffPortal
		url3 = 'http://www.newgrounds.com%s' % (stuffPortal) 
	# Optional for specifics	
	#elif pointMe == 5:
		#arStr = main.myArt[2]
		#url3 = 'http://www.newgrounds.com/portal/view/%s' % (arStr)


	stuffPage = c.get(url3)
	ukey = find_between(stuffPage.content,'userkey" value="','/> <input ty')
	ukey = ukey[:-1]
	titleName = find_between( stuffPage.content,'<title>','</title>')
	voteseed = find_between( stuffPage.content, 'vote_seed" value', '/>' )
	voteseed = voteseed[:-1]
	voteseed = voteseed[2:]
	votekey = find_between( stuffPage.content, 'vote_key" value', '/>' )
	votekey = votekey[:-1]
	votekey = votekey[2:]
	voteGO = find_between( stuffPage.content, 'v0">', '>' )
	voteFin = find_between( voteGO, 'value="', '/' )
	voteFin = voteFin[:-1]
	subID = find_between( stuffPage.content,'submission_id" value=','/>')
	subID = subID[:-1]
	subID = subID[1:]

	head2 = {
		'Host': 'www.newgrounds.com',
		'Connection': 'keep-alive',
		'Content-Length': '455',
		'Accept': '*/*',
		'Origin': 'http://www.newgrounds.com',
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Referer': 'http://www.newgrounds.com/portal/view/664703',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'en-US,en;q=0.8',
		# Dynamic
		'Cookie': '__cfduid=d0280b2e5603e61a0490ee49b0597f5e61443492016; __gads=ID=4a8bdbdfc8c587f7:T=1444621581:S=ALNI_MaYZGDCKYqVCpTSOOag-lGSiF2bzQ; ng_adcode_country_id=2; remember_me_checkbox=1; __utma=1.626776772.1446153177.1446251722.1447816297.4; __utmz=1.1447816297.4.4.utmcsr=newgrounds.com|utmccn=(referral)|utmcmd=referral|utmcct=/portal/view/666222; vmk1du5I8m=G8EbR5mA0MIqgtM12Zz80%2FFTHwI_knBAbcPKNrw3LNehDm3U8ckqJVKi%2FyLtcNpbb8LVBFw7UQYptTCxmPLAKuGrH2DM6ZYoYROXJ8uMdc4W6airAoT6ly1r7lInqZH6jh3AE6E86WnGvsAsJzwTmy_qXWG4qAk7otRBeFfpto0%3D; NGBBS_timestamp=1447984270; NGBBS_last_visit=1447962509; __utmt=1; __utma=158261541.131652178.1443499216.1447962507.1447984268.116; __utmb=158261541.3.10.1447984268; __utmc=158261541; __utmz=158261541.1447813910.111.13.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __pRlCldnABP__=1447984280; __pRlCldn__=1447984280; __pRlCDf665109__=1447984280; vmkIdu5l8m=1AgQYsED2XUZdK64gE0pb1ep3_HRRpKtMsVblojMJV7E5ErdljlHc0LcIjJY7v0rw2C1tHcbyJR2pfPNVnymzFXPGxw44xML72F3ZCwAaSKVP03Xnfe4N8DggsdwW7PXn8hijG4tJYgVOAfgpYLfnUT2vyKWBjXvAVBUBq7jMq4%3D; NG_GG_username=Wayne; ng_user0=a%3A2%3A%7Bs%3A7%3A%22default%22%3Ba%3A0%3A%7B%7Ds%3A12%3A%22Flash_portal%22%3Ba%3A1%3A%7Bs%3A21%3A%22suitabilities_to_view%22%3Ba%3A3%3A%7Bi%3A0%3Bs%3A1%3A%22e%22%3Bi%3A1%3Bs%3A1%3A%22t%22%3Bi%3A2%3Bs%3A1%3A%22m%22%3B%7D%7D%7D',
	}
	data2={
		'userkey': ukey,
		'vote_seed': voteseed,
		'vote_key': votekey,
		'item_id': subID,
		'portal_id': '1',
		'vote': voteFin,
		}

	r = requests.post(url2, headers=head2, data=data2)

	#Check status code between 200 and 403
	if r.status_code==200:
		#Resume vote if 200 is found
		print '\nVoting on submission...\n'
		print 'Details:\n\nTitle: %s \n\nItem ID: %s' % (titleName, iid)
		print 'Vote_seed: %s' % (voteseed)
		print 'Vote_key: %s' % (votekey)
		print 'Vote: %s \n' % (voteFin)

		getoutp = r.text
		getoutp2 = r.text
		#Text between tags to display message
		getoutp = find_between( getoutp,'<\/strong>! ','<\/strong><\/p>')
		#Text between tags to display vote power
		getoutp2 = find_between( getoutp2,'orth <strong>','<\/strong> v')
		#Show data
		print '\n' + getoutp +'\n\n' + 'Vote Power: ' + getoutp2

		print '\nVote complete.\n'
		print (time.strftime("%I:%M:%S"))
		print '\n'
	else:
		#Restart vote if 403 is found
		v0te()

	if pointMe == 1:
		cpPrompt()
	elif pointMe == 2:
		cpTime()
	elif pointMe == 3:
		rapidGo()
	elif pointMe == 4:
		time.sleep(1)
		if numy <= 75:
			v0te()
		else:
			numy = 1
			cpPrompt()
	#elif pointMe == 5:
		#cpPrompt()

def main():
	global USERNAME
	global PASSWORD
	global pointMe
	global numy
	global NumCTRL

	#main.myArt = ['636683','593455','569806','565387','565098','563490','511436','533442']

	pointMe = 0
	numy = 1
	NumCTRL = 0

	print '\n'
	print ' _____                                 _         _       _   '
	print '|   | |___ _ _ _ ___ ___ ___ _ _ ___ _| |___ ___| |_ ___| |_ '
	print '| | | | -_| | | | . |  _| . | | |   | . |_ -|___| . | . |  _|'
	print '|_|___|___|_____|_  |_| |___|___|_|_|___|___|   |___|___|_|  '
	print '                |___|'
	print 'By Pythogen\n'

	USERNAME = raw_input("Enter Username: ")
	PASSWORD = raw_input("Enter Password: ")


main()

with requests.Session() as c:

	#For login
	url = 'https://www.newgrounds.com/passport/mode/iframe/appsession/32505dee0326519102fa0b3385c79d06bcfa37ee3e06ef'
	c.get(url)
	login_data = dict(username = USERNAME, password = PASSWORD, remember = 1, login = 1)
	c.post(url, data=login_data, headers={"Referer" : "https://www.newgrounds.com/"})
	#To confirm login
	page = c.get('https://www.newgrounds.com/')
	Check = page.content.find("loggedin")
	#Confirmation Condition
	if Check == -1:
		print 'Login failed...'
	else:
		print '\nWelcome, ' + USERNAME + '\n'
		cpPrompt()
