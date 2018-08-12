
# Email Spider - Email Extractor
# Coded by LogicPy

from bs4 import BeautifulSoup
from time import sleep
import requests
import sys
import random
import string
import re
from tqdm import tqdm

bingVal = 0
bingVal2 = 0

banner = """                                                             
           ____                      ,
          /---.'.__             ____//
               '--.\           /.---'
          _______  \\         //
        /.------.\  \|      .'/  ______
       //  ___  \ \ ||/|\  //  _/_----.\__
      |/  /.-.\  \ \:|< >|// _/.'..\   '--'
         //   \'. | \'.|.'/ /_/ /  \\
        //     \ \_\/" ' ~\-'.-'    \\
       //       '-._| :H: |'-.__     \\
      //           (/'==='\)'-._\     ||
      ||                        \\    \|
      ||                         \\    '
      |/                          \\
                                   ||
                                   ||
                                   \\

   _____           _ _    _____     _   _         
  |   __|_____ ___|_| |  |   __|___|_|_| |___ ___ 
  |   __|     | .'| | |  |__   | . | | . | -_|  _|
  |_____|_|_|_|__,|_|_|  |_____|  _|_|___|___|_|  
                               |_|                                                           
  - Coded by LogicPy -
"""

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def main():
  global bingVal
  global bingVal2

  print banner

  v = 0

  while(v==0):
    cmd = raw_input(" Command> ")
    cmd = cmd.lower()
    if cmd == "bing.scan":
      bingVal = raw_input(" Enter randomizer value (2-6): ")
      bingVal = int(bingVal)
      bingVal2 = raw_input(" \n 1) All Services\n 2) Gmail\n 3) Yahoo\n 4) Hotmail\n 5) Outlook\n\n Enter values: ")
      bingVal2 = int(bingVal2)
      scan()

    elif cmd == "help":
      print """
      --------------------------------------
      -------------- [ Help ] --------------
      Commands:

       bing.scan  - Use bing extractor
       info       - Script information
       exit       - Quit
      --------------------------------------
      --------------------------------------
        """
    elif cmd == "info":
      info()
    elif cmd == "exit":
      sys.exit()
    else:
      print "\n [Invalid command]\n"

def info():
  print """
  -------------------------------------------------------
  -------------------- [Information] --------------------

  This script extracts email addresses from the internet.
  -------------------------------------------------------
      """

def random_generator(bval, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(bval))

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def remove_duplicates(input_list):
  if input_list == []:
    return []

  input_list=sorted(input_list)

  output_list = [input_list[0]]
  for item in input_list:
    if item >output_list[-1]:
      output_list.append(item)
  return output_list  

def scan():
  global bingVal2

  print "\n [Scanner Activated]\n"

  for cycle in range(1,999999):

    x = "contact " + random_generator(bingVal)

    urlCon = "https://www.bing.com/search?q=%s" % (x)

    r  = requests.get(urlCon)

    y = find_between(r.text,'="b_algo"><h2><a href="','"')

    #print y

    if y != "":

      try:
        r2 = requests.get(y)

        y2 = r2.content

        emails = re.findall(r'[\w\.-]+@[\w\.-]+', y2) 

        filtered = remove_duplicates(emails)

        for email in filtered:
          if bingVal2 == 1:
            if "gmail" in email or "yahoo" in email or "hotmail" in email or "outlook" in email:
              print " %s" % (email)
              f = open('list.txt','a')
              f.write(email + '\n')
              f.close()
          elif bingVal2 == 2:
            if "gmail" in email:
              print " %s" % (email)
              f = open('list.txt','a')
              f.write(email + '\n')
              f.close()
          elif bingVal2 == 3:
            if "yahoo" in email:
              print " %s" % (email)
              f = open('list.txt','a')
              f.write(email + '\n')
              f.close()
          elif bingVal2 == 4:
            if "hotmail" in email:
              print " %s" % (email)
              f = open('list.txt','a')
              f.write(email + '\n')
              f.close()
          elif bingVal2 == 5:
            if "outlook" in email:
              print " %s" % (email)
              f = open('list.txt','a')
              f.write(email + '\n')
              f.close()
          else:
            sys.exit()
      except:
        pass

main()