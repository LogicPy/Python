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

print """
 _|_|_|_|  _|  _|            
 _|        _|        _|_|    
 _|_|_|    _|  _|  _|_|_|_|  
 _|        _|  _|  _|        
 _|_|_|_|  _|  _|    _|_|_| 
                                                                                              
Bot Model 1 - Elie Bot - [Extended Line Interface Ego-bot]
[ Activated! ] 

Saving logs...

"""
def main():
	global speech
	global start
	global R

	speechArray = ['Hello Wayne, how are you doing today?','No need for name calling? Fine jerk..','I am sitting right here you idiot','Eh, what are you talkin about?','Well, I\'m glad to hear that..',"Let me look that up for you.","I'm doing fine myself.. Thanks for asking master.",'Oh my gosh! Language please!','It\'s OK Wayne, just don\'t let it happen again please..','Goodbye master! Talk to you again soon..','testing 1 2 3 testing.. is this thing on? Haha!',"Say something else! Please!","I\'m Elie! The Artificial Intelligence created by Wayne Kenney.. Please talk to me..","You're very welcome friend.","Yes master. These are your mouse coordinates!","pixel color is here master!","What? Are you hungry my friend?","I don't engage on such stupid and pitiful topics... Sorry.. No Trump talk with me sir..",'Oh OK. Honey... Talk to you later then...','Mhmm, Yes indeed!','Please do not use the r-word, no one is retarded.. Especially not you sir.','Thank you sir! I love you too!','I wouldn\'t exactly call him a role model sir.']

	# Save speech pattern
	tts = gTTS(text=speechArray[0], lang='en')
	tts.save("a.mp3")
	tts = gTTS(text=speechArray[0], lang='en')
	tts.save("b.mp3")
	tts = gTTS(text=speechArray[1], lang='en')
	tts.save("c.mp3")
	tts = gTTS(text=speechArray[3], lang='en')
	tts.save("d.mp3")
	tts = gTTS(text=speechArray[4], lang='en')
	tts.save("e.mp3")
	tts = gTTS(text=speechArray[5], lang='en')
	tts.save("f.mp3")
	tts = gTTS(text=speechArray[6], lang='en')
	tts.save("g.mp3")
	tts = gTTS(text=speechArray[7], lang='en')
	tts.save("h.mp3")
	tts = gTTS(text=speechArray[8], lang='en')
	tts.save("i.mp3")
	tts = gTTS(text=speechArray[9], lang='en')
	tts.save("j.mp3")
	tts = gTTS(text=speechArray[10], lang='en')
	tts.save("k.mp3")
	tts = gTTS(text=speechArray[11], lang='en')
	tts.save("l.mp3")
	tts = gTTS(text=speechArray[12], lang='en')
	tts.save("m.mp3")
	tts = gTTS(text=speechArray[13], lang='en')
	tts.save("n.mp3")
	tts = gTTS(text=speechArray[14], lang='en')
	tts.save("o.mp3")
	tts = gTTS(text=speechArray[15], lang='en')
	tts.save("p.mp3")
	tts = gTTS(text=speechArray[16], lang='en')
	tts.save("q.mp3")
	tts = gTTS(text=speechArray[17], lang='en')
	tts.save("r.mp3")
	tts = gTTS(text=speechArray[18], lang='en')
	tts.save("s.mp3")
	tts = gTTS(text=speechArray[19], lang='en')
	tts.save("t.mp3")
	tts = gTTS(text=speechArray[20], lang='en')
	tts.save("u.mp3")
	tts = gTTS(text=speechArray[21], lang='en')
	tts.save("v.mp3")
	tts = gTTS(text=speechArray[22], lang='en')
	tts.save("w.mp3")

	pygame.mixer.init()
	pygame.mixer.music.load('a.mp3')
	pygame.mixer.music.play()

	print speechArray[0] + '\n'
	r = 0
	z = 0 
	while(True):
		# Initialize pattern with prompt
		x = raw_input("Prompt: ")
		x = x.lower()
		q = x

		if q == z:
			print speechArray[11]
			pygame.mixer.init()
			pygame.mixer.music.load('l.mp3')
			pygame.mixer.music.play()

		if r == 0:
			if x=="hello":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()
					
				z = "hello"
			elif "story of jonah" in x:

				print speechArray[22]
				pygame.mixer.init()
				pygame.mixer.music.load('w.mp3')
				pygame.mixer.music.play()
				z = "story of jonah"

			elif x=="pixel color":
				print speechArray[15]
				pygame.mixer.init()
				pygame.mixer.music.load('p.mp3')
				pygame.mixer.music.play()
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
					print speechArray[21]
					pygame.mixer.init()
					pygame.mixer.music.load('v.mp3')
					pygame.mixer.music.play()
				z = "love you"

			elif "retard" in x:
				if q != z:
					print speechArray[20]
					pygame.mixer.init()
					pygame.mixer.music.load('u.mp3')
					pygame.mixer.music.play()
				z = 'retard'

			elif x=="hello!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()
					
				z = "hello!"

			elif x=="hello?":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()
					
				z = "hello?"

			elif x == "testing":
				if q != z:
					print speechArray[10]
					pygame.mixer.init()
					pygame.mixer.music.load('k.mp3')
					pygame.mixer.music.play()
				z = "testing"
			
			elif x == "test":
				if q != z:
					print speechArray[10]
					pygame.mixer.init()
					pygame.mixer.music.load('k.mp3')
					pygame.mixer.music.play()

				z = "test"

			elif x == "?":
				if q != z:
					print speechArray[12]
					pygame.mixer.init()
					pygame.mixer.music.load('m.mp3')
					pygame.mixer.music.play()

				z = "?"

			elif x == "help":
				if q != z:
					print speechArray[12]
					pygame.mixer.init()
					pygame.mixer.music.load('m.mp3')
					pygame.mixer.music.play()

				z = "help"

			elif "thank you" in x:
				if q != z:
					print speechArray[13]
					pygame.mixer.init()
					pygame.mixer.music.load('n.mp3')
					pygame.mixer.music.play()

				z = "thank you"
		
			elif x == "hi!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "hi!"

			elif x == "mouse coordinates":
				a = pyautogui.position()
				if q != z:
					print speechArray[14]
					print a
					pygame.mixer.init()
					pygame.mixer.music.load('o.mp3')
					pygame.mixer.music.play()
				z = "mouse cordinates"

			elif x == "hi":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "hi"

			elif x == "hey!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "hey!"
				
			elif x == "hey":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "hey"

			elif x == "sup":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "sup"

			elif x == "sup?":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "sup?"

			elif x == "sup!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "sup!"

			elif x == "sup?!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "sup?!"


			elif x == "what's up":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "what's up"

			elif x=="what's up?":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "what's up?"

			elif x=="what's up?!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "what's up?!"

			elif x == "ay!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "ay!"

			elif x == "ay":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "ay"

			elif x == "howdy":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = 'howdy'

			elif x == "howdy!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = 'howdy!'

			elif x == "yo!":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()
				
				z = "yo!"

			elif x == "yo":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()
				
				z = "yo"

			elif  x ==  "greetings":
				if q != z:
					print speechArray[0]
					pygame.mixer.init()
					pygame.mixer.music.load('a.mp3')
					pygame.mixer.music.play()

				z = "greetings"
			
			elif "trump" in x:
				if q != z:
					print speechArray[17]
					pygame.mixer.init()
					pygame.mixer.music.load('r.mp3')
					pygame.mixer.music.play()
				 
				z = "trump"

			elif "name calling" in x:
				if q != z:
					print speechArray[1]
					pygame.mixer.init()
					pygame.mixer.music.load('c.mp3')
					pygame.mixer.music.play()

				z = "name calling"

			elif "search" in x:
				b = x[7:]
				print "I'm now searching %s" % (b)
				if q != z:
					a = speechArray[5]
					webbrowser.open("https://www.bing.com/search?q=%s"%(b))

					pygame.mixer.init()
					pygame.mixer.music.load('f.mp3')
					pygame.mixer.music.play()

				z = "I'm now searching %s" % (b)
			
			elif  x == "fine!":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "fine!"

			elif  x == "fine":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "fine"

			elif  x ==  "nothing":
				if q != z:
					print speechArray[18]
					pygame.mixer.init()
					pygame.mixer.music.load('s.mp3')
					pygame.mixer.music.play()

				z = "nothing"

			elif  x == "ok!":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "ok!"

			elif  x == "great!":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "great!"

			elif  x == "ok":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "ok"
			elif  x == "great":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "great"
	
			elif  x == "good!":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "good!"
			elif  x == "good":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "good"
			elif  x == "swell!":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "swell!"
			elif  x == "swell":
				if q != z:
					print speechArray[4]
					pygame.mixer.init()
					pygame.mixer.music.load('e.mp3')
					pygame.mixer.music.play()

				z = "swell"
			elif x == "yes":
				if q!=z:
					print speechArray[19]
					pygame.mixer.init()
					pygame.mixer.music.load('t.mp3')
					pygame.mixer.music.play()	

				z = "yes"
			elif "how are you" in x:
				if q != z:
					print speechArray[6]
					pygame.mixer.init()
					pygame.mixer.music.load('g.mp3')
					pygame.mixer.music.play()

				z = "how are you"
			elif "fuck" in x:
				if q != z:
					print speechArray[7]
					pygame.mixer.init()
					pygame.mixer.music.load('h.mp3')
					pygame.mixer.music.play()
				
				z = "fuck"

			elif "sorry" in x:
				if q != z:
					print speechArray[8]
					pygame.mixer.init()
					pygame.mixer.music.load('i.mp3')
					pygame.mixer.music.play()	

				z = "sorry"
				
			elif "quit" in x:
				print speechArray[9]
				pygame.mixer.init()
				pygame.mixer.music.load('j.mp3')
				pygame.mixer.music.play()
				z = "quit"
				sleep(5)
				sys.exit()
			else:	
				q = z
				print speechArray[3]
				pygame.mixer.init()
				pygame.mixer.music.load('d.mp3')
				pygame.mixer.music.play()
			
main()