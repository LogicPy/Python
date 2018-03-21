
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# Frame.py:

# Modules
import requests
from random import randint
import time
import os

# Program Information
print '\nLiveLeak Username Extractor\n'

# Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def processReq():

	# Shorten method
	global c

	fw = open('output.txt','w')

	with requests.Session() as c:
	
		while(True):
			# Starting..
			for i in range(1, 100):
				land = 'http://www.liveleak.com/subscription?a=browse&channel_token=04c_1302956196&container_id=channel_subscribers&items_per_page=5&ajax=1&page=%s' % (i)
				processReq.page = c.get(land)
				src = processReq.page.content
				elOne = '<a href="c/'
				elTwo = '"><img src'
				a =  find_between(src, elOne, elTwo )
				print a
				fw.writelines(a + '\n')

# Process Request
processReq()