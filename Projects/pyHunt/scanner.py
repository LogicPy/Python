import socket
import random
import time
import errno
from threading import Thread
import os
from datetime import datetime

print '  _____         _     _                _   '
print ' (_____)       (_)   (_)        _     (_)_ '
print ' (_)__(_)_   _ (_)___(_) _   _ (_)__  (___)'
print ' (_____)(_) (_)(_______)(_) (_)(____) (_)  '
print ' (_)    (_)_(_)(_)   (_)(_)_(_)(_) (_)(_)_ '
print ' (_)     (____)(_)   (_) (___) (_) (_) (__)'
print '          __(_)                            '    
print '         (___)              Pythogen	   \n' 

# Check start variable
chStart = 0
n=0
arr=[]

def Main():
	global oct1
	global oct2
	global oct3
	global oct4
	global portNum
	global chStart
	oct1 = random.randint(20,120)
	oct2 = random.randint(1,255)
	oct3 = random.randint(1,255)
	oct4 = random.randint(1,255)

	# Check start condition
	if chStart == 0:
		chStart = 1
		portNum = raw_input("\n Select port: ")
		print ''


def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)


def Scan():
	global ipGen
	global portNum
	global arr
	global n
	global timestamp

	# s as socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Increase scan speed by setting timeout

	dateTimeObj = datetime.now()

	# if port 80 scan faster otherwise... take it slow.. ;)
	if portNum == str(80):
		s.settimeout(0.25)
	
	else:
		s.settimeout(0.50)

	try:
		# Connection Attempt
		s.connect((ipGen,int(portNum)))
	except socket.error as e:
		# Connection Fail output
		print ' - Connection failed on %s.. - Timestamp : %s - ' % (ipGen,dateTimeObj)
	else:
		# Connection Success output
		print ' - Connection success! on %s - Timestamp : %s -  [%s]' % (ipGen,i,dateTimeObj)
		print '\n\n'
		print ' ___                             ___ '
		print '|  _|   _____               _   |_  |'
		print '| |    |   __|___ _ _ ___ _| |    | |'
		print '| |    |   __| . | | |   | . |    | |'
		print '| |_   |__|  |___|___|_|_|___|   _| |'
		print '|___|                           |___|'
		print '\n\n'
		#data = s.recv(500)
		#print data
		n = n + 1
		# current date and time

		#try:
		#	print " - Output Data: %s" % (data)
		#except:
		#	print " - Error on output.. Woopsi! Heh heh!"

		print ' - inserted into index : ' + str(n)
		arr.insert(n, ipGen)

		# Add successful IP to clipboard
		addToClipBoard(ipGen)
		

def Start():
	global oct1
	global oct2
	global oct3
	global oct4
	global ipGen
	global i

	print "\n - Configured with 9999 cycles.\n"

	for i in xrange(9999):
		ipGen = '%s.%s.%s.%s' % (oct1, oct2, oct3, oct4)
		#ipGen = '113.66.62.24'
		print ' [%s]Scanning %s.' % (i,ipGen)
		#t = Thread(target=Scan, args=())
		#t.start()
		Scan()
		Main()


def Finished():
	global arr
	global n
	global ipGen

	print '\n[Finished]'

	print "Found %s boxes... - %s" % (str(n),ipGen)

	for i in arr:
		print i

	fin = raw_input("\nScan Complete. Press ENTER to exit...\n")

Main()
Start()
Finished()