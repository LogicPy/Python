from bs4 import BeautifulSoup
from time import sleep
import requests

arEx = []
arFin = []

keyword = "WordPress"

keywords = open("keywords.txt", "r")
kwords = keywords.read().split('\n')

banner = """
  ____  _                _____       _     _           
 |  _ \(_)              / ____|     (_)   | |          
 | |_) |_ _ __   __ _  | (___  _ __  _  __| | ___ _ __ 
 |  _ <| | '_ \ / _` |  \___ \| '_ \| |/ _` |/ _ \ '__|
 | |_) | | | | | (_| |  ____) | |_) | | (_| |  __/ |   
 |____/|_|_| |_|\__, | |_____/| .__/|_|\__,_|\___|_|   
                 __/ |        | |                      
                |___/         |_|       
 - WordPress Powered Website Extractor -             
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

	saveEm = open("gathered.txt","w")
	for p in arFin:
		saveEm.write(p + "\n")
	saveEm.close()

main()