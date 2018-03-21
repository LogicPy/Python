# Wayne Kenney - 2016

# Plenty of Fish - Profile Spider
# Get attention by mass-browsing

#Modules
import requests
from random import randint
from time import sleep

#Program Information
print '\nPyAqua-1.0 - Requests Module Prototype\nBy Pythogen'

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
	Service = 'POF Spider'
	#Login URL
	login_URL = 'https://www.pof.com/processLogin.aspx'
	#login_URL redirected to after login_URL containing keyword
	landing = 'http://www.pof.com/'
	#The keyword that indicates successful login_URL detection
	keyword = 'Logout'

	#Display Banner
	print '\n%s\n' % (Service)

	#Authentication prompt
	USERNAME = raw_input("Username: ")
	PASSWORD = raw_input("Password: ")


#Go to main 
main()

#Console prompt after successful login
def cpPrompt():
	global c

	pone = "<a href='viewprofile.aspx?profile_id="
	ptwo = "' >"

	#Command line Construct. Add commands here..
	while(True):

		#Listen for command input
		cmd = raw_input('%s>' % (USERNAME))

		#Command Construct
		if cmd == '?':
			#Show list of commands
			print '\n- go (Start checking profiles..)\n- quit\n'

		elif cmd == 'go':
			# Initiate
			while(True):
				# Get profile ID
				processReq.page = c.get('http://www.pof.com/inbox.aspx')
				grab =  find_between( processReq.page.content, pone, ptwo) + '\n'
				# Setup get query
				go = 'http://www.pof.com/viewprofile.aspx?profile_id=%s' % (grab)
				print go
				# Check profile
				processReq.page = c.get(go)
				# Pause for 1 second
				sleep(1)

		elif cmd == 'quit':
			quit()
			
	
#Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def processReq():
	#Shorten method
	global c
	with requests.Session() as c:
	

		#POST Login data
		login_data = \
		{
			'login': '',
			'tfset': '240',
			'sid': 'rrfrxhoodhkpgdk50ulyfkaq',
			'password': PASSWORD,
			'username': USERNAME,
			'url': '',

		}

		#Header data
		header_data = \
		{
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
			'Upgrade-Insecure-Requests': '1',
			'Referer': 'http://www.pof.com/inbox.aspx',
			'Origin': 'http://www.pof.com',
			'Host': 'www.pof.com',
			'Cookie': 'ft=Thursday, April 28, 2016 6:39:19 PM; installid=ae58ae64-b5af-4ec1-a561-3d227d1916c8; isfirstrun=everyoneonline.aspx; my_ipcountry=1; username=WayneKenneyy; user_idb=129008014; usernameb=WayneKenneyy; tmp_track=129008014; pof_cookie=id_129008014__79_5545__89_4259462418; ASP.NET_SessionId=rrfrxhoodhkpgdk50ulyfkaq; POFIMSession=635974982832470010; isfirstrun_mmv=meetme.aspx; t_user_id=129008014; __utma=181982502.1458391091.1461893952.1461926258.1461953365.4; __utmb=181982502.5.9.1461953575493; __utmc=181982502; __utmz=181982502.1461896824.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=181982502.|2=intent=want%20to%20date%20but%20nothing%20serious=1^3=age=26=1^4=Gender=Male%20United%20States=1; _gat=1; ingres=appSessionIDPrefix=bfbd5adf-9abf-4c31-abcb-bff305d4386f; _ga=GA1.2.1458391091.1461893952',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Content-Length': '97',
			'Connection': 'keep-alive',
			'Cache-Control': 'max-age=0',
			'Accept-Language': 'en-US,en;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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
				print '\nWelcome, ' + USERNAME + '\n'
				#Login success. Go to command console
				cpPrompt()


#Process Auth Details
processReq()