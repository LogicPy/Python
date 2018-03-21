from urllib2 import urlopen
import urllib2
from bs4 import BeautifulSoup as soup
import sys

# Playing with Beautiful Soup...

# BeautifulSoup based web bot - Newgrounds'
# Wayne Kenney - 2017

# Parsing Notes: 
# (Find all divs) 					- var = parsing.findAll("div")
# (Find all divs with class name)   - var = parsing.findAll("div",{"class":"forumthread-title"})

def ForumPosts():

	foo = []
	fay = []

	# Web Data Extraction
	# (1) Find all DIVs with class name "forumthread-title"..
	allparagraphs = parsing.findAll("div",{"class":"forumthread-title"})
	
	# (2) Find all links within extracted DIVs..
	for i in allparagraphs:
	# (3) Append links to list
		foo.append( i.findAll("a") )

	for x in foo:
	# (4) Show links
		#print x
		fay.append(find_between(str(x),'">','</a>'))

	for y in fay:
		print "Title: %s" % y


def gatherUsers():
	fi  = []
	users = parsing.findAll("strong")
	for i in users:
		fi.append(find_between(str(i),"<strong>","</strong>"))
		
	for pu in fi:
		print "User: %s" % pu

# Declare Website with User-Agent
site = "http://www.newgrounds.com/community"
hdr = {'User-Agent': 'Mozilla/5.0'}

# Initial Request
req = urllib2.Request(site,headers=hdr)
uclient = urlopen(req)

# Read Content (Grab HTML)
page = uclient.read()

# Close session after gathering HTML
uclient.close()

# Prepare to parse HTML
parsing = soup(page,"html.parser")

# Use findAll function to extract all Divs (can be cycled with loop)
alldivs = parsing.findAll("a")

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def Console():

	print "\nWelcome to Newgrounds!\n"

	while(True):
		con = raw_input("Enter Command: ")
		if con == "help":
			print """
	Commands:
		forum.posts - Gather recent Forum posts
		get.users   - Gather recent/active users
			"""
		elif con == "forum.posts":
			print "\n"
			ForumPosts()
			print "\n"
		elif con == "get.users":
			print "\n"
			gatherUsers()
			print "\n"
		else:
			print "\nYou have entered an invalid command.\n"


Console()