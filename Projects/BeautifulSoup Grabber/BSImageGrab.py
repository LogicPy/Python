
# BeautifulSoup Grabber

# This is a console based script that allows the user to grab all images, paragraphs or headings from a specified website and 
# it generates a styled HTML file for viewing the downloaded content.

# Just a practice script

# Wayne Kenney 2017

from urllib2 import urlopen
from bs4 import BeautifulSoup as soup

# Styles for HTML output
styles = """
<style>
html
	{
	background-color: #0C2025;
	}\n
img
	{ 
	padding:5px;
	border-style:solid;
	border-width: 2px; 
	border-color: #DAD5B1; 
	border-radius: 5px; 
	margin-left: auto;
	margin-right: auto;
	display: block;
	}
</style>
		"""

# Function for Image Grabbing
def imgparse():
	global x
	# Direct urllib to user's provided website
	uclient = urlopen(x)

	# Read HTML content
	grab_cnt = uclient.read()

	uclient.close()

	# Prepare parsing
	parsing = soup(grab_cnt,"html.parser")

	# Find all img tags
	imageGrab = parsing.findAll("img")

	# Declarations for Cycle
	a = []
	i = 0
	# Cycle parsed list of parsed images
	for imgGrabbed in imageGrab:
		# if i is 0, then create the text file
		if i == 0:
			a.append(str(imgGrabbed))
			# First cycle write to.
			file = open("extracted.html","w")
			file.write(styles)
			file.write(a[i] + '\n<br><br>')
			i=i+1
		# otherwise, if i is greater than 0, append to text file
		elif i > 0:
			a.append(str(imgGrabbed))
			# Second cycle and above, append to.
			file = open("extracted.html","a")
			# prevent out of range using condition with list length
			if i <= len(a):
				file.write(a[i] + '\n<br><br>')
			i = i + 1

	file.close()
	print "\n  Process complete! Check the script directory for the generated HTML file."
	prompt()


# Main Prompt - Select Command
def prompt():
	global x
	inp = raw_input("\n What would you like to do?> ")
	if inp == "help":
		print """
	Commands:
		image.grab - (Grab all images)
		p.grab - (Grab all paragraphs)
		h1.grab - (Grab all h1 headers)
		exit - (Exit script)
		"""	 
	   	prompt()
	elif inp == "image.grab":
	 	x = raw_input("\n Enter URL: ")
	 	imgparse()
	elif inp == "exit":
		print "\n  Goodbye!"
		exit()
	else:
		print "\n  You have entered an invalid command. Type 'help' for a list of commands."
		prompt()

prompt()