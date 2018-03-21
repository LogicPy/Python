# Pythogen

# Reference: Three passwords per username Cycle / Switch to next three passwords in the list after full username Cycle

# Three passwords per username Cycle
# Specific pattern for username specific rate limits
# Enable greater time duration between specific usernames
# while still cycling all passwords.
# Three password attempts at a time per username,
# Any size password list and every user:password combo will 
# be attempted.

# Example [ Pattern illustrated ]:
# user1:pass1
# user1:pass2
# user1:pass3
# user2:pass1
# user2:pass2
# user2:pass3
# user3:pass1, etc...
# ...
# user1:pass4
# user1:pass5
# user1:pass6
# user2:pass4
# user2:pass5, etc....


import time

# Variables for indice control
a = 0
b = 3

def Cycle():
	# Keep slice values accessable
	global a
	global b

	# Load Username List
	text_file = open("users.txt", "r")
	# Load Password List
	text_file2 = open("pw.txt", "r")

	# Username Split Newline 
	user = text_file.read().split('\n')
	# Password Split Newline
	pw = text_file2.read().split('\n')

	# User cycle
	for u in user:
		# Password cycle with pw slice
		# Slice for specific pw range per user
		for p in pw[a:b]:
			# Print process
			print '%s:%s' % (u,p)
			time.sleep(1)

	# Slice variables increment
	a = a + 3
	b = b + 3
	# Recursive
	Cycle()

Cycle()
# Press enter to exit
x = raw_input("")
