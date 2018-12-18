import sys
import smtplib
from tqdm import tqdm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from time import sleep

print """
   _____                    _____     _ _         
  |     |___ ___ ___    ___|     |___|_| |___ ___ 
  | | | | .'|_ -|_ -|  | -_| | | | .'| | | -_|  _|
  |_|_|_|__,|___|___|  |___|_|_|_|__,|_|_|___|_|  
                                                
"""

# Email Details
gmail_user = ''
gmail_password = ''

# Load Text
try:
	f = open('targets.txt','r')
	print "  [1] Email List Loaded."
except:
	print "  [!] Email List Not Found! \n\n  [i] Create Text File 'targets.txt' \n"
	sys.exit()

Loaded = f.read().split('\n')
print "  [2] Email List Filtered.\n"

def main():

	while(True):
		cmd = raw_input(" Enter command> ")
		cmd = cmd.lower()
		if cmd == "start":
			mailer()
		elif cmd == "help":
			print """ 

	Mass eMailer - by LogicPy 

			"""
		elif cmd == "exit":
			sys.exit()
		else:
			print "\n Invalid command (type 'help' for command list) \n"

def mailer():

	subject = raw_input(" Enter Subject> ")
	body = raw_input(" Enter Body> ")

	if subject == "" or body == "":

		print "\n Please populate all fields."

		mailer()

	else:

		prmpt = raw_input("\n [ Press ENTER to activate ] \n")

		for dest in tqdm(Loaded):

			sent_from = gmail_user  
			to = [dest]  

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

			except:  
			    pass

main()