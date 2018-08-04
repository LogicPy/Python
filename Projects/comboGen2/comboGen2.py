import sys

# ComboGen2
# Two character combination generator
# Coded by LogicPy

choice = 0
genAr = []

def calculate():
	global choice

	twochar1 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

	if choice == 1:
		num1 = map(str, raw_input('Enter a range: ').split(','))

		for i in num1:
			for x in num1:
				print "%s%s" % (i,x)
				genAr.append(i + x)

	if choice == 2:
		for i in twochar1:
			for u in twochar1:
				print "%s%s" % (i,u)
				genAr.append(i + u)

	for save in genAr:
		f = open('list.txt','a')
		f.write(save + '\n')
		f.close()

def main():
	global choice

	print "\nPython two-character username generator (For dictionary attacks)\n"

	while(True):
		cmd = raw_input("Enter command> ")
		cmd = cmd.lower()
		# input specific chars seperated by commas
		if cmd == "input":
			choice = 1
			calculate()
		# calculate stored chars and then generate
		if cmd == "twochar":
			choice = 2
			calculate()
		if cmd == "help":
			print """
	------------------------ help ------------------------
	input   - enter combination characters (seperated by comma)
	twochar - use pre-existing array of characters 
	exit    - Quit
	------------------------------------------------------
			"""
		elif cmd == "exit":
			sys.exit()
		else: 
			print "\n Invalid command (type 'help' for command list)\n"

main()