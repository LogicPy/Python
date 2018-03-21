import socket
import random
import time
import errno
from threading import Thread
import os


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

	# s as socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Increase scan speed by setting timeout
	s.settimeout(0.5)

	try:
		# Connection Attempt
		s.connect((ipGen,int(portNum)))
	except socket.error as e:
		# Connection Fail output
		print ' - Connection failed on %s..' % (ipGen)
	else:
		# Connection Success output
		print ' - Connection success! on %s! - [%s]' % (ipGen,i)
		print '\n\n'
		print ' ___                             ___ '
		print '|  _|   _____               _   |_  |'
		print '| |    |   __|___ _ _ ___ _| |    | |'
		print '| |    |   __| . | | |   | . |    | |'
		print '| |_   |__|  |___|___|_|_|___|   _| |'
		print '|___|                           |___|'
		print '\n\n'
		#data = s.recv(1024)
		#print data
		x = raw_input("Press ENTER to Copy Address and resume..\n")
		# Add successful IP to clipboard
		addToClipBoard(ipGen)
		

def Start():
	global oct1
	global oct2
	global oct3
	global oct4
	global ipGen
	global i

	for i in xrange(900):
		ipGen = '%s.%s.%s.%s' % (oct1, oct2, oct3, oct4)
		#ipGen = '113.66.62.24'
		print ' [%s]Scanning %s.' % (i,ipGen)
		#t = Thread(target=Scan, args=())
		#t.start()
		Scan()
		Main()


def Finished():
	print '\n[Finished]'
	fin = raw_input("\nScan Complete. Press ENTER to exit...\n")

Main()
Start()
Finished()