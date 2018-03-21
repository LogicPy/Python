
# Wayne Kenney - 2016

# Hard-Drive Mapper (sPyder)

# This script creates text logs of the OS file structure,

# Mapping all exe, txt, doc, docx, lnk, jpg, bmp and png files.

# Monitor Activity (Optional):

# Logs/Records active windows 

# Import Modules
import os
import subprocess
import shutil
import requests
from time import sleep
import urllib
import win32gui
from ctypes import *
import sys
import time

# Global Variables
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Drive to Scan 			[Spider this drive]
scanDrive = 'C:\\'
# Drive to Save Maps/Logs 	[Save results to this drive]
saveDrive = 'F:\\'


# Folder Structure/Creation Routine
def createFolder():

	# Create Map Result Folder
	dirBase = r'%sHDSpider\Maps' % (saveDrive)

	# Create Acitivity Log Folder 
	dirBase2 = r'%sHDSpider\Logs' % (saveDrive) 

	# If !EXIST then Create Conditions
	if not os.path.exists(dirBase):
		os.makedirs(dirBase)
	if not os.path.exists(dirBase2):
		os.makedirs(dirBase2)

# Window Title Capturing Routine
def getWindowTitle():
	global wnt

	# Get window in focus
	hwnd = user32.GetForegroundWindow()

	# Extract the window's title
	title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(title),512)
	
	# Display title in console
	print "\n\n[ %s ]\n" % ( title.value)

	# Window Logs (Logs) - \Logs\
	wnt.writelines('%s : %s' % (title.value,time.strftime("%I:%M:%S")) + '\n')

	# Close
	kernel32.CloseHandle(hwnd)


# File Mapping Routine
def dMap(dlet):
	global wnt 

	# Using specified base dir and os.walk to crawl
	folder = dlet

	# Create Dirs (Maps and Logs)
	createFolder()

	# Maps/Logs (F:\Logs\Maps\)
	# Create Window Title Log File (Logs) - \Logs\
	wnt = open('%sHDSpider\Logs\Window_Titles.txt' % (saveDrive),'w')
	
	# Create text Files for Map Lags
	exes = open('%sHDSpider\Maps\exeList.txt' % (saveDrive),'w')
	txts = open('%sHDSpider\Maps\TxtList.txt' % (saveDrive),'w')
	docs = open('%sHDSpider\Maps\docList.txt' % (saveDrive),'w')
	docx = open('%sHDSpider\Maps\docxList.txt' % (saveDrive),'w')
	lnks = open('%sHDSpider\Maps\lnkList.txt' % (saveDrive),'w')
	jpgs = open('%sHDSpider\Maps\jpgList.txt' % (saveDrive),'w')
	bmps = open('%sHDSpider\Maps\BmpList.txt' % (saveDrive),'w')
	pngs = open('%sHDSpider\Maps\pngList.txt' % (saveDrive),'w')

	# DateStamp in Map Log
	exes.writelines('[Executables Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	txts.writelines('[Text Files Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	docs.writelines('[Windows Documents Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	docx.writelines('[Word Documents Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	lnks.writelines('[Shortcut Links Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	jpgs.writelines('[JPG Images Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	bmps.writelines('[BMP Images Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')
	pngs.writelines('[PNG Images Extracted - %s]:' % (time.strftime("%d/%m/%Y")) + '\n\n')

	# Pr-edeclared range sufficient for provided formats
	for i in range(1,9):
		for (paths, dirs, files) in os.walk(folder):
    			for file in files:

    				# Condition for EXE
    				if i==1:

    					# Exe Extraction..
        				if file.endswith(".exe"):

        					# Exe Mapping
        					print os.path.join(paths, file)
        					exes.writelines(os.path.join(paths, file) + '\n')
      						pass
        					
        			# Text File Extraction..
        			if i==2:

        				# Condition for TXT
        				if file.endswith(".txt"):
								
        					# Txt Mapping
							print os.path.join(paths, file)
							txts.writelines(os.path.join(paths, file) + '\n')
							pass
					
					# Document Extraction..
					if i==3:

						# Condition for regular documents
						if file.endswith(".doc"):
								
        					# Doc Mapping
							print os.path.join(paths, file)
							docs.writelines(os.path.join(paths, file) + '\n')
							pass

					# Word Docx Extraction..
					if i==4:

						# Condition for Microsoft Word documents
						if file.endswith(".docx"):
								
        					# Docx Mapping
							print os.path.join(paths, file)
							docx.writelines(os.path.join(paths, file) + '\n')
							pass
					
					# Shortcut Extraction..
					if i==5:

						# Condition for Shortcut Files
						if file.endswith(".lnk"):
								
        					# Shortcut Mapping
							print os.path.join(paths, file)
							lnks.writelines(os.path.join(paths, file) + '\n')
							pass

					# JPeg Extraction..
					if i==6:

						# Condition for JPG Images
						if file.endswith(".jpg"):
								
        					# JPEG Mapping
							print os.path.join(paths, file)
							jpgs.writelines(os.path.join(paths, file) + '\n')
							pass

					# Bitmap Extraction..
					if i==7:

						# Condition for BMP Images
						if file.endswith(".bmp"):
								
        					# Bitmap Mapping
							print os.path.join(paths, file)
							bmps.writelines(os.path.join(paths, file) + '\n')
							pass

					# PNG Extraction..
					if i==8:

						# Condition for PNG Images
						if file.endswith(".png"):
								
        					# PNG Mapping
							print os.path.join(paths, file)
							pngs.writelines(os.path.join(paths, file) + '\n')
							pass

# Counter Routine [1s]
def cnter():
	global cnt

	# Increment
	cnt = cnt + 1
	
	# 1 Second Delay
	sleep(1)

	# Capture and Log Window Title
	getWindowTitle()

	# Display Count Vale to Console
	print "\n%s\n" % (cnt)



def main():
	# Initialize
	global cnt
	global scanDrive

	# Count Var Value Default = 0
	cnt = 0

	# Activated. Prompt to insert Drive and Press enter to Start Mapping..
	x = raw_input("\nInsert External Device and Press ENTER.\n")

	# 1) Start Mapping (Maps)
	# Save to : /Maps/
	dMap(scanDrive)

	next = raw_input("\nWould you like to monitor this computer's activity? (y/n): ")
	if next == 'y':

		# 2) Start Monitoring (Logs)
		# Save to : /Logs/
		while(True):
			# Call Counter Routine
			cnter()

	else:
		return 0
		
# Activate
main()
	