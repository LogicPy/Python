
import sys

def main():

	print "\nPassword List Manager 1.1\nWayne Kenney\nJanuary 24th, 2017\n"
	print "\nWelcome Wayne.."
	print "\nInput List: /listy.txt"
	print "Output List: /listy2.txt\n"
	print "Enter a command for list modification (type: 'help' for command list)\n"

	while(True):
		inp = raw_input("Command: ")
		inp = inp.lower()
		if inp == "help":
			print "\n-------Commands-------\nchar.min - Set minimum character limit\ndupe.kill - Remove duplicates\nlisty.cont - Show loaded list or add more passwords\nsave.breach - Save/store cracked username:password combination\nview.breach - Review saved cracks\nclear.breach - Clear breach list\nexit - Close application\n----------------------\n"
		elif inp == "char.min":
			lmt = raw_input("\nEnter minimum limit: ")
			charLimit(lmt)
		elif inp == "listy.cont":

			listyconf = raw_input("Add passwords or view them? (input/load): ")
			listyconf = listyconf.lower()
			if listyconf == "input":
				addpw2list = raw_input("Enter password: ")
				listycontLoad = open("listy.txt", "a")
				listycontLoad.write(addpw2list + "\n")
				listycontLoad.close()
			elif listyconf == "load":
				listycontLoad = open("listy.txt", "r").read().split('\n')
				listycontArr = []
				print "\nListy content:\n"
				for listyDisplay in listycontLoad:
					print listyDisplay
				print ""
			else:
				print "Invalid option.. Returning to main function."

		elif inp == "dupe.kill":
			dupeKill()

		elif inp == "save.breach":
			saveUsr = raw_input("Enter username: ")
			savePw = raw_input("Enter password: ")
			saveIT = open("saved.txt", "a")
			saveIT.write(saveUsr + ":" + savePw + "\n")
			saveIT.close()
			print "\nHack saved!\n"
		elif inp == "view.breach":
			breachLoad = open("saved.txt", "r").read().split('\n')
			breachArr = []
			print "\nYour cracks:\n"
			for breachLoaded in breachLoad:
				print breachLoaded
			print ""
		elif inp == "clear.breach":
			conf = raw_input("Are you sure you want to clear your crack list? (y/n): ")
			conf = conf.lower()
			if conf == "y":
				print "\nBreach list cleared!\n"
				listyClearLoad = open("saved.txt", "w")
				listyClearLoad.write("")
				listyClearLoad.close()
			elif conf == "n":
				print "\nBreach list not cleared...\n"
			else:
				print "\nInvalid input. List not cleared.\n"
		elif inp == "exit":
			sys.exit(1)
		else:
			print "\nYou have entered an invalid command..\n"

def dupeKill():
	text_fileinit = open("listy2.txt", "w")
	text_fileinit.write("")
	text_fileinit.close()
	
	# Load list
	text_file = open("listy.txt", "r")
	# Split newline
	t = text_file.read().split('\n')
	
	# Filter duplicates
	s = []
	for i in t:
		if i not in s:
			s.append(i)

	# Save without duplicates
	for x in s:
		text_file = open("listy2.txt", "a")
		text_file.write(x + "\n")
		text_file.close()

	print "\nDuplicates removed.\n"

def charLimit(lim):

	text_fileinit = open("listy2.txt", "w")
	text_fileinit.write("")
	text_fileinit.close()

	# Load list
	text_file = open("listy.txt", "r")

	# Split newline
	listI = text_file.read().split('\n')

	# Catch array
	catchDat = []
	remArr = []

	# Iterate and filter
	for lst in listI:
		if len(lst) >= int(lim):
			catchDat.append(lst)
			print lst
		else:
			remArr.append(lst)

	print "\n--Passwords Filtered--\n"
	for remItems in remArr:
		
		print remItems
	print "----------------------\n"

	for ctch in catchDat:
		text_file = open("listy2.txt", "a")
		text_file.write(ctch + "\n")
		text_file.close()

	# Back to main
	main()

main()