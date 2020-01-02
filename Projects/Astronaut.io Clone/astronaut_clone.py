import socket
import requests
from time import sleep
import random
from random import randint
import webbrowser


#Used for finding values between tags
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Randomize selection between MOV or IMG
arr = ['MOV ','IMG ']
arrnum = randint(0, 1)
x = randint(0001, 9999)

#randomized number with new identifier MOV or IMG
print arr[arrnum]+ str(x)

# Initial generated Request
req =  requests.get("https://www.youtube.com/results?search_query=" + arr[arrnum]+ str(x))
print "Getting first link.."

# Get between tags to find new refreshed link
x = find_between(req.content,'<link rel="alternate" media="handheld" href="','"><link rel="alternate"')
b = x
print x 

# Go to new link (Second Request)!
req2 = requests.get(b)

# Get (new html to check)
r = find_between(req2.content,'<a aria-hidden="true"  href="/watch','" class=" yt-uix-sessionlink')
print "Getting new link.\n"

print r
x = r

# Print finalized html link! :D
url = 'https://www.youtube.com/watch' + x

print 'Now viewing: ' + url

# Open with webbrowser module! ;)
webbrowser.open(url)
