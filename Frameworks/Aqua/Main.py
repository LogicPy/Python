
# Authenticate Query Unification Application
# Wayne Kenney - 2015                                   
#  _____                 ___     ___ 
# |  _  |___ _ _ ___ ___|_  |   |   |
# |     | . | | | .'|___|_| |_ _| | |
# |__|__|_  |___|__,|   |_____|_|___|
#         |_|                        
# By Pythogen

# Main.py:

from subprocess import call
                                   
print' _____                 ___     ___ '
print'|  _  |___ _ _ ___ ___|_  |   |   |'
print'|     | . | | | . |___|_| |_ _| | |'
print'|__|__|_  |___|__,|   |_____|_|___|'
print'        |_|                        '
print 'Authenticate Query Unification Application - By Pythogen - 2015'

print '\n\nType ? for commands.\n'
def main():
	while(True):
		cmd = raw_input("cmd>")
		if cmd == 'run':
			call(["python","Frame.py"])
		elif cmd == '?':
			print '\nCommands:\n\n- run (Run framework)\n- convert (Convert header data to dictionary format for the framework)\n- quit\n'
		elif cmd == 'convert':
			call(["python","Convert.py"])
		elif cmd == 'quit':
			quit()
main()