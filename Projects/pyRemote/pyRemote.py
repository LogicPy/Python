                                  
#  _____     _   _                   
# |  _  |_ _| |_| |_ ___ ___ ___ ___ 
# |   __| | |  _|   | . | . | -_|   |
# |__|  |_  |_| |_|_|___|_  |___|_|_|
#       |___|           |___|        
# Can't get any more elite

# Enables remote command execution via Gmail

import imaplib
import smtplib
import time

# Login IMAP config:
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('pythogen@gmail.com', 'passxz')
# Login SMTP config:
GMAIL_USERNAME = "pythogen@gmail.com"
GMAIL_PASSWORD = "passxz"
recipient = "waynekenneyjr@gmail.com"

# Main routine:
def main():
	while(True):
		# Delay between each command check
		time.sleep(5)

		# Display most recent email
		cmdCheck = raw_email.find("echo.info")

		if cmdCheck == -1:
			print "Command not found..."
		else:
			print raw_email
			sendDat()

		configR()

def sendDat():

	email_subject = "I'm here!"
	body_of_email = "This is a requested broadcast."

	session = smtplib.SMTP('smtp.gmail.com', 587)
	session.ehlo()
	session.starttls()
	session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

	headers = "\r\n".join(["from: " + GMAIL_USERNAME,
    	                   "subject: " + email_subject,
        	               "to: " + recipient,
            	           "mime-version: 1.0",
                	       "content-type: text/html"])
                 
	content = headers + "\r\n\r\n" + body_of_email
	session.sendmail(GMAIL_USERNAME, recipient, content)
	print '\nSent mail\n'

# More configuration:
def configR():

	mail.list()

	mail.select("inbox")

	result, data = mail.search(None, "ALL")

	ids = data[0]
	id_list = ids.split()
	latest_email_id = id_list[-1]

	result, data = mail.fetch(latest_email_id, "(RFC822)")

	# Set variable to global for access
	# outside of ConfigR func
	global raw_email

	raw_email = data[0][1]

	# Call main function to start command listener
	main()

# Prepare...
configR()