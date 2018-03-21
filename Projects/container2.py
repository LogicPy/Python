# Container/Water calculator
# Wayne Kenney - 2017

# Finding amount of water between containers

inp_Height = [3,2,2,5,4,3,2,3,3,3,4,4,3]

# Features:
# I've added an input prompt to enable a user to customize his/her own
# set. The default set is [3,2,2,5,4,3,2,3,3,3,4,4,3] and you can process
# it by typing the command "default", otherwise if you'd like to use your
# own height values simply use the command "custom".


def prompt():

	custom = []
	custom2 = []

	while(True):
		cmd = raw_input("Enter command (type 'help' for list of commands): ")
		if cmd == "help":
			print """
		Commands: 
			default - [3,2,2,5,4,3,2,3,3,3,4,4,3]
			custom  - Create your own height list
			"""
		elif cmd == "custom":
			while(True):
				cset = raw_input("\nEnter Set Value one at a time (type END when finished): ")
				if cset == "END" or cset == 'end':

					for i in custom:
						# Convert from string to int and add to new list
						custom2.append(int(i))

					print '\nYour set %s' % (custom2)
					print 'Passing to water...\n'
					# pass custom list to water function
					water(custom2)
					break

				else:
					custom.append(cset)
		elif cmd == "default":
			# otherwise, use default list
			water(inp_Height)


def water(inp_Height):

	water = 0
	left = []
	right = []

	print '\nInput heights: %s\n' % (inp_Height)

	seq = inp_Height[0]

    # Scan left to right
	for height in inp_Height:
		# Max accumulation for left to right
		if (height > seq):
			seq = height
		left.append(seq)
	
	print 'Left to right scan: %s\n' % (left)
	

	seq = inp_Height[-1]

    # Scan right to left
	for height in reversed(inp_Height):
		# Max accumulation for right to left
		if (height > seq):
			seq = height		
		right.insert(0, seq)
	
	print 'Right to left scan: %s\n' % (right)

	#
	for i, height in enumerate(inp_Height):
		water = water + min(left[i], right[i]) - height
	print "\nFinal result: %s" % (water)
	print "%s containers of water between containers.\n" % (water)
	return water

prompt()
