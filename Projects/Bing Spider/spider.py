from bs4 import BeautifulSoup
from time import sleep
import requests
import sys

arEx = []
arFin = []

keyword = "WordPress"

keywords = open("keywords.txt", "r")
kwords = keywords.read().split('\n')

banner = """                                                             
 _____ _            _____     _   _            ___     ___   
| __  |_|___ ___   |   __|___|_|_| |___ ___   |_  |   |_  |  
| __ -| |   | . |  |__   | . | | . | -_|  _|   _| |_ _ _| |_ 
|_____|_|_|_|_  |  |_____|  _|_|___|___|_|    |_____|_|_____|
            |___|        |_|                                  
 - WordPress Website Gathering Tool -             

"""

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def main():
	global arEx
	global keyword
	global kwords

	print banner

	v = 0

	while(v==0):
		cmd = raw_input(" Command> ")
		if cmd == "run":
			scan()
		elif cmd == "help":
			print "\n [Commands]\n\n run - activate scanner\n rate.tester - check scan results for rate limit (use after scan) \n info - script information\n exit - exit script\n"
		elif cmd == "info":
			info()
		elif cmd == "exit":
			sys.exit()
		elif cmd == "rate.tester":
			print "\n [Rate Limit Tester ]\n"
			print " To be included soon. Check back for version 1.2 ...\n"
		else:
			print "\n [Invalid command]\n"

def info():
	print """
 [Information]\n\n This script allows to quickly find WordPress targets for web pen testing. 
 The script uses Bing to search your specified keywords then it checks the 
 content of every resulting link to determine if they are running WordPress.

 Edit 'keywords.txt' and insert keywords (example: 'food blog')
 Run script and type 'run' to begin.
 The results will be saved to 'gathered.txt'.

 Optional: Use rate limit tester to check if targets are vulnerable to 
 dictionary attacks.

 Review results and organize targets.
 Finally use WP-Knight or WPScan to attack targets.

 Note: This script is not intended for malicious purposes.

 Written by LogicPy (Wayne Kenney)
			"""

def scan():
	global arEx
	
	print "\n [Scanner Activated]\n"

	for x in kwords:

		print " ---------------- %s ----------------" % (x)

		urlCon = "https://www4.bing.com/search?q=%s" % (x)

		r  = requests.get(urlCon)

		data = r.text

		soup = BeautifulSoup(data,"lxml")

		for link in soup.find_all('a'):
			ar = link.get('href')
			try:
				if "http" in ar:
					arEx.append(ar)
			except:
				pass

		for i in arEx:
			try:
				cr = requests.get(i)
				grbsrc = cr.text.encode("utf-8")
				if keyword in grbsrc:
					print i
					arFin.append(i)
			except:
				pass
		arEx = []

	saveEm = open("gathered.txt","w")
	for p in arFin:
		saveEm.write(p + "\n")
	saveEm.close()

main()