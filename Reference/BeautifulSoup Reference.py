

# BeautifulSoup reference...
# Very basic stuff. Memorized, but still a nice organized scraping reference.

# Import all modules
from urllib2 import urlopen
from bs4 import BeautifulSoup as soup

def waynecool():
	# Navigate to url using urlopen function of urllib2 module
	uclient = urlopen("http://wayne.cool/")

	# read content of page. Store HTML in page variable
	page = uclient.read()

	# Close session after gathering HTML
	uclient.close()

	# Prepare to parse HTML
	parsing = soup(page,"html.parser")

	# Find first h2 element
	print parsing.h2

	# Use findAll function to extract all Divs (can be cycled with loop)
	alldivs = parsing.findAll("div")

	# Print last element in div list
	print alldivs[-1]

	# Var for Div Count
	i = 0
	# Cycle divs
	for sel_div in alldivs:
		# Increment for counting divs
		i=i+1
		print "\n(%s) - Div: %s" % (i,sel_div)

	# Find all paragraph tags with class name 'vsc'
	allparagraphs = parsing.findAll("p",{"class":"vsc"})

	# Extract/Display paragraph tag with class 'vsc'
	print allparagraphs


# Scrape personal website ¯\_(ツ)_/¯
waynecool()