
# Google Chrome History Search
# By Pythogen - 2018

# Search Chrome history using specified keyword

import os
import sqlite3
import operator
from collections import OrderedDict
import matplotlib.pyplot as plt
from time import sleep

def EPE_Main():
	# Kill Chrome process for password extraction
	os.system('taskkill /F /IM chrome.exe')

def parse(url):
	try:
		parsed_url_components = url.split('//')
		sublevel_split = parsed_url_components[1].split('/', 1)
		domain = sublevel_split[0].replace("www.", "")
		return domain
	except IndexError:
		print "Index[e]"

# Analysis function with keyword definition
def analyze(results):
	global arrHist
	arrHist = []

	histKeywrd = raw_input("\nEnter a keyword >")

	for site, count in sites_count_sorted.items():
		
		if histKeywrd in str(site):
			print "\n[%s] - content found\n" % (histKeywrd)
			arrHist.append(site)
			
		print site, count

	historyExtracted(arrHist)

# Pass history results for output
def historyExtracted(histList):
	print "\n\n-----------------------"
	print "History Search Results:"
	print "-----------------------\n"
	for i in histList:
		print i
	print "\nExtraction Complete!\n"

# Chrome's path
data_path = os.path.expanduser('~')+"\AppData\Local\Google\Chrome\User Data\Default"
files = os.listdir(data_path)

history_db = os.path.join(data_path, 'history')

# Using SQL to query Chrome's DB
c = sqlite3.connect(history_db)
cursor = c.cursor()
select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
cursor.execute(select_statement)

results = cursor.fetchall() #tuple

# Dictionary for iterations
sites_count = {}

for url, count in results:
	url = parse(url)
	if url in sites_count:
		sites_count[url] += 1
	else:
		sites_count[url] = 1

sites_count_sorted = OrderedDict(sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True))

EPE_Main()
analyze (sites_count_sorted)