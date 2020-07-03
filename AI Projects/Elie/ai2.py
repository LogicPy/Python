import pyautogui
from gtts import gTTS
import os
from time import sleep
import time
import random
from pynput import keyboard
import pyglet
import requests
import pygame
import webbrowser
import sys
import tkinter
# Intelligence engine
import pyttsx3


def main():
	global r
	global engine
	global rate
	global voices

	print """
	                             
	 _|_|_|_|  _|  _|            
	 _|        _|        _|_|    
	 _|_|_|    _|  _|  _|_|_|_|  
	 _|        _|  _|  _|        
	 _|_|_|_|  _|  _|    _|_|_|  
	                             
	 Enable Lite Interaction ego-bot
	 """

	speechArray = ['Hello Wayne, how are you doing today?','No need for name calling? Fine jerk..','I am sitting right here you idiot','Eh, what are you talkin about?','Well, I\'m glad to hear that..',"Let me look that up for you.","I'm doing fine myself.. Thanks for asking master.",'Oh my gosh! Language please!','It\'s OK Wayne, just don\'t let it happen again please..','Goodbye master! Talk to you again soon..','testing 1 2 3 testing.. is this thing on? Haha!',"Say something else! Please!","I\'m Elie! The Artificial Intelligence created by Wayne Kenney.. Please talk to me..","You're very welcome friend.","Yes master. These are your mouse coordinates!","pixel color is here master!","What? Are you hungry my friend?","I don't engage on such stupid and pitiful topics... Sorry.. No Trump talk with me sir..",'Oh OK. Honey... Talk to you later then...','Mhmm, Yes indeed!','Please do not use the r-word, no one is retarded.. Especially not you sir.','Thank you sir! I love you too!','I wouldn\'t exactly call him a role model sir.']
	
	engine = pyttsx3.init()
	rate = engine.getProperty('rate')
	voices = engine.getProperty('voices')   
	engine.setProperty('rate', 125) 
	engine.setProperty('voice', voices[1].id)   # Female voice

	print(speechArray[0] + '\n')
	r = 0
	z = 0 
	while(True):
		# Initialize pattern with prompt
		x = raw_input("Prompt: ")
		x = x.lower()
		q = x

		if q == z:
			print(speechArray[11])
			engine.say(speechArray[11])
			engine.runAndWait()

		if r == 0:
			if x=="hello":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()
					
				z = "hello"
			elif "story of jonah" in x:

				print(speechArray[22])
				engine.say(speechArray[22])
				engine.runAndWait()
					
				z = "story of jonah"

			elif x=="pixel color":
				print (speechArray[15])
				engine.say(speechArray[15])
				engine.runAndWait()
				x, y = pyautogui.position()

				pixelColor = pyautogui.screenshot().getpixel((x, y))
				ss = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
				ss += ' RGB: (' + str(pixelColor[0]).rjust(3)
				ss += ', ' + str(pixelColor[1]).rjust(3)
				ss += ', ' + str(pixelColor[2]).rjust(3) + ')'
				print(ss)
				sleep(1.0)

			elif "love you" in x:
				if q != z:
					print(speechArray[21])
					engine.say(speechArray[21])
					engine.runAndWait()
				z = "love you"

			elif "retard" in x:
				if q != z:
					print(speechArray[20])
					engine.say(speechArray[20])
					engine.runAndWait()
				z = 'retard'

			elif x=="hello!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()
					
				z = "hello!"

			elif x=="hello?":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()
					
				z = "hello?"

			elif x == "testing":
				if q != z:
					print(speechArray[10])
					engine.say(speechArray[10])
					engine.runAndWait()
				z = "testing"
			
			elif x == "test":
				if q != z:
					print(speechArray[10])
					engine.say(speechArray[10])
					engine.runAndWait()

				z = "test"

			elif x == "?":
				if q != z:
					print(speechArray[12])
					engine.say(speechArray[12])
					engine.runAndWait()

				z = "?"

			elif x == "help":
				if q != z:
					print(speechArray[12])
					engine.say(speechArray[12])
					engine.runAndWait()
				z = "help"

			elif "thank you" in x:
				if q != z:
					print(speechArray[13])
					engine.say(speechArray[13])
					engine.runAndWait()

				z = "thank you"
		
			elif x == "hi!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = "hi!"

			elif x == "mouse coordinates":
				a = pyautogui.position()
				if q != z:
					print(speechArray[14])
					print(a)
					engine.say(speechArray[14])
					engine.runAndWait()
				z = "mouse cordinates"

			elif x == "hi":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = "hi"

			elif x == "hey!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = "hey!"
				
			elif x == "hey":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = "hey"

			elif x == "sup":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "sup"

			elif x == "sup?":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "sup?"

			elif x == "sup!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "sup!"

			elif x == "sup?!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "sup?!"


			elif x == "what's up":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "what's up"

			elif x=="what's up?":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = "what's up?"

			elif x=="what's up?!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "what's up?!"

			elif x == "ay!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "ay!"

			elif x == "ay":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "ay"

			elif x == "howdy":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = 'howdy'

			elif x == "howdy!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				z = 'howdy!'

			elif x == "yo!":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				
				z = "yo!"

			elif x == "yo":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()

				
				z = "yo"

			elif  x ==  "greetings":
				if q != z:
					print(speechArray[0])
					engine.say(speechArray[0])
					engine.runAndWait()


				z = "greetings"
			
			elif "trump" in x:
				if q != z:
					print(speechArray[17])
					engine.say(speechArray[17])
					engine.runAndWait()
				 
				z = "trump"

			elif "name calling" in x:
				if q != z:
					print(speechArray[1])
					engine.say(speechArray[1])
					engine.runAndWait()


				z = "name calling"

			elif "search" in x:
				b = x[7:]
				print ("I'm now searching %s" % (b))
				if q != z:
					a = speechArray[5]
					webbrowser.open("https://www.bing.com/search?q=%s"%(b))

					engine.say(speechArray[5])
					engine.runAndWait()


				z = "I'm now searching %s" % (b)
			
			elif  x == "fine!":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()


				z = "fine!"

			elif  x == "fine":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()


				z = "fine"

			elif  x ==  "nothing":
				if q != z:
					print(speechArray[18])
					engine.say(speechArray[18])
					engine.runAndWait()


				z = "nothing"

			elif  x == "ok!":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()


				z = "ok!"

			elif  x == "great!":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "great!"

			elif  x == "ok":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()


				z = "ok"
			elif  x == "great":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "great"
	
			elif  x == "good!":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "good!"
			elif  x == "good":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "good"
			elif  x == "swell!":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "swell!"
			elif  x == "swell":
				if q != z:
					print(speechArray[4])
					engine.say(speechArray[4])
					engine.runAndWait()

				z = "swell"
			elif x == "yes":
				if q!=z:
					print(speechArray[19])
					engine.say(speechArray[19])
					engine.runAndWait()

				z = "yes"
			elif "how are you" in x:
				if q != z:
					print(speechArray[6])
					engine.say(speechArray[6])
					engine.runAndWait()

				z = "how are you"
			elif "fuck" in x:
				if q != z:
					print(speechArray[7])
					engine.say(speechArray[7])
					engine.runAndWait()
				
				z = "fuck"

			elif "sorry" in x:
				if q != z:
					print(speechArray[8])
					engine.say(speechArray[8])
					engine.runAndWait()

				z = "sorry"
				
			elif "quit" in x:
				print(speechArray[9])
				engine.say(speechArray[9])
				engine.runAndWait()
				z = "quit"
				sleep(5)
				sys.exit()
			else:	
				q = z
				print(speechArray[3])
				engine.say(speechArray[3])
				engine.runAndWait()
			
main()